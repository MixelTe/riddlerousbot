#!/bin/bash

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./ping.sh <URL>"
    exit 1
fi

URL=$1
# Get timestamp in UTC+3 (adjusting TZ variable for the command)
TIMESTAMP=$(TZ="Etc/GMT-3" date +"%Y-%m-%d %H:%M:%S")

# Use curl to get the status code and the response body
# -s: silent, -i: include headers (to get status), -L: follow redirects
RESPONSE=$(curl -s -i -m 10 "$URL")

# Extract the HTTP status code
STATUS=$(echo "$RESPONSE" | grep "HTTP/" | awk '{print $2}' | tail -n 1)

# Extract the body (everything after the first blank line)
BODY=$(echo "$RESPONSE" | sed '1,/^\r\{0,1\}$/d')

if [ "$STATUS" = "200" ]; then
    echo "[$TIMESTAMP] INFO: Status $STATUS OK"
elif [ -z "$STATUS" ]; then
    echo "[$TIMESTAMP] CRITICAL: Connection failed. Reason: Could not resolve host or timeout"
else
    # Handles 4xx, 5xx and other non-200 codes
    LEVEL="ERROR"
    [[ "$STATUS" =~ ^3 ]] && LEVEL="WARNING" # Optional: label 3xx as warning

    echo "[$TIMESTAMP] $LEVEL: Status $STATUS Body: $BODY"
fi