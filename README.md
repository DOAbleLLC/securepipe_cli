# SecurePipe CLI

A comprehensive command-line interface for SecurePipe - the secure infrastructure pipeline management platform.

## Features

- 🔐 **Authentication & Authorization**: Secure login with JWT tokens and SAM integration
- 🏢 **Account Management**: Multi-tenant account management with tier-based features
- 🏢 **Workspace Management**: Organize projects across workspaces
- 📁 **Project Management**: Manage infrastructure projects and pipelines
- 🔄 **Pipeline Management**: Create, execute, and monitor infrastructure pipelines
- 🔒 **Security Features**: Network policies, encryption, compliance, and threat detection
- 📊 **Monitoring**: Real-time pipeline monitoring and analytics
- 🛡️ **Zero Trust**: Advanced security with context-based access control

## Installation

### From PyPI (Recommended)

```bash
pip install securepipe-cli
```

### From Source

```bash
git clone https://github.com/securepipe/securepipe-cli.git
cd securepipe-cli
pip install -e .
```

### Quick Install Script

```bash
curl -fsSL https://install.securepipe.com | sh
```

## Quick Start

### 1. Authentication

```bash
# Login to SecurePipe
securepipe auth login

# Check authentication status
securepipe auth status

# Show current user
securepipe auth whoami
```

### 2. Account Management

```bash
# List accounts
securepipe account list

# Create new account
securepipe account create --name "My Organization"

# Select account as default
securepipe account select <account-id>
```

### 3. Workspace Management

```bash
# List workspaces
securepipe workspace list

# Create workspace
securepipe workspace create --name "Development" --account-id <account-id>

# Select workspace as default
securepipe workspace select <workspace-id>
```

### 4. Project Management

```bash
# List projects
securepipe project list

# Create project
securepipe project create --name "My Project" --workspace-id <workspace-id>

# Select project as default
securepipe project select <project-id>
```

### 5. Pipeline Management

```bash
# List pipelines
securepipe pipeline list

# Create pipeline from YAML
securepipe pipeline create --file pipeline.yaml

# Execute pipeline
securepipe pipeline run --pipeline-id <pipeline-id>

# Monitor execution
securepipe pipeline status --pipeline-id <pipeline-id>
```

## Configuration

The CLI stores configuration in `~/.securepipe/config.json`:

```json
{
  "api_url": "https://api.securepipe.com",
  "api_token": "your-jwt-token",
  "default_account_id": "account-id",
  "default_workspace_id": "workspace-id",
  "default_project_id": "project-id",
  "timeout": 30,
  "verify_ssl": true
}
```

### Environment Variables

```bash
export SECUREPIPE_API_URL="https://api.securepipe.com"
export SECUREPIPE_TOKEN="your-jwt-token"
export SECUREPIPE_DEFAULT_ACCOUNT="account-id"
```

## Command Reference

### Authentication Commands

```bash
securepipe auth login          # Login with username/password
securepipe auth logout         # Logout and clear tokens
securepipe auth status         # Check authentication status
securepipe auth whoami         # Show current user info
```

### Account Commands

```bash
securepipe account list        # List all accounts
securepipe account create      # Create new account
securepipe account show        # Show account details
securepipe account update      # Update account
securepipe account delete      # Delete account
securepipe account select      # Select default account
```

### Workspace Commands

```bash
securepipe workspace list      # List workspaces
securepipe workspace create    # Create workspace
securepipe workspace show      # Show workspace details
securepipe workspace update    # Update workspace
securepipe workspace delete    # Delete workspace
securepipe workspace select    # Select default workspace
```

### Project Commands

```bash
securepipe project list        # List projects
securepipe project create      # Create project
securepipe project show        # Show project details
securepipe project update      # Update project
securepipe project delete      # Delete project
securepipe project select      # Select default project
```

### Pipeline Commands

```bash
securepipe pipeline list       # List pipelines
securepipe pipeline create     # Create pipeline
securepipe pipeline show       # Show pipeline details
securepipe pipeline run        # Execute pipeline
securepipe pipeline status     # Check execution status
securepipe pipeline logs       # View execution logs
securepipe pipeline delete     # Delete pipeline
```

### Security Commands

```bash
securepipe sam policies list   # List SAM policies
securepipe sam roles list      # List SAM roles
securepipe sam users list      # List SAM users
securepipe network-policy list # List network policies
securepipe encryption list     # List encryption keys
```

### Configuration Commands

```bash
securepipe config show         # Show configuration
securepipe config set          # Set configuration value
securepipe config reset        # Reset to defaults
```

## Examples

### Complete Workflow

```bash
# 1. Login
securepipe auth login

# 2. Create account
securepipe account create --name "My Company"

# 3. Create workspace
securepipe workspace create --name "Production" --account-id <account-id>

# 4. Create project
securepipe project create --name "Web App" --workspace-id <workspace-id>

# 5. Create pipeline
securepipe pipeline create --file terraform-pipeline.yaml

# 6. Execute pipeline
securepipe pipeline run --pipeline-id <pipeline-id> --wait
```

### CI/CD Integration

```bash
# Set up CI environment
export SECUREPIPE_TOKEN=$CI_SECUREPIPE_TOKEN
export SECUREPIPE_DEFAULT_ACCOUNT=$CI_ACCOUNT_ID

# Run pipeline
securepipe pipeline run --pipeline-id $CI_PIPELINE_ID --wait
```

### Network Security

```bash
# Create allow policy for web traffic
securepipe network-policy create \
  --name "Web Access" \
  --source-type workspace \
  --source-id <source-id> \
  --destination-type workspace \
  --destination-id <dest-id> \
  --protocol tcp \
  --port-range "80,443" \
  --direction ingress \
  --action allow
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/securepipe/securepipe-cli.git
cd securepipe-cli
poetry install
poetry install --group dev
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=securepipe_cli

# Run specific test
poetry run pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Lint code
poetry run flake8 src/ tests/

# Type checking
poetry run mypy src/
```

### Building

```bash
# Build package
poetry build

# Build for distribution
poetry run pyinstaller --onefile --name=securepipe src/securepipe_cli/main.py
```

## Architecture

The CLI follows a modular architecture:

```
securepipe_cli/
├── main.py              # CLI entry point
├── config.py            # Configuration management
├── auth.py              # Authentication handling
├── api_client.py        # API client for backend
├── commands/            # Command modules
│   ├── auth.py         # Authentication commands
│   ├── account.py      # Account management
│   ├── workspace.py    # Workspace management
│   ├── project.py      # Project management
│   ├── pipeline.py     # Pipeline management
│   └── ...
└── utils/              # Utility functions
    ├── display.py      # Output formatting
    └── validation.py   # Input validation
```

## Security

- **JWT Authentication**: Secure token-based authentication
- **Token Storage**: Secure storage using keyring or encrypted config
- **SSL Verification**: Enforced SSL certificate verification
- **Input Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Secure error handling without information leakage

## Support

- **Documentation**: [docs.securepipe.com/cli](https://docs.securepipe.com/cli)
- **API Reference**: [api.securepipe.com](https://api.securepipe.com)
- **Issues**: [GitHub Issues](https://github.com/securepipe/securepipe-cli/issues)
- **Community**: [Community Forum](https://community.securepipe.com)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines. 