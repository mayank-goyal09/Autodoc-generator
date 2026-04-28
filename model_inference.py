import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class DocstringGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[SETUP] Loading AI Model on {self.device.upper()}...")
        
        # Salesforce CodeGen 350M Mono - fine-tuned for Python code
        self.model_name = "Salesforce/codegen-350M-mono"
        
        print(f"[FETCH] Loading Tokenizer for {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("[FETCH] Loading Model Weights...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, 
            trust_remote_code=True
        ).to(self.device)
        print("[READY] CodeGen model loaded successfully!")

    def predict(self, code_snippet):
        if not code_snippet or not isinstance(code_snippet, str):
            return "No description available."
        
        # Diverse few-shot prompt to prevent bad/arithmetic defaults
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
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=50,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the part after the final prompt's "Summary:"
        if "Summary:" in full_text:
            summary = full_text.split("Summary:")[-1].strip()
            summary = summary.split("\n")[0].strip()
            
            if summary:
                summary = summary.strip('"\' ')
                summary = summary[0].upper() + summary[1:]
                if not summary.endswith("."):
                    summary += "."
                return summary
        
        return "Auto-generated documentation."