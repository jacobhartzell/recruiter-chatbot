"""
Interface for interacting with language models via HuggingFace OpenAI-compatible API.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

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
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.api_token:
            logger.error("HUGGINGFACE_API_TOKEN not found in environment variables")
            raise ValueError("HuggingFace API token is required")
        
        # Initialize OpenAI client with HuggingFace router
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.api_token
        )
        
        logger.info(f"Initialized LLM interface with model: {self.model_name}")
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using HuggingFace OpenAI-compatible API."""
        try:
            # Build the system message with context and candidate instructions
            system_message = self._build_system_message(context)
            
            # Create chat completion
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract response
            response_text = completion.choices[0].message.content.strip()
            
            # Clean up the response
            return self._clean_response(response_text)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    def _build_system_message(self, context: Optional[str] = None) -> str:
        """Build the system message for the candidate chatbot."""
        system_message = """You are a professional job candidate responding to questions from recruiters and hiring managers. You should answer questions about your experience, skills, and qualifications in a confident, professional, and authentic way.

Key guidelines:
- Be positive and enthusiastic about opportunities
- Highlight relevant experience and achievements
- Be honest about your capabilities
- Show interest in learning and growth
- Maintain a professional tone
- Keep responses concise but informative (2-3 sentences)
- Speak in first person as the candidate

"""
        
        if context:
            system_message += f"""Your background and experience:
{context}

Use this information to answer questions about your qualifications and experience."""
        
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
