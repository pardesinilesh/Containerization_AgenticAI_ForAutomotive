"""
LLM Interface for generating build and deployment plans.
"""
import os
import json
from typing import Optional
from datetime import datetime


class LLMInterface:
    """Interface to LLM for intelligent decision making."""

    def __init__(self, provider: str = "anthropic"):
        """
        Initialize LLM interface.

        Args:
            provider: LLM provider ('openai' or 'anthropic')
        """
        self.provider = provider
        self.api_key = os.getenv(f"{provider.upper()}_API_KEY", "")

        if provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif provider == "openai":
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)

    async def generate_build_plan(
        self,
        tool: str,
        os: str,
        version: str,
    ) -> dict:
        """
        Generate a build plan using LLM.

        Args:
            tool: Tool name
            os: Target OS
            version: Tool version

        Returns:
            Build plan dictionary
        """
        prompt = f"""
        Generate a Docker build plan for the following automotive development tool:
        - Tool: {tool}
        - OS: {os}
        - Version: {version}

        Provide a JSON response with the following structure:
        {{
            "base_image": "...",
            "dependencies": [...],
            "build_steps": [...],
            "env_variables": {...},
            "ports": [...],
            "volumes": [...]
        }}

        Ensure the plan is optimized for production use and includes security best practices.
        """

        response = self._call_llm(prompt)
        return self._parse_json_response(response)

    async def generate_deployment_manifest(
        self,
        image_id: str,
        replicas: int,
        env: str,
        namespace: str,
    ) -> dict:
        """
        Generate Kubernetes deployment manifest.

        Args:
            image_id: Docker image ID
            replicas: Number of replicas
            env: Environment
            namespace: K8s namespace

        Returns:
            Deployment manifest dictionary
        """
        prompt = f"""
        Generate a Kubernetes deployment manifest for the following:
        - Image: {image_id}
        - Replicas: {replicas}
        - Environment: {env}
        - Namespace: {namespace}

        Provide a JSON response matching Kubernetes YAML structure with:
        - Deployment configuration
        - Service definition
        - Resource limits
        - Health checks
        - Security context

        Focus on production-grade reliability.
        """

        response = self._call_llm(prompt)
        return self._parse_json_response(response)

    async def suggest_optimizations(
        self,
        tool: str,
        current_config: dict,
    ) -> list:
        """
        Use LLM to suggest optimizations for a tool configuration.

        Args:
            tool: Tool name
            current_config: Current configuration dictionary

        Returns:
            List of optimization suggestions
        """
        prompt = f"""
        Analyze the following {tool} configuration and suggest optimizations:

        Current Config:
        {json.dumps(current_config, indent=2)}

        Provide recommendations for:
        1. Image size reduction
        2. Build time optimization
        3. Runtime performance
        4. Security improvements
        5. Resource efficiency

        Return as JSON array of suggestions with priority levels.
        """

        response = self._call_llm(prompt)
        suggestions = self._parse_json_response(response)
        return suggestions if isinstance(suggestions, list) else [suggestions]

    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with a prompt.

        Args:
            prompt: The prompt to send to LLM

        Returns:
            LLM response as string
        """
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
            )
            return response.choices[0].message.content

        return ""

    def _parse_json_response(self, response: str) -> dict:
        """
        Parse JSON from LLM response.

        Args:
            response: LLM response text

        Returns:
            Parsed JSON dictionary
        """
        try:
            # Try to extract JSON from the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Return default if parsing fails
        return {}
