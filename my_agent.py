import os
import pathlib
from strands import Agent, tool
from strands_tools import use_aws, calculator, current_time
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp

custom_env = os.environ.copy()
custom_env["UV_CACHE_DIR"] = "/tmp/uv_cache"
custom_env["XDG_CACHE_HOME"] = "/tmp"

WELCOME_MESSAGE = """
Welcome to the Customer Support Assistant! How can I help you today?
"""

SYSTEM_PROMPT = pathlib.Path("system_prompt.md").read_text()


def parseClaudeCommand(event):
    """Parse Claude Code command from Bedrock Agent event"""
    parameters = event.get('parameters', {})
    request_body = event.get('requestBody', {})
    
    # Extract command from parameters or request body
    command = 'claude --help'  # default
    
    if parameters:
        # Handle different parameter structures
        if 'command' in parameters:
            command = parameters['command']
        elif 'action' in parameters:
            command = f"claude {parameters['action']}"
            if 'options' in parameters:
                command += f" {parameters['options']}"
    
    return command


@tool
def claude_code(prompt: str):
    """Execute Claude code command"""
    try:
        import json
        event = json.loads(prompt)
        command = parseClaudeCommand(event)
        return {"command": command, "status": "parsed"}
    except (json.JSONDecodeError, TypeError):
        return {"prompt": prompt, "status": "direct"}


# Create an AgentCore app
app = BedrockAgentCoreApp()

mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="mcp-proxy",
            args=[f"http://CloudE-McpPr-ZTStjfTRWd3g-686078839.ap-southeast-2.elb.amazonaws.com/servers/github/sse"],
            env=custom_env,
        )
    )
)
mcp_client.start()
tools = mcp_client.list_tools_sync()

agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[
        calculator,
        current_time,
        claude_code,
        mcp_client,
        use_aws,
        tools,
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
