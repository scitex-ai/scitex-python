<!-- ---
!-- Timestamp: 2025-08-31 05:04:43
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.claude/to_claude/guidelines/python/HOW-TO-DEBUG-with-MULTIPLE_AGENTS.md
!-- --- -->

### Session Management
```bash
# Create session
screen -dmS debug_$ISSUE_ID

# Send commands
screen -S debug_$ISSUE_ID -X stuff "python script.py\n"

# Capture output with history
screen -S debug_$ISSUE_ID -X hardcopy -h /tmp/debug_capture.txt

# Clean up
screen -S debug_$ISSUE_ID -X quit
```

### Live Debugging
```bash
# List current code
screen -S debug_$ISSUE_ID -X stuff "l\n"

# Inspect variables
screen -S debug_$ISSUE_ID -X stuff "pp locals()\n"

# Continue execution
screen -S debug_$ISSUE_ID -X stuff "c\n"
```

## CIPDB Integration

### Agent-Specific Breakpoints
```python
import cipdb
import os

# Only DebuggerAgent stops here
cipdb.set_trace(os.getenv("AGENT_ID") == "DebuggerAgent")

# ID-based conditional breakpoints
cipdb.set_trace(id="validation_error")
cipdb.set_trace(id="db_connection")
cipdb.set_trace(id="auth_failure")
```

### Environment Control
```bash
# Agent identification
export AGENT_ID=DebuggerAgent

# Selective breakpoint activation
export CIPDB_IDS=validation_error,auth_failure

# Disable all breakpoints
export CIPDB_ID=false
```

## Multi-Agent Workflow

### 1. Issue Identification
```bash
# Initial error capture
screen -dmS error_scan
screen -S error_scan -X stuff "python failing_script.py\n"
sleep 2
screen -S error_scan -X hardcopy -h /tmp/initial_error.txt
grep "Traceback\|Error" /tmp/initial_error.txt
```

### 2. Breakpoint Insertion
File: problematic_script.py
```python
# Add conditional breakpoints at suspected locations
import cipdb

def validate_input(data):
    cipdb.set_trace(id="input_validation")
    # validation logic here

def database_query(sql):
    cipdb.set_trace(id="db_query")
    # database code here
```

### 3. Targeted Debugging
```bash
# Activate specific breakpoints
export CIPDB_IDS=input_validation
export AGENT_ID=DebuggerAgent

# Start debugging session
screen -dmS debug_input
screen -S debug_input -X stuff "python problematic_script.py\n"
sleep 1

# Capture debugger state
screen -S debug_input -X hardcopy -h /tmp/debug_state.txt
tail -20 /tmp/debug_state.txt
```

### 4. State Analysis
```bash
# Extract current location
grep "^> " /tmp/debug_state.txt | tail -1

# Check variable states
screen -S debug_input -X stuff "pp vars()\n"
sleep 0.5
screen -S debug_input -X hardcopy -h /tmp/vars.txt
```

### 5. Hypothesis Testing
```bash
# Modify variables in debugger
screen -S debug_input -X stuff "data['field'] = 'corrected_value'\n"

# Continue and observe
screen -S debug_input -X stuff "c\n"
sleep 2
screen -S debug_input -X hardcopy -h /tmp/result.txt
```

## Output Parsing

### Session Status Check
```bash
# Check if debugger is active
tail -1 /tmp/debug_capture.txt | grep -q "ipdb>" && echo "In debugger"

# Extract current file and line
grep "^> " /tmp/debug_capture.txt | tail -1 | awk '{print $2 ":" $3}'
```

### Error Detection
```bash
# Check for exceptions
grep -i "traceback\|error\|exception" /tmp/debug_capture.txt

# Success indicators
grep -i "completed\|success\|passed" /tmp/debug_capture.txt
```

## Agent Coordination

### TestAgent Setup
```bash
export AGENT_ID=TestAgent
# TestAgent inserts breakpoints but doesn't stop
cipdb.set_trace(id="test_failure", condition=False)
```

### DebuggerAgent Activation
```bash
export AGENT_ID=DebuggerAgent
export CIPDB_IDS=test_failure
# DebuggerAgent activates TestAgent's breakpoints
```

## Best Practices

1. Session Naming
   - Use: debug_${ISSUE_ID}_${TIMESTAMP}
   - Avoid conflicts between concurrent debugging

2. Timing
   - Add sleep 0.5-2s after commands before capture
   - Screen needs time to process

3. Cleanup
   - Run screen -wipe periodically
   - Set CIPDB_ID=false in production

4. Breakpoint IDs
   - Use descriptive names: auth_failure, db_timeout
   - Document ID purposes in code comments

## Integration Benefits

- No wrapper complexity - direct screen usage
- CIPDB enables selective debugging per agent
- Multiple agents can debug same codebase simultaneously
- Full observability through screen captures
- Simple environment variable control

The combination provides powerful debugging without architectural overhead.

<!-- EOF -->
