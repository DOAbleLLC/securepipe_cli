# SecurePipe CLI Quick Reference

## Overview

This quick reference guide provides essential commands and examples for the SecurePipe CLI. Use this guide for daily operations and common tasks.

## Authentication

```bash
# Login
securepipe auth login

# Check status
securepipe auth status

# Logout
securepipe auth logout

# Show current user
securepipe auth whoami
```

## Account Management

```bash
# Create account
securepipe account create --name "My Organization"

# List accounts
securepipe account list

# Show account details
securepipe account show --account-id 1

# Update account
securepipe account update --account-id 1 --name "Updated Name"

# Delete account
securepipe account delete --account-id 1
```

## Workspace Management

```bash
# Create workspace
securepipe workspace create --name "My Workspace" --account-id 1

# List workspaces
securepipe workspace list --account-id 1

# Show workspace details
securepipe workspace show --workspace-id 1

# Update workspace
securepipe workspace update --workspace-id 1 --name "Updated Workspace"

# Delete workspace
securepipe workspace delete --workspace-id 1

# Set current workspace
securepipe workspace select --workspace-id 1

# Show current workspace
securepipe workspace current
```

## Project Management

```bash
# Create project
securepipe project create --name "My Project" --workspace-id 1

# List projects
securepipe project list --workspace-id 1

# Show project details
securepipe project show --project-id 1

# Update project
securepipe project update --project-id 1 --name "Updated Project"

# Delete project
securepipe project delete --project-id 1

# Set current project
securepipe project select --project-id 1

# Show current project
securepipe project current
```

## Pipeline Management

```bash
# Create pipeline
securepipe pipeline create --name "My Pipeline" --file pipeline.yaml --project-id 1

# List pipelines
securepipe pipeline list --project-id 1

# Show pipeline details
securepipe pipeline show --pipeline-id 1

# Execute pipeline
securepipe pipeline execute --pipeline-id 1

# Execute with variables
securepipe pipeline execute --pipeline-id 1 --variables "env=prod,region=us-west-2"

# Execute and wait
securepipe pipeline execute --pipeline-id 1 --wait

# Follow execution logs
securepipe pipeline execute --pipeline-id 1 --follow

# Update pipeline
securepipe pipeline update --pipeline-id 1 --name "Updated Pipeline"

# Delete pipeline
securepipe pipeline delete --pipeline-id 1
```

## Execution Zones (Enterprise)

```bash
# List execution zones
securepipe zones list --workspace-id 1

# Show zone details
securepipe zones show --zone-id 1

# Create custom zone (Enterprise only)
securepipe zones create \
  --workspace-id 1 \
  --name "Production Zone" \
  --cloud-provider aws \
  --region us-west-2 \
  --vpc-cidr 10.0.0.0/16 \
  --external-vault \
  --vault-provider hashicorp \
  --vault-endpoint https://vault.company.com

# Configure external vault
securepipe zones configure-vault \
  --zone-id 1 \
  --vault-provider hashicorp \
  --vault-endpoint https://vault.company.com \
  --vault-auth-method approle \
  --vault-secret-path /securepipe/zone-1

# Test vault connection
securepipe zones test-vault --zone-id 1

# Store secret
securepipe zones store-secret \
  --zone-id 1 \
  --secret-path /aws/credentials \
  --secret-data '{"access_key": "AKIA...", "secret_key": "..."}'

# List secrets
securepipe zones list-secrets --zone-id 1

# Get secret
securepipe zones get-secret --zone-id 1 --secret-path /aws/credentials

# Delete secret
securepipe zones delete-secret --zone-id 1 --secret-path /aws/credentials
```

## Network Policy Management

```bash
# List network policies
securepipe network-policy list --workspace-id 1

# Create network policy
securepipe network-policy create \
  --name "Web Server Access" \
  --workspace-id 1 \
  --source-type workspace \
  --source-id 1 \
  --destination-type workspace \
  --destination-id 1 \
  --protocol tcp \
  --port-range "80,443" \
  --direction ingress \
  --action allow \
  --enabled

# Update network policy (requires full UUID)
securepipe network-policy update <FULL_UUID> --name "Updated Name" --disabled
```

## SAM (Secure Access Management)

### Policy Management
```bash
# Create policy
securepipe sam policies create read-only \
  --description "Read-only access" \
  --policy-document policy.json

# List policies
securepipe sam policies list --account-id 1

# Show policy details
securepipe sam policies get --policy-id 1 --account-id 1

# Update policy
securepipe sam policies update --policy-id 1 --account-id 1 --description "Updated"

# Delete policy
securepipe sam policies delete --policy-id 1 --account-id 1
```

### Role Management
```bash
# Create role
securepipe sam roles create developer \
  --description "Developer role"

# List roles
securepipe sam roles list --account-id 1

# Show role details
securepipe sam roles get --role-id 1 --account-id 1

# Update role
securepipe sam roles update --role-id 1 --account-id 1 --description "Updated"

# Delete role
securepipe sam roles delete --role-id 1 --account-id 1

# Attach policy to role
securepipe sam roles attach-policy --role-id 1 --policy-id 1 --account-id 1

# List role policies
securepipe sam roles list-policies --role-id 1 --account-id 1
```

### User Management
```bash
# Assign role to user
securepipe sam users assign-role --user-id 1 --role-id 1 --account-id 1

# Remove role from user
securepipe sam users remove-role --user-id 1 --role-id 1 --account-id 1

# List user roles
securepipe sam users list-roles --user-id 1 --account-id 1

# Get user permissions
securepipe sam users permissions --user-id 1 --account-id 1
```

### Permission Checking
```bash
# Check single permission
securepipe sam check-permission --user-id 1 --action "read" --resource "pipeline:123" --account-id 1

# Check multiple permissions
securepipe sam check-permissions --user-id 1 --permissions permissions.json --account-id 1
```

## Application Management

```bash
# Create application
securepipe application create \
  --name "My App" \
  --description "My application" \
  --application-type WEB_APPLICATION \
  --security-level high \
  --network-tier private \
  --project-id 1

# List applications
securepipe application list --project-id 1

# Show application details
securepipe application show --application-id 1

# Update application
securepipe application update --application-id 1 --name "Updated App"

# Delete application
securepipe application delete --application-id 1
```

## Application Templates

```bash
# Create template
securepipe application-templates create \
  --name "Web App Template" \
  --description "Template for web applications" \
  --category web \
  --complexity medium \
  --application-type WEB_APPLICATION \
  --security-level high \
  --workspace-id 1 \
  --project-id 1

# List templates
securepipe application-templates list --workspace-id 1

# Show template details
securepipe application-templates show --template-id 1

# Update template
securepipe application-templates update --template-id 1 --name "Updated Template"

# Delete template
securepipe application-templates delete --template-id 1

# Create application from template
securepipe application-templates create-application \
  --template-id 1 \
  --workspace-id 1 \
  --project-id 1 \
  --parameters '{"app_name": "My App"}'
```

## Pipeline Templates

```bash
# Create template
securepipe templates create \
  --name "Terraform Template" \
  --description "Terraform deployment template" \
  --template-type terraform \
  --content-file template.yaml \
  --project-id 1

# List templates
securepipe templates list --project-id 1

# Show template details
securepipe templates show --template-id 1

# Update template
securepipe templates update --template-id 1 --name "Updated Template"

# Delete template
securepipe templates delete --template-id 1

# Create pipeline from template
securepipe templates create-pipeline \
  --template-id 1 \
  --name "My Pipeline" \
  --project-id 1 \
  --variables '{"environment": "production"}'
```

## Compliance Management

```bash
# List compliance frameworks
securepipe compliance frameworks list

# Show framework details
securepipe compliance frameworks show --framework-id 1

# Run compliance check
securepipe compliance check \
  --framework-id 1 \
  --target "pipeline:123" \
  --output json

# List compliance reports
securepipe compliance reports list --workspace-id 1

# Show compliance report
securepipe compliance reports show --report-id 1
```

## Security Management

```bash
# Create security policy
securepipe security policies create \
  --name "Network Security" \
  --type network_segmentation \
  --rules '{"allowed_ports": [22, 80, 443]}' \
  --priority 50

# List security policies
securepipe security policies list

# Show security policy
securepipe security policies show --policy-id 1

# Create secret
securepipe security secrets create \
  --name "Database Password" \
  --value "secret123" \
  --type password \
  --tags "database,production"

# List secrets
securepipe security secrets list

# Get secret
securepipe security secrets get --secret-id 1

# Run security scan
securepipe security scans run \
  --type container_vulnerability \
  --target "docker.io/library/nginx:latest"
```

## Monitoring

```bash
# Get execution status
securepipe monitoring status --execution-id 123

# Get execution logs
securepipe monitoring logs --execution-id 123

# Get execution metrics
securepipe monitoring metrics --execution-id 123

# List recent executions
securepipe monitoring executions --limit 10

# Get system health
securepipe monitoring health
```

## Error Handling

```bash
# List error handling rules
securepipe error-handling rules list

# Create error handling rule
securepipe error-handling rules create \
  --name "Retry on Timeout" \
  --error-type timeout \
  --action retry \
  --max-retries 3

# Show error handling rule
securepipe error-handling rules show --rule-id 1

# Test error handling
securepipe error-handling test --rule-id 1 --scenario timeout
```

## Pipeline Engine (Advanced)

```bash
# Execute pipeline with engine
securepipe pipeline-engine execute --pipeline-id 123

# Execute with variables
securepipe pipeline-engine execute --pipeline-id 123 --variables '{"env": "prod"}'

# Execute asynchronously
securepipe pipeline-engine execute --pipeline-id 123 --async

# Get execution status
securepipe pipeline-engine status --pipeline-id 123 --execution-id 456

# Cancel execution
securepipe pipeline-engine cancel --pipeline-id 123 --execution-id 456

# Validate pipeline
securepipe pipeline-engine validate --pipeline-id 123

# Generate execution plan
securepipe pipeline-engine plan --pipeline-id 123
```

## SAM Advanced Features

```bash
# Test policy
securepipe sam-advanced test-policy --policy-id 1

# Generate policy report
securepipe sam-advanced generate-report --policy-id 1

# Monitor policy usage
securepipe sam-advanced monitor-usage

# View policy dashboard
securepipe sam-advanced dashboard

# Generate policy documentation
securepipe sam-advanced generate-docs --policy-id 1

# Check policy health
securepipe sam-advanced health-check

# Validate policy syntax
securepipe sam-advanced validate-policy --policy-id 1
```

## SAM Monitoring

```bash
# Record custom metric
securepipe sam-monitoring metrics record \
  --metric-name "user_login" \
  --value 1 \
  --labels '{"user_id":"123","action":"login"}'

# Get performance metrics
securepipe sam-monitoring performance metrics

# Get usage statistics
securepipe sam-monitoring usage stats

# List alerts
securepipe sam-monitoring alerts list

# Check system health
securepipe sam-monitoring health check

# Get audit logs
securepipe sam-monitoring audit logs --limit 50
```

## Utility Commands

```bash
# Initialize SecurePipe
securepipe init

# Show configuration
securepipe config show

# Update configuration
securepipe config set --key "api_url" --value "https://api.securepipe.com"

# Show version
securepipe --version

# Show help
securepipe --help

# Show command help
securepipe <command> --help
```

## Common Patterns

### Setting Up a New Project
```bash
# 1. Login
securepipe auth login

# 2. Create or select account
securepipe account create --name "My Organization"
# or
securepipe account list

# 3. Create workspace
securepipe workspace create --name "Development" --account-id 1

# 4. Create project
securepipe project create --name "My Project" --workspace-id 1

# 5. Set context
securepipe workspace select --workspace-id 1
securepipe project select --project-id 1
```

### Creating and Running a Pipeline
```bash
# 1. Create pipeline
securepipe pipeline create --name "Deploy App" --file pipeline.yaml --project-id 1

# 2. Execute pipeline
securepipe pipeline execute --pipeline-id 1 --wait --follow

# 3. Monitor execution
securepipe monitoring status --execution-id 123
```

### Managing Network Security
```bash
# 1. Create allow policy for web traffic
securepipe network-policy create \
  --name "Web Access" \
  --workspace-id 1 \
  --source-type workspace \
  --source-id 1 \
  --destination-type workspace \
  --destination-id 1 \
  --protocol tcp \
  --port-range "80,443" \
  --direction ingress \
  --action allow \
  --enabled

# 2. Create deny policy for security
securepipe network-policy create \
  --name "Block Public" \
  --workspace-id 1 \
  --source-type workspace \
  --source-id 1 \
  --destination-type workspace \
  --destination-id 1 \
  --protocol all \
  --port-range "*" \
  --direction ingress \
  --action deny \
  --enabled
```

### Setting Up SAM Access Control
```bash
# 1. Create policy
securepipe sam policies create developer \
  --description "Developer access" \
  --policy-document developer-policy.json

# 2. Create role
securepipe sam roles create developer \
  --description "Developer role"

# 3. Attach policy to role
securepipe sam roles attach-policy --role-id 1 --policy-id 1 --account-id 1

# 4. Assign role to user
securepipe sam users assign-role --user-id 1 --role-id 1 --account-id 1

# 5. Test permissions
securepipe sam check-permission --user-id 1 --action "read" --resource "pipeline:123" --account-id 1
```

## Output Formats

### JSON Output
```bash
# Many commands support JSON output
securepipe workspace list --account-id 1 --format json

# For API-like responses
securepipe pipeline show --pipeline-id 1 --format json
```

### Table Output (Default)
```bash
# Default table format
securepipe workspace list --account-id 1

# With custom columns
securepipe pipeline list --project-id 1 --columns "id,name,status,created_at"
```

## Environment Variables

```bash
# Set API URL
export SECUREPIPE_API_URL="https://api.securepipe.com"

# Set authentication token
export SECUREPIPE_TOKEN="your-token-here"

# Set default account
export SECUREPIPE_DEFAULT_ACCOUNT="1"

# Set default workspace
export SECUREPIPE_DEFAULT_WORKSPACE="1"

# Set default project
export SECUREPIPE_DEFAULT_PROJECT="1"
```

## Configuration File

The CLI uses `~/.securepipe/config.json` for configuration:

```json
{
  "api_url": "https://api.securepipe.com",
  "default_account": "1",
  "default_workspace": "1",
  "default_project": "1",
  "output_format": "table",
  "timeout": 30,
  "retry_attempts": 3
}
```

## Troubleshooting

### Common Issues

#### Authentication Problems
```bash
# Check auth status
securepipe auth status

# Re-login if needed
securepipe auth logout
securepipe auth login
```

#### Context Issues
```bash
# Check current context
securepipe workspace current
securepipe project current

# Set context explicitly
securepipe workspace select --workspace-id 1
securepipe project select --project-id 1
```

#### Permission Issues
```bash
# Check user permissions
securepipe sam users permissions --user-id 1 --account-id 1

# Check specific permission
securepipe sam check-permission --user-id 1 --action "create" --resource "pipeline" --account-id 1
```

### Debug Mode
```bash
# Enable verbose output
securepipe --verbose <command>

# Show debug information
securepipe --debug <command>
```

## Getting Help

```bash
# General help
securepipe --help

# Command group help
securepipe workspace --help

# Specific command help
securepipe workspace create --help

# Version information
securepipe --version
```

## Support Resources

- **Documentation**: [docs.securepipe.com](https://docs.securepipe.com)
- **API Reference**: [api.securepipe.com](https://api.securepipe.com)
- **Community**: [community.securepipe.com](https://community.securepipe.com)
- **Support**: [support@securepipe.com](mailto:support@securepipe.com) 