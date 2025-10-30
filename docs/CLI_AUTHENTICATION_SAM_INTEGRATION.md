# CLI Authentication & SAM Integration Guide

> **Comprehensive guide to SecurePipe CLI authentication system and its integration with SAM (SecurePipe Access Management)**

## Table of Contents
- [Overview](#overview)
- [Authentication Architecture](#authentication-architecture)
- [CLI Authentication Flow](#cli-authentication-flow)
- [SAM Integration](#sam-integration)
- [Security Controls](#security-controls)
- [Configuration Management](#configuration-management)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

## Overview

SecurePipe CLI provides enterprise-grade authentication with deep integration to SAM (SecurePipe Access Management). The system implements a multi-layer security architecture that ensures every CLI command is protected by comprehensive access controls while maintaining a smooth user experience.

### Key Features

- **🔐 JWT Token-Based Authentication**: Secure login with automatic token management
- **⚖️ SAM Permission Integration**: Every CLI command protected by fine-grained permissions
- **🌐 Context-Based Access Control**: Time, location, device, and risk-based restrictions
- **📊 Real-Time Monitoring**: Comprehensive audit logging and metrics
- **🛡️ Zero Trust Integration**: Advanced security with SAM as the foundation
- **🔑 API Key Support**: Long-lived keys for automation and integrations

## Authentication Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLI Authentication Architecture              │
├─────────────────────────────────────────────────────────────────┤
│  🔐 Authentication Layer                                        │
│  ├── JWT Token Management                                       │
│  ├── API Key Support (sp_ prefix)                               │
│  ├── Secure Token Storage (600 permissions)                     │
│  └── Automatic Token Validation                                 │
├─────────────────────────────────────────────────────────────────┤
│  ⚖️ Authorization Layer (SAM)                                   │
│  ├── Fine-Grained Permission Checking                           │
│  ├── Role-Based Access Control (RBAC)                           │
│  ├── Context-Based Access Control                               │
│  └── Resource Ownership Validation                              │
├─────────────────────────────────────────────────────────────────┤
│  🛡️ Security Controls                                           │
│  ├── Rate Limiting (Burst/Per-Minute/Per-Hour)                  │
│  ├── Time-Based Access Control                                  │
│  ├── Location-Based Restrictions                                │
│  └── Risk-Based Authentication                                  │
├─────────────────────────────────────────────────────────────────┤
│  📊 Monitoring & Audit                                          │
│  ├── Real-Time Permission Metrics                               │
│  ├── Comprehensive Audit Logging                                │
│  ├── Performance Monitoring                                     │
│  └── Security Event Correlation                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

**CLI Files:**
- `cli/main.py` - Main CLI entry point with command registration
- `cli/client.py` - Main client for SecurePipe CLI operations
- `cli/api_client.py` - HTTP client for communicating with backend API
- `cli/config.py` - Configuration management and token storage
- `cli/commands/auth.py` - Authentication commands
- `cli/commands/sam.py` - SAM management commands
- `cli/commands/sam_advanced.py` - Advanced SAM features
- `cli/commands/sam_monitoring.py` - SAM monitoring and metrics

## CLI Authentication Flow

### Step-by-Step Authentication Process

```bash
# 1. Initial Authentication
securepipe auth login --username admin@company.com
# → Prompts for password
# → Validates credentials with backend
# → Receives JWT token and user info
# → Stores securely in ~/.securepipe/config.json

# 2. Context Setup
securepipe account use my-account
securepipe workspace use production
securepipe project use my-project
# → Sets default context for future commands

# 3. Command Execution with SAM
securepipe pipeline create my-pipeline
# → CLI includes JWT token in request
# → Backend validates token
# → SAM checks permissions automatically
# → Returns success/error based on permissions

# 4. Permission Verification
securepipe sam permissions check --action "pipeline:create" --resource "pipeline:*"
# → Explicit permission checking
# → Shows detailed permission information
```

### Authentication Commands

```bash
# Login and Authentication
securepipe auth login --username admin@company.com
securepipe auth logout
securepipe auth status
securepipe auth whoami

# API Key Management
securepipe auth api-key --name "automation-key" --expires-days 90
securepipe auth list-keys
securepipe auth revoke-key <key_id>
```

### Configuration Storage

**File Location:** `~/.securepipe/config.json` (600 permissions)

```json
{
    "api_url": "http://localhost:8000",
    "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "current_user": {
        "id": 123,
        "username": "admin",
        "email": "admin@company.com",
        "role": "ADMIN",
        "is_superuser": true
    },
    "default_account_id": "account_123",
    "default_workspace_id": "workspace_456",
    "default_project_id": "project_789",
    "timeout": 30,
    "verify_ssl": true
}
```

## SAM Integration

### Automatic Permission Checking

Every CLI command automatically triggers SAM permission evaluation:

```python
# Backend automatically checks permissions for each API call
await sam_service.require_permission(
    user_id=current_user.id,
    action="pipeline:create",
    resource="pipeline:*",
    account_id=account_id,
    workspace_id=workspace_id,
    project_id=project_id,
    context={
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": datetime.now().isoformat()
    }
)
```

### SAM Management Commands

#### Role Management
```bash
# Create and manage roles
securepipe sam roles create --name "PipelineAdmin" --description "Pipeline administration"
securepipe sam roles list --account-id 123
securepipe sam roles get --role-id 456

# Role assignment
securepipe sam users assign-role --user-id 123 --role-id 456
securepipe sam users remove-role --user-id 123 --role-id 456
```

#### Policy Management
```bash
# Create and manage policies
securepipe sam policies create --name "SecurePolicy" --policy-file policy.json
securepipe sam policies list --workspace-id 456
securepipe sam policies get --policy-id 789

# Policy attachment
securepipe sam attachments attach-to-role --role-id 123 --policy-id 456
securepipe sam attachments detach-from-role --role-id 123 --policy-id 456
```

#### Permission Checking
```bash
# Check specific permissions
securepipe sam permissions check --action "pipeline:create" --resource "pipeline:*"
securepipe sam permissions check --action "account:delete" --resource "account:123" --context context.json

# Get user permissions
securepipe sam users get-permissions --user-id 123 --account-id 456
```

### Advanced SAM Features

#### Policy Testing and Validation
```bash
# Test policies against standard scenarios
securepipe sam-advanced test-policy --policy-id 123

# Generate policy reports
securepipe sam-advanced generate-report --policy-id 123

# Policy health checks
securepipe sam-advanced health-check

# Policy validation
securepipe sam-advanced validate-policy --policy-id 123
```

#### Usage Monitoring
```bash
# Monitor policy usage
securepipe sam-advanced monitor-usage

# Get analytics dashboard
securepipe sam-advanced dashboard

# Generate documentation
securepipe sam-advanced generate-docs --policy-id 123
```

### SAM Monitoring and Metrics

#### Real-Time Metrics
```bash
# Record custom metrics
securepipe sam-monitoring metrics record --metric-name "permission_checks" --value 1 --labels '{"user_id":"123"}'

# Get metrics
securepipe sam-monitoring metrics get --metric-name "permission_checks" --start-time "2024-01-01T00:00:00Z"

# Aggregated metrics
securepipe sam-monitoring metrics aggregate --metric-name "permission_checks" --aggregation "avg" --window 3600
```

#### Performance Monitoring
```bash
# Performance metrics
securepipe sam-monitoring performance metrics --duration 1h

# Usage metrics
securepipe sam-monitoring usage metrics --account-id 123
```

#### Audit Logging
```bash
# View audit logs
securepipe sam-monitoring audit logs --user-id 123 --action "pipeline:create" --limit 50

# Export audit data
securepipe sam-monitoring audit export --start-time "2024-01-01T00:00:00Z" --end-time "2024-01-31T23:59:59Z" --format json
```

#### Alert Configuration
```bash
# Configure alert rules
securepipe sam-monitoring config alert --metric "permission_denials" --condition "gt" --threshold 10 --window 300 --severity high --name "High Denial Rate"

# Rate limiting configuration
securepipe sam-monitoring config rate-limit --burst-limit 10 --per-minute 60 --per-hour 1000

# Session configuration
securepipe sam-monitoring config session --timeout 3600 --idle-timeout 1800 --max-sessions 5
```

## Security Controls

### Context-Based Access Control

#### Time-Based Access
```python
# Business hours enforcement
if not is_business_hours():
    raise AccessDeniedError("Access restricted to business hours (9 AM - 6 PM)")

# Weekend restrictions
if is_weekend() and not is_emergency_access():
    raise AccessDeniedError("Weekend access requires emergency approval")
```

#### Location-Based Access
```python
# IP address validation
if not is_allowed_ip(request.client.host):
    raise AccessDeniedError("Access denied from this IP address")

# Geographic restrictions
if not is_allowed_country(ip_country):
    raise AccessDeniedError("Access denied from this geographic location")
```

#### Device-Based Access
```python
# User agent validation
if not is_modern_browser(user_agent):
    raise AccessDeniedError("Modern browser required")

# Malicious user agent blocking
if is_malicious_user_agent(user_agent):
    raise AccessDeniedError("Suspicious user agent detected")
```

#### Risk-Based Access
```python
# Risk scoring
risk_score = calculate_risk_score(user_id, action, resource, context)
if risk_score > risk_threshold:
    raise AccessDeniedError(f"Risk score {risk_score} exceeds threshold {risk_threshold}")
```

### Rate Limiting

**Configuration:**
- **Burst Limit**: 10 requests per burst
- **Per-Minute Limit**: 60 requests per minute
- **Per-Hour Limit**: 1000 requests per hour

**Implementation:**
```python
# Rate limit checking
rate_limit_check = await rate_limit_service.check_rate_limit(
    user_id=user_id,
    action=action,
    ip_address=ip_address,
    context=context
)

if not rate_limit_check['allowed']:
    raise RateLimitExceededError(f"Rate limit exceeded: {rate_limit_check['reason']}")
```

### Resource Ownership Validation

**Multi-Level Validation:**
```python
# Account-level validation
if not await is_account_member(user_id, account_id):
    raise AccessDeniedError("User is not a member of this account")

# Workspace-level validation
if not await has_workspace_access(user_id, workspace_id):
    raise AccessDeniedError("User does not have access to this workspace")

# Project-level validation
if not await has_project_access(user_id, project_id):
    raise AccessDeniedError("User does not have access to this project")

# Pipeline-level validation
if not await has_pipeline_access(user_id, pipeline_id):
    raise AccessDeniedError("User does not have access to this pipeline")
```

## Configuration Management

### Configuration Manager

```python
# cli/config.py
class ConfigManager:
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".securepipe"
        self.config_file = self.config_dir / "config.json"
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has API token)."""
        config = self.load_config()
        return config.api_token is not None
    
    def clear_auth(self) -> None:
        """Clear authentication data."""
        self.update_config(
            api_token=None,
            current_user=None
        )
    
    def set_context(self, account_id: Optional[str] = None, 
                   workspace_id: Optional[str] = None,
                   project_id: Optional[str] = None) -> None:
        """Set current context (account/workspace/project)."""
        updates = {}
        if account_id is not None:
            updates['default_account_id'] = account_id
        if workspace_id is not None:
            updates['default_workspace_id'] = workspace_id
        if project_id is not None:
            updates['default_project_id'] = project_id
        
        if updates:
            self.update_config(**updates)
```

### Environment Variables

```bash
# CLI Configuration
SECUREPIPE_API_URL="http://localhost:8000"
SECUREPIPE_CONFIG_DIR="~/.securepipe"
SECUREPIPE_DEBUG="false"

# Authentication
SECUREPIPE_TOKEN_TIMEOUT=3600
SECUREPIPE_VERIFY_SSL="true"
```

## Error Handling

### Authentication Errors

**Common Error Scenarios:**
```python
# 401 Unauthorized - Token expired/invalid
if response.status_code == 401:
    click.echo("❌ Authentication failed: Token expired or invalid")
    click.echo("Run 'securepipe auth login' to re-authenticate")

# 403 Forbidden - Insufficient permissions
if response.status_code == 403:
    click.echo("❌ Permission denied: Insufficient permissions")
    click.echo("Contact your administrator for access")

# 429 Too Many Requests - Rate limit exceeded
if response.status_code == 429:
    click.echo("⚠️ Rate limit exceeded. Please try again later")

# Connection Error - Backend unavailable
if connection_error:
    click.echo("❌ Cannot connect to SecurePipe API")
    click.echo("Please check if the backend is running and the URL is correct")
```

### Error Recovery

**Automatic Recovery:**
```python
# Token refresh on 401
if response.status_code == 401:
    if await refresh_token():
        # Retry request with new token
        return await retry_request()
    else:
        # Prompt for re-login
        return await prompt_relogin()

# Rate limit backoff
if response.status_code == 429:
    retry_after = response.headers.get('Retry-After', 60)
    await asyncio.sleep(retry_after)
    return await retry_request()
```

## Best Practices

### Security Best Practices

1. **Secure Token Storage**
   ```bash
   # Ensure proper file permissions
   chmod 600 ~/.securepipe/config.json
   chmod 700 ~/.securepipe/
   ```

2. **Regular Token Rotation**
   ```bash
   # Rotate API keys regularly
   securepipe auth revoke-key <old_key_id>
   securepipe auth api-key --name "new-key" --expires-days 30
   ```

3. **Principle of Least Privilege**
   ```bash
   # Use specific permissions instead of wildcards
   securepipe sam permissions check --action "pipeline:read" --resource "pipeline:123"
   # Instead of: --resource "pipeline:*"
   ```

4. **Context Validation**
   ```bash
   # Always verify context before operations
   securepipe auth status
   securepipe sam permissions check --action "account:delete" --resource "account:123"
   ```

### Operational Best Practices

1. **Monitoring and Alerting**
   ```bash
   # Set up monitoring for permission denials
   securepipe sam-monitoring config alert --metric "permission_denials" --threshold 5 --severity medium
   
   # Monitor authentication failures
   securepipe sam-monitoring config alert --metric "auth_failures" --threshold 3 --severity high
   ```

2. **Regular Auditing**
   ```bash
   # Export audit logs regularly
   securepipe sam-monitoring audit export --start-time "2024-01-01T00:00:00Z" --end-time "2024-01-31T23:59:59Z" --format json --file audit_logs.json
   ```

3. **Policy Testing**
   ```bash
   # Test policies before deployment
   securepipe sam-advanced test-policy --policy-id 123
   securepipe sam-advanced validate-policy --policy-id 123
   ```

## Troubleshooting

### Common Issues

**Authentication Problems:**
```bash
# Check authentication status
securepipe auth status

# Verify token validity
securepipe auth whoami

# Clear and re-authenticate
securepipe auth logout
securepipe auth login --username admin@company.com
```

**Permission Issues:**
```bash
# Check specific permissions
securepipe sam permissions check --action "pipeline:create" --resource "pipeline:*"

# View user permissions
securepipe sam users get-permissions --user-id 123

# Check role assignments
securepipe sam users list-roles --user-id 123
```

**Configuration Issues:**
```bash
# Check configuration
cat ~/.securepipe/config.json

# Reset configuration
rm ~/.securepipe/config.json
securepipe config init
```

**Connection Issues:**
```bash
# Test API connectivity
curl -H "Authorization: Bearer $(jq -r .api_token ~/.securepipe/config.json)" http://localhost:8000/api/v1/health

# Check backend status
securepipe health check
```

### Debug Mode

```bash
# Enable debug mode for detailed logging
securepipe --debug auth login --username admin@company.com

# View debug logs
tail -f ~/.securepipe/logs/debug.log
```

## API Reference

### Authentication Endpoints

```python
# Login
POST /api/v1/auth/login
{
    "username": "admin@company.com",
    "password": "password"
}

# Response
{
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": 123,
        "username": "admin",
        "email": "admin@company.com",
        "role": "ADMIN"
    }
}
```

### SAM Endpoints

```python
# Check permissions
POST /api/v1/sam/permissions/check
{
    "action": "pipeline:create",
    "resource": "pipeline:*",
    "account_id": 123,
    "workspace_id": 456,
    "project_id": 789,
    "context": {
        "ip_address": "192.168.1.100",
        "user_agent": "SecurePipe-CLI/1.0.0"
    }
}

# Response
{
    "allowed": true,
    "action": "pipeline:create",
    "resource": "pipeline:*",
    "context": {...}
}
```

### Monitoring Endpoints

```python
# Record metrics
POST /api/v1/sam/monitoring/metrics/record
{
    "metric_name": "permission_checks",
    "value": 1.0,
    "labels": {
        "user_id": "123",
        "action": "pipeline:create"
    }
}

# Get audit logs
GET /api/v1/sam/monitoring/audit/logs?user_id=123&action=pipeline:create&limit=50
```

---

## Summary

SecurePipe CLI provides a comprehensive authentication and authorization system that integrates deeply with SAM. The multi-layer security architecture ensures enterprise-grade protection while maintaining usability. Key features include:

- **🔐 Secure JWT-based authentication** with automatic token management
- **⚖️ Fine-grained SAM permission checking** for every CLI command
- **🌐 Context-based access control** with time, location, device, and risk factors
- **📊 Comprehensive monitoring and audit logging** for compliance
- **🛡️ Zero Trust integration** with advanced security controls
- **🔑 API key support** for automation and integrations

This system provides the foundation for secure, compliant, and auditable CLI operations in enterprise environments. 