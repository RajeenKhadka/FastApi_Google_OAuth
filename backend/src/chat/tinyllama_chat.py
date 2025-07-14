# Alternative lightweight chat module with TinyLlama
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional


class TinyLlamaChatBot:
    def __init__(self):
        """Initialize the TinyLlama model and tokenizer"""
        print("Loading TinyLlama-1.1B-Chat model...")
        
        # TinyLlama is much smaller but still way better than DialoGPT
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.conversation_history = []
            print("TinyLlama model loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load TinyLlama model: {e}")
            raise e
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response from TinyLlama"""
        try:
            # Format as chat conversation
            if len(self.conversation_history) == 0:
                # First message
                prompt = f"<|user|>\n{user_input}</s>\n<|assistant|>\n"
            else:
                # Continue conversation
                conversation = ""
                for msg in self.conversation_history[-4:]:  # Keep last 4 exchanges
                    conversation += f"<|{msg['role']}|>\n{msg['content']}</s>\n"
                prompt = conversation + f"<|user|>\n{user_input}</s>\n<|assistant|>\n"
            
            # Tokenize
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            
            # Clean response
            response = response.split("</s>")[0].strip()
            response = response.split("<|user|>")[0].strip()
            
            if not response or len(response) < 2:
                response = "I'm sorry, I didn't understand that. Could you rephrase?"
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            print(f"TinyLlama generation error: {e}")
            return "I'm having trouble processing that. Could you try again?"
    
    def reset_conversation(self):
        """Reset the chat history"""
        self.conversation_history = []


# Global chatbot instance
# chatbot = TinyLlamaChatBot()  # Uncomment to use TinyLlama instead
