# AWS Chatbot

An AI-powered chatbot for managing AWS services using natural language. Built with the Model Context Protocol (MCP) framework and AWS MCP servers.

## Features

- 🤖 **Natural Language Interface**: Interact with AWS services using plain English
- 🔧 **Comprehensive AWS Support**: Access all AWS CLI commands through the AWS MCP server
- 🌐 **Web Interface**: Modern, responsive web UI for easy interaction
- 💻 **CLI Interface**: Command-line interface for terminal users
- 🔒 **Security First**: Built-in safety controls and read-only mode
- ⚡ **Real-time**: Fast responses with streaming support
- 🎯 **Smart Suggestions**: AI-powered command suggestions and help

## Prerequisites

- Python 3.11 or newer
- AWS CLI configured with appropriate credentials
- An AWS account with proper IAM permissions
- Access to a compatible LLM (Claude, GPT-4, etc.)

## Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd aws-chatbot
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Configure MCP settings:**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml if needed
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# LLM Configuration
LLM_MODEL=US Claude 3.7 Sonnet By Anthropic (Served via LiteLLM)
LLM_BASE_URL=http://your-llm-server:7177
LLM_API_KEY=your-api-key

# AWS Configuration
AWS_REGION=us-east-1
AWS_API_MCP_PROFILE_NAME=default

# Optional AWS MCP Server Configuration
READ_OPERATIONS_ONLY=false
REQUIRE_MUTATION_CONSENT=false

# Web Server Configuration
HOST=0.0.0.0
PORT=50333
```

### AWS Credentials

Ensure your AWS credentials are properly configured. You can use:

- AWS CLI: `aws configure`
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- IAM roles (recommended for EC2 instances)
- AWS profiles

## Usage

### Web Interface

Start the web server:

```bash
uv run scripts/run_web.py
```

Then open your browser to `http://localhost:50333`

### CLI Interface

Start the command-line interface:

```bash
uv run scripts/run_cli.py
```

### Example Queries

Try these example queries:

- "List all EC2 instances"
- "Show me S3 buckets in us-west-2"
- "What RDS databases do I have?"
- "Create a security group for web servers"
- "Show VPC information"
- "List Lambda functions"

### Running Examples

The `examples/` directory contains demonstration scripts:

```bash
# Basic demo with sample queries
uv run examples/demo.py

# Compare LLM-driven vs direct agent approaches
uv run examples/demo_llm_vs_direct.py

# Demonstrate memory features
uv run examples/demo_memory_feature.py
```

### Testing Setup

Verify your installation and configuration:

```bash
uv run tests/test_setup.py
```

## Security Considerations

### Read-Only Mode

For safer exploration, enable read-only mode:

```env
READ_OPERATIONS_ONLY=true
```

This restricts the agent to only execute read operations.

### Mutation Consent

Require explicit consent for write operations:

```env
REQUIRE_MUTATION_CONSENT=true
```

### IAM Permissions

Use the principle of least privilege:

- **Read-only access**: Use `ReadOnlyAccess` policy
- **Full access**: Use `AdministratorAccess` policy (be careful!)
- **Custom policies**: Create specific policies for your use case

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web/CLI UI    │    │   AWS Agent     │    │   AWS MCP       │
│                 │◄──►│                 │◄──►│   Server        │
│  - FastAPI      │    │  - MCP Agent    │    │                 │
│  - HTML/JS      │    │  - Custom LLM   │    │  - AWS CLI      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │                 │
                       │  - Claude 3.7   │
                       │  - via LiteLLM  │
                       └─────────────────┘
```

## Development

### Project Structure

```
aws-chatbot/
├── src/aws_chatbot/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── llm_adapter.py     # Custom LLM adapter
│   ├── aws_agent.py       # Main AWS agent logic
│   ├── web_app.py         # FastAPI web application
│   └── main.py            # CLI entry point
├── scripts/
│   ├── run_web.py         # Web server launcher
│   └── run_cli.py         # CLI launcher
├── examples/
│   ├── demo.py            # Basic demo
│   ├── demo_llm_vs_direct.py  # LLM vs direct comparison
│   └── demo_memory_feature.py # Memory feature demo
├── tests/
│   └── test_setup.py      # Setup and import tests
├── templates/
│   └── index.html         # Web UI template
├── static/
│   ├── style.css          # Web UI styles
│   └── script.js          # Web UI JavaScript
├── .env.example           # Environment variables template
├── config.yaml.example    # MCP configuration template
└── README.md
```

### Running in Development

1. **Install development dependencies:**
   ```bash
   uv add --dev pytest black isort mypy
   ```

2. **Run tests:**
   ```bash
   uv run pytest
   ```

3. **Format code:**
   ```bash
   uv run black src/
   uv run isort src/
   ```

## Troubleshooting

### Common Issues

1. **Agent not initializing:**
   - Check AWS credentials
   - Verify LLM service is accessible
   - Check network connectivity

2. **MCP server timeout:**
   - Increase timeout in configuration
   - Check system performance
   - Verify AWS CLI installation

3. **Permission errors:**
   - Check IAM permissions
   - Verify AWS profile configuration
   - Review security policies

### Logs

Check logs in the `logs/` directory for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool provides programmatic access to AWS services. Always:

- Review commands before execution
- Use appropriate IAM permissions
- Test in non-production environments first
- Monitor AWS costs and usage
- Follow your organization's security policies

The authors are not responsible for any AWS charges or security issues that may arise from using this tool.