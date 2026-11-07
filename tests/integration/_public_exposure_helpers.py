"""Trusted child probes and real installed-metadata fixtures for CLI exposure."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_CHILD = r"""
import contextlib,json,logging,os,runpy,sys
from pathlib import Path
source,owned,operation,payload=sys.argv[1:]; sys.path.insert(0,source)
owned=Path(owned).resolve()
for name in ['home','state','runtime','tmp']:
    (owned/name).mkdir(exist_ok=True)
os.environ.update(HOME=str(owned/'home'),SCITEX_DIR=str(owned/'state'),
                  XDG_RUNTIME_DIR=str(owned/'runtime'),TMPDIR=str(owned/'tmp'))
logging.getLogger().addHandler(logging.NullHandler())
def guard(event,args):
    if event=='subprocess.Popen':
        argv=args[1]
        if not (request.get('allow_owned_console') and isinstance(argv,(list,tuple))
                and len(argv)>=6 and argv[0]==sys.executable and argv[1]=='-c'
                and argv[3:5]==['owned_parser','main']
                and argv[5] in {'scitex-owned-parser','owned-parser'}):
            raise AssertionError('discovery attempted an unapproved process operation')
    if event in {'socket.connect','socket.bind'}:
        raise AssertionError('discovery attempted a network operation')
    if event=='open':
        mode,flags=args[1:3]
        write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write and not isinstance(args[0],int) and not Path(args[0]).resolve().is_relative_to(owned):
            raise AssertionError('discovery attempted an unowned write')
    if event in {'os.mkdir','os.remove','os.rmdir','os.chmod','os.chown'}:
        if not isinstance(args[0],int) and not Path(args[0]).resolve().is_relative_to(owned):
            raise AssertionError('discovery attempted an unowned mutation')
    if event in {'os.rename','os.link','os.symlink'}:
        if any(not Path(path).resolve().is_relative_to(owned) for path in args[:2]):
            raise AssertionError('discovery attempted an unowned path mutation')
sys.addaudithook(guard)
request=json.loads(payload)
if request.get('fixture_site'):
    sys.path.insert(0,request['fixture_site'])
    os.environ['PYTHONPATH']=request['fixture_site']
executed=[]
def trace(frame,event,arg):
    if event=='call' and frame.f_code.co_name=='<module>':
        filename=frame.f_code.co_filename.replace('\\','/')
        if any('/'+name+'/' in filename for name in request.get('peers',[])):
            executed.append(filename)
sys.setprofile(trace); import scitex
bootstrap_peer_execution=sorted(set(executed)); executed.clear()
if operation=='invoke':
    sys.argv=['scitex',*request['args']]
    if request.get('complete'):
        os.environ.update(_SCITEX_COMPLETE='bash_complete',COMP_WORDS=request['complete'],COMP_CWORD=str(len(request['complete'].split())))
    # Capture actual OS descriptors too: a certified console uses a real child.
    original_out,original_err=os.dup(1),os.dup(2)
    outpath,errpath=owned/'stdout.txt',owned/'stderr.txt'
    with outpath.open('w+') as output,errpath.open('w+') as error:
        try:
            os.dup2(output.fileno(),1)
            os.dup2(error.fileno(),2)
            with contextlib.redirect_stdout(output),contextlib.redirect_stderr(error):
                try:
                    runpy.run_module('scitex',run_name='__main__')
                    code=0
                except SystemExit as exc:
                    code=exc.code if isinstance(exc.code,int) else (0 if exc.code is None else 1)
                finally:
                    output.flush()
                    error.flush()
        finally:
            os.dup2(original_out,1)
            os.dup2(original_err,2)
            os.close(original_out)
            os.close(original_err)
    result={'code':code,'stdout':outpath.read_text(),'stderr':errpath.read_text(),
            'peer_imports':sorted(set(executed)),
            'bootstrap_peer_execution':bootstrap_peer_execution}
elif operation=='developer-listing':
    import click
    from scitex.cli.dev import dev
    ctx=click.Context(dev)
    listed=dev.list_commands(ctx)
    resolved={name:dev.get_command(ctx,name) for name in listed}
    result={'listed':listed,
            'unresolved':[name for name,command in resolved.items() if command is None],
            'hidden':[name for name,command in resolved.items() if command is not None and command.hidden]}
elif operation=='developer-aliases':
    import click
    from scitex.cli.main import cli
    from scitex.cli._lazy_subcommands import DEV_COMMANDS,DEV_PEERS
    dev=cli.get_command(click.Context(cli),'dev')
    registered={name:cli.commands.get(name) for name in DEV_COMMANDS|DEV_PEERS}
    result={'registered':[name for name,command in registered.items() if command is not None],
            'unresolved':[name for name,command in registered.items()
                          if command is not None and dev.get_command(click.Context(dev),name) is None],
            'absent':[name for name in DEV_PEERS
                      if dev.get_command(click.Context(dev),name) is None]}
elif operation in {'web-eligibility','event-eligibility'}:
    from scitex_dev.cli_providers import list_cli_providers
    from scitex.cli.main import cli
    name,owner=('event','scitex-events') if operation=='event-eligibility' else ('web','scitex-web')
    result={'installed':any(row.distribution==owner for row in list_cli_providers()),
            'listed':name in cli.list_commands(None)}
elif operation=='owners':
    import click
    from scitex.cli.main import cli
    from scitex_sdk.cli import main as sdk
    from importlib.metadata import distribution, PackageNotFoundError
    try:
        distribution('scitex-cards')
    except PackageNotFoundError:
        cards=None
    else:
        from scitex_cards._cli import main as cards
    from scitex_clew._cli._main import main as clew
    from scitex_ssh.cli import main as ssh
    from scitex_writer._cli import main_group as writer
    writer_name=writer.name
    from scitex_dev._cli import main as owner
    context=click.Context(cli)
    before={n:(id(c),c.hidden) for n,c in owner.commands.items()}
    dev=cli.get_command(context,'dev')
    upkeep=owner.get_command(click.Context(owner),'dev')
    same={'sdk':cli.get_command(context,'sdk') is sdk,
          'cards':cli.get_command(context,'cards') is cards and (cards is not None or 'todo' not in cli.commands),
          'clew':cli.get_command(context,'clew') is clew,
          'ssh':cli.get_command(context,'ssh') is ssh,
          'writer':cli.get_command(context,'writer') is writer and writer.name==writer_name,
          'skills':dev.get_command(click.Context(dev),'skills') is upkeep.get_command(click.Context(upkeep),'skills'),
          'linter':dev.get_command(click.Context(dev),'linter') is owner.get_command(click.Context(owner),'linter')}
    dev.get_command(click.Context(dev),'dev')
    after={n:(id(c),c.hidden) for n,c in owner.commands.items()}
    result={'same':same,'owner_unchanged':before==after,
            'retired_imports':[n for n in ('scitex_app','scitex_ui') if n in sys.modules]}
elif operation=='tuple-alias':
    import click
    from click.testing import CliRunner
    from scitex_dev.ecosystem import deprecated_alias
    @click.group()
    def root():
        pass
    @root.group()
    def canonical():
        pass
    @canonical.command('echo-value')
    @click.argument('value')
    @click.option('--label',required=True)
    @click.option('--exit-code',type=int,default=0)
    def echo_value(value,label,exit_code):
        click.echo(json.dumps({'value':value,'label':label}))
        raise SystemExit(exit_code)
    deprecated_alias(root,'legacy',target=('canonical','echo-value'),remove_in='99.0')
    probe=CliRunner().invoke(root,['legacy','owned value','--label','owned label','--exit-code','7'])
    result={'code':probe.exit_code,'stdout':probe.stdout,'stderr':probe.stderr,
            'hidden':root.get_command(click.Context(root),'legacy').hidden}
elif operation=='python':
    from importlib.metadata import PackageNotFoundError,distribution
    exports={'dict':('scitex-dict','DotDict'),'compat':('scitex-compat','deprecated'),
             'types':('scitex-types','ArrayLike'),'decorators':('scitex-decorators','numpy_fn')}
    public={}; missing=[]
    for name,(owner,symbol) in exports.items():
        public[name]=name in scitex.__all__ and name in vars(scitex)
        try: distribution(owner)
        except PackageNotFoundError: missing.append(owner)
        else: public[name]=public[name] and hasattr(getattr(scitex,name),symbol)
    result={'public':public,'missing_owners':missing}
else:
    raise AssertionError('unknown owned probe')
sys.setprofile(None)
if request.get('installed_cards'):
    from importlib.metadata import distribution, PackageNotFoundError
    try:
        distribution('scitex-cards')
    except PackageNotFoundError:
        result['cards_installed']=False
    else:
        result['cards_installed']=True
if request.get('developer_metadata'):
    from scitex_dev.cli_providers import list_cli_providers
    result['declared_dev_peers']=[r.name for r in list_cli_providers() if r.name in {'newb','resource','template'} and r.status in {'declared','legacy_unknown'}]
print(json.dumps(result))
"""


def _probe(tmp_path, operation, payload=None):
    """Run the real entry point in a fresh, strictly bounded owned process."""
    source = str(Path(__file__).resolve().parents[2] / "src")
    environment = {
        key: value
        for key, value in os.environ.items()
        if not any(
            part in key.upper()
            for part in ("API_KEY", "TOKEN", "PASSWORD", "SECRET", "CREDENTIAL")
        )
    }
    environment["COVERAGE_FILE"] = str(tmp_path / ".coverage")
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            _CHILD,
            source,
            str(tmp_path),
            operation,
            json.dumps(payload or {}),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=45,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture
def installed_parser(tmp_path):
    """A real owned dist-info console declaration and an argparse launcher."""
    import csv

    site = tmp_path / "installed"
    site.mkdir()
    imported = tmp_path / "provider-imported"
    called = tmp_path / "provider-called"
    (site / "owned_parser.py").write_text(
        "import argparse,json\nfrom pathlib import Path\n"
        f"Path({str(imported)!r}).touch()\n"
        "def main():\n"
        f"    Path({str(called)!r}).touch()\n"
        "    parser=argparse.ArgumentParser(description='Owned parser fixture')\n"
        "    parser.add_argument('--value',default='owned')\n"
        "    parser.add_argument('--exit-code',type=int,default=0)\n"
        "    args=parser.parse_args()\n"
        "    print(json.dumps({'value':args.value}))\n"
        "    return args.exit_code\n"
    )
    info = site / "scitex_owned_parser-1.0.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: scitex-owned-parser\nVersion: 1.0\n"
    )
    (info / "entry_points.txt").write_text(
        "[console_scripts]\nscitex-owned-parser = owned_parser:main\n"
        "[scitex.cli]\nowned-parser = owned_parser:main\n"
    )
    with (info / "RECORD").open("w") as stream:
        writer = csv.writer(stream)
        for name in (
            "owned_parser.py",
            "scitex_owned_parser-1.0.dist-info/METADATA",
            "scitex_owned_parser-1.0.dist-info/entry_points.txt",
            "scitex_owned_parser-1.0.dist-info/RECORD",
        ):
            writer.writerow((name, "", ""))
    return site, imported, called
