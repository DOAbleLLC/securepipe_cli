# SecurePipe CLI

A comprehensive command-line interface for SecurePipe - the secure infrastructure pipeline management platform.

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

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

## Backend Health Notes

If CLI commands cannot reach the backend, verify service health:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/detailed
```

Default backend rate limit is 100 requests/min per client IP.

If backend health reports the DB as unhealthy but Postgres is up, restart the backend container to ensure latest code/config is loaded (Compose is not using auto-reload):

```bash
cd ../securepipe
docker compose restart backend
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

### User-Friendly Setup (Recommended)

After installing from source, set up user-friendly aliases:

```bash
# Navigate to CLI directory
cd securepipe_cli

# Run installation script to set up aliases
./install.sh

# Reload shell configuration
source ~/.zshrc  # or ~/.bashrc

# Now you can use both commands
securepipe --help
sp --help
```

## Quick Start

### 1. Authentication

```bash
# Login to SecurePipe
securepipe auth login
sp auth login  # Short command alias

# Check authentication status
securepipe auth status
sp auth status  # Short command alias

# Show current user
securepipe auth whoami
sp auth whoami  # Short command alias
```

### 2. Account Management

```bash
# List accounts
securepipe account list
sp account list  # Short command alias

# Create new account
securepipe account create --name "My Organization"
sp account create --name "My Organization"  # Short command alias

# Select account as default
securepipe account select <account-id>
sp account select <account-id>  # Short command alias
```

### 3. Workspace Management

```bash
# List workspaces
securepipe workspace list
sp workspace list  # Short command alias

# Create workspace
securepipe workspace create --name "Development" --account-id <account-id>
sp workspace create --name "Development" --account-id <account-id>  # Short command alias

# Select workspace as default
securepipe workspace select <workspace-id>
sp workspace select <workspace-id>  # Short command alias
```

### 4. Project Management

```bash
# List projects
securepipe project list
sp project list  # Short command alias

# Create project
securepipe project create --name "My Project" --workspace-id <workspace-id>
sp project create --name "My Project" --workspace-id <workspace-id>  # Short command alias

# Select project as default
securepipe project select <project-id>
sp project select <project-id>  # Short command alias
```

### 5. Pipeline Management

```bash
# List pipelines
securepipe pipeline list
sp pipeline list  # Short command alias

# Create pipeline from YAML
securepipe pipeline create --file pipeline.yaml
sp pipeline create --file pipeline.yaml  # Short command alias

# Execute pipeline
securepipe pipeline run --pipeline-id <pipeline-id>
sp pipeline run --pipeline-id <pipeline-id>  # Short command alias

# Monitor execution
securepipe pipeline status --pipeline-id <pipeline-id>
sp pipeline status --pipeline-id <pipeline-id>  # Short command alias
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
sp auth login                  # Short command alias
securepipe auth logout         # Logout and clear tokens
sp auth logout                 # Short command alias
securepipe auth status         # Check authentication status
sp auth status                 # Short command alias
securepipe auth whoami         # Show current user info
sp auth whoami                 # Short command alias
```

### Account Commands

```bash
securepipe account list        # List all accounts
sp account list                # Short command alias
securepipe account create      # Create new account
sp account create              # Short command alias
securepipe account show        # Show account details
sp account show                # Short command alias
securepipe account update      # Update account
sp account update              # Short command alias
securepipe account delete      # Delete account
sp account delete              # Short command alias
securepipe account select      # Select default account
sp account select              # Short command alias
```

### Workspace Commands

```bash
securepipe workspace list      # List workspaces
sp workspace list              # Short command alias
securepipe workspace create    # Create workspace
sp workspace create            # Short command alias
securepipe workspace show      # Show workspace details
sp workspace show              # Short command alias
securepipe workspace update    # Update workspace
sp workspace update            # Short command alias
securepipe workspace delete    # Delete workspace
sp workspace delete            # Short command alias
securepipe workspace select    # Select default workspace
sp workspace select            # Short command alias
```

### Project Commands

```bash
securepipe project list        # List projects
sp project list                # Short command alias
securepipe project create      # Create project
sp project create              # Short command alias
securepipe project show        # Show project details
sp project show                # Short command alias
securepipe project update      # Update project
sp project update              # Short command alias
securepipe project delete      # Delete project
sp project delete              # Short command alias
securepipe project select      # Select default project
sp project select              # Short command alias
```

### Pipeline Commands

```bash
securepipe pipeline list       # List pipelines
sp pipeline list               # Short command alias
securepipe pipeline create     # Create pipeline
sp pipeline create             # Short command alias
securepipe pipeline show       # Show pipeline details
sp pipeline show               # Short command alias
securepipe pipeline run        # Execute pipeline
sp pipeline run                # Short command alias
securepipe pipeline status     # Check execution status
sp pipeline status             # Short command alias
securepipe pipeline logs       # View execution logs
sp pipeline logs               # Short command alias
securepipe pipeline delete     # Delete pipeline
sp pipeline delete             # Short command alias
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