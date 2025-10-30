#!/bin/bash
# SecurePipe CLI Installation Script
# Sets up user-friendly aliases: securepipe and sp

set -e

echo "🚀 Installing SecurePipe CLI..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_PATH="$SCRIPT_DIR/securepipe_wrapper.sh"

# Detect shell and add aliases
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
    echo "📝 Detected zsh shell"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
    echo "📝 Detected bash shell"
else
    echo "⚠️  Unsupported shell: $SHELL"
    echo "Please manually add the following aliases to your shell configuration:"
    echo "alias securepipe='$WRAPPER_PATH'"
    echo "alias sp='$WRAPPER_PATH'"
    exit 1
fi

# Check if aliases already exist
if grep -q "alias securepipe=" "$SHELL_RC"; then
    echo "✅ SecurePipe aliases already exist in $SHELL_RC"
else
    # Add aliases to shell configuration
    echo "" >> "$SHELL_RC"
    echo "# SecurePipe CLI Aliases" >> "$SHELL_RC"
    echo "alias securepipe='$WRAPPER_PATH'" >> "$SHELL_RC"
    echo "alias sp='$WRAPPER_PATH'" >> "$SHELL_RC"
    echo "✅ Added SecurePipe aliases to $SHELL_RC"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "You can now use:"
echo "  securepipe --help    # Show help"
echo "  sp --help           # Show help (short version)"
echo "  securepipe auth login    # Login"
echo "  sp auth login       # Login (short version)"
echo ""
echo "To start using the aliases, either:"
echo "  1. Restart your terminal"
echo "  2. Or run: source $SHELL_RC"
echo "" 