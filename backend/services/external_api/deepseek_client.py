import requests
from config import DEEPSEEK_API_KEY
from typing import Optional, Dict, Any, List

class DeepSeekClient:
    """
    Simple DeepSeek API client - send prompts, get responses.
    """
    
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
        if not self.api_key:
            print("Warning: DEEPSEEK_API_KEY not found. Client will not work properly.")
    
    def chat(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Send a prompt to DeepSeek and get a response.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response (default: 1000)
            temperature: Response creativity 0.0-1.0 (default: 0.7)
            
        Returns:
            The response text from DeepSeek
            
        Raises:
            Exception: If API call fails
        """
        if not self.api_key:
            raise Exception("DEEPSEEK_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected DeepSeek API response format: {e}")
    
    def chat_with_system(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Send a prompt with system message to DeepSeek.
        
        Args:
            system_prompt: System/instruction prompt
            user_prompt: User's actual prompt
            max_tokens: Maximum tokens in response
            temperature: Response creativity 0.0-1.0
            
        Returns:
            The response text from DeepSeek
        """
        if not self.api_key:
            raise Exception("DEEPSEEK_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected DeepSeek API response format: {e}")