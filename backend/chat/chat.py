# Chat module with Hugging Face DialoGPT
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional


class ChatBot:
    def __init__(self):
        """Initialize the DialoGPT model and tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
        self.chat_history_ids = None
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response from the chatbot"""
        # Encode user input
        new_user_input_ids = self.tokenizer.encode(
            user_input + self.tokenizer.eos_token, 
            return_tensors='pt'
        )
        
        # Append to chat history or start new conversation
        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1)
        else:
            bot_input_ids = new_user_input_ids
        
        # Generate response
        self.chat_history_ids = self.model.generate(
            bot_input_ids, 
            max_length=1000, 
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode the response
        response = self.tokenizer.decode(
            self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], 
            skip_special_tokens=True
        )
        
        return response
    
    def reset_conversation(self):
        """Reset the chat history"""
        self.chat_history_ids = None


# Global chatbot instance
chatbot = ChatBot()
