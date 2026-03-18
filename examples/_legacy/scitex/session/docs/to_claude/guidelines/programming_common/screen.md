<!-- ---
!-- Timestamp: 2025-09-02 00:58:41
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/programming_common/screen.md
!-- --- -->

Agents can use THEIR OWN TERMINAL by using `screen` as follows:

``` bash
# Parameters
ISSUE_ID="1234"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCREEN_NAME="debug_$ISSUE_ID_$TIMESTAMP"
CAPTURE_FILE="./debug/$SCREEN_NAME.txt"
WORKING_DIR="$(pwd)"

# Create Screen Session
screen -dmS "$SCREEN_NAME"
# List created screen session as a confirmation
screen -list | grep "$SCREEN_NAME"
# Cat the contents in the screen session as humans see
screen -S "$SCREEN_NAME" -X hardcopy -h "$CAPTURE_FILE" && cat "$CAPTURE_FILE"
# Send commands to the screen session
screen -S "$SCREEN_NAME" -X stuff "cd $WORKING_DIR\n"
screen -S "$SCREEN_NAME" -X stuff "python script.py\n"
# Although executing the script may take time, you can check the screen session anytime
screen -S "$SCREEN_NAME" -X hardcopy -h "$CAPTURE_FILE" && cat "$CAPTURE_FILE"
# Cleanup the screen session
screen -S "$SCREEN_NAME" -X quit
```

<!-- EOF -->
