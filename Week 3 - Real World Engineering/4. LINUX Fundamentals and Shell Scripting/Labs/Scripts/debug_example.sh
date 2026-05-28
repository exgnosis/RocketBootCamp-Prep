#!/bin/bash
set -x   # Enable debug mode
msg="Debugging in action"
echo "Message: $msg"
set +x   # Disable debug mode
echo "Script finished."
