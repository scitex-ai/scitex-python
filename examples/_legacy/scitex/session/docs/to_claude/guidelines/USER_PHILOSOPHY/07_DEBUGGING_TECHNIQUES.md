<!-- ---
!-- Timestamp: 2025-09-01 08:32:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/07_DEBUGGING_TECHNIQUES.md
!-- --- -->

# Debugging Techniques

1.  Basic Tools
    -   Screen sessions for isolation
        -   See `./docs/to_claude/guidelines/python/programming_common/screen.md` (MCP server support)
    -   CIPDB for conditional debugging
        -   See `./docs/to_claude/guidelines/python/official/cipdb.md`
    -   IceCream for variable inspection
        -   See `./docs/to_claude/guidelines/python/icrecream.md`

2.  Quick Debug Setup

```bash
screen -dmS debug_session
screen -S debug_session -X stuff "python script.py\n"
sleep 2
screen -S debug_session -X hardcopy -h /tmp/output.txt
```

1.  Code Integration

```python
import cipdb
from icecream import ic

def debug_function(data):
    ic(data)
    cipdb.set_trace(id="function_debug")
    result = ic(process_data(data))
    return result
```

1.  Targeted Debugging

```bash
export CIPDB_IDS=function_debug
python script.py
```

1.  Best Practices
    -   Name sessions: debug_${ISSUE_ID}
    -   Add sleep 1-2s before screen capture
    -   Use ic.disable() in production
    -   Run screen -wipe periodically

2.  Benefits
    -   Multiple agents debug independently
    -   Selective breakpoints by agent ID
    -   Complete session capture

```

1.  Screen Session Handling

1.  CIPDB (Conditional ipdb) for selective debugging independently from other agents

1.  IceCream Integration

1.  Multi-Agent Workflow
    -   Issue Identification
        ```bash
        screen -dmS error_scan
        screen -S error_scan -X stuff "python failing_script.py\n"
        sleep 2
        screen -S error_scan -X hardcopy -h /tmp/initial_error.txt
        grep "Traceback\\|Error" /tmp/initial_error.txt
        ```

    -   Enhanced Debugging with IceCream

        File: problematic_script.py
        ```python
        import cipdb
        from icecream import ic

        def validate_input(data):
            ic(data)
            cipdb.set_trace(id="input_validation")
            result = ic(validation_logic(data))
            return result

        def database_query(sql):
            ic(sql)
            cipdb.set_trace(id="db_query")
            connection = ic(get_connection())
            return execute_query(connection, sql)
        ```

    -   Targeted Debugging
        ```bash
        export CIPDB_IDS=input_validation
        export AGENT_ID=DebuggerAgent
        screen -dmS debug_input
        screen -S debug_input -X stuff "python problematic_script.py\n"
        sleep 1
        screen -S debug_input -X hardcopy -h /tmp/debug_state.txt
        ```

    -   State Analysis with IceCream Output
        ```bash
        grep "ic|" /tmp/debug_state.txt
        grep "^> " /tmp/debug_state.txt | tail -1
        screen -S debug_input -X stuff "pp vars()\n"
        ```

2.  Best Practices
    -   Session Naming
        -   Use: debug_${ISSUE_ID}_${TIMESTAMP}
        -   Avoid conflicts between concurrent debugging

    -   Timing
        -   Add sleep 0.5-2s after commands before capture
        -   Screen needs time to process

    -   IceCream Configuration
        -   Disable ic in production: ic.disable()
        -   Use agent-specific prefixes
        -   Include context for complex debugging

    -   Cleanup
        -   Run screen -wipe periodically
        -   Set CIPDB_ID=false in production

    -   Integration Pattern
        ```python

        from icecream import ic
        import cipdb
        import os

        def debug_function(data):
            ic(data)
            cipdb.set_trace(id="function_debug") # You need to insert this line to inspect with ID
            result = ic(process_data(data))
            return result
        ```

        `CIPDB_ID=function_debug python /path/to/filename.py`

3.  Integration Benefits
    -   IceCream provides lightweight variable inspection
    -   CIPDB enables selective debugging by boolean, `$CLAUD_AGENT_ID`, `$CIPD_ID`, or `CIPD_IDS`
        -   Multiple agents can debug same codebase simultaneously
    -   Screen captures show everything human developers can see
        Keep in mind the line number limitation in `~/.screenrc`

<!-- EOF -->
