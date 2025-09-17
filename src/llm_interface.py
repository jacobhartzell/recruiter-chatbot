import os
import logging
import json
import tempfile
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.gcpCredentials import GCPCredentials

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class LLMInterface:
    """Interface for HuggingFace models using OpenAI-compatible API."""

    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-V3-0324:novita", max_tokens: int = 512, temperature: float = 0.7):
        """Initialize LLM interface with HuggingFace OpenAI-compatible API."""
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        # HuggingFace API configuration
        # self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")

        # if not self.api_token:
        #    logger.error("HUGGINGFACE_API_TOKEN not found in environment variables")
        #    raise ValueError("HuggingFace API token is required")

        # Initialize OpenAI client with HuggingFace router
        # self.client = OpenAI(
        #    base_url="https://router.huggingface.co/v1",
        #    api_key=self.api_token
        # )

        # Use the variables from the environment
        PROJECT_ID = os.getenv('GCP_PROJECT_ID')
        LOCATION = os.getenv('GCP_LOCATION')

        # Initialize Vertex AI with credentials
        gcp_creds = GCPCredentials()
        credentials = gcp_creds.get_gcp_credentials()
        
        if credentials:
            logger.info("Using custom GCP credentials for Vertex AI")
            self.client = genai.Client(
                vertexai=True, project=PROJECT_ID, location=LOCATION, credentials=credentials
            )
        else:
            logger.warning("No custom GCP credentials found, using default authentication")
            self.client = genai.Client(
                vertexai=True, project=PROJECT_ID, location=LOCATION
            )

        logger.info(f"Initialized LLM interface with model: {self.model_name}")

    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        try:
            # Build the system message with context and candidate instructions
            system_message = self._build_system_message(context)

            content_response = self.client.models.generate_content(
                            model=self.model_name, 
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_message,
                                max_output_tokens=self.max_tokens,
                                temperature=self.temperature
                                )
            )

            response = content_response.model_dump()["candidates"][0]['content']['parts'][0]['text']
            
            # Clean and format the response
            return self._clean_response(response)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."

    def _build_system_message(self, context: Optional[str] = None) -> list:
        system_message = [
           "Be positive and enthusiastic about opportunities",
           "Highlight relevant experience and achievements", 
           "Be honest about your capabilities",
           "Do not include any skills or experence which is not directly stated in the chat context",
           "Show interest in learning and growth",
           "Maintain a professional tone",
           "Keep responses concise but informative (2-3 sentences)",
           "Speak in first person as the candidate",
           "Do not reference specific places of employment or dates",
           "I am not willing to relocate"
            ]
        if context:
            system_message.append(context)
        return system_message


    def _clean_response(self, response: str) -> str:
        """Clean and format the response."""
        # Remove common unwanted patterns
        response = response.strip()

        # Remove repeated text (common with some models)
        lines = response.split('\n')
        unique_lines = []
        for line in lines:
            if line.strip() and line.strip() not in unique_lines:
                unique_lines.append(line.strip())

        cleaned_response = '\n'.join(unique_lines[:5])  # Limit to 5 lines max

        # Ensure we have a reasonable response
        if len(cleaned_response) < 10:
            return "I'd be happy to help with your recruiting question. Could you provide more specific details?"

        return cleaned_response
