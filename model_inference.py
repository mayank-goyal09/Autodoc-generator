import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class DocstringGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[SETUP] Loading AI Model on {self.device.upper()}...")
        
        # Phi-1.5 is extremely good at Python logic and very stable
        self.model_name = "microsoft/phi-1_5"
        
        print(f"[FETCH] Loading Tokenizer for {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        
        print("[FETCH] Loading Model Weights...")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, trust_remote_code=True).to(self.device)
        print("[READY] Phi-1.5 model loaded successfully!")

    def predict(self, code_snippet):
        if not code_snippet or not isinstance(code_snippet, str):
            return "No description available."

        prompt = f"""Provide a concise, one-sentence description for the Python function.

Code:
def add(a, b):
    return a + b
Summary: Returns the sum of two numbers.

Code:
{code_snippet}
Summary:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=40,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the part after the final prompt's "Summary:"
        if "Summary:" in full_text:
            # Split by Summary: and take the last part
            summary = full_text.split("Summary:")[-1].strip()
            # Stop at the first newline or period
            summary = summary.split("\n")[0].split(".")[0].strip()
            # Remove any stray quotes
            summary = summary.strip('\'" ')
            return summary + "." if summary else "Automated code documentation."
        
        return "Auto-generated documentation."