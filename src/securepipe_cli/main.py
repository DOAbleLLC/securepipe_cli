#!/usr/bin/env python3
"""
SecurePipe CLI Wrapper
A working CLI interface that bypasses import issues
"""

import click
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

def load_config() -> Optional[Dict[str, Any]]:
    """Load CLI configuration"""
    config_file = Path.home() / ".securepipe" / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def save_config(config: Dict[str, Any]) -> None:
    """Save CLI configuration"""
    config_file = Path.home() / ".securepipe" / "config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """Make API request with authentication"""
    config = load_config()
    if not config:
        raise click.ClickException("No configuration found. Run 'securepipe auth login' first.")
    
    url = f"{config['api_url']}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if config.get('api_token'):
        headers["Authorization"] = f"Bearer {config['api_token']}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 401:
            raise click.ClickException("Authentication failed. Run 'securepipe auth login' to re-authenticate.")
        elif response.status_code >= 400:
            error_msg = "API Error"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_msg)
            except:
                pass
            raise click.ClickException(f"{error_msg} (Status: {response.status_code})")
        
        return response.json() if response.content else {}
        
    except requests.exceptions.ConnectionError:
        raise click.ClickException("Cannot connect to SecurePipe API. Is the backend running?")
    except requests.exceptions.Timeout:
        raise click.ClickException("Request timed out. Please try again.")
    except Exception as e:
        raise click.ClickException(f"Request failed: {e}")

def show_welcome_banner():
    """Display the SecurePipe welcome banner"""
    # SecurePipe text logo
    click.echo("+======================================================================================+")
    click.echo("|   ███████╗███████╗ ██████╗██╗   ██╗██████╗ ███████╗    ██████╗ ██╗██████╗ ███████╗   |")
    click.echo("|   ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██╔════╝    ██╔══██╗██║██╔══██╗██╔════╝   |")
    click.echo("|   ███████╗█████╗  ██║     ██║   ██║██████╔╝█████╗      ██████╔╝██║██████╔╝█████╗     |")
    click.echo("|   ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██╔══╝      ██╔═══╝ ██║██╔═══╝ ██╔══╝     |")
    click.echo("|   ███████║███████╗╚██████╗╚██████╔╝██║  ██║███████╗    ██║     ██║██║     ███████╗   |")
    click.echo("|   ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝     ╚══════╝   |")
    click.echo("+======================================================================================+")
    click.echo("")

@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0", prog_name="SecurePipe")
@click.pass_context
def cli(ctx):
    """SecurePipe CLI - Secure Infrastructure Pipeline Management"""
    if ctx.invoked_subcommand is None:
        show_welcome_banner()
        click.echo(ctx.get_help())
    pass

# Authentication Commands
@cli.group()
def auth():
    """Authentication commands"""
    pass

@auth.command()
@click.option('--username', '-u', prompt=True, help='Username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
def login(username: str, password: str):
    """Login to SecurePipe"""
    try:
        config = load_config() or {"api_url": "http://localhost:8000"}
        
        response = requests.post(
            f"{config['api_url']}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            config['api_token'] = data['access_token']
            config['current_user'] = data.get('user', {})
            save_config(config)
            
            click.echo("✅ Login successful!")
            click.echo(f"👤 User: {data.get('user', {}).get('username', 'Unknown')}")
            click.echo(f"📧 Email: {data.get('user', {}).get('email', 'Unknown')}")
        else:
            click.echo("❌ Login failed. Check your credentials.")
            
    except Exception as e:
        click.echo(f"❌ Login failed: {e}")

@auth.command()
def logout():
    """Logout from SecurePipe"""
    config = load_config()
    if config:
        config['api_token'] = None
        config['current_user'] = None
        save_config(config)
    click.echo("✅ Logged out successfully")

@auth.command()
def status():
    """Check authentication status"""
    config = load_config()
    if not config or not config.get('api_token'):
        click.echo("❌ Not authenticated")
        return
    
    try:
        data = make_request('GET', '/api/v1/auth/me')
        click.echo("✅ Authenticated")
        click.echo(f"👤 User: {data.get('username', 'Unknown')}")
        click.echo(f"📧 Email: {data.get('email', 'Unknown')}")
    except Exception as e:
        click.echo(f"❌ Authentication check failed: {e}")

# Account Commands
@cli.group()
def account():
    """Account management commands"""
    pass

@account.command()
def list():
    """List accounts"""
    try:
        data = make_request('GET', '/api/v1/accounts/')
        accounts = data.get('accounts', data.get('items', []))
        
        if not accounts:
            click.echo("No accounts found")
            return
        
        click.echo(f"📋 Accounts ({len(accounts)}):")
        for account in accounts:
            click.echo(f"  🏢 {account.get('name', 'Unknown')} (ID: {account.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list accounts: {e}")

@account.command()
@click.option('--name', '-n', prompt=True, help='Account name')
@click.option('--tier', type=click.Choice(['FREE', 'PAID', 'ENTERPRISE']), default='FREE', help='Account tier')
def create(name: str, tier: str):
    """Create a new account"""
    try:
        data = make_request('POST', '/api/v1/accounts/', {
            'name': name,
            'tier': tier
        })
        
        click.echo("✅ Account created successfully!")
        click.echo(f"🏢 Name: {data.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"💳 Tier: {data.get('tier', 'Unknown')}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create account: {e}")

# Workspace Commands
@cli.group()
def workspace():
    """Workspace management commands"""
    pass

@workspace.command()
@click.option('--account-id', '-a', help='Account ID (uses default if not specified)')
def list(account_id: Optional[str]):
    """List workspaces"""
    try:
        config = load_config()
        if not account_id:
            account_id = config.get('default_account_id')
            if not account_id:
                click.echo("❌ No account ID specified and no default account set")
                return
        
        data = make_request('GET', f'/api/v1/workspaces/?account_id={account_id}')
        workspaces = data.get('workspaces', data.get('items', []))
        
        if not workspaces:
            click.echo("No workspaces found")
            return
        
        click.echo(f"📋 Workspaces ({len(workspaces)}):")
        for workspace in workspaces:
            click.echo(f"  🏢 {workspace.get('name', 'Unknown')} (ID: {workspace.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list workspaces: {e}")

@workspace.command()
@click.option('--name', '-n', prompt=True, help='Workspace name')
@click.option('--description', '-d', help='Workspace description')
@click.option('--account-id', '-a', help='Account ID (uses default if not specified)')
def create(name: str, description: Optional[str], account_id: Optional[str]):
    """Create a new workspace"""
    try:
        config = load_config()
        if not account_id:
            account_id = config.get('default_account_id')
            if not account_id:
                click.echo("❌ No account ID specified and no default account set")
                return
        
        workspace_data = {
            'name': name
        }
        if description:
            workspace_data['description'] = description
        
        data = make_request('POST', '/api/v1/workspaces/', workspace_data)
        
        click.echo("✅ Workspace created successfully!")
        click.echo(f"🏢 Name: {data.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"📝 Description: {data.get('description', 'None')}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create workspace: {e}")

# Project Commands
@cli.group()
def project():
    """Project management commands"""
    pass

@project.command()
@click.option('--workspace-id', '-w', help='Workspace ID (uses default if not specified)')
def list(workspace_id: Optional[str]):
    """List projects"""
    try:
        config = load_config()
        if not workspace_id:
            workspace_id = config.get('default_workspace_id')
            if not workspace_id:
                click.echo("❌ No workspace ID specified and no default workspace set")
                return
        
        account_id = config.get('default_account_id')
        if not account_id:
            click.echo("❌ No default account set")
            return
        
        data = make_request('GET', f'/api/v1/projects/?workspace_id={workspace_id}')
        projects = data.get('projects', data.get('items', []))
        
        if not projects:
            click.echo("No projects found")
            return
        
        click.echo(f"📋 Projects ({len(projects)}):")
        for project in projects:
            click.echo(f"  📁 {project.get('name', 'Unknown')} (ID: {project.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list projects: {e}")

@project.command()
@click.option('--name', '-n', prompt=True, help='Project name')
@click.option('--description', '-d', help='Project description')
@click.option('--workspace-id', '-w', help='Workspace ID (uses default if not specified)')
def create(name: str, description: Optional[str], workspace_id: Optional[str]):
    """Create a new project"""
    try:
        config = load_config()
        if not workspace_id:
            workspace_id = config.get('default_workspace_id')
            if not workspace_id:
                click.echo("❌ No workspace ID specified and no default workspace set")
                return
        
        project_data = {
            'name': name,
            'workspace_id': int(workspace_id)
        }
        if description:
            project_data['description'] = description
        
        data = make_request('POST', '/api/v1/projects/', project_data)
        
        click.echo("✅ Project created successfully!")
        click.echo(f"📁 Name: {data.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"📝 Description: {data.get('description', 'None')}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create project: {e}")

# Pipeline Commands
@cli.group()
def pipeline():
    """Pipeline management commands"""
    pass

@pipeline.command()
@click.option('--project-id', '-p', help='Project ID (uses default if not specified)')
def list(project_id: Optional[str]):
    """List pipelines"""
    try:
        config = load_config()
        if not project_id:
            project_id = config.get('default_project_id')
            if not project_id:
                click.echo("❌ No project ID specified and no default project set")
                return
        
        account_id = config.get('default_account_id')
        workspace_id = config.get('default_workspace_id')
        if not account_id or not workspace_id:
            click.echo("❌ No default account or workspace set")
            return
        
        data = make_request('GET', f'/api/v1/pipelines/?project_id={project_id}')
        pipelines = data.get('pipelines', data.get('items', []))
        
        if not pipelines:
            click.echo("No pipelines found")
            return
        
        click.echo(f"📋 Pipelines ({len(pipelines)}):")
        for pipeline in pipelines:
            click.echo(f"  🔄 {pipeline.get('name', 'Unknown')} (ID: {pipeline.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list pipelines: {e}")

@pipeline.command()
@click.option('--name', '-n', prompt=True, help='Pipeline name')
@click.option('--description', '-d', help='Pipeline description')
@click.option('--project-id', '-p', help='Project ID (uses default if not specified)')
def create(name: str, description: Optional[str], project_id: Optional[str]):
    """Create a new pipeline"""
    try:
        config = load_config()
        if not project_id:
            project_id = config.get('default_project_id')
            if not project_id:
                click.echo("❌ No project ID specified and no default project set")
                return
        
        pipeline_data = {
            'name': name,
            'project_id': int(project_id)
        }
        if description:
            pipeline_data['description'] = description
        
        data = make_request('POST', '/api/v1/pipelines/', pipeline_data)
        
        click.echo("✅ Pipeline created successfully!")
        click.echo(f"🔄 Name: {data.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"📝 Description: {data.get('description', 'None')}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create pipeline: {e}")

# Audit Commands
@cli.group()
def audit():
    """Audit log commands"""
    pass

@audit.command()
@click.option('--limit', '-l', default=10, help='Number of logs to show')
@click.option('--type', '-t', type=click.Choice(['sam', 'general']), default='sam', help='Type of audit logs')
def logs(limit: int, type: str):
    """Show audit logs"""
    try:
        if type == 'sam':
            data = make_request('GET', f'/api/v1/sam/audit/permission-checks?limit={limit}')
        else:
            data = make_request('GET', f'/api/v1/governance/audit-logs?limit={limit}')
        
        if not data:
            click.echo("No audit logs found")
            return
        
        click.echo(f"📋 {type.upper()} Audit Logs ({len(data)}):")
        for i, log in enumerate(data, 1):
            if type == 'sam':
                click.echo(f"  {i}. [{log.get('event_timestamp', 'Unknown')}] User {log.get('user_id', 'Unknown')} - {log.get('action', 'Unknown')} on {log.get('resource', 'Unknown')} - {'✅ Granted' if log.get('permission_granted') else '❌ Denied'}")
            else:
                click.echo(f"  {i}. [{log.get('timestamp', 'Unknown')}] User {log.get('user_id', 'Unknown')} - {log.get('action', 'Unknown')} on {log.get('resource_type', 'Unknown')}")
            
    except Exception as e:
        click.echo(f"❌ Failed to get audit logs: {e}")

@audit.command()
def stats():
    """Show audit statistics"""
    try:
        data = make_request('GET', '/api/v1/sam/audit/stats/overview')
        
        if not data:
            click.echo("No audit statistics available")
            return
        
        click.echo("📊 SAM Audit Statistics:")
        click.echo(f"  🔐 Permission Checks: {data.get('permission_checks', {}).get('total', 0)}")
        click.echo(f"  ✅ Granted: {data.get('permission_checks', {}).get('granted', 0)}")
        click.echo(f"  ❌ Denied: {data.get('permission_checks', {}).get('denied', 0)}")
        click.echo(f"  📈 Grant Rate: {data.get('permission_checks', {}).get('grant_rate', 0):.1f}%")
        click.echo(f"  👥 Role Operations: {data.get('role_operations', {}).get('total', 0)}")
        click.echo(f"  📋 Policy Operations: {data.get('policy_operations', {}).get('total', 0)}")
        
    except Exception as e:
        click.echo(f"❌ Failed to get audit statistics: {e}")

# Config Commands
@cli.group()
def config():
    """Configuration commands"""
    pass

@config.command()
def show():
    """Show current configuration"""
    config_data = load_config()
    if not config_data:
        click.echo("❌ No configuration found")
        return
    
    click.echo("📋 Configuration:")
    click.echo(f"  API URL: {config_data.get('api_url', 'Not set')}")
    click.echo(f"  Has Token: {'Yes' if config_data.get('api_token') else 'No'}")
    click.echo(f"  Account ID: {config_data.get('default_account_id', 'Not set')}")
    click.echo(f"  Workspace ID: {config_data.get('default_workspace_id', 'Not set')}")
    click.echo(f"  Project ID: {config_data.get('default_project_id', 'Not set')}")

@config.command()
@click.option('--account-id', '-a', help='Set default account ID')
@click.option('--workspace-id', '-w', help='Set default workspace ID')
@click.option('--project-id', '-p', help='Set default project ID')
def set(account_id: Optional[str], workspace_id: Optional[str], project_id: Optional[str]):
    """Set configuration values"""
    config_data = load_config() or {}
    
    if account_id:
        config_data['default_account_id'] = account_id
        click.echo(f"✅ Default account ID set to: {account_id}")
    
    if workspace_id:
        config_data['default_workspace_id'] = workspace_id
        click.echo(f"✅ Default workspace ID set to: {workspace_id}")
    
    if project_id:
        config_data['default_project_id'] = project_id
        click.echo(f"✅ Default project ID set to: {project_id}")
    
    if not any([account_id, workspace_id, project_id]):
        click.echo("❌ Please specify at least one value to set (--account-id, --workspace-id, or --project-id)")
        return
    
    save_config(config_data)

@config.command()
def reset():
    """Reset configuration to defaults"""
    if click.confirm("Are you sure you want to reset the configuration?"):
        config_file = Path.home() / ".securepipe" / "config.json"
        if config_file.exists():
            config_file.unlink()
        click.echo("✅ Configuration reset")

# Health Commands
@cli.group()
def health():
    """Health check commands (backend status & dependencies)."""
    pass

@health.command('status')
def health_status():
    """Check basic backend health (/api/v1/health)"""
    try:
        data = make_request('GET', '/api/v1/health')
        try:
            from rich import print_json
            print_json(json.dumps(data))
        except ImportError:
            click.echo(json.dumps(data, indent=2))
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")

@health.command('detailed')
def health_detailed():
    """Check detailed backend health (/api/v1/health/detailed)"""
    try:
        data = make_request('GET', '/api/v1/health/detailed')
        try:
            from rich import print_json
            print_json(json.dumps(data))
        except ImportError:
            click.echo(json.dumps(data, indent=2))
    except Exception as e:
        click.echo(f"❌ Detailed health check failed: {e}")

@health.command('ready')
def health_ready():
    """Check readiness endpoint (/api/v1/health/ready)"""
    try:
        data = make_request('GET', '/api/v1/health/ready')
        try:
            from rich import print_json
            print_json(json.dumps(data))
        except ImportError:
            click.echo(json.dumps(data, indent=2))
    except Exception as e:
        click.echo(f"❌ Readiness check failed: {e}")

if __name__ == '__main__':
    cli() 