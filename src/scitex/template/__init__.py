"""SciTeX template — thin compatibility shim for scitex-template.

Every public name that used to live in ``scitex.template`` now lives in the
standalone ``scitex-template`` package (module ``scitex_template``). This
file aliases ``scitex.template`` to ``scitex_template`` via ``sys.modules``
so every previous import path — including deep submodule paths like
``scitex.template._mcp.handlers`` and ``scitex.template._project.clone_research``
— resolves to the same object as the direct import.

Public API (grep-able surface; real definitions in scitex_template):

    Cloners:          clone_template, clone_module, clone_research,
                      clone_research_minimal, clone_scitex_minimal,
                      clone_pip_project, clone_singularity,
                      clone_writer_directory
    Constants:        MINIMAL_INCLUDE_DIRS, CODE_TEMPLATES, PROJECT_STRUCTURE
    Code snippets:    get_code_template, list_code_templates, get_all_templates
    Info:             get_available_templates_info
    Customization:    customize_template, customize_minimal_template
    Generators:       create_project_config, create_paths_config,
                      create_env_template, create_requirements_file,
                      create_minimal_readme, create_project_readme,
                      build_directory_tree
    Scholar integ.:   setup_scholar_writer_integration, ensure_integration
    Git re-exports:   init_git_repo, find_parent_git, create_child_git,
                      remove_child_git

Install: ``pip install scitex[template]``  (or ``pip install scitex-template``).
See: https://github.com/ywatanabe1989/scitex-template
"""

import sys as _sys

try:
    import scitex_template as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.template requires the 'scitex-template' package. "
        "Install with: pip install scitex[template]  (or: pip install scitex-template)"
    ) from _e

_sys.modules[__name__] = _real
