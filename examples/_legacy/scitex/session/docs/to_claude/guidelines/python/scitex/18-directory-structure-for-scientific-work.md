<!-- ---
!-- Timestamp: 2025-05-30 08:21:56
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/IMPORTANT-SCITEX-18-directory-structure-for-scientific-work.md
!-- --- -->

## Directory Structure of Scientific Project

```
<project root>
│
├── config/                 # Configuration files
│   └── *.yaml              # YAML config files (PATH.yaml, etc.)
│
├── data/                   # Centralized data storage
│   └── <dir_name>/         # Organized by category
│        └── file.ext → ../../scripts/<script>_out/file.ext  # Symlinks to script outputs
│
└── scripts/                # Script files and outputs
    └── <category>/
        ├── script.py       # Python script
        └── script_out/     # Output directory for this script
            ├── file.ext    # Output files
            └── logs/       # Logging directory for each run (managed by `stx.session.start` and `stx.session.close`)
                ├── RUNNING
                ├── FINISHED_SUCCESS
                └── FINISHED_FAILURE
└── examples/
└── tests/
└── .dev/
```


**IMPORTANT**:
- DO NOT CREATE DIRECTORIES IN PROJECT ROOT
- Create child directories under predefined directories instead

## Temporal Working Space: `./.dev`
- For your temporally work, use `./.dev`
  - Organize playground with categoris:
    `./.dev/category-name-1/...`
    `./.dev/category-name-2/...`

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->
