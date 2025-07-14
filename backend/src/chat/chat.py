# Simple AI chatbot using TinyLlama model
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random


class ChatBot:
    def __init__(self):
        print("Loading TinyLlama-1.1B-Chat model... This may take a moment.")
        
        # Load TinyLlama model for chat
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Fix pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.unk_token or "[PAD]"
                self.tokenizer.pad_token_id = self.tokenizer.unk_token_id or 0
                
            # Store conversation history for context
            self.conversation_history = []
            print("TinyLlama model loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load TinyLlama: {e}")
            raise Exception("Could not load AI model. Please check your setup.")
    
    
    def generate_response(self, user_input: str) -> str:
        # Main method to get chat response
        try:
            # Build conversation prompt with proper TinyLlama format
            if len(self.conversation_history) == 0:
                # First message - simple system prompt
                prompt = f"<|system|>\nYou are a helpful AI assistant. Keep responses brief and helpful.</s>\n<|user|>\n{user_input}</s>\n<|assistant|>\n"
            else:
                # Include conversation history for context
                prompt = "<|system|>\nYou are a helpful AI assistant. Keep responses brief and helpful.</s>\n"
                
                # Add last 6 messages for context (3 user-assistant pairs)
                for msg in self.conversation_history[-6:]:
                    if msg['role'] == 'user':
                        prompt += f"<|user|>\n{msg['content']}</s>\n"
                    else:
                        prompt += f"<|assistant|>\n{msg['content']}</s>\n"
                
                # Add current message
                prompt += f"<|user|>\n{user_input}</s>\n<|assistant|>\n"
            
            # Tokenize the prompt
            encoded = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512,
                return_attention_mask=True
            )
            
            # Generate response from model
            with torch.no_grad():
                outputs = self.model.generate(
                    encoded.input_ids,
                    attention_mask=encoded.attention_mask,
                    max_new_tokens=100,  # Increased for fuller responses
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and clean response
            response = self.tokenizer.decode(outputs[0][encoded.input_ids.shape[1]:], skip_special_tokens=True)
            response = self._clean_response(response)
            
            # Save to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            print(f"Chat error: {e}")
            return "I'm having trouble processing that. Could you try rephrasing?"
    
    
    def _clean_response(self, response: str) -> str:
        # Clean and validate the generated response
        response = ' '.join(response.split())  # Remove extra whitespace
        
        # Remove chat formatting artifacts
        artifacts = ['<|user|>', '<|assistant|>', '<|system|>', '</s>', '<|endoftext|>', 
                    'User:', 'Assistant:', '<pad>', '<unk>']
        for artifact in artifacts:
            response = response.replace(artifact, '')
        
        # Handle empty or too short responses
        if not response or len(response.strip()) < 2:
            return self._get_fallback_response()
        
        # Limit response length
        if len(response) > 250:  # Increased from 150 to 250
            sentences = response.split('. ')
            if len(sentences) > 1:
                response = '. '.join(sentences[:2]) + '.'  # Keep first 2 sentences
            else:
                response = response[:250] + '...'
        
        # Remove code blocks that might cause issues
        if '```' in response:
            response = response.split('```')[0].strip()
        
        # Final validation
        if not response.strip() or len(response.strip()) < 2:
            return self._get_fallback_response()
            
        return response.strip()
    
    def _get_fallback_response(self) -> str:
        # Get a random fallback response when generation fails
        fallback_responses = [
            "That's interesting! Tell me more.",
            "I see. What else would you like to talk about?",
            "Could you elaborate on that?",
            "I'm listening. Please continue.",
            "What do you think about it?",
            "I'd love to hear more about your thoughts."
        ]
        return random.choice(fallback_responses)
    
    def reset_conversation(self):
        # Reset the chat history
        self.conversation_history = []


# Global chatbot instance
chatbot = ChatBot()
