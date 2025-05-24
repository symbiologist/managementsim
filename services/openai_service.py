"""
OpenAI service for Emergency Medicine Case Simulator
"""

import os
from typing import List, Dict
from openai import OpenAI
from config.case_config import SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT


class OpenAIService:
    """Service for handling OpenAI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o"  # Default model
    
    def get_case_presentation(self, case_content: str) -> str:
        """
        Generate initial case presentation using OpenAI.
        
        Args:
            case_content (str): Case details and information
            
        Returns:
            str: Initial case presentation from AI
            
        Raises:
            Exception: If OpenAI API call fails
        """
        system_message = SYSTEM_PROMPT + "\n\n" + case_content
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Present the case based on the details provided in your system instructions."}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting case presentation: {str(e)}")
    
    def get_chat_response(self, case_content: str, chat_history: List[Dict[str, str]], user_message: str) -> str:
        """
        Generate chat response based on conversation history.
        
        Args:
            case_content (str): Case details and information
            chat_history (List[Dict[str, str]]): Previous conversation messages
            user_message (str): Latest user message
            
        Returns:
            str: AI response to user message
            
        Raises:
            Exception: If OpenAI API call fails
        """
        system_message = SYSTEM_PROMPT + "\n\n" + case_content
        
        # Build conversation messages
        messages = [{"role": "system", "content": system_message}]
        
        # Add chat history (exclude system messages)
        for msg in chat_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting chat response: {str(e)}")
    
    def generate_case_summary(self, chat_history: List[Dict[str, str]]) -> str:
        """
        Generate case summary from chat history.
        
        Args:
            chat_history (List[Dict[str, str]]): Conversation messages
            
        Returns:
            str: Generated case summary
            
        Raises:
            Exception: If OpenAI API call fails
        """
        if not chat_history:
            return "No case information available to summarize yet."
        
        # Format chat history for summary
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                role_label = "Student/Resident (User)"
            elif msg["role"] == "assistant":
                role_label = "Attending (AI)"
            else:
                continue
            
            formatted_history.append(f"{role_label}: {msg['content']}")
        
        history_text = "\n".join(formatted_history)
        
        messages = [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": f"Please summarize the following case interaction transcript:\n\n{history_text}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Could not generate summary at this time. Error: {str(e)[:100]}..."
    
    def set_model(self, model_name: str):
        """
        Set the OpenAI model to use.
        
        Args:
            model_name (str): Model name (e.g., 'gpt-4o', 'gpt-3.5-turbo')
        """
        self.model = model_name
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available OpenAI models.
        
        Returns:
            List[str]: Available model names
        """
        return [
            "gpt-4o",
            "gpt-4-turbo", 
            "gpt-3.5-turbo"
        ]
