#!/bin/bash
# SecurePipe CLI Wrapper
# Allows users to run: securepipe, sp, or ./securepipe

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the securepipe CLI
"$SCRIPT_DIR/securepipe" "$@" 