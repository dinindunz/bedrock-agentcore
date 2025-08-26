# Bedrock AgentCore - Claude Code Integration Approaches

This repository demonstrates three different approaches to integrating Claude Code with AWS Bedrock AgentCore for automated incident response. The project was created to solve the problem of applying surgical code fixes rather than broad improvements when responding to CloudWatch log errors.

## Problem Statement

In previous implementations using AWS Strands, agents would make drastic changes when only simple fixes were needed (e.g., adding an IAM permission). Despite system prompts emphasizing "apply ONLY the specific fix needed, no broader improvements," Strands consistently failed to apply surgical code fixes. This repository tests different Claude Code integration approaches to achieve precise, targeted fixes.

## Project Structure

```
bedrock-agentcore/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .bedrock_agentcore.yaml             # AgentCore configuration
├── Dockerfile                          # Container configuration
├── LICENSE.md                          # License information
│
├── Agent Implementations/
│   ├── claude_cli_agent.py             # Direct Claude Code CLI integration
│   ├── claude_sdk_agent.py             # Claude Code SDK integration
│   ├── claude_strands_multi_agent.py   # Strands orchestrator with Claude Code SDK
│   └── my_agent.py                     # Current chosen implementation (Claude Code SDK)
│
├── prompts/
│   └── strands_agent.md                # System prompt for Strands agent
│
└── ui/                                 # Web interface (if applicable)
    ├── app.js
    └── config.js
```

## Three Integration Approaches

### 1. Claude Code CLI Agent (`claude_cli_agent.py`)

**Direct CLI Integration**
- Calls `claude` CLI command directly using subprocess
- Simplest implementation with minimal dependencies
- Uses `--print` flag for non-interactive mode
- Configured for AWS Bedrock with specific model and region

**Pros:**
- Lightweight and straightforward
- Direct access to Claude Code CLI features
- Easy to debug and troubleshoot

**Cons:**
- Requires Claude Code CLI to be installed and configured
- Limited error handling and response streaming
- Less control over conversation flow

### 2. Claude Code SDK Agent (`claude_sdk_agent.py`)

**SDK Integration with Enhanced Features**
- Uses `claude-code-sdk` for programmatic access
- Supports async operations and response streaming
- Configurable tools and system prompts
- Better error handling and logging

**Pros:**
- More robust and feature-rich
- Better integration with Python ecosystem
- Streaming responses and async support
- Configurable tool access

**Cons:**
- Additional SDK dependency
- More complex setup and configuration

### 3. Claude Code + AWS Strands Multi-Agent (`claude_strands_multi_agent.py`)

**Orchestrator Pattern**
- Uses Strands framework as the main orchestrator
- Claude Code CLI wrapped as a tool within Strands
- Combines Strands' agent capabilities with Claude Code's code generation
- System prompt loaded from external file

**Pros:**
- Leverages Strands' orchestration capabilities
- Modular tool-based architecture
- External prompt management
- Can combine multiple tools and agents

**Cons:**
- Most complex implementation
- Potential for the same "broad changes" issue that prompted this research
- Additional framework dependency

## Current Implementation

The `my_agent.py` file currently uses the **Claude Code SDK approach** as it has proven most effective for surgical code fixes. This implementation includes:

- MCP (Model Context Protocol) server integration for GitHub operations
- Enhanced tool configuration including Bash, Read, Edit, and WebSearch
- Proper async handling and error management
- Integration with external MCP proxy for GitHub operations

## Key Features

### Surgical Code Fixes
All implementations are designed to apply minimal, targeted fixes rather than broad improvements:
- Focus on specific error resolution
- Preserve existing code patterns and architecture
- Avoid unnecessary refactoring or "improvements"
- Maintain original variable names and structure

### AWS Integration
- Configured for AWS Bedrock in `ap-southeast-2` region
- Uses `apac.anthropic.claude-sonnet-4-20250514-v1:0` model
- Environment variable configuration for AWS credentials
- CloudWatch log integration for automated incident response

### Automated Workflow
The system is designed for automated incident response:
1. CloudWatch error detection
2. Automated analysis and root cause identification
3. Surgical code fix generation
4. GitHub PR creation with minimal scope changes
5. Jira ticket creation and tracking

## Setup and Installation

### Prerequisites
- Python 3.8+
- AWS CLI configured with appropriate permissions
- Claude Code CLI (for CLI agent approach)
- Claude Code SDK (for SDK approach)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dinindunz/bedrock-agentcore.git
cd bedrock-agentcore
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
export AWS_REGION=ap-southeast-2
export CLAUDE_CODE_USE_BEDROCK=1
export ANTHROPIC_MODEL=apac.anthropic.claude-sonnet-4-20250514-v1:0
```

4. Configure AgentCore with the chosen implementation:
```bash
agentcore configure --entrypoint my_agent.py
```

### Running the Agent

Choose your preferred implementation and run:

```bash
# For Claude Code CLI approach
python claude_cli_agent.py

# For Claude Code SDK approach (recommended)
python claude_sdk_agent.py

# For Strands multi-agent approach
python claude_strands_multi_agent.py

# Current implementation
python my_agent.py
```

## Usage

Send requests to the agent with a JSON payload:

```json
{
  "prompt": "A Lambda function in the notification service is failing with SNS:Publish authorization error. The assumed role 
NotificationServiceStack-NotificationServiceService-naMxIgnRPzFQ/notification-service lacks permission to publish to SNS topic arn:aws:sns:ap-southeast-2:1234567890:user-notifications. Analyze 
the GitHub repository dinindunz/notification-service. Analyze the code and apply ONLY the specific fix needed, no broader improvements. Remember: Your role is automated incident response with 
minimal, targeted fixes only. No improvements beyond fixing the specific error then raise a PR."
}
```

The agent will respond with:
```json
{
  "result": "[Claude Code's analysis and suggested fix]"
}
```

## Testing Results

Based on testing, the **Claude Code SDK approach** (`claude_sdk_agent.py`) has proven most effective for:
- Applying surgical fixes without unnecessary changes
- Maintaining code structure and patterns
- Providing precise error resolution
- Avoiding the "broad improvements" problem seen with Strands

## Contributing

When contributing to this project:
1. Test changes against all three implementation approaches
2. Ensure surgical fix capabilities are maintained
3. Update documentation for any new features
4. Follow the existing code patterns and structure

## License

See `LICENSE.md` for license information.

## Related Work

This project builds upon previous work with AWS Strands agents for CloudWatch log monitoring and automated incident response. The key innovation is achieving surgical code fixes through different Claude Code integration patterns.
