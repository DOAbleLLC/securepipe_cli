import json
from pathlib import Path
from typing import Optional, Dict, Any

import click
import requests


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
            response = requests.get(url, headers=headers, params=params, timeout=60)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=60)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=60)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=60)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=60)
        else:
            raise ValueError(f"Unsupported method: {method}")

        if response.status_code == 401:
            raise click.ClickException("Authentication failed. Run 'securepipe auth login' to re-authenticate.")
        elif response.status_code >= 400:
            error_msg = "API Error"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_msg)
            except Exception:
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
@click.version_option(version="1.1.0", prog_name="SecurePipe")
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
    """Account information commands (read-only)"""
    pass


@account.command()
def list():
    """List accounts (read-only)"""
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
@click.argument('account_id', required=False)
def show(account_id: Optional[str]):
    """Show account details (read-only)"""
    try:
        if not account_id:
            click.echo("❌ Account ID is required")
            return

        data = make_request('GET', f'/api/v1/accounts/{account_id}')

        click.echo(f"🏢 Account Details:")
        click.echo(f"  📛 Name: {data.get('name', 'Unknown')}")
        click.echo(f"  🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"  📊 Tier: {data.get('tier', 'Unknown')}")
        click.echo(f"  📊 Status: {data.get('status', 'Unknown')}")

        if data.get('description'):
            click.echo(f"  📝 Description: {data['description']}")

        if data.get('created_at'):
            click.echo(f"  📅 Created: {data['created_at']}")
        if data.get('updated_at'):
            click.echo(f"  📅 Updated: {data['updated_at']}")

    except Exception as e:
        click.echo(f"❌ Failed to show account: {e}")


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

        data = make_request('GET', '/api/v1/workspaces/')
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
@click.option('--account-id', '-a', help='Account ID (uses default if not specified)')
@click.option('--description', '-d', help='Workspace description')
@click.option('--slug', '-s', help='Workspace slug')
def create(name: str, account_id: Optional[str], description: Optional[str], slug: Optional[str]):
    """Create a new workspace"""
    try:
        config = load_config()
        if not account_id:
            account_id = config.get('default_account_id')
            if not account_id:
                click.echo("❌ No account ID specified and no default account set")
                return

        data = {
            'name': name,
            'account_id': int(account_id)
        }

        if description:
            data['description'] = description
        if slug:
            data['slug'] = slug

        response = make_request('POST', '/api/v1/workspaces/', data=data)

        click.echo("✅ Workspace created successfully!")
        click.echo(f"🏢 Name: {response.get('name', name)}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")
        click.echo(f"📁 Account: {response.get('account_id', account_id)}")

        if response.get('description'):
            click.echo(f"📝 Description: {response['description']}")

    except Exception as e:
        click.echo(f"❌ Failed to create workspace: {e}")


@workspace.command()
@click.argument('workspace_id', required=False)
def show(workspace_id: Optional[str]):
    """Show workspace details"""
    try:
        if not workspace_id:
            click.echo("❌ Workspace ID is required")
            return

        data = make_request('GET', f'/api/v1/workspaces/{workspace_id}')

        click.echo(f"🏢 Workspace Details:")
        click.echo(f"  📛 Name: {data.get('name', 'Unknown')}")
        click.echo(f"  🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"  📁 Account: {data.get('account_id', 'Unknown')}")
        click.echo(f"  📊 Status: {data.get('status', 'Unknown')}")

        if data.get('description'):
            click.echo(f"  📝 Description: {data['description']}")
        if data.get('slug'):
            click.echo(f"  🏷️  Slug: {data['slug']}")

        if data.get('created_at'):
            click.echo(f"  📅 Created: {data['created_at']}")
        if data.get('updated_at'):
            click.echo(f"  📅 Updated: {data['updated_at']}")

    except Exception as e:
        click.echo(f"❌ Failed to show workspace: {e}")


@workspace.command()
@click.argument('workspace_id', required=False)
@click.option('--name', '-n', help='New workspace name')
@click.option('--description', '-d', help='New workspace description')
@click.option('--slug', '-s', help='New workspace slug')
def update(workspace_id: Optional[str], name: Optional[str], description: Optional[str], slug: Optional[str]):
    """Update workspace details"""
    try:
        if not workspace_id:
            click.echo("❌ Workspace ID is required")
            return

        if not any([name, description, slug]):
            click.echo("❌ At least one field to update must be specified")
            return

        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if slug:
            data['slug'] = slug

        response = make_request('PUT', f'/api/v1/workspaces/{workspace_id}', data=data)

        click.echo("✅ Workspace updated successfully!")
        click.echo(f"🏢 Name: {response.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Failed to update workspace: {e}")


@workspace.command()
@click.argument('workspace_id', required=False)
@click.confirmation_option(prompt='Are you sure you want to delete this workspace?')
def delete(workspace_id: Optional[str]):
    """Delete a workspace"""
    try:
        if not workspace_id:
            click.echo("❌ Workspace ID is required")
            return

        make_request('DELETE', f'/api/v1/workspaces/{workspace_id}')
        click.echo("✅ Workspace deleted successfully!")

    except Exception as e:
        click.echo(f"❌ Failed to delete workspace: {e}")


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

        data = make_request('GET', '/api/v1/projects/')
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
@click.option('--workspace-id', '-w', help='Workspace ID (uses default if not specified)')
@click.option('--description', '-d', help='Project description')
@click.option('--slug', '-s', help='Project slug')
def create(name: str, workspace_id: Optional[str], description: Optional[str], slug: Optional[str]):
    """Create a new project"""
    try:
        config = load_config()
        if not workspace_id:
            workspace_id = config.get('default_workspace_id')
            if not workspace_id:
                click.echo("❌ No workspace ID specified and no default workspace set")
                return

        data = {
            'name': name,
            'workspace_id': int(workspace_id)
        }

        if description:
            data['description'] = description
        if slug:
            data['slug'] = slug

        response = make_request('POST', '/api/v1/projects/', data=data)

        click.echo("✅ Project created successfully!")
        click.echo(f"📁 Name: {response.get('name', name)}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")
        click.echo(f"🏢 Workspace: {response.get('workspace_id', workspace_id)}")

        if response.get('description'):
            click.echo(f"📝 Description: {response['description']}")

    except Exception as e:
        click.echo(f"❌ Failed to create project: {e}")


@project.command()
@click.argument('project_id', required=False)
def show(project_id: Optional[str]):
    """Show project details"""
    try:
        if not project_id:
            click.echo("❌ Project ID is required")
            return

        data = make_request('GET', f"/api/v1/projects/{project_id}")

        click.echo(f"📁 Project Details:")
        click.echo(f"  📛 Name: {data.get('name', 'Unknown')}")
        click.echo(f"  🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"  🏢 Workspace: {data.get('workspace_id', 'Unknown')}")
        click.echo(f"  📊 Status: {data.get('status', 'Unknown')}")

        if data.get('description'):
            click.echo(f"  📝 Description: {data['description']}")
        if data.get('slug'):
            click.echo(f"  🏷️  Slug: {data['slug']}")

        if data.get('created_at'):
            click.echo(f"  📅 Created: {data['created_at']}")
        if data.get('updated_at'):
            click.echo(f"  📅 Updated: {data['updated_at']}")

    except Exception as e:
        click.echo(f"❌ Failed to show project: {e}")


@project.command()
@click.argument('project_id', required=False)
@click.option('--name', '-n', help='New project name')
@click.option('--description', '-d', help='New project description')
@click.option('--slug', '-s', help='New project slug')
def update(project_id: Optional[str], name: Optional[str], description: Optional[str], slug: Optional[str]):
    """Update project details"""
    try:
        if not project_id:
            click.echo("❌ Project ID is required")
            return

        if not any([name, description, slug]):
            click.echo("❌ At least one field to update must be specified")
            return

        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if slug:
            data['slug'] = slug

        response = make_request('PUT', f"/api/v1/projects/{project_id}", data=data)

        click.echo("✅ Project updated successfully!")
        click.echo(f"📁 Name: {response.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Failed to update project: {e}")


@project.command()
@click.argument('project_id', required=False)
@click.confirmation_option(prompt='Are you sure you want to delete this project?')
def delete(project_id: Optional[str]):
    """Delete a project"""
    try:
        if not project_id:
            click.echo("❌ Project ID is required")
            return

        make_request('DELETE', f"/api/v1/projects/{project_id}")
        click.echo("✅ Project deleted successfully!")

    except Exception as e:
        click.echo(f"❌ Failed to delete project: {e}")


# Application Commands
@cli.group()
def application():
    """Application management commands"""
    pass


@application.command()
@click.option('--project-id', '-p', help='Project ID (uses default if not specified)')
@click.option('--type', '-t', help='Filter by application type')
@click.option('--status', '-s', help='Filter by application status')
def list(project_id: Optional[str], type: Optional[str], status: Optional[str]):
    """List applications"""
    try:
        config = load_config()
        if not project_id:
            project_id = config.get('default_project_id')
            if not project_id:
                click.echo("❌ No project ID specified and no default project set")
                return

        params = {}
        if type:
            params['type'] = type
        if status:
            params['status'] = status

        data = make_request('GET', '/api/v1/applications/', params=params)
        applications = data.get('applications', data.get('items', []))

        if not applications:
            click.echo("No applications found")
            return

        click.echo(f"📋 Applications ({len(applications)}):")
        for app in applications:
            click.echo(f"  📱 {app.get('name', 'Unknown')} (ID: {app.get('id', 'Unknown')})")
            click.echo(f"     🔧 Type: {app.get('application_type', app.get('type', 'Unknown'))}")
            click.echo(f"     📊 Status: {app.get('status', 'Unknown')}")
            click.echo(f"     🛡️  Security: {app.get('security_level', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Failed to list applications: {e}")


@application.command()
@click.option('--name', '-n', prompt=True, help='Application name')
@click.option('--project-id', '-p', help='Project ID (uses default if not specified)')
@click.option('--type', '-t', type=click.Choice(['web_application', 'api_service', 'microservice', 'database', 'container', 'serverless', 'desktop', 'mobile', 'iot', 'custom']), default='web_application', help='Application type')
@click.option('--description', '-d', help='Application description')
@click.option('--security-level', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']), default='medium', help='Security level')
def create(name: str, project_id: Optional[str], type: str, description: Optional[str], security_level: str):
    """Create a new application"""
    try:
        config = load_config()
        if not project_id:
            project_id = config.get('default_project_id')
            if not project_id:
                click.echo("❌ No project ID specified and no default project set")
                return

        data = {
            'name': name,
            'application_type': type.upper(),
            'security_level': security_level.upper(),
            'security_scan_enabled': True,
            'security_scan_frequency': 'weekly',
            'network_isolation_required': False,
            'network_policy_enforced': True,
            'compliance_scan_enabled': True,
            'compliance_scan_frequency': 'monthly',
            'cross_boundary_enabled': False,
            'service_discovery_enabled': True
        }

        if description:
            data['description'] = description

        response = make_request('POST', f"/api/v1/applications/?project_id={project_id}", data=data)

        click.echo("✅ Application created successfully!")
        click.echo(f"📛 Name: {response.get('name', name)}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")
        click.echo(f"📁 Project: {response.get('project_id', project_id)}")
        click.echo(f"🔧 Type: {response.get('application_type', response.get('type', type))}")
        click.echo(f"🛡️  Security Level: {response.get('security_level', security_level)}")
        click.echo(f"📊 Status: {response.get('status', 'draft')}")

        if response.get('description'):
            click.echo(f"📝 Description: {response['description']}")

    except Exception as e:
        click.echo(f"❌ Failed to create application: {e}")


@application.command()
@click.argument('application_id', required=False)
def show(application_id: Optional[str]):
    """Show application details"""
    try:
        if not application_id:
            click.echo("❌ Application ID is required")
            return

        data = make_request('GET', f"/api/v1/applications/{application_id}")

        click.echo(f"📱 Application Details:")
        click.echo(f"  📛 Name: {data.get('name', 'Unknown')}")
        click.echo(f"  🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"  📁 Project: {data.get('project_id', 'Unknown')}")
        click.echo(f"  🔧 Type: {data.get('application_type', data.get('type', 'Unknown'))}")
        click.echo(f"  📊 Status: {data.get('status', 'Unknown')}")
        click.echo(f"  🛡️  Security Level: {data.get('security_level', 'Unknown')}")
        click.echo(f"  🌐 Network Tier: {data.get('network_tier', 'Unknown')}")

        if data.get('description'):
            click.echo(f"  📝 Description: {data['description']}")

        if data.get('created_at'):
            click.echo(f"  📅 Created: {data['created_at']}")
        if data.get('updated_at'):
            click.echo(f"  📅 Updated: {data['updated_at']}")

    except Exception as e:
        click.echo(f"❌ Failed to show application: {e}")


@application.command()
@click.argument('application_id', required=False)
@click.option('--name', '-n', help='New application name')
@click.option('--description', '-d', help='New application description')
@click.option('--type', '-t', type=click.Choice(['web_application', 'api_service', 'microservice', 'database', 'container', 'serverless', 'desktop', 'mobile', 'iot', 'custom']), help='New application type')
@click.option('--security-level', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']), help='New security level')
def update(application_id: Optional[str], name: Optional[str], description: Optional[str], type: Optional[str], security_level: Optional[str]):
    """Update application details"""
    try:
        if not application_id:
            click.echo("❌ Application ID is required")
            return

        if not any([name, description, type, security_level]):
            click.echo("❌ At least one field to update must be specified")
            return

        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if type:
            data['type'] = type
        if security_level:
            data['security_level'] = security_level

        response = make_request('PUT', f"/api/v1/applications/{application_id}", data=data)

        click.echo("✅ Application updated successfully!")
        click.echo(f"📛 Name: {response.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Failed to update application: {e}")


@application.command()
@click.argument('application_id', required=False)
@click.confirmation_option(prompt='Are you sure you want to delete this application?')
def delete(application_id: Optional[str]):
    """Delete an application"""
    try:
        if not application_id:
            click.echo("❌ Application ID is required")
            return

        make_request('DELETE', f"/api/v1/applications/{application_id}")
        click.echo("✅ Application deleted successfully!")

    except Exception as e:
        click.echo(f"❌ Failed to delete application: {e}")


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

        data = make_request('GET', '/api/v1/pipelines/')
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
@click.option('--project-id', '-p', help='Project ID (uses default if not specified)')
@click.option('--description', '-d', help='Pipeline description')
@click.option('--type', '-t', type=click.Choice(['security_scan', 'compliance_check', 'deployment', 'testing', 'custom']), default='deployment', help='Pipeline type')
def create(name: str, project_id: Optional[str], description: Optional[str], type: str):
    """Create a new pipeline"""
    try:
        config = load_config()
        if not project_id:
            project_id = config.get('default_project_id')
            if not project_id:
                click.echo("❌ No project ID specified and no default project set")
                return

        data = {
            'name': name,
            'project_id': int(project_id),
            'pipeline_type': type,
            'configuration': {
                'steps': [
                    {
                        'name': 'default_step',
                        'type': 'script',
                        'script': 'echo "Pipeline created successfully"'
                    }
                ]
            }
        }

        if description:
            data['description'] = description

        response = make_request('POST', '/api/v1/pipelines/', data=data)

        click.echo("✅ Pipeline created successfully!")
        click.echo(f"🔄 Name: {response.get('name', name)}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")
        click.echo(f"📁 Project: {response.get('project_id', project_id)}")
        click.echo(f"🔧 Type: {response.get('pipeline_type', response.get('type', type))}")

        if response.get('description'):
            click.echo(f"📝 Description: {response['description']}")

    except Exception as e:
        click.echo(f"❌ Failed to create pipeline: {e}")


@pipeline.command()
@click.argument('pipeline_id', required=False)
def show(pipeline_id: Optional[str]):
    """Show pipeline details"""
    try:
        if not pipeline_id:
            click.echo("❌ Pipeline ID is required")
            return

        data = make_request('GET', f"/api/v1/pipelines/{pipeline_id}")

        click.echo(f"🔄 Pipeline Details:")
        click.echo(f"  📛 Name: {data.get('name', 'Unknown')}")
        click.echo(f"  🆔 ID: {data.get('id', 'Unknown')}")
        click.echo(f"  📁 Project: {data.get('project_id', 'Unknown')}")
        click.echo(f"  🔧 Type: {data.get('pipeline_type', data.get('type', 'Unknown'))}")
        is_active = data.get('is_active', 'Unknown')
        status_display = "Active" if is_active is True else "Inactive" if is_active is False else "Unknown"
        click.echo(f"  📊 Status: {status_display}")

        if data.get('description'):
            click.echo(f"  📝 Description: {data['description']}")

        if data.get('created_at'):
            click.echo(f"  📅 Created: {data['created_at']}")
        if data.get('updated_at'):
            click.echo(f"  📅 Updated: {data['updated_at']}")

    except Exception as e:
        click.echo(f"❌ Failed to show pipeline: {e}")


@pipeline.command()
@click.argument('pipeline_id', required=False)
@click.option('--name', '-n', help='New pipeline name')
@click.option('--description', '-d', help='New pipeline description')
@click.option('--type', '-t', type=click.Choice(['security_scan', 'compliance_check', 'deployment', 'testing', 'custom']), help='New pipeline type')
def update(pipeline_id: Optional[str], name: Optional[str], description: Optional[str], type: Optional[str]):
    """Update pipeline details"""
    try:
        if not pipeline_id:
            click.echo("❌ Pipeline ID is required")
            return

        if not any([name, description, type]):
            click.echo("❌ At least one field to update must be specified")
            return

        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if type:
            data['type'] = type

        response = make_request('PUT', f"/api/v1/pipelines/{pipeline_id}", data=data)

        click.echo("✅ Pipeline updated successfully!")
        click.echo(f"🔄 Name: {response.get('name', 'Unknown')}")
        click.echo(f"🆔 ID: {response.get('id', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Failed to update pipeline: {e}")


@pipeline.command()
@click.argument('pipeline_id', required=False)
@click.confirmation_option(prompt='Are you sure you want to delete this pipeline?')
def delete(pipeline_id: Optional[str]):
    """Delete a pipeline"""
    try:
        if not pipeline_id:
            click.echo("❌ Pipeline ID is required")
            return

        make_request('DELETE', f"/api/v1/pipelines/{pipeline_id}")
        click.echo("✅ Pipeline deleted successfully!")

    except Exception as e:
        click.echo(f"❌ Failed to delete pipeline: {e}")


@pipeline.command()
@click.argument('pipeline_id', required=False)
def execute(pipeline_id: Optional[str]):
    """Execute a pipeline"""
    try:
        if not pipeline_id:
            click.echo("❌ Pipeline ID is required")
            return

        response = make_request('POST', f"/api/v1/pipelines/{pipeline_id}/execute")

        click.echo("✅ Pipeline execution started!")
        click.echo(f"🔄 Execution ID: {response.get('id', 'Unknown')}")
        click.echo(f"📊 Status: {response.get('status', 'Unknown')}")
        click.echo(f"📅 Started: {response.get('started_at', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Failed to execute pipeline: {e}")


@pipeline.command()
@click.argument('pipeline_id', required=False)
def executions(pipeline_id: Optional[str]):
    """List pipeline executions"""
    try:
        if not pipeline_id:
            click.echo("❌ Pipeline ID is required")
            return

        data = make_request('GET', f"/api/v1/pipelines/{pipeline_id}/executions")

        if not data:
            click.echo("No executions found")
            return

        click.echo(f"📋 Pipeline Executions ({len(data)}):")
        for execution in data:
            click.echo(f"  🔄 ID: {execution.get('id', 'Unknown')}")
            click.echo(f"     📊 Status: {execution.get('status', 'Unknown')}")
            click.echo(f"     📅 Started: {execution.get('started_at', 'Unknown')}")
            if execution.get('completed_at'):
                click.echo(f"     📅 Completed: {execution['completed_at']}")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to list pipeline executions: {e}")


@pipeline.command()
@click.argument('pipeline_id', required=False)
@click.argument('execution_id', required=False)
def cancel(pipeline_id: Optional[str], execution_id: Optional[str]):
    """Cancel a pipeline execution"""
    try:
        if not pipeline_id or not execution_id:
            click.echo("❌ Pipeline ID and Execution ID are required")
            return

        make_request('PATCH', f"/api/v1/pipelines/{pipeline_id}/executions/{execution_id}/cancel")
        click.echo("✅ Pipeline execution cancelled successfully!")

    except Exception as e:
        click.echo(f"❌ Failed to cancel pipeline execution: {e}")


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
@click.option('--account-id', '-a', help='Default account ID')
@click.option('--workspace-id', '-w', help='Default workspace ID')
@click.option('--project-id', '-p', help='Default project ID')
def set(account_id: Optional[str], workspace_id: Optional[str], project_id: Optional[str]):
    """Set configuration values"""
    config_data = load_config() or {}

    if account_id:
        config_data['default_account_id'] = account_id
    if workspace_id:
        config_data['default_workspace_id'] = workspace_id
    if project_id:
        config_data['default_project_id'] = project_id

    save_config(config_data)
    click.echo("✅ Configuration updated")


@config.command()
def reset():
    """Reset configuration to defaults"""
    if click.confirm("Are you sure you want to reset the configuration?"):
        config_file = Path.home() / ".securepipe" / "config.json"
        if config_file.exists():
            config_file.unlink()
        click.echo("✅ Configuration reset")
