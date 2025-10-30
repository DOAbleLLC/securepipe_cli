# SecurePipe CLI Test Suite

This directory contains comprehensive unit tests for all SecurePipe CLI commands.

## Test Structure

```
tests/
├── README.md                    # This file
├── pytest.ini                  # Pytest configuration
├── conftest.py                  # Shared test fixtures
├── test_runner.py              # Test runner script
├── test_cli_commands.py        # Main CLI tests
├── test_cli_auth.py            # Authentication command tests
├── test_cli_pipeline.py        # Pipeline command tests
├── test_cli_workspace.py       # Workspace command tests
├── test_cli_project.py         # Project command tests
└── test_cli_init_utils.py      # Init and utils command tests
```

## Test Coverage

### Authentication Commands (`test_cli_auth.py`)
- ✅ Login with email/password
- ✅ Login with API token
- ✅ Login failure handling
- ✅ Logout functionality
- ✅ Whoami command (authenticated/unauthenticated)
- ✅ Status command
- ✅ Token refresh
- ✅ Interactive login

### Pipeline Commands (`test_cli_pipeline.py`)
- ✅ Create pipeline from YAML file
- ✅ List pipelines
- ✅ Describe pipeline
- ✅ Run pipeline
- ✅ Pipeline logs
- ✅ Delete pipeline
- ✅ Export pipeline
- ✅ Offline create (basic, terraform templates)
- ✅ Offline validate
- ✅ Offline edit
- ✅ Offline sync
- ✅ Offline diff
- ✅ Offline status

### Workspace Commands (`test_cli_workspace.py`)
- ✅ Create workspace
- ✅ List workspaces
- ✅ Describe workspace (Fixed: Logic error in show endpoint)
- ✅ Update workspace
- ✅ Delete workspace
- ✅ Add member to workspace
- ✅ List workspace members
- ✅ Select workspace as default

### Project Commands (`test_cli_project.py`)
- ✅ Create project
- ✅ List projects (Fixed: Parameter passing and response model issues)
- ✅ Describe project (Fixed: Account ID field missing)
- ✅ Update project (Fixed: Account ID field missing)
- ✅ Delete project
- ✅ Add member to project
- ✅ Remove member from project
- ✅ Select project as default (Fixed: Account ID field missing)

### Init Commands (`test_cli_init_utils.py`)
- ✅ Initialize basic project
- ✅ Initialize terraform project
- ✅ Initialize docker project
- ✅ Initialize kubernetes project
- ✅ Force overwrite existing directory
- ✅ Error handling for non-empty directories

### Utils Commands (`test_cli_init_utils.py`)
- ✅ Validate configuration
- ✅ Clear cache
- ✅ Show configuration
- ✅ Set context (account/workspace/project)
- ✅ Show context
- ✅ Version command
- ✅ Health check
- ✅ Export configuration
- ✅ Import configuration

### SAM Monitoring Commands (`test_cli_sam_monitoring.py`)
- ✅ System health checks
- ✅ Performance metrics retrieval
- ✅ Usage metrics collection
- ✅ Security alerts listing
- ✅ Custom metrics recording
- ✅ Metrics aggregation
- ✅ Audit log viewing and export
- ✅ Alert rule configuration
- ✅ Rate limit configuration
- ✅ Session management configuration
- ✅ Dashboard creation and management
- ✅ Configuration validation
- ✅ Error handling for invalid inputs
- ✅ Output format validation (table, json, yaml)

### Main CLI (`test_cli_commands.py`)
- ✅ CLI version
- ✅ CLI help
- ✅ Verbose mode
- ✅ Error handling
- ✅ Configuration management
- ✅ Context management

## Running Tests

### Using Make (Recommended)
```bash
# Run all tests
make test-all

# Run specific test suites
make test-auth
make test-pipeline
make test-workspace
make test-project
make test-init-utils

# Run with coverage
make test-coverage

# Clean test cache
make clean-cache
```

### Using pytest directly
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_cli_pipeline.py -v

# Run specific test
python -m pytest tests/test_cli_pipeline.py::TestPipelineCommands::test_pipeline_offline_create_basic_template -v

# Run with coverage
python -m pytest tests/ --cov=cli --cov-report=html
```

### Using the test runner
```bash
python tests/test_runner.py
```

## Test Dependencies

The tests use the following dependencies:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `click.testing` - CLI testing utilities

Install test dependencies:
```bash
pip install pytest pytest-cov pytest-mock
# or
make install-test-deps
```

## Test Patterns

### Mocking API Calls
```python
def test_api_call(self, runner, mock_client):
    mock_client.get.return_value = {"data": "test"}
    
    with patch('cli.commands.module.get_client') as mock_get_client:
        mock_get_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(command_group, ['subcommand'])
        
        assert result.exit_code == 0
        mock_client.get.assert_called_once()
```

### Testing File Operations
```python
def test_file_operation(self, runner, temp_config_dir):
    test_file = temp_config_dir / "test.yaml"
    
    result = runner.invoke(command_group, ['--file', str(test_file)])
    
    assert result.exit_code == 0
    assert test_file.exists()
```

### Testing Configuration
```python
def test_config_operation(self, runner, mock_config):
    with patch('cli.commands.module.get_config_manager') as mock_get_config:
        mock_get_config.return_value = mock_config
        
        result = runner.invoke(command_group, ['config-command'])
        
        assert result.exit_code == 0
```

## Adding New Tests

When adding new CLI commands, follow this pattern:

1. Create test class inheriting from `TestCLIBase`
2. Use fixtures for common setup (runner, temp directories, mock clients)
3. Test both success and failure scenarios
4. Mock external API calls
5. Verify command output and side effects
6. Add test to appropriate test file or create new file if needed

Example:
```python
class TestNewCommands(TestCLIBase):
    def test_new_command_success(self, runner, mock_client):
        """Test successful execution of new command"""
        mock_client.post.return_value = {"status": "success"}
        
        with patch('cli.commands.new.get_client') as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_client
            
            result = runner.invoke(new_group, ['new-command', '--param', 'value'])
            
            assert result.exit_code == 0
            assert "success" in result.output
    
    def test_new_command_failure(self, runner, mock_client):
        """Test failure handling of new command"""
        mock_client.post.side_effect = APIError(400, "Bad request")
        
        with patch('cli.commands.new.get_client') as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_client
            
            result = runner.invoke(new_group, ['new-command', '--param', 'value'])
            
            assert result.exit_code != 0
            assert "Bad request" in result.output
```

## Continuous Integration

These tests are designed to run in CI/CD environments. They:
- Use temporary directories for isolation
- Mock external dependencies
- Don't require network access
- Clean up after themselves
- Provide clear failure messages

## Coverage Goals

- **Command Coverage**: All CLI commands should have tests
- **Path Coverage**: Test both success and failure paths
- **Edge Cases**: Test invalid inputs, missing files, network errors
- **Integration**: Test command interactions and workflows

Current coverage target: **90%** of CLI code
