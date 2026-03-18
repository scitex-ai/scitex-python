<!-- ---
!-- Timestamp: 2025-09-01 08:23:25
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/05_PRIORITY_CONFIG.md
!-- --- -->

# Centraliazed, PriorityConfig

-   **./config**
    Centralized directory for parameters, meaning scripts should avoid to define parameters as much as possible

-   **Logically Separated YAML files**
    e.g., `./config/PATH.yaml`, `./config/COLORS.yaml`

-   **Precedence with Priority**
    direct → config → env → default

-   **Type conversion**: Automatic type casting

Please see the official documentation (`./docs/to_claude/guidelines/python/official/priority_config-README.md`)

<!-- EOF -->
