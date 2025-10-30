# SecurePipe CLI Usage Guide

## 🚀 Quick Start

### Option 1: Direct Execution (Recommended)
```bash
./securepipe --help
./securepipe auth login
```

### Option 2: User-Friendly Aliases
After running the installation script:
```bash
./install.sh
source ~/.zshrc  # or restart terminal
```

Then use:
```bash
securepipe --help
sp --help
```

### Option 3: Global Installation
```bash
pip install -e .
```

Then use from anywhere:
```bash
securepipe --help
sp --help
```

## 📋 Available Commands

### Authentication
```bash
securepipe auth login      # Login to SecurePipe
securepipe auth logout     # Logout
securepipe auth status     # Check authentication status
```

### Account Management
```bash
securepipe account list    # List accounts
securepipe account create  # Create new account
```

### Workspace Management
```bash
securepipe workspace list    # List workspaces
securepipe workspace create  # Create new workspace
```

### Project Management
```bash
securepipe project list    # List projects
securepipe project create  # Create new project
```

### Pipeline Management
```bash
securepipe pipeline list    # List pipelines
securepipe pipeline create  # Create new pipeline
```

### Configuration
```bash
securepipe config show     # Show current configuration
securepipe config set      # Set configuration values
securepipe config reset    # Reset configuration
```

### Audit & Monitoring
```bash
securepipe audit logs      # Show audit logs
securepipe audit stats     # Show audit statistics
```

## 🎯 Short Commands (sp)

All commands work with the short `sp` alias:
```bash
sp --help
sp auth login
sp account list
sp workspace create
```

## 🔧 Troubleshooting

### Module Import Warnings
If you see warnings like:
```
RuntimeWarning: 'src.securepipe_cli.main' found in sys.modules...
```

**Solution**: Use `./securepipe` instead of `python3 -m src.securepipe_cli.main`

### Backend Health

If commands fail with connectivity errors, verify backend health:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/detailed
```

If health fails, see backend troubleshooting for Redis/S3/Nomad checks.

If the database shows unhealthy but Postgres is reachable, restart backend to load latest code/config (Compose doesn't auto-reload):

```bash
cd ../securepipe
docker compose restart backend
```

### Command Not Found
If `securepipe` or `sp` commands are not found:

1. **Check if aliases are set up**:
   ```bash
   alias | grep securepipe
   ```

2. **Re-run installation**:
   ```bash
   ./install.sh
   source ~/.zshrc  # or ~/.bashrc
   ```

3. **Install globally**:
   ```bash
   pip install -e .
   ```

## 📁 File Structure
```
securepipe_cli/
├── securepipe              # Main launcher (no warnings)
├── securepipe_wrapper.sh   # Shell wrapper
├── install.sh              # Installation script
├── src/securepipe_cli/     # Source code
└── pyproject.toml          # Package configuration
```

## 🎨 Welcome Screen
The CLI displays a beautiful SecurePipe logo on startup:
```
+======================================================================================+
|   ███████╗███████╗ ██████╗██╗   ██╗██████╗ ███████╗    ██████╗ ██╗██████╗ ███████╗   |
|   ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██╔════╝    ██╔══██╗██║██╔══██╗██╔════╝   |
|   ███████╗█████╗  ██║     ██║   ██║██████╔╝█████╗      ██████╔╝██║██████╔╝█████╗     |
|   ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██╔══╝      ██╔═══╝ ██║██╔═══╝ ██╔══╝     |
|   ███████║███████╗╚██████╗╚██████╔╝██║  ██║███████╗    ██║     ██║██║     ███████╗   |
|   ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝     ╚══════╝   |
+======================================================================================+
``` 