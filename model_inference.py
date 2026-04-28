import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class DocstringGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[SETUP] Loading AI Model on {self.device.upper()}...")
        
        # CodeT5+ (220M) — Salesforce's encoder-decoder model for code understanding
        # Unlike Phi-1.5 (which just predicts next tokens), CodeT5+ actually reads 
        # and understands code semantics before generating a summary
        self.model_name = "Salesforce/codet5p-220m"
        
        print(f"[FETCH] Loading Tokenizer for {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        print("[FETCH] Loading Model Weights...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name, 
            trust_remote_code=True
        ).to(self.device)
        print("[READY] CodeT5+ model loaded successfully!")

    def predict(self, code_snippet):
        if not code_snippet or not isinstance(code_snippet, str):
            return "No description available."
        
        # Diverse few-shot examples so the model doesn't default to 
        # arithmetic descriptions for everything (the old Phi-1.5 problem)
        prompt = f"""Summarize the following Python function in one sentence.

Code:
def add(a, b):
    return a + b
Summary: Returns the sum of two numbers.

Code:
def is_even(n):
    return n % 2 == 0
Summary: Checks if a number is even.

Code:
def greet(name):
    return f"Hello, {{name}}!"
Summary: Returns a greeting string for the given name.

Code:
def withdraw(self, amount):
    if amount > self.balance:
        raise ValueError("Insufficient funds")
    self.balance -= amount
Summary: Withdraws the specified amount from the account balance.

Code:
{code_snippet}
Summary:"""
        
        input_ids = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            max_length=512, 
            truncation=True
        ).input_ids.to(self.device)
        
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids, 
                max_new_tokens=50,
                num_beams=4,           # Beam search for higher quality
                early_stopping=True,
            )
        
        # Decode only the newly generated tokens (skip the input prompt)
        summary = self.tokenizer.decode(
            generated_ids[0][input_ids.shape[-1]:], 
            skip_special_tokens=True
        ).strip()
        
        # If model echoed part of the prompt, extract just the summary
        if "Summary:" in summary:
            summary = summary.split("Summary:")[-1].strip()
        
        # Stop at first newline (in case model continues generating)
        summary = summary.split("\n")[0].strip()
        
        # Clean up: capitalize and ensure period at end
        if summary:
            summary = summary.strip('"\' ')
            summary = summary[0].upper() + summary[1:]
            if not summary.endswith("."):
                summary += "."
            return summary
        
        return "Auto-generated documentation."