FROM public.ecr.aws/docker/library/python:3.13-slim
WORKDIR /app

# Install Node.js 18
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
COPY ./prompts/strands_agent.md strands_agent.md
# COPY ./prompts/claude_agent.md claude_agent.md
# Install from requirements file
RUN pip install -r requirements.txt

# Set environment variables for Bedrock
ENV CLAUDE_CODE_USE_BEDROCK=1
ENV AWS_REGION=ap-southeast-2
ENV ANTHROPIC_MODEL=apac.anthropic.claude-sonnet-4-20250514-v1:0


RUN pip install aws-opentelemetry-distro>=0.10.0

# Set AWS region environment variable
ENV AWS_REGION=ap-southeast-2
ENV AWS_DEFAULT_REGION=ap-southeast-2


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 8080
EXPOSE 8000

# Copy entire project (respecting .dockerignore)
COPY . .

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "my_agent"]
