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
Welcome to the Customer Support Assistant! How can I help you today?
"""

SYSTEM_PROMPT = pathlib.Path("system_prompt.md").read_text()


@tool
def claude_code(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Bedrock Agent handler for Claude Code execution
    """
    logger.info(f'Received event: {json.dumps(event, indent=2)}')
    
    try:
        # Parse the Claude Code command from the request
        claude_command = parse_claude_command(event)
        
        # Execute Claude Code
        result = execute_claude_code(claude_command)
        
        # Return response in Bedrock Agent format
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup"),
                "apiPath": event.get("apiPath"),
                "httpMethod": event.get("httpMethod"),
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({
                            "success": True,
                            "output": result["output"],
                            "error": result["error"],
                            "exitCode": result["exitCode"]
                        })
                    }
                }
            }
        }
        
    except Exception as error:
        logger.error(f'Error in agent handler: {str(error)}')
        
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup"),
                "apiPath": event.get("apiPath"),
                "httpMethod": event.get("httpMethod"),
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({
                            "success": False,
                            "error": str(error)
                        })
                    }
                }
            }
        }


def parse_claude_command(event: Dict[str, Any]) -> str:
    """
    Parse Claude Code command from Bedrock Agent event
    """
    parameters = event.get("parameters", {})
    request_body = event.get("requestBody", {})
    
    # Extract command from parameters or request body
    command = "claude --help"  # default
    
    if parameters:
        # Handle different parameter structures
        if "command" in parameters:
            command = parameters["command"]
        elif "action" in parameters:
            command = f"claude {parameters['action']}"
            if "options" in parameters:
                command += f" {parameters['options']}"
    
    if request_body and "content" in request_body:
        try:
            body = json.loads(request_body["content"])
            if "command" in body:
                command = body["command"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f'Could not parse request body: {str(e)}')
    
    logger.info(f'Parsed Claude command: {command}')
    return command


def execute_claude_code(command: str) -> Dict[str, Any]:
    """
    Execute Claude Code command
    """
    # Split command and remove 'claude' from the beginning
    args = command.split()[1:] if command.startswith('claude ') else command.split()
    
    # Set up environment variables
    env = os.environ.copy()
    env.update({
        'CLAUDE_CODE_USE_BEDROCK': '1',
        'AWS_REGION': env.get('AWS_REGION', 'us-east-1'),
        'ANTHROPIC_MODEL': env.get('ANTHROPIC_MODEL', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
    })
    
    try:
        # Execute the command with timeout
        result = subprocess.run(
            ['claude'] + args,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minutes timeout
        )
        
        logger.info(f'Claude Code exited with code {result.returncode}')
        logger.info(f'STDOUT: {result.stdout}')
        logger.info(f'STDERR: {result.stderr}')
        
        return {
            "output": result.stdout,
            "error": result.stderr,
            "exitCode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        logger.error('Claude Code command timed out after 5 minutes')
        return {
            "output": "",
            "error": "Command timed out after 5 minutes",
            "exitCode": -1
        }
    
    except subprocess.CalledProcessError as e:
        logger.error(f'Claude Code failed with exit code {e.returncode}')
        return {
            "output": e.stdout or "",
            "error": e.stderr or str(e),
            "exitCode": e.returncode
        }
    
    except Exception as e:
        logger.error(f'Failed to start Claude Code: {str(e)}')
        return {
            "output": "",
            "error": str(e),
            "exitCode": -1
        }


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
