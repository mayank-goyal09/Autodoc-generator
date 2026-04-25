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

        # We use a structured prompt to tell the model exactly what we want
        prompt = f"Code:\n{code_snippet}\n\nSummary of the function in one sentence:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=50,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the part after our prompt
        if "Summary of the function in one sentence:" in full_text:
            summary = full_text.split("Summary of the function in one sentence:")[1].strip()
            # Clean up and take only the first sentence/line
            summary = summary.split("\n")[0].split(". ")[0].strip()
            return summary if summary else "Automated code documentation."
        
        return "Auto-generated documentation."