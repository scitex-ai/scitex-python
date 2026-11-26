"""Pure release-boundary controls using real archives and public Git fixtures."""

from __future__ import annotations

import base64
import contextlib
import copy
import csv
import functools
import hashlib
import importlib.util
import io
import json
import os
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
import zipfile
import zlib
from pathlib import Path

import tomllib

if not __debug__:
    raise RuntimeError("Release identity controls require assertions enabled")

HERE = Path(__file__).parent
REPOSITORY = HERE.parent.parent
HELPER = HERE / "release-identity.py"
HELPER_SHA = hashlib.sha256(HELPER.read_bytes()).hexdigest()
SPEC = importlib.util.spec_from_file_location("owned_umbrella_release_identity", HELPER)
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)
DOCS = RELEASE.DOCS
# Synthetic stand-in for the release-time Sphinx bundle (gitignored, untracked).
DOCS_FILES = {
    "index.html": b"<html>scitex docs</html>\n",
    "_static/basic.css": b"body { margin: 0 }\n",
    "api/scitex.io.html": b"<html>io</html>\n",
}
CONFIG = "scitex/cli/__init__.py"
SCRIPT = "scitex/__version__.py"
PREFIX = "repos/scitex-ai/scitex-python"


def git(*arguments):
    return subprocess.run(
        ["/usr/bin/git", "-C", str(REPOSITORY), *arguments],
        check=True,
        capture_output=True,
        timeout=7,
        env={
            "PATH": "/usr/bin:/bin",
            "LANG": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        },
    ).stdout


SOURCE = git("rev-parse", "HEAD").decode().strip()
PYPROJECT = git("show", SOURCE + ":pyproject.toml")
PROJECT = tomllib.loads(PYPROJECT.decode())["project"]
VERSION = PROJECT["version"]
TAG = "v" + VERSION
DIST_INFO = "scitex-" + VERSION + ".dist-info"
SDIST_ROOT = "scitex-" + VERSION
CONFIG_BYTES = git("show", SOURCE + ":src/" + CONFIG)
SCRIPT_BYTES = git("show", SOURCE + ":src/" + SCRIPT)
INIT_BYTES = git("show", SOURCE + ":src/scitex/__init__.py")
LICENSE_BYTES = git("show", SOURCE + ":LICENSE")

# Frozen static metadata from the pinned Hatchling 1.30.1 producer, bound to
# public pyproject (42 core requirements / 77 extras). No backend build.
PRODUCER_HEADERS = zlib.decompress(
    base64.b85decode(
        b"c-p0%U3c5K5r*&mD|ELvkrO-4m)qntyPLLqn*BJ*wmm&Py?{tqLQE120LoT>eF0LEW#AoPm|pB|LOlbL_?#KM;QlO~sD%^"
        b"De@J7M?yeV?=T~RHh*n-NY^9vMKRfy5`LpwjXJ?;>wiRY~y?DQ<blV%bk)2grx%h48Ho99hYGwTIiyLi18M1TgMpYv_IMu"
        b"BeqN^9-rv4A2*;!@Jelz-utlaYNpFUnM{;FHqi?w{R*f`hQ>!(lG%58?#xi8`A?#>%_VkIx$yngd^dc<Wv-uQ7TKk8~|{k"
        b"?_r5C2fqWN~h!sNF`^y0Yg=KeqfNdu^4|X7~R+!S};@@w*Y#tu%8BdaA4)q&<5-_`jK@Y=vsB7ylaUa4Q%8+?y@_cr4*h`"
        b"_~fc-PuP~`Sy^@5BI)l?9_Dc|MJ_%<@57rOWifQBk^a|_-6k2(+?kh`TXJRZ*q61O>M8owpkw9=1D86jq2pGk-~Jo`JQxg"
        b"Frry@(s};YKJj<)KUJG24~@M%Hue*%*1n`=Z*&!&rdyx=&<OvB8zqfzCApQ2?n6T@KKr&B?Be=*akW@3zV|)z5&Bc-WLL|"
        b"2@qVcNeJUBqy}j?EW%hG5{_*Lj{qsJu_|=yo#@_jPXPs<=!LOfvLAC5dQJs5)`-WZ{(YC?hqv+Oy@2|mRKLq@rp3mjO(3)"
        b"*>G2i5JzRBZv`Ca#ZI3Fr>Z11NZy0z~k(!}jsV8bu(&3IXfW^A^mQR~o5bBp<@^YcwRj`qd-!@Ppa&^PW*82PC4`RgCYc}"
        b"q!q^8P>TdT9JW{3O2)%6IhTbp3kq?(NuM$Ll{T>#i3oDSWTL85*mH{_5S^D_`B`2~{<!x_$Td_4%{(w;Q!KvQoW#_x9QO)"
        b"r<3s80dtv+PLKM(Du9dV(%v(u?}sL{Lt0HCRcYm(Khkb{lp~tK0MOp%k+^Bgdb}<FwfK1+9NC9vKzm6+y?C8`~`&>eP^Ya"
        b"pbLts8hJO~?xkO{2*giA!cFD8A(_rs`t;lv7c}Jm<MNMPZO29<-@aarHAq%qEyn_0(p6lmYX1zc2|~Ime-l5r{3?-0{9kP"
        b"THmY+*+g_F)XX+5I$SP^{I`q$cuW4;qm?q|uU^?yOO6z^cx}vEtcZ{>dR0mYA&^F&|dg0f=Mm8nNZ6@LsMby*pFNxoc^eb"
        b"n+2wQD*Bm8K&IKO;DzPgpwV3gZUuT538^=q&VB|Xa^hk;4m%Kww^6>ir{n}4Zc>Z8xoPU^naZE&=<s`l4D+&d$#7k<_1+&"
        b"D^wUla^ALp`R((dvi69~Lr{vUvM;@m+*`m)@yKW=NrQaPJ-!(=^{DSm!n-EJ7vl@hVcJ)ylt{?~i`QEV6@Y>JsFKhaXAS6"
        b"}hmC6(QYqewL7RFM^lm{oA625qHg%P-RYAYvhfeLn<+j!`D$$A|t!KY=p0`5_luSBXjCBS+R=--YN0()MXfBC3Y=!yKH5x"
        b"L{~(Wn}UZTsP(#$(?U>Wjs99<HZRJJx^ZoD8CK9T==x&gsCFe9;hn^Kib{%nU$4pxtMa~x;?sTc%~fRd%7@8CYG~A8OH>o"
        b"0GrvmQ_;9Y+Tbui~;V{e4V!_2Kcf8=w)%uRjU6w)DH`*~OsI7{#ZYx_K$+PRH?PL+L#U^QY<ss4fICIIHVouO;-YD_=7@>"
        b"%*Z0|$+aj||=gr$E5VRv1nbeX+d?Sq9^MRsT_UCXLir#{MOOjsk;jGpCwRd`i?w_sFlm%JGu!2RyNDRXY<M2YI_o4y&^Rk"
        b";)NO5UrRGSxKtu1GavcW2ak<M?Fo3a=PT);M&Fy}vgyL}#rkKY{hmP*bLMmG0M<%a!VcDc^o4jA7K%uJ&GA*<<T>>ySmTW"
        b"zNrSA@|5=?ww!u8PMQ+P#FsWzh=A!uP|x6@7I?>UJu(jY5mM5Djv$DxO3H>uJo2k%8pBZvAPQZ9AhfpTeQ0DQSZ_4ueLl}"
        b"9ca}`J#Zi6zE-Si_Os>EcdL6Q+SuNQp=QhJ{7#!{<5z9zG4J2h%PnK381q*p>Z=Ls&A<Ib`JWORMygn;#)r*Ij^h;gY9ma"
        b"U`#Sh~E>0Il^}YAhYw3IlrOJ)%qsyZAVg}L5X3423Gu#wsgMIR$JmLEg{8l-hzwX(dQy@2{&saZXHMtfiSx%-&l+I*You)"
        b"UrCa396w#{kHv2PXjh^(CMb;YiUV+NGVKV(F?77rOxro}_Xlxc99LFJm9WK@|Zn_;Z0i#P1bJ?2`O{Nvm!)2MCs2}C9z<z"
        b"@L+ah{fGsg15SW9wY-Ya&YKvaOEEU9QC;*~{cllfO)pC>hMPdYl|)TaDYx^Lm}NoAKe;W9Kv_%{DovsF@Z{wtdJ8PVd6DI"
        b">}=*O&;>vOamW$xhd?wx?&hfvC@nMRyMLzLtEzD&^xW0qN`$WgNr%7+XbVYblC4zBJeLbOQIgS+AjvGD*885N`puF#oTFD"
        b"PW*)T4)56T{zBP<qwK~Z@PcXW1KZtdaBdoETr1=1rQ66>&gEGtrbFh4Gw{DQ%T{#WQ8NrwG?jmdviBEeh1NUrjIQbGMy-|"
        b"&Bc`#tw(NL1u^Pf$QRKXz;K%Te!C7r?7-^e{>_t@uP0LK7I^8z6<=ASB$5_zlAhSq23CUROR#`>>6!r#-%$+Ldc*mK2$qO"
        b"hamK)PeG=E|pTG8{OraR%PO|92OPOfUBd=$<dm3JE{i?whsj1k4Qyl+fhX6*fCWs6ysU2$jXzy6sLCfU&K`<cOE--A*@ub"
        b"&$-hU>T}_YIC(FiT52N^Z(|)guZ@F{)lm-bT&DmV^2Om)>g(ml?b4d-6N(b74B4;-;+1vHj69e!)ugZZNX2nYE`%+fNjhZ"
        b"Um5I_Wh4m$y+q?Zf5EtTt@{dMq7JohEM|0aDyCycy|Pn$pV2Wv^0!dS`&Jxd7XJgXXXy}HpyMbtkK+*()0r=Ey(E@6*Y3u"
        b"KC9u$<*PEXoxOlBy}o5{23A|nAls(*-sj5ZXVUgR!4hSNx6&V0Gd9NR)vP=n!lAz&z~sSXrH$~eoGnWs9$4ngo-v>|gEB_"
        b"RQk7w2motN=F48HS*4UOYEqaP4G(#Xge?poNnn5-Wsu6^QW{``8W)R8>&7cJknqjUWG=oM+Xof&6G=pSLXa)@kp&4Qcp&3"
        b"NcItoETXa?CxXoi?rXa*T1G{aydG(%8MXa@O6XoeY9<wZg>h(tm&$bi{(%Mh9&iWHhbINC3z7(!@<a3nO#ahGKfuO{1)&<"
        b"rB9&<x^_lMoQG#U_b`W|)COGlT-+7{tgWb<5U*K^AGj5SVJgNGhiVql{vC7v^Gl7oxDd3zCVv3sbSf2`L!B<Vh6!VT)Ma1"
        b"t}=+f@G40fK;m2!dR-;!d$A?!W`6V5vZ&gP^{O&7!OKySQzAW1+2p&Q6|NmC$J7HLq<BR3`yv)G8VB8D}w?ZR*p_}SQ$Fe"
        b"VG%6SVP#OP!y*g{IxK7z2m6R3bXW+@>98n1)?r~TP0T<pqr-xHq{D&?)?s1vrZ^iw9To<$4vS!WPJv7vR?eD8k!MUYnb(X"
        b"Jm72_%WHL?}vs_*$V}%t@84Ijm${0}krHl!b7G-!^T9h#=h<-Ab8PQA5ir!1fSwa0u&VbObWK6I~Bx68}M4(YB62Vw162T"
        b"nW%Y-B;5`i=peLyr3eb5vZeH3_7^pUZH0u0Dwfdqk~gexMkKmwysAOX=>Ab}txkboQzNDv$lNYG>?kiZ}mNI*0dNMI}yNR"
        b"Ut>kRVAQkRaJqAOX=NTfHp{Bp^fxBxsiFY~=(Jh{pm6L?VF%<Z=QDXb=k|5QMV-+oC`MGpRrVal2whH5N#W4A_Vm8-kTu9"
        b"7%qn4db+LjCtgz5+q#uFbf-Ok0y1bMEHyjBNCcGR6^zEY1+eOP>!zbob#iB=bsFPG+*SHGta0Tb7r(`F=LhJ7AH2TOWPOs"
        b"AZ*XcxdVzA6M%%_EaHe^1JHEDAP5W=gb{ukK=JwvKrr?!P+irIS*u{6__&Ev(H@%@d5s3i&9))km|XUuSgC_~gtLW&u(Tf"
        b"{3fCASVa5@Gs2(wwx&(+zdMkp`E;CY~%7vO48IRXNQQ=h2%o9K3bySpNZL_X}#E;j2NDR1<V!PvP!;fHTPm+L=y+q7K8(<"
        b"hpcUdr(?jjIeF`<d=av4BufrA!;jbn!lmP8L37Q_!3I*lMOj2-ShoAkJ0HBY4GFQ=tEd~PiLNwWq{5ZV@IT7)1q0pQY^7C"
        b">?4nm~vRaX_Q}aEPJ#0f1ol7g1=F7I0`I6<~OW6oJVGDTLzvQ3NGhm<URD93cfa2r(IN{XvSuzzrWr#=anch<zA968<G1l"
        b"LZ?yWNI1UapnRbsRw|dD8L3t92Fyxexo|kteGmR31-Y11c*m40Vj1&ad9e-;L=(>fS^tssoNzsHYOWT*0h7btceMpzZ-Eh"
        b"jBh`-VS2Thb1J$8hfUh?d$RLZ#K{JfHGUS8^R1VO<W3|9I=)|5j8(d>sEF%0VM@o1QaWDjfiOIm0TM*PfP#^2$B9xp5TqP"
        b"V&CfqnfA|TOdE8$6wjH?BpVRWEllQZa<xjtW;?ijOa7=&xDgMJx#Z~12OmFTsEKf6l%<c=({MQ90ljPy*IbR&;Yeu*1!3@"
        b"whZk8z7^Ni7sD5AaqnYx9Tiv2=JCH@kkh^Ygi$yyAdbb>(`v1Nr&(3%a%2K3Yatzh12v^Ppi8$VXTYsV3t`_YTN5xi|ZRC"
        b"30x1O837pA6GSuzE1*6U58ofn$sb5~bdXz|*`4jV7I+M9~^c!+5xmd@^Pp$fV-A4x*u*L$bY*TWG`9yFizN{)BN{XHU*Ji"
        b"9=ctr*SAge?Eq^0%v4sws1~{GQ>w<C>rKuXgE6ML4mm6P&CMtkSL*nrTC&~J!cr_TPPMMT}V1vJV`PuCnv3dYMW*wnRNz?"
        b"^DQ*W2BAbcgQNJ0#^X7XBGJAH$>Qmk!l90ohOw43!x!Xwq-E+O(P%1LBU!Ax%HTkKMbSv!M6yvFLUBmKLb5p-%h8Bf%a-d"
        b"w70+Rwu;08IKx69UV$Oy;aZbj`YwyLN^R=RfpHP|O_tBV3%>;911%fPomF;MlJm`k`j3D%!KIJv%17Fi`proK!WIjkh%bp"
        b"{N<#f4(5tdV87zrTvWct#E`^r2w#F?32#X}Zp069|e!ymqyH~*u0ho4ZH_q+=6Ag~S_nZ@nZ@d7X&yo=n-(tS@Rpr{~Xoc"
        b"Yzj@j9a^_FR0+LCsQ=qe;-O73yX;^W?;2losZfA4WjrDc<)B5J*Q&h^CICLpC~&j+iuRM-)7aj6u}P5t*KTMO5mwLyA14h"
        b"v?ivEX=2lD&(+}icreuB-qCb0)$f65@E52hM07$j#M%-#?u<CFGfr#?-L9JOY|!YXSxG6C>}r|?2v|;Kp)GP573X&Rz~$<"
        b"FJk#a__$B!mcRR%aa=*%)5EYk`yYI;Wuy"
    )
)
PRODUCER_ENTRY_POINTS = (
    b"[console_scripts]\nscitex = scitex.__main__:main\n"
    b"scitex-mcp-server = scitex._mcp:main\nscitex-pkg = scitex.cli.pkg:pkg\n\n"
    b"[scitex_dev.docs]\nscitex = scitex\n\n"
    b"[scitex_dev.skills]\nscitex = scitex\n\n"
)


@functools.lru_cache(maxsize=1)
def public_source_files():
    """Read only selected public Git blobs, with no filesystem dereference."""
    entries = RELEASE.git_tree(SOURCE, REPOSITORY)
    with RELEASE.GitBodies(REPOSITORY) as stream:
        ignore = stream.body(entries[".gitignore"])
        _, selected = RELEASE.selected_paths(
            entries, tomllib.loads(PYPROJECT.decode()), ignore
        )
        return {name: stream.body(entries[name]) for name in sorted(selected)}


def public_wheel_files():
    return {
        name.removeprefix("src/"): body
        for name, body in public_source_files().items()
        if name.startswith("src/scitex/")
    }


def metadata(version=VERSION, name="scitex", duplicate=False):
    body = (
        PRODUCER_HEADERS.decode()
        .replace("Name: scitex\n", "Name: " + name + "\n")
        .replace("Version: " + VERSION + "\n", "Version: " + version + "\n")
    )
    if duplicate:
        body += "Version: " + version + "\n"
    return body.encode()


def declared_dev_floor():
    """The scitex-dev floor exactly as pyproject declares it, as bytes."""
    return next(
        r for r in PROJECT["dependencies"] if r.startswith("scitex-dev>=")
    ).encode()


def record_bytes(files, record_name):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for name, body in sorted(files.items()):
        digest = (
            base64.urlsafe_b64encode(hashlib.sha256(body).digest()).decode().rstrip("=")
        )
        writer.writerow((name, "sha256=" + digest, str(len(body))))
    writer.writerow((record_name, "", ""))
    return output.getvalue().encode()


def wheel(
    files=None,
    version=VERSION,
    metadata_owner=DIST_INFO,
    record_owner=None,
    changes=None,
    modes=None,
    record_transform=None,
    duplicate=None,
    metadata_body=None,
    entry_points=PRODUCER_ENTRY_POINTS,
    wheel_body=(
        b"Wheel-Version: 1.0\nGenerator: owned-fixture\n"
        b"Root-Is-Purelib: true\nTag: py3-none-any\n"
    ),
    license_body=LICENSE_BYTES,
    docs=DOCS_FILES,
):
    bodies = (
        {CONFIG: CONFIG_BYTES, SCRIPT: SCRIPT_BYTES, "scitex/__init__.py": INIT_BYTES}
        if files is None
        else dict(files)
    )
    bodies.update({DOCS.WHEEL + name: body for name, body in (docs or {}).items()})
    bodies[metadata_owner + "/METADATA"] = (
        metadata(version) if metadata_body is None else metadata_body
    )
    if entry_points is not None:
        bodies[metadata_owner + "/entry_points.txt"] = entry_points
    if wheel_body is not None:
        bodies[metadata_owner + "/WHEEL"] = wheel_body
    if license_body is not None:
        bodies.setdefault(metadata_owner + "/licenses/LICENSE", license_body)
    record = (record_owner or metadata_owner) + "/RECORD"
    encoded = record_bytes(bodies, record)
    bodies[record] = record_transform(encoded) if record_transform else encoded
    bodies.update(changes or {})
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, body in sorted(bodies.items()):
            entry = zipfile.ZipInfo(name)
            entry.create_system = 3
            entry.external_attr = (modes or {}).get(name, stat.S_IFREG | 420) << 16
            archive.writestr(entry, body)
        if duplicate:
            archive.writestr(duplicate, bodies[duplicate])
    return output.getvalue()


def sdist(
    files=None,
    version=VERSION,
    project=PYPROJECT,
    root=SDIST_ROOT,
    additions=None,
    omit=(),
    metadata_body=None,
    docs=DOCS_FILES,
):
    bodies = (
        {
            "src/" + CONFIG: CONFIG_BYTES,
            "src/" + SCRIPT: SCRIPT_BYTES,
            "src/scitex/__init__.py": INIT_BYTES,
        }
        if files is None
        else dict(files)
    )
    bodies.update({DOCS.SOURCE + name: body for name, body in (docs or {}).items()})
    bodies.update(
        {
            "pyproject.toml": project,
            "PKG-INFO": metadata(version) if metadata_body is None else metadata_body,
        }
    )
    for name in omit:
        bodies.pop(name)
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz", compresslevel=1) as archive:
        directory = tarfile.TarInfo(root)
        directory.type = tarfile.DIRTYPE
        directory.mode = 493
        archive.addfile(directory)
        for name, body in sorted(bodies.items()):
            entry = tarfile.TarInfo(root + "/" + name)
            entry.size = len(body)
            entry.mode = 420
            if name in RELEASE.PUBLIC_LINKS:
                entry.type = tarfile.SYMTYPE
                entry.size = 0
                entry.linkname = body.decode()
                archive.addfile(entry)
            else:
                archive.addfile(entry, io.BytesIO(body))
        for entry, body in additions or []:
            archive.addfile(entry, io.BytesIO(body) if body is not None else None)
    return output.getvalue()


@functools.lru_cache(maxsize=1)
def whole_archives():
    return (wheel(files=public_wheel_files()), sdist(files=public_source_files()))


def replace_record_size(raw):
    rows = list(csv.reader(io.StringIO(raw.decode())))
    for row in rows:
        if row[0] == CONFIG:
            row[2] = "999999"
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\n").writerows(rows)
    return output.getvalue().encode()


def routes(project=PYPROJECT):
    digest = hashlib.sha1(
        b"blob " + str(len(project)).encode() + b"\x00" + project
    ).hexdigest()
    return {
        (PREFIX + "/git/ref/tags/" + TAG, 200): {
            "ref": "refs/tags/" + TAG,
            "object": {"type": "commit", "sha": SOURCE},
        },
        (PREFIX + "/compare/" + SOURCE + "...main", 200): {
            "base_commit": {"sha": SOURCE},
            "status": "ahead",
        },
        (PREFIX + "/contents/pyproject.toml?ref=" + SOURCE, 200): {
            "encoding": "base64",
            "content": base64.b64encode(project).decode(),
            "sha": digest,
        },
    }


class QueryFixture:
    def __init__(self, values):
        self.values = values
        self.calls = []

    def __call__(self, path, status=200):
        self.calls.append((path, status))
        if (path, status) not in self.values:
            raise AssertionError("unapproved deterministic request: " + path)
        return copy.deepcopy(self.values[path, status])


class ResponseFixture:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, limit):
        return self.body[:limit]


def admitted_routes():
    return {
        **routes(),
        ("orgs/scitex-ai/public_members/fixture-member", 204): {"status": 204},
    }


@contextlib.contextmanager
def environment_inputs(values):
    previous = dict(os.environ)
    os.environ.clear()
    os.environ.update(values)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(previous)


@contextlib.contextmanager
def argument_inputs(values):
    previous = sys.argv
    sys.argv = list(values)
    try:
        yield
    finally:
        sys.argv = previous


def refusal(operation, exception=ValueError, message=None):
    try:
        operation()
    except exception as error:
        return message is None or message in str(error)
    return False


class TagAndAdmissionTests(unittest.TestCase):
    def test_exact_existing_tag_resolves_promoted_public_version(self):
        # Arrange
        query = QueryFixture(routes())
        # Act
        result = RELEASE.resolve(TAG, query)
        # Assert
        assert result == {"tag": TAG, "commit": SOURCE, "version": VERSION}

    def test_tag_path_and_shell_escapes_make_zero_requests(self):
        # Arrange
        for tag in (
            "v2.43.8/../../main",
            "v2.43.8?ref=main",
            "v2.43.8\nmain",
            "v2.43.8;echo bad",
            "v02.43.8",
            "$(anything)",
            "v2.43.8%2fmain",
        ):
            with self.subTest(tag=tag):
                query = QueryFixture({})
                # Act
                refused = refusal(lambda: RELEASE.resolve(tag, query), ValueError)
                requests = query.calls
                # Assert
                assert refused and requests == []

    def test_real_annotated_tag_chain(self):
        # Arrange
        values = routes()
        values[PREFIX + "/git/ref/tags/" + TAG, 200]["object"] = {
            "type": "tag",
            "sha": "a" * 40,
        }
        values[PREFIX + "/git/tags/" + "a" * 40, 200] = {
            "object": {"type": "commit", "sha": SOURCE}
        }
        # Act
        result = RELEASE.resolve(TAG, QueryFixture(values))["commit"]
        # Assert
        assert result == SOURCE

    def test_annotation_cycle_refused(self):
        # Arrange
        values = routes()
        values[PREFIX + "/git/ref/tags/" + TAG, 200]["object"] = {
            "type": "tag",
            "sha": "a" * 40,
        }
        values[PREFIX + "/git/tags/" + "a" * 40, 200] = {
            "object": {"type": "tag", "sha": "b" * 40}
        }
        values[PREFIX + "/git/tags/" + "b" * 40, 200] = {
            "object": {"type": "tag", "sha": "a" * 40}
        }
        # Act
        refused = refusal(
            lambda: RELEASE.resolve(TAG, QueryFixture(values)), ValueError, "cyclic"
        )
        # Assert
        assert refused

    def test_annotation_depth_refused(self):
        # Arrange
        values = routes()
        values[PREFIX + "/git/ref/tags/" + TAG, 200]["object"] = {
            "type": "tag",
            "sha": "a" * 40,
        }
        for first, second in zip("abcde", "bcdef"):
            values[PREFIX + "/git/tags/" + first * 40, 200] = {
                "object": {"type": "tag", "sha": second * 40}
            }
        # Act
        refused = refusal(
            lambda: RELEASE.resolve(TAG, QueryFixture(values)), ValueError, "depth"
        )
        # Assert
        assert refused

    def test_wrong_ref_and_noncommit_object_refused(self):
        # Arrange
        for mutation in ("ref", "blob"):
            with self.subTest(mutation=mutation):
                values = routes()
                ref = values[PREFIX + "/git/ref/tags/" + TAG, 200]
                if mutation == "ref":
                    ref["ref"] = "refs/heads/main"
                else:
                    ref["object"]["type"] = "blob"
                # Act
                refused = refusal(
                    lambda: RELEASE.resolve(TAG, QueryFixture(values)), ValueError
                )
                # Assert
                assert refused

    def test_not_promoted_source_refused(self):
        # Arrange
        for status in ("behind", "diverged", "unknown"):
            with self.subTest(status=status):
                values = routes()
                values[PREFIX + "/compare/" + SOURCE + "...main", 200]["status"] = (
                    status
                )
                # Act
                refused = refusal(
                    lambda: RELEASE.resolve(TAG, QueryFixture(values)),
                    ValueError,
                    "promoted",
                )
                # Assert
                assert refused

    def test_comparison_base_identity_is_required(self):
        # Arrange
        values = routes()
        values[PREFIX + "/compare/" + SOURCE + "...main", 200]["base_commit"]["sha"] = (
            "f" * 40
        )
        # Act
        refused = refusal(
            lambda: RELEASE.resolve(TAG, QueryFixture(values)), ValueError, "promoted"
        )
        # Assert
        assert refused

    def test_source_version_tampering_has_valid_git_blob_but_is_refused(self):
        # Arrange
        changed = PYPROJECT.replace(
            ('version = "' + VERSION + '"').encode(), b'version = "99.99.99"'
        )
        # Act
        refused = refusal(
            lambda: RELEASE.resolve(TAG, QueryFixture(routes(changed))),
            ValueError,
            "metadata differ",
        )
        # Assert
        assert refused

    def test_source_metadata_git_blob_tampering_refused(self):
        # Arrange
        values = routes()
        values[PREFIX + "/contents/pyproject.toml?ref=" + SOURCE, 200]["sha"] = "0" * 40
        # Act
        refused = refusal(
            lambda: RELEASE.resolve(TAG, QueryFixture(values)),
            ValueError,
            "Git identity",
        )
        # Assert
        assert refused

    def test_both_actors_require_confirmed_membership(self):
        # Arrange
        environment = {
            "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
            "GITHUB_ACTOR": "fixture-member",
            "GITHUB_TRIGGERING_ACTOR": "fixture-trigger",
        }
        values = {
            (f"orgs/scitex-ai/public_members/{actor}", 204): {"status": 204}
            for actor in ("fixture-member", "fixture-trigger")
        }
        query = QueryFixture(values)
        # Act
        with environment_inputs(environment):
            RELEASE.member_admission(query)
        result = set(query.calls)
        # Assert
        assert result == set(values)

    def test_unknown_membership_fails_closed(self):
        # Arrange
        environment = {
            "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
            "GITHUB_ACTOR": "fixture-member",
            "GITHUB_TRIGGERING_ACTOR": "fixture-member",
        }
        query = QueryFixture(
            {("orgs/scitex-ai/public_members/fixture-member", 204): {"status": 404}}
        )
        with environment_inputs(environment):
            # Act
            refused = refusal(
                lambda: RELEASE.member_admission(query), ValueError, "not confirmed"
            )
            # Assert
            assert refused

    def test_foreign_repository_and_unknown_actor_make_zero_requests(self):
        # Arrange
        for changes in (
            {"GITHUB_REPOSITORY": "foreign/writer"},
            {"GITHUB_TRIGGERING_ACTOR": ""},
            {"GITHUB_ACTOR": "member/escape"},
        ):
            with self.subTest(changes=changes):
                environment = {
                    "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
                    "GITHUB_ACTOR": "fixture-member",
                    "GITHUB_TRIGGERING_ACTOR": "fixture-member",
                    **changes,
                }
                query = QueryFixture({})
                with environment_inputs(environment):
                    # Act
                    refused = refusal(
                        lambda: RELEASE.member_admission(query), ValueError
                    )
                    # Assert
                requests = query.calls
                assert refused and requests == []


class HttpIdentityTests(unittest.TestCase):
    def test_actual_api_request_is_bounded_and_uses_existing_identity_protocol(self):
        # Arrange
        observed = []

        def fake(request, timeout):
            observed.append(
                (
                    request.full_url,
                    timeout,
                    request.get_header("Accept"),
                    request.get_header("X-github-api-version"),
                    request.get_header("Authorization"),
                )
            )
            return ResponseFixture(b'{"fixture":true}')

        # Act
        with environment_inputs({}):
            result = RELEASE.api("repos/scitex-ai/scitex-python", open_url=fake)
        result = (result, observed)
        # Assert
        assert result == (
            {"fixture": True},
            [
                (
                    "https://api.github.com/repos/scitex-ai/scitex-python",
                    10,
                    "application/vnd.github+json",
                    "2022-11-28",
                    None,
                )
            ],
        )

    def test_status_mismatch_and_oversized_body_fail_closed(self):
        # Arrange
        for response in (ResponseFixture(b"{}", 202), ResponseFixture(b"x" * 1048577)):
            with self.subTest(status=response.status, bytes=len(response.body)):
                # Act
                refused = refusal(
                    lambda: RELEASE.api(
                        "repos/scitex-ai/scitex-python",
                        open_url=lambda request, timeout: response,
                    ),
                    ValueError,
                )
                # Assert
                assert refused

    def test_membership_204_requires_exact_response_status(self):
        # Arrange
        with environment_inputs({}):
            # Act
            result = RELEASE.api(
                "orgs/scitex-ai/public_members/fixture-member",
                status=204,
                open_url=lambda request, timeout: ResponseFixture(b"", 204),
            )
            # Assert
            assert result == {"status": 204}


class ResolveCliTests(unittest.TestCase):
    def test_real_resolve_cli_emits_bound_outputs_using_only_fake_network(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="writer-resolve-output-") as directory:
            output = Path(directory) / "github-output"
            environment = {
                "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
                "GITHUB_ACTOR": "fixture-member",
                "GITHUB_TRIGGERING_ACTOR": "fixture-member",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_EVENT_NAME": "push",
                "GITHUB_SHA": SOURCE,
            }
            # Act
            with (
                environment_inputs(environment),
                argument_inputs([str(HELPER), "resolve", "--tag", TAG]),
                contextlib.redirect_stdout(io.StringIO()) as captured,
            ):
                RELEASE.main(query=QueryFixture(admitted_routes()))
            result = (json.loads(captured.getvalue()), output.read_text().splitlines())
            # Assert
            assert result == (
                {"tag": TAG, "commit": SOURCE, "version": VERSION},
                ["tag=" + TAG, "commit=" + SOURCE, "version=" + VERSION],
            )

    def test_push_commit_mismatch_refuses_before_emitting_output(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="writer-resolve-output-") as directory:
            output = Path(directory) / "github-output"
            environment = {
                "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
                "GITHUB_ACTOR": "fixture-member",
                "GITHUB_TRIGGERING_ACTOR": "fixture-member",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_EVENT_NAME": "push",
                "GITHUB_SHA": "a" * 40,
            }
            with (
                environment_inputs(environment),
                argument_inputs([str(HELPER), "resolve", "--tag", TAG]),
            ):
                # Act
                refused = refusal(
                    lambda: RELEASE.main(query=QueryFixture(admitted_routes())),
                    ValueError,
                    "push event",
                )
                # Assert
                output_exists = output.exists()
            assert refused and not output_exists


class ArchiveTests(unittest.TestCase):
    def test_real_wheel_carries_actual_umbrella_init_cli_and_version(self):
        # Arrange
        # Act
        result = RELEASE.wheel_identity(wheel(), VERSION)["members"]
        # Assert
        assert result > 2

    def test_wheel_body_tampering_preserves_old_record_and_refuses(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: RELEASE.wheel_identity(
                wheel(changes={CONFIG: CONFIG_BYTES + b"\n# changed\n"}), VERSION
            ),
            ValueError,
            "RECORD",
        )
        # Assert
        assert refused

    def test_record_hash_and_size_tampering_refused(self):
        # Arrange
        for changed in (
            lambda raw: raw.replace(b"sha256=", b"sha512=", 1),
            replace_record_size,
        ):
            with self.subTest(change=changed):
                # Act
                refused = refusal(
                    lambda: RELEASE.wheel_identity(
                        wheel(record_transform=changed), VERSION
                    ),
                    ValueError,
                    "RECORD",
                )
                # Assert
                assert refused

    def test_record_extra_or_missing_member_refused(self):
        # Arrange
        # Act
        extra_record_refused = refusal(
            lambda: RELEASE.wheel_identity(
                wheel(record_transform=lambda raw: b"unknown.py,,\n" + raw), VERSION
            ),
            ValueError,
            "RECORD",
        )
        unrecorded_refused = refusal(
            lambda: RELEASE.wheel_identity(
                wheel(changes={"unknown.py": b"new unrecorded member"}), VERSION
            ),
            ValueError,
            "unrecorded",
        )
        # Assert
        assert extra_record_refused and unrecorded_refused

    def test_wheel_version_tampering_refused(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: RELEASE.wheel_identity(wheel(version="99.99.99"), VERSION),
            ValueError,
            "version",
        )
        # Assert
        assert refused

    def test_metadata_and_record_must_have_same_distribution_owner(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: RELEASE.wheel_identity(
                wheel(record_owner="foreign-7.dist-info"), VERSION
            ),
            ValueError,
        )
        # Assert
        assert refused

    def test_wheel_member_escape_backslash_and_absolute_refused(self):
        # Arrange
        for name in ("../escape.py", "/absolute.py", "a\\escape.py"):
            with self.subTest(name=name):
                # Act
                refused = refusal(
                    lambda: RELEASE.wheel_identity(
                        wheel(changes={name: b"synthetic unsafe member"}), VERSION
                    ),
                    ValueError,
                )
                # Assert
                assert refused

    def test_wheel_symlink_and_special_mode_refused(self):
        # Arrange
        for mode in (stat.S_IFLNK | 511, stat.S_IFIFO | 384, stat.S_IFCHR | 384):
            with self.subTest(mode=mode):
                # Act
                refused = refusal(
                    lambda: RELEASE.wheel_identity(
                        wheel(modes={CONFIG: mode}), VERSION
                    ),
                    ValueError,
                )
                # Assert
                assert refused

    def test_wheel_duplicate_member_refused(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: RELEASE.wheel_identity(wheel(duplicate=CONFIG), VERSION),
            ValueError,
            "duplicate",
        )
        # Assert
        assert refused

    def test_actual_source_sdist_is_accepted(self):
        # Arrange
        # Act
        result = RELEASE.sdist_identity(sdist(), VERSION)["members"]
        # Assert
        assert result > 3

    def test_metadata_only_sdist_is_refused(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: RELEASE.sdist_identity(sdist(files={}), VERSION), ValueError
        )
        # Assert
        assert refused

    def test_tar_escape_and_absolute_member_refused(self):
        # Arrange
        for name in (SDIST_ROOT + "/../escape", "/absolute", "a\\escape"):
            with self.subTest(name=name):
                entry = tarfile.TarInfo(name)
                entry.size = 1
                # Act
                refused = refusal(
                    lambda: RELEASE.sdist_identity(
                        sdist(additions=[(entry, b"x")]), VERSION
                    ),
                    ValueError,
                )
                # Assert
                assert refused

    def test_tar_symbolic_and_hard_links_refused_without_dereference(self):
        # Arrange
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE):
            with self.subTest(kind=kind):
                entry = tarfile.TarInfo(SDIST_ROOT + "/public-link")
                entry.type = kind
                entry.linkname = "/synthetic-private-target"
                # Act
                refused = refusal(
                    lambda: RELEASE.sdist_identity(
                        sdist(additions=[(entry, None)]), VERSION
                    ),
                    ValueError,
                )
                # Assert
                assert refused

    def test_tar_multiple_roots_refused(self):
        # Arrange
        entry = tarfile.TarInfo("other-root/public.py")
        entry.size = 1
        # Act
        refused = refusal(
            lambda: RELEASE.sdist_identity(sdist(additions=[(entry, b"x")]), VERSION),
            ValueError,
            "multiple roots",
        )
        # Assert
        assert refused

    def test_sdist_metadata_and_project_versions_must_agree(self):
        # Arrange
        for changed in (
            sdist(version="99.99.99"),
            sdist(
                project=PYPROJECT.replace(
                    ('version = "' + VERSION + '"').encode(), b'version = "99.99.99"'
                )
            ),
        ):
            with self.subTest(version_source=hashlib.sha256(changed).hexdigest()):
                # Act
                refused = refusal(
                    lambda: RELEASE.sdist_identity(changed, VERSION), ValueError
                )
                # Assert
                assert refused

    def test_sdist_duplicate_identity_headers_refused(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: RELEASE.sdist_identity(
                sdist(metadata_body=metadata(duplicate=True)), VERSION
            ),
            ValueError,
        )
        # Assert
        assert refused


class WholeSourceTests(unittest.TestCase):
    def source_identity(self, wheel_raw=None, sdist_raw=None, commit=SOURCE):
        original_wheel, original_sdist = whole_archives()
        return RELEASE.source_payload_identity(
            wheel_raw or original_wheel,
            sdist_raw or original_sdist,
            commit,
            source_root=REPOSITORY,
        )

    def test_every_actual_selected_source_member_matches_exact_git_source(self):
        # Arrange
        # Act
        identity = self.source_identity()
        result = (
            identity["git_commit"],
            identity["wheel_public_members"],
            identity["sdist_public_members"],
        )
        # Assert
        assert result == (SOURCE, len(public_wheel_files()), len(public_source_files()))

    def test_rehashed_wheel_payload_still_refuses_changed_public_bytes(self):
        # Arrange
        files = public_wheel_files()
        files[CONFIG] += b"\n# coordinated tamper\n"
        changed = wheel(files=files)
        RELEASE.wheel_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(wheel_raw=changed),
            ValueError,
            "public source bytes",
        )
        # Assert
        assert refused

    def test_missing_required_tracked_wheel_member_refused(self):
        # Arrange
        files = public_wheel_files()
        omitted = next(name for name in sorted(files) if name not in {CONFIG, SCRIPT})
        del files[omitted]
        changed = wheel(files=files)
        RELEASE.wheel_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(wheel_raw=changed), ValueError, "membership"
        )
        # Assert
        assert refused

    def test_rehashed_foreign_wheel_package_member_refused(self):
        # Arrange
        files = public_wheel_files()
        files["scitex/untracked_fixture.py"] = b"foreign package member\n"
        changed = wheel(files=files)
        RELEASE.wheel_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(wheel_raw=changed), ValueError, "membership"
        )
        # Assert
        assert refused

    def test_rehashed_payload_outside_package_and_dist_info_refused(self):
        # Arrange
        files = public_wheel_files()
        files["foreign_fixture.py"] = b"foreign top-level member\n"
        changed = wheel(files=files)
        RELEASE.wheel_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(wheel_raw=changed),
            ValueError,
            "undeclared payload",
        )
        # Assert
        assert refused

    def test_real_sdist_public_byte_tampering_refused(self):
        # Arrange
        files = dict(public_source_files())
        files["src/" + CONFIG] += b"\n# changed\n"
        changed = sdist(files=files)
        RELEASE.sdist_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(sdist_raw=changed),
            ValueError,
            "public source bytes",
        )
        # Assert
        assert refused

    def test_missing_tracked_sdist_payload_refused(self):
        # Arrange
        files = dict(public_source_files())
        del files["README.md"]
        changed = sdist(files=files)
        RELEASE.sdist_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(sdist_raw=changed),
            ValueError,
            "membership differs",
        )
        # Assert
        assert refused

    def test_untracked_extra_sdist_member_refused(self):
        # Arrange
        files = dict(public_source_files())
        files["untracked_fixture.txt"] = b"synthetic foreign member\n"
        changed = sdist(files=files)
        RELEASE.sdist_identity(changed, VERSION)
        # Act
        refused = refusal(
            lambda: self.source_identity(sdist_raw=changed),
            ValueError,
            "public source membership differs",
        )
        # Assert
        assert refused

    def test_malformed_or_absent_source_commit_fails_closed(self):
        # Arrange
        for commit in ("not-a-commit", "0" * 40):
            with self.subTest(commit=commit):
                # Act
                refused = refusal(
                    lambda: self.source_identity(commit=commit), ValueError
                )
                # Assert
                assert refused


class ProofAndCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="umbrella-release-proof-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.wheel_path = self.directory / (SDIST_ROOT + "-py3-none-any.whl")
        self.sdist_path = self.directory / (SDIST_ROOT + ".tar.gz")
        wheel_raw, sdist_raw = whole_archives()
        self.wheel_path.write_bytes(wheel_raw)
        self.sdist_path.write_bytes(sdist_raw)

    def proof(self, **changes):
        arguments = {
            "directory": self.directory,
            "tag": TAG,
            "commit": SOURCE,
            "run": "123456",
            "attempt": "1",
            "source_root": REPOSITORY,
            **changes,
        }
        with environment_inputs({"SCITEX_CI_SIF_SHA256": RELEASE.SIF_SHA256}):
            return RELEASE.artifact_proof(**arguments)

    def cli(self, mode, changes=None, commit=SOURCE, revalidate=False, query=None):
        environment = {
            "PATH": "/usr/bin:/bin",
            "GITHUB_RUN_ID": "123456",
            "GITHUB_RUN_ATTEMPT": "1",
            "SCITEX_CI_SIF_SHA256": RELEASE.SIF_SHA256,
            **(changes or {}),
        }
        arguments = [
            str(HELPER),
            mode,
            "--tag",
            TAG,
            "--commit",
            commit,
            "--dist",
            str(self.directory),
        ]
        if revalidate:
            arguments.append("--revalidate")
        previous = Path.cwd()
        try:
            os.chdir(REPOSITORY)
            with (
                environment_inputs(environment),
                argument_inputs(arguments),
                contextlib.redirect_stdout(io.StringIO()) as captured,
            ):
                RELEASE.main(query=query or QueryFixture({}))
        finally:
            os.chdir(previous)
        return json.loads(captured.getvalue())

    def test_exact_two_actual_source_archives_have_bound_proof(self):
        # Arrange
        # Act
        proof = self.proof()
        result = (proof["tag"], proof["commit"], proof["run"], len(proof["files"]))
        # Assert
        assert result == (TAG, SOURCE, "123456", 2)

    def test_extra_hidden_or_regular_artifact_refused(self):
        # Arrange
        for name in ("extra.txt", ".hidden"):
            with self.subTest(name=name):
                path = self.directory / name
                path.write_bytes(b"synthetic extra artifact")
                try:
                    # Act
                    refused = refusal(lambda: self.proof(), ValueError)
                    # Assert
                    assert refused
                finally:
                    path.unlink()

    def test_symlink_artifact_refused(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="writer-retained-wheel-") as retained:
            target = Path(retained) / self.wheel_path.name
            self.wheel_path.rename(target)
            self.wheel_path.symlink_to(target)
            # Act
            refused = refusal(lambda: self.proof(), ValueError, "regular file")
            # Assert
            assert refused

    def test_symlink_artifact_directory_refused(self):
        # Arrange
        link = self.directory / "dist-link"
        link.symlink_to(self.directory, target_is_directory=True)
        # Act
        refused = refusal(lambda: self.proof(directory=link), ValueError)
        # Assert
        assert refused

    def test_malformed_source_run_or_attempt_refused(self):
        # Arrange
        for change in ({"commit": "not-a-sha"}, {"run": "run;escape"}, {"attempt": ""}):
            with self.subTest(change=change):
                # Act
                refused = refusal(lambda: self.proof(**change), ValueError)
                # Assert
                assert refused

    def test_real_write_and_verify_proof_positive(self):
        # Arrange
        written = self.cli("write-proof")
        # Act
        result = self.cli("verify-proof")
        # Assert
        assert result == written

    def test_stale_run_and_attempt_proof_refused(self):
        # Arrange
        self.cli("write-proof")
        for changed in ({"GITHUB_RUN_ID": "999999"}, {"GITHUB_RUN_ATTEMPT": "2"}):
            with self.subTest(changed=changed):
                # Act
                refused = refusal(
                    lambda: self.cli("verify-proof", changed), ValueError, "proof"
                )
                # Assert
                assert refused

    def test_stale_source_proof_refused(self):
        # Arrange
        self.cli("write-proof")
        path = self.directory / RELEASE.PROOF
        value = json.loads(path.read_bytes())
        value["commit"] = "a" * 40
        path.write_text(json.dumps(value))
        # Act
        refused = refusal(lambda: self.cli("verify-proof"), ValueError, "proof")
        # Assert
        assert refused

    def test_actual_checkout_must_equal_declared_release_commit(self):
        # Arrange
        # Act
        refused = refusal(
            lambda: self.cli("write-proof", commit="a" * 40),
            ValueError,
            "checkout and release commit",
        )
        # Assert
        assert refused

    def test_existing_proof_is_not_overwritten(self):
        # Arrange
        self.cli("write-proof")
        # Act
        refused = refusal(lambda: self.cli("write-proof"), FileExistsError)
        # Assert
        assert refused

    def test_final_publisher_revalidation_accepts_same_existing_tag(self):
        # Arrange
        written = self.cli("write-proof")
        environment = {
            "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
            "GITHUB_ACTOR": "fixture-member",
            "GITHUB_TRIGGERING_ACTOR": "fixture-member",
        }
        with environment_inputs({}):
            # Act
            result = self.cli(
                "verify-proof",
                environment,
                revalidate=True,
                query=QueryFixture(admitted_routes()),
            )
            # Assert
            assert result == written

    def test_final_publisher_revalidation_refuses_retargeted_tag(self):
        # Arrange
        self.cli("write-proof")
        changed_source = "a" * 40
        values = admitted_routes()
        values[PREFIX + "/git/ref/tags/" + TAG, 200]["object"]["sha"] = changed_source
        values[PREFIX + "/compare/" + changed_source + "...main", 200] = {
            "base_commit": {"sha": changed_source},
            "status": "ahead",
        }
        values[PREFIX + "/contents/pyproject.toml?ref=" + changed_source, 200] = values[
            PREFIX + "/contents/pyproject.toml?ref=" + SOURCE, 200
        ]
        environment = {
            "GITHUB_REPOSITORY": RELEASE.REPOSITORY,
            "GITHUB_ACTOR": "fixture-member",
            "GITHUB_TRIGGERING_ACTOR": "fixture-member",
        }
        with environment_inputs({}):
            # Act
            refused = refusal(
                lambda: self.cli(
                    "verify-proof",
                    environment,
                    revalidate=True,
                    query=QueryFixture(values),
                ),
                ValueError,
                "release tag identity changed",
            )
            # Assert
            assert refused

    def test_coordinated_wheel_body_and_record_tampering_after_proof_refused(self):
        # Arrange
        self.cli("write-proof")
        files = public_wheel_files()
        files[CONFIG] += b"\n# changed\n"
        self.wheel_path.write_bytes(wheel(files=files))
        # Act
        refused = refusal(
            lambda: self.cli("verify-proof"), ValueError, "public source bytes"
        )
        # Assert
        assert refused

    def test_sdist_body_tampering_after_proof_refused(self):
        # Arrange
        self.cli("write-proof")
        files = dict(public_source_files())
        files["src/" + CONFIG] += b"\n# changed\n"
        self.sdist_path.write_bytes(sdist(files=files))
        # Act
        refused = refusal(
            lambda: self.cli("verify-proof"), ValueError, "public source bytes"
        )
        # Assert
        assert refused


class UmbrellaSelectionTests(unittest.TestCase):
    def layout_fixture(self, root):
        environment = {
            "PATH": "/usr/bin:/bin",
            "HOME": str(root),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        }

        def command(*arguments):
            return subprocess.run(
                ["git", "-C", str(root), *arguments],
                check=True,
                capture_output=True,
                timeout=7,
                env=environment,
            ).stdout

        command("init", "--quiet", "--template=")
        for name in (
            "pyproject.toml",
            ".gitignore",
            "LICENSE",
            "src/scitex/__init__.py",
            "src/scitex/cli/__init__.py",
            "src/scitex/__version__.py",
        ):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(public_source_files()[name])
        command("add", "--all")
        command(
            "update-index",
            "--add",
            "--cacheinfo",
            "160000",
            SOURCE,
            ".worktrees/owned-empty",
        )
        command(
            "-c",
            "user.name=Public Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "public fixture",
        )
        return command("rev-parse", "HEAD").decode().strip()

    def test_clean_public_layout_and_empty_gitlink_are_admitted(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="umbrella-layout-") as temporary:
            root = Path(temporary)
            commit = self.layout_fixture(root)
            (root / ".worktrees/owned-empty").mkdir(parents=True)
            # Act
            result = RELEASE.check_source_layout(commit, root)
            # Assert
            assert result is None

    def test_nonempty_gitlink_refuses_before_any_backend_walk(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="umbrella-layout-") as temporary:
            root = Path(temporary)
            commit = self.layout_fixture(root)
            foreign = root / ".worktrees/owned-empty/foreign-body"
            foreign.parent.mkdir(parents=True)
            foreign.write_bytes(b"synthetic unowned body")
            # Act
            refused = refusal(lambda: RELEASE.check_source_layout(commit, root))
            # Assert
            assert refused

    def test_dirty_public_source_refuses_before_backend_traversal(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="umbrella-layout-") as temporary:
            root = Path(temporary)
            commit = self.layout_fixture(root)
            (root / "src/scitex/__init__.py").write_bytes(b"changed public body")
            # Act
            refused = refusal(lambda: RELEASE.check_source_layout(commit, root))
            # Assert
            assert refused

    def test_real_selected_source_keeps_package_and_public_link_count(self):
        # Arrange
        wheel_files = public_wheel_files()
        source_files = public_source_files()
        # Act
        result = (
            len(wheel_files),
            len(source_files),
            len(set(source_files) & set(RELEASE.PUBLIC_LINKS)),
        )
        # Assert
        assert (result[0], result[2]) == (69, 7)

    def test_all_reviewed_git_link_literals_are_preserved_without_dereference(self):
        # Arrange
        raw = sdist(files=public_source_files())
        # Act
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
            result = {
                item.name.removeprefix(SDIST_ROOT + "/"): item.linkname
                for item in archive
                if item.issym()
            }
        # Assert
        assert result == RELEASE.PUBLIC_LINKS

    def test_changed_literal_link_refused_with_same_public_member_name(self):
        # Arrange
        files = dict(public_source_files())
        files[next(iter(RELEASE.PUBLIC_LINKS))] = b"different-relative-public-target"
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                whole_archives()[0], sdist(files=files), SOURCE, REPOSITORY
            )
        )
        # Assert
        assert refused

    def test_unowned_nonempty_gitlink_payload_cannot_enter_sdist(self):
        # Arrange
        files = dict(public_source_files())
        files[".worktrees/full-green/foreign.py"] = b"synthetic foreign body"
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                whole_archives()[0], sdist(files=files), SOURCE, REPOSITORY
            )
        )
        # Assert
        assert refused

    def test_changed_ignore_authority_is_not_silently_reinterpreted(self):
        # Arrange
        entries = RELEASE.git_tree(SOURCE, REPOSITORY)
        ignore = git("show", SOURCE + ":.gitignore") + b"\n*.py\n"
        # Act
        refused = refusal(
            lambda: RELEASE.selected_paths(
                entries, tomllib.loads(PYPROJECT.decode()), ignore
            )
        )
        # Assert
        assert refused

    def test_tracked_link_under_ignored_path_refuses_selection(self):
        # Arrange
        entries = dict(RELEASE.git_tree(SOURCE, REPOSITORY))
        entries["data/scholar"] = ("120000", "0" * 40, None)
        # Act
        refused = refusal(
            lambda: RELEASE.selected_paths(
                entries,
                tomllib.loads(PYPROJECT.decode()),
                git("show", SOURCE + ":.gitignore"),
            )
        )
        # Assert
        assert refused

    def test_real_tree_tracks_no_ignored_link(self):
        # Arrange
        entries = RELEASE.git_tree(SOURCE, REPOSITORY)
        ignore = git("show", SOURCE + ":.gitignore")
        # Act
        _, selected = RELEASE.selected_paths(
            entries, tomllib.loads(PYPROJECT.decode()), ignore
        )
        # Assert
        assert {name for name, row in entries.items() if row[0] == "120000"} <= selected

    def test_new_force_include_cannot_change_reviewed_package_mapping(self):
        # Arrange
        entries = RELEASE.git_tree(SOURCE, REPOSITORY)
        project = tomllib.loads(PYPROJECT.decode())
        project["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"] = {
            "foreign": "scitex/foreign"
        }
        # Act
        refused = refusal(
            lambda: RELEASE.selected_paths(
                entries, project, git("show", SOURCE + ":.gitignore")
            )
        )
        # Assert
        assert refused

    def test_unowned_inner_and_python_route_refuse_before_apptainer_or_scratch(self):
        # Arrange
        wrapper = HERE / "exec-in-sif.sh"
        cases = (("../foreign.sh", "3.12"), ("run-in-sif.sh", "3.99"))
        # Act
        results = [
            subprocess.run(
                ["/bin/bash", str(wrapper), *case],
                capture_output=True,
                timeout=7,
                env={"PATH": "/usr/bin:/bin", "HOME": "/synthetic-not-created"},
            ).returncode
            for case in cases
        ]
        # Assert
        assert results == [1, 1]


class DocsBundleTests(unittest.TestCase):
    """The release-time Sphinx bundle (PS-121) is admitted only as reviewed."""

    def test_docs_bundle_identity_is_bound_into_the_source_proof(self):
        # Arrange
        wheel_raw, sdist_raw = whole_archives()
        # Act
        identity = RELEASE.source_payload_identity(
            wheel_raw, sdist_raw, SOURCE, REPOSITORY
        )
        # Assert
        assert identity["docs_bundle"]["members"] == len(DOCS_FILES)

    def test_docs_less_wheel_is_refused_rather_than_shipped(self):
        # Arrange
        wheel_raw = wheel(files=public_wheel_files(), docs=None)
        sdist_raw = sdist(files=public_source_files(), docs=None)
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="no docs bundle index",
        )
        # Assert
        assert refused

    def test_wheel_bundle_must_equal_sdist_bundle(self):
        # Arrange
        docs = {**DOCS_FILES, "index.html": b"<html>tampered</html>\n"}
        wheel_raw = wheel(files=public_wheel_files(), docs=docs)
        _, sdist_raw = whole_archives()
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="docs bundles differ",
        )
        # Assert
        assert refused

    def test_sphinx_build_caches_are_refused(self):
        # Arrange
        docs = {**DOCS_FILES, ".doctrees/index.doctree": b"cache"}
        wheel_raw = wheel(files=public_wheel_files(), docs=docs)
        sdist_raw = sdist(files=public_source_files(), docs=docs)
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="build caches",
        )
        # Assert
        assert refused

    def test_tracked_docs_bundle_is_refused(self):
        # Arrange
        entries = dict(RELEASE.git_tree(SOURCE, REPOSITORY))
        entries[DOCS.SOURCE + "index.html"] = entries["LICENSE"]
        ignore = git("show", SOURCE + ":.gitignore")
        # Act
        refused = refusal(
            lambda: RELEASE.selected_paths(
                entries, tomllib.loads(PYPROJECT.decode()), ignore
            ),
            message="must not be tracked",
        )
        # Assert
        assert refused

    def test_wheel_target_must_declare_the_reviewed_artifacts(self):
        # Arrange
        entries = RELEASE.git_tree(SOURCE, REPOSITORY)
        project = tomllib.loads(PYPROJECT.decode())
        del project["tool"]["hatch"]["build"]["targets"]["wheel"]["artifacts"]
        ignore = git("show", SOURCE + ":.gitignore")
        # Act
        refused = refusal(
            lambda: RELEASE.selected_paths(entries, project, ignore),
            message="Hatch mapping changed",
        )
        # Assert
        assert refused

    def test_reviewed_artifacts_are_the_ones_pyproject_declares(self):
        # Arrange
        build = tomllib.loads(PYPROJECT.decode())["tool"]["hatch"]["build"]
        # Act
        declared = [build["targets"][name]["artifacts"] for name in ("wheel", "sdist")]
        # Assert
        assert declared == [DOCS.ARTIFACTS, DOCS.ARTIFACTS]

    def test_bundle_cli_reports_identity_of_built_archives(self):
        # Arrange
        wheel_raw, sdist_raw = whole_archives()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "w.whl").write_bytes(wheel_raw)
            (root / "s.tar.gz").write_bytes(sdist_raw)
            command = [
                sys.executable,
                "-I",
                "-S",
                "-B",
                str(HERE / "release_docs_bundle.py"),
            ]
            # Act
            result = subprocess.run(
                [*command, str(root / "w.whl"), str(root / "s.tar.gz")],
                capture_output=True,
                timeout=7,
            )
        # Assert
        assert result.returncode == 0 and b'"members": 3' in result.stdout


class SourceMetadataTests(unittest.TestCase):
    def test_rehashed_wheel_cannot_change_pure_python_platform_headers(self):
        # Arrange
        valid = b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        headers = (
            valid.replace(b"1.0", b"9.0"),
            valid.replace(b"true", b"false"),
            valid.replace(b"py3-none-any", b"cp312-cp312-linux_x86_64"),
            valid + b"Tag: py3-none-any\n",
        )
        _, sdist_raw = whole_archives()
        wheels = [wheel(files=public_wheel_files(), wheel_body=raw) for raw in headers]
        # Act
        results = [
            refusal(
                lambda raw=raw: RELEASE.source_payload_identity(
                    raw, sdist_raw, SOURCE, REPOSITORY
                ),
                message="wheel platform",
            )
            for raw in wheels
        ]
        # Assert
        assert results == [True, True, True, True]

    def test_required_wheel_metadata_cannot_be_omitted_with_recomputed_record(self):
        # Arrange
        wheel_raw = wheel(files=public_wheel_files(), wheel_body=None)
        _, sdist_raw = whole_archives()
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="wheel platform",
        )
        # Assert
        assert refused

    def test_archive_identity_checks_rehashed_wheel_platform_before_admission(self):
        # Arrange
        wheel_raw = wheel(
            wheel_body=(
                b"Wheel-Version: 1.0\nRoot-Is-Purelib: false\nTag: py3-none-any\n"
            )
        )
        # Act
        refused = refusal(
            lambda: RELEASE.wheel_identity(wheel_raw, VERSION),
            message="wheel platform",
        )
        # Assert
        assert refused

    def test_wheel_license_payload_cannot_be_absent_with_recomputed_record(self):
        # Arrange
        wheel_raw = wheel(files=public_wheel_files(), license_body=None)
        _, sdist_raw = whole_archives()
        # Act
        refused = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="license payload",
        )
        # Assert
        assert refused

    def test_both_artifacts_require_exact_source_license_declaration(self):
        # Arrange
        valid = metadata()
        headers = (
            valid.replace(b"License-File: LICENSE\n", b""),
            valid.replace(b"License-File: LICENSE\n", b"License-File: OTHER\n"),
            valid + b"License-File: LICENSE\n",
        )
        pairs = [
            (
                wheel(
                    files=public_wheel_files(),
                    metadata_body=raw if side == 0 else valid,
                ),
                sdist(
                    files=public_source_files(),
                    metadata_body=raw if side == 1 else valid,
                ),
            )
            for side in (0, 1)
            for raw in headers
        ]
        # Act
        results = [
            refusal(
                lambda w=w, s=s: RELEASE.source_payload_identity(
                    w, s, SOURCE, REPOSITORY
                ),
                message="source License-File",
            )
            for w, s in pairs
        ]
        # Assert
        assert results == [True, True, True, True, True, True]

    def test_genuine_backend_metadata_binds_all_extras_and_entry_groups(self):
        # Arrange
        wheel_raw, sdist_raw = whole_archives()
        # Act
        result = RELEASE.source_payload_identity(
            wheel_raw, sdist_raw, SOURCE, REPOSITORY
        )
        # Assert
        assert result["metadata_source"] == {
            "runtime_requirements": 632,
            "extras": 77,
            "entry_point_groups": 3,
        }

    def test_rehashed_wheel_cannot_strip_declared_runtime_dependencies(self):
        # Arrange
        headers = b"\n".join(
            line
            for line in metadata().split(b"\n")
            if not line.startswith(b"Requires-Dist:")
        )
        wheel_raw = wheel(files=public_wheel_files(), metadata_body=headers)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="runtime requirements",
        )
        # Assert
        assert result

    def test_declared_dependency_floor_is_in_producer_metadata(self):
        # Arrange: guards the tamper case below against a no-op replacement.
        declared = declared_dev_floor()
        # Act
        headers = metadata()
        # Assert
        assert declared in headers

    def test_rehashed_wheel_cannot_change_declared_dependency_floor(self):
        # Arrange: the floor is read from pyproject, so a floor bump keeps
        # this tamper case meaningful.
        headers = metadata().replace(declared_dev_floor(), b"scitex-dev>=0.0.1")
        wheel_raw = wheel(files=public_wheel_files(), metadata_body=headers)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="runtime requirements",
        )
        # Assert
        assert result

    def test_rehashed_wheel_cannot_omit_source_extras(self):
        # Arrange
        headers = metadata().replace(b"Provides-Extra: all\n", b"")
        wheel_raw = wheel(files=public_wheel_files(), metadata_body=headers)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="source extras",
        )
        # Assert
        assert result

    def test_normalized_duplicate_extra_refuses_even_with_recomputed_record(self):
        # Arrange
        headers = metadata() + b"Provides-Extra: Docs\n"
        wheel_raw = wheel(files=public_wheel_files(), metadata_body=headers)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="source extras",
        )
        # Assert
        assert result

    def test_rehashed_wheel_cannot_change_requires_python(self):
        # Arrange
        headers = metadata().replace(
            b"Requires-Python: >=3.10", b"Requires-Python: >=3.11"
        )
        wheel_raw = wheel(files=public_wheel_files(), metadata_body=headers)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="Requires-Python",
        )
        # Assert
        assert result

    def test_sdist_pkg_info_must_retain_runtime_metadata(self):
        # Arrange
        headers = b"\n".join(
            line
            for line in metadata().split(b"\n")
            if not line.startswith(b"Requires-Dist:")
        )
        wheel_raw, _ = whole_archives()
        sdist_raw = sdist(files=public_source_files(), metadata_body=headers)
        RELEASE.sdist_identity(sdist_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="runtime requirements",
        )
        # Assert
        assert result

    def test_generated_extra_marker_cannot_bind_requirement_to_another_extra(self):
        # Arrange
        headers = metadata().replace(b"extra == 'all'", b"extra == 'docs'", 1)
        wheel_raw = wheel(files=public_wheel_files(), metadata_body=headers)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="runtime requirements",
        )
        # Assert
        assert result

    def test_rehashed_console_binding_cannot_target_another_callable(self):
        # Arrange
        entries = PRODUCER_ENTRY_POINTS.replace(
            b"scitex.__main__:main", b"foreign.entry:main"
        )
        wheel_raw = wheel(files=public_wheel_files(), entry_points=entries)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="entry points",
        )
        # Assert
        assert result

    def test_rehashed_entry_points_cannot_add_undeclared_group(self):
        # Arrange
        entries = PRODUCER_ENTRY_POINTS + b"[foreign.group]\nforeign = scitex:main\n"
        wheel_raw = wheel(files=public_wheel_files(), entry_points=entries)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="entry points",
        )
        # Assert
        assert result

    def test_declared_entry_points_cannot_be_absent(self):
        # Arrange
        wheel_raw = wheel(files=public_wheel_files(), entry_points=None)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="entry points",
        )
        # Assert
        assert result

    def test_same_owner_unknown_dist_info_payload_refuses(self):
        # Arrange
        files = {**public_wheel_files(), DIST_INFO + "/foreign.py": b"# undeclared\n"}
        wheel_raw = wheel(files=files)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="undeclared payload",
        )
        # Assert
        assert result

    def test_source_byte_bound_license_cannot_be_rehashed_to_other_text(self):
        # Arrange
        files = {
            **public_wheel_files(),
            DIST_INFO + "/licenses/LICENSE": b"foreign license\n",
        }
        wheel_raw = wheel(files=files)
        _, sdist_raw = whole_archives()
        RELEASE.wheel_identity(wheel_raw, VERSION)
        # Act
        result = refusal(
            lambda: RELEASE.source_payload_identity(
                wheel_raw, sdist_raw, SOURCE, REPOSITORY
            ),
            message="license bytes",
        )
        # Assert
        assert result

    def test_marker_quotes_order_and_parentheses_keep_same_source_contract(self):
        # Arrange
        project = {
            "name": "scitex",
            "dependencies": [],
            "optional-dependencies": {"docs": ["example>=2; python_version < '3.12'"]},
        }
        headers = (
            b"Metadata-Version: 2.4\nLicense-File: LICENSE\nProvides-Extra: docs\n"
            b'Requires-Dist: Example>=2; extra == "docs" '
            b'and (python_version < "3.12")\n'
        )
        # Act
        result = RELEASE.metadata_source_identity(headers, headers, None, project)
        # Assert
        assert result == {
            "runtime_requirements": 1,
            "extras": 1,
            "entry_point_groups": 0,
        }

    def test_marker_condition_cannot_change_while_extra_identity_is_retained(self):
        # Arrange
        project = {
            "name": "scitex",
            "dependencies": [],
            "optional-dependencies": {"docs": ["example>=2; python_version < '3.12'"]},
        }
        headers = (
            b"Metadata-Version: 2.4\nLicense-File: LICENSE\nProvides-Extra: docs\n"
            b"Requires-Dist: example>=2; python_version >= '3.12' and extra == 'docs'\n"
        )
        # Act
        result = refusal(
            lambda: RELEASE.metadata_source_identity(headers, headers, None, project),
            message="runtime requirements",
        )
        # Assert
        assert result

    def test_unknown_or_cyclic_source_extra_never_manufactures_metadata(self):
        # Arrange
        projects = [
            {"name": "scitex", "optional-dependencies": {"all": ["scitex[absent]"]}},
            {"name": "scitex", "optional-dependencies": {"all": ["scitex[all]"]}},
        ]
        # Act
        result = [
            refusal(lambda: RELEASE.declared_metadata(project), message="source extra")
            for project in projects
        ]
        # Assert
        assert result == [True, True]

    def test_unsupported_direct_url_and_dynamic_metadata_fail_closed(self):
        # Arrange
        projects = [
            {
                "name": "scitex",
                "dependencies": ["example @ https://public.invalid/a.whl"],
            },
            {"name": "scitex", "dynamic": ["dependencies"]},
        ]
        # Act
        result = [
            refusal(lambda: RELEASE.declared_metadata(project)) for project in projects
        ]
        # Assert
        assert result == [True, True]


def owned_driver_fixture(mode):
    """Execute the real tracked lifecycle seam with an owned synthetic child."""
    source = (HERE / "run-in-sif.sh").read_text()
    start = source.index("# BEGIN owned temporary-root lifecycle")
    end = source.index("# END owned temporary-root lifecycle") + len(
        "# END owned temporary-root lifecycle"
    )
    lifecycle = source[start:end]
    with tempfile.TemporaryDirectory(prefix="umbrella-owned-driver-") as temporary:
        parent = Path(temporary)
        unrelated = parent / "unrelated"
        unrelated.mkdir()
        (unrelated / "retained").write_text("keep")
        script = parent / "fixture.sh"
        bodies = {
            "success": 'printf done > "$TMPDIR/result"; return 0',
            "failure": 'printf failed > "$TMPDIR/result"; return 37',
            "term": 'printf ready > "$FIXTURE_PARENT/ready"; while :; do sleep 1; done',
            "int": 'printf ready > "$FIXTURE_PARENT/ready"; while :; do sleep 1; done',
            "stubborn-term": (
                'trap "" TERM; printf ready > "$FIXTURE_PARENT/ready"; '
                "while :; do sleep 1; done"
            ),
            "symlink": (
                'mv "$TMPDIR" "$TMPDIR.saved"; '
                'ln -s "$FIXTURE_PARENT/unrelated" "$TMPDIR"'
            ),
            "replacement": (
                'mv "$TMPDIR" "$TMPDIR.saved"; mkdir "$TMPDIR"; '
                'printf replacement > "$TMPDIR/retained"'
            ),
        }
        script.write_text(
            'set -euo pipefail\nTMPDIR="$(mktemp -d "$FIXTURE_PARENT/owned-XXXXXX")"\n'
            'printf "%s" "$TMPDIR" > "$FIXTURE_PARENT/root"\n' + lifecycle + "\n"
            'readonly OWNED_TMPDIR="$TMPDIR"\n'
            'readonly OWNED_TMP_ID="$(stat -c \'%d:%i:%u:%a\' -- "$TMPDIR")"\n'
            "driver_body() {\n"
            'printf "%s" "$BASHPID" > "$FIXTURE_PARENT/child"\n'
            + bodies[mode]
            + "\n}\nrun_owned_body\n"
        )
        process = subprocess.Popen(
            ["/usr/bin/bash", str(script)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env={
                "PATH": "/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "FIXTURE_PARENT": str(parent),
            },
        )
        try:
            if mode in {"term", "int", "stubborn-term"}:
                deadline = time.monotonic() + 3
                while not (parent / "ready").exists() and process.poll() is None:
                    if time.monotonic() > deadline:
                        raise RuntimeError("owned driver fixture did not become ready")
                    time.sleep(0.01)
                process.send_signal(signal.SIGINT if mode == "int" else signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=7)
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=7)
            raise
        root = Path((parent / "root").read_text())
        child = int((parent / "child").read_text())
        return {
            "exit": process.returncode,
            "root_absent": not root.exists() and not root.is_symlink(),
            "child_reaped": not Path("/proc/" + str(child)).exists(),
            "unrelated": (unrelated / "retained").read_text(),
            "cleanup_refused": b"cleanup refused" in stderr,
            "replacement_retained": (root / "retained").read_text()
            if mode == "replacement"
            else None,
            "stdout": stdout,
        }


class OwnedDriverCleanupTests(unittest.TestCase):
    def test_all_three_real_drivers_share_the_same_owned_lifecycle(self):
        # Arrange
        sources = [
            (HERE / name).read_text()
            for name in ("run-in-sif.sh", "build-in-sif.sh", "publish-in-sif.sh")
        ]
        # Act
        blocks = [
            text.split("# BEGIN owned temporary-root lifecycle", 1)[1].split(
                "# END owned temporary-root lifecycle", 1
            )[0]
            for text in sources
        ]
        # Assert
        assert len(set(blocks)) == 1

    def test_success_reaps_child_and_removes_only_created_scratch(self):
        # Arrange
        # Act
        result = owned_driver_fixture("success")
        # Assert
        assert result == {
            "exit": 0,
            "root_absent": True,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": False,
            "replacement_retained": None,
            "stdout": b"",
        }

    def test_failure_keeps_child_status_and_cleans_owned_scratch(self):
        # Arrange
        # Act
        result = owned_driver_fixture("failure")
        # Assert
        assert result == {
            "exit": 37,
            "root_absent": True,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": False,
            "replacement_retained": None,
            "stdout": b"",
        }

    def test_term_reaps_owned_group_and_cleans_scratch(self):
        # Arrange
        # Act
        result = owned_driver_fixture("term")
        # Assert
        assert result == {
            "exit": 143,
            "root_absent": True,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": False,
            "replacement_retained": None,
            "stdout": b"",
        }

    def test_int_reaps_owned_group_and_cleans_scratch(self):
        # Arrange
        # Act
        result = owned_driver_fixture("int")
        # Assert
        assert result == {
            "exit": 130,
            "root_absent": True,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": False,
            "replacement_retained": None,
            "stdout": b"",
        }

    def test_term_ignoring_owned_child_is_killed_by_birth_fenced_watchdog(self):
        # Arrange
        # Act
        result = owned_driver_fixture("stubborn-term")
        # Assert
        assert result == {
            "exit": 143,
            "root_absent": True,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": False,
            "replacement_retained": None,
            "stdout": b"",
        }

    def test_symlink_replacement_cannot_delete_unrelated_scratch(self):
        # Arrange
        # Act
        result = owned_driver_fixture("symlink")
        # Assert
        assert result == {
            "exit": 1,
            "root_absent": False,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": True,
            "replacement_retained": None,
            "stdout": b"",
        }

    def test_inode_replacement_is_retained_and_refused(self):
        # Arrange
        # Act
        result = owned_driver_fixture("replacement")
        # Assert
        assert result == {
            "exit": 1,
            "root_absent": False,
            "child_reaped": True,
            "unrelated": "keep",
            "cleanup_refused": True,
            "replacement_retained": "replacement",
            "stdout": b"",
        }


if __name__ == "__main__":
    unittest.main(verbosity=2)
