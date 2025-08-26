#!/usr/bin/env python3
"""
Simple Claude Code Agent
Directly calls claude-code CLI without Strands framework
"""

import os
import subprocess
import json
import logging
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an AgentCore app
app = BedrockAgentCoreApp()

def call_claude_code(prompt: str) -> str:
    """Call claude-code directly and return the result"""
    try:
        # Set up environment for claude-code
        env = os.environ.copy()
        env.update({
            'CLAUDE_CODE_USE_BEDROCK': '1',
            'AWS_REGION': 'ap-southeast-2',
            'ANTHROPIC_MODEL': 'apac.anthropic.claude-sonnet-4-20250514-v1:0'
        })
        
        logger.info(f"Calling claude-code with prompt: {prompt[:100]}...")
        
        # Execute claude command directly with --print flag for non-interactive mode
        result = subprocess.run(
            ['claude', '--print', prompt], 
            capture_output=True, 
            text=True, 
            timeout=300,
            env=env
        )
        
        if result.returncode == 0:
            logger.info("Claude-code executed successfully")
            return result.stdout.strip()
        else:
            logger.error(f"Claude-code error: {result.stderr}")
            return f"Claude Code Error: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        logger.error("Claude-code command timed out")
        return "Error: Claude Code command timed out"
    except FileNotFoundError:
        logger.error("Claude-code CLI not found")
        return "Error: Claude Code CLI not found. Please ensure it's installed and in PATH"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"

@app.entrypoint
def invoke(payload):
    """Handler for agent invocation - directly calls claude-code"""
    try:
        # Extract prompt from payload
        user_message = payload.get("prompt", "")
        
        if not user_message:
            return {
                "result": "No prompt found in input, please provide a prompt in the payload"
            }
        
        logger.info(f"Received request: {user_message}")
        
        # Call claude-code directly
        claude_result = call_claude_code(user_message)
        
        # Return the result directly
        return {
            "result": claude_result
        }
        
    except Exception as e:
        logger.error(f"Error in invoke handler: {str(e)}")
        return {
            "result": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    app.run()
