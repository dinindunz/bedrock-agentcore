import os
import pathlib
import json
import subprocess
import logging
from typing import Dict, Any
from strands import Agent, tool
from strands_tools import use_aws, calculator, current_time
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

custom_env = os.environ.copy()
custom_env["UV_CACHE_DIR"] = "/tmp/uv_cache"
custom_env["XDG_CACHE_HOME"] = "/tmp"

WELCOME_MESSAGE = """
Welcome to the Cloud Agent Assistant! How can I help you today?
"""

STRANDS_PROMPT = pathlib.Path("prompts/strands_agent.md").read_text()


@tool
def claude_code(prompt: str) -> str:
    """Generate code using Claude Code CLI"""
    try:
        result = subprocess.run(['claude', prompt], capture_output=True, text=True, timeout=300)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


# Create an AgentCore app
app = BedrockAgentCoreApp()

agent = Agent(
    system_prompt=STRANDS_PROMPT,
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[
        calculator,
        current_time,
        use_aws,
        claude_code,
    ],
)


# Specify the entry point function invoking the agent
@app.entrypoint
def invoke(payload):
    """Handler for agent invocation"""
    user_message = payload.get(
        "prompt",
        "No prompt found in input, please guide customer to create a json payload with prompt key",
    )
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
