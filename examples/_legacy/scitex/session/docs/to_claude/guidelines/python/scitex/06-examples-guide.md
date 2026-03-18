<!-- ---
!-- Timestamp: 2025-08-31 17:55:12
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/SCITEX-06-examples-guide.md
!-- --- -->

# Example Guidelines

## MUST USE `SCITEX`
All example files MUST use `scitex` and follow the `scitex` framework
Understand all the `scitex` guidelines in this directory

## `./examples` directory
- Output directory creation is automatically handled by:
  - `stx.session.start`
  - `stx.session.close`
  - `stx.io.save`
- `./examples` directory must contain key features to demonstrate the project

## MUST RUN AND PRODUCE EXPLANATORY RESULTS
- Implementing examples is not sufficient
- ALWAYS RUN IMPLEMENTED EXAMPLES AND PRODUCE EXPLANATORY RESULTS
  - Embrace figures for visual understanding
  - Logs are automatically created by the scitex framework is also valuable
  - The less comment in the script, the better.
  - If comments need, it should be handled in `src` or `scripts`, possibly with verbose option.

## Start from small
1. Ensure each example works correctly one by one
   Before working on multiple example files, complete a specific example
   For example, if an issue found across multiple files, first, try to fix it on a file and run it to check the troubleshooting works.
2. Increment this step gradually until all examples are prepared correctly.


## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`
```

CLAUDE UNDERSTOOD: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/IMPORTANT-SCITEX-06-examples-guide.md

<!-- EOF -->
