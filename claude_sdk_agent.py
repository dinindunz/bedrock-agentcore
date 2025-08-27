#!/usr/bin/env python3
"""
Claude SDK Agent
Uses claude-code-sdk with AgentCore for code generation and analysis
"""

import asyncio
import logging
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an AgentCore app
app = BedrockAgentCoreApp()

async def call_claude_sdk(prompt: str) -> str:
    """Call claude-code-sdk and return the complete response"""
    try:
        logger.info(f"Calling claude-code-sdk with prompt: {prompt[:100]}...")
        
        # Configure claude-code-sdk options
        options = ClaudeCodeOptions(
            system_prompt="You are an expert software engineer and code analyst. Provide clear, well-documented code and thorough analysis.",
            allowed_tools=["Bash", "Read", "Edit", "WebSearch"],
            max_turns=10
        )
        
        response_text = ""
        
        async with ClaudeSDKClient(options=options) as client:
            # Send the query
            await client.query(prompt)
            
            # Stream and collect the response
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_text += block.text
        
        logger.info("Claude SDK executed successfully")
        return response_text.strip()
        
    except Exception as e:
        logger.error(f"Error calling claude-code-sdk: {str(e)}")
        return f"Error: {str(e)}"

@app.entrypoint
def invoke(payload):
    """Handler for agent invocation - calls claude-code-sdk"""
    try:
        # Extract prompt from payload
        user_message = payload.get("prompt", "")
        
        if not user_message:
            return {
                "result": "No prompt found in input, please provide a prompt in the payload"
            }
        
        logger.info(f"Received request: {user_message}")
        
        # Call claude-code-sdk asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            claude_result = loop.run_until_complete(call_claude_sdk(user_message))
        finally:
            loop.close()
        
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
