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

@click.group()
@click.version_option(version="1.0.0", prog_name="SecurePipe")
def cli():
    """SecurePipe CLI - Secure Infrastructure Pipeline Management"""
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
        
        data = make_request('GET', f'/api/v1/accounts/{account_id}/workspaces/')
        workspaces = data.get('workspaces', data.get('items', []))
        
        if not workspaces:
            click.echo("No workspaces found")
            return
        
        click.echo(f"📋 Workspaces ({len(workspaces)}):")
        for workspace in workspaces:
            click.echo(f"  🏢 {workspace.get('name', 'Unknown')} (ID: {workspace.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list workspaces: {e}")

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
        
        data = make_request('GET', f'/api/v1/accounts/{account_id}/workspaces/{workspace_id}/projects/')
        projects = data.get('projects', data.get('items', []))
        
        if not projects:
            click.echo("No projects found")
            return
        
        click.echo(f"📋 Projects ({len(projects)}):")
        for project in projects:
            click.echo(f"  📁 {project.get('name', 'Unknown')} (ID: {project.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list projects: {e}")

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
        
        data = make_request('GET', f'/api/v1/accounts/{account_id}/workspaces/{workspace_id}/projects/{project_id}/pipelines/')
        pipelines = data.get('pipelines', data.get('items', []))
        
        if not pipelines:
            click.echo("No pipelines found")
            return
        
        click.echo(f"📋 Pipelines ({len(pipelines)}):")
        for pipeline in pipelines:
            click.echo(f"  🔄 {pipeline.get('name', 'Unknown')} (ID: {pipeline.get('id', 'Unknown')})")
            
    except Exception as e:
        click.echo(f"❌ Failed to list pipelines: {e}")

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
def reset():
    """Reset configuration to defaults"""
    if click.confirm("Are you sure you want to reset the configuration?"):
        config_file = Path.home() / ".securepipe" / "config.json"
        if config_file.exists():
            config_file.unlink()
        click.echo("✅ Configuration reset")

if __name__ == '__main__':
    cli() 