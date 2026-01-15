"""
LLM Service using OpenRouter API
"""
import os
import json
import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using a model that supports JSON mode well and is capable
DEFAULT_MODEL = "mistralai/devstral-2512:free" 

async def generate_response(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Generate a completion from OpenRouter.
    Returns a parsed JSON dictionary if possible, or raw text wrapped in dict.
    """
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set. Using mock response.")
        return {
            "reasoning": "LLM API Key missing. Simulation running in fallback mode.",
            "actions": {"action": "wait"},
            "emotional_state": "neutral"
        }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://chronicleops.sim",
        "X-Title": "ChronicleOps Simulation",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API Error: {response.text}")
                return {
                    "reasoning": f"API Error: {response.status_code}",
                    "actions": {},
                    "error": True
                }
                
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            try:
                # Attempt to parse JSON response
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from LLM response")
                return {
                    "reasoning": content,
                    "actions": {}
                }
                
    except Exception as e:
        logger.exception("LLM generation failed")
        return {
            "reasoning": f"System Error: {str(e)}",
            "actions": {},
            "error": True
        }
