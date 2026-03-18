#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-12 14:35:00 (ywatanabe)"
# File: /home/ywatanabe/.bin/utils/wsl2-buzzer.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1

# WSL2-compatible buzzer notification script that works by using Windows PowerShell
# Usage: ./wsl2-buzzer.sh [OPTIONS]
# Options:
#   -t SECONDS   Time in seconds to wait before alert (default: 0)
#   -m MESSAGE   Custom message to display (default: "BUZZER ALERT!")
#   -r NUMBER    Repeat count for the alert (default: 3)
#   -i SECONDS   Interval between repeats in seconds (default: 1)
#   -f FREQUENCY Beep frequency in Hz (default: 750)
#   -d DURATION  Beep duration in ms (default: 300)

# Default values
WAIT_TIME=0
MESSAGE="BUZZER ALERT!"
REPEAT_COUNT=3
INTERVAL=1
FREQUENCY=750
DURATION=300

# Parse command line options
while getopts "t:m:r:i:f:d:" opt; do
    case $opt in
        t) WAIT_TIME=$OPTARG ;;
        m) MESSAGE=$OPTARG ;;
        r) REPEAT_COUNT=$OPTARG ;;
        i) INTERVAL=$OPTARG ;;
        f) FREQUENCY=$OPTARG ;;
        d) DURATION=$OPTARG ;;
        *) echo "Invalid option"; exit 1 ;;
    esac
done

# Wait before alert if specified
if [ $WAIT_TIME -gt 0 ]; then
    echo "Waiting for $WAIT_TIME seconds..."
    sleep $WAIT_TIME
fi

# Function to produce alert using PowerShell
buzz() {
    # Visual notification with colored text
    echo -e "\033[1;31m$MESSAGE\033[0m"

    # Use PowerShell to make a beep sound on Windows
    powershell.exe -Command "[console]::beep($FREQUENCY,$DURATION)" >/dev/null 2>&1

    # Try to use system notification if available
    if command -v notify-send &> /dev/null; then
        notify-send -u critical "BUZZER" "$MESSAGE"
    fi
}

# Produce the alert the specified number of times
for ((repeat=1; repeat <= REPEAT_COUNT; repeat++)); do
    buzz

    # Don't sleep after the last alert
    if [ $repeat -lt $REPEAT_COUNT ]; then
        sleep $INTERVAL
    fi
done

exit 0

# EOF
