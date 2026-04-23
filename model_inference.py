import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class DocstringGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚙️ Loading AI Model on {self.device.upper()}...")
        
        # Switching to a more standard GPT-based model to avoid T5/SentencePiece issues
        self.model_name = "microsoft/CodeGPT-small-py"
        
        print(f"📥 Loading Tokenizer for {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        print("📥 Loading Model Weights...")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        print("✅ Model loaded successfully!")

    def predict(self, code_snippet):
        if not code_snippet or not isinstance(code_snippet, str):
            return "No description available."

        # For GPT models, we execute the code followed by a docstring start token
        input_text = code_snippet + '\n\n    """'
        
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        
        with torch.no_grad():
            # Generate until we hit a closing quote or newline
            outputs = self.model.generate(
                input_ids, 
                max_new_tokens=50,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode only the NEW tokens (the generated part)
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the docstring part
        if '"""' in generated_text:
            # We want what comes AFTER the start of our input prompt
            # But since GPT generates the WHOLE sequence, we just take the suffix
            summary = generated_text[len(input_text):].split('"""')[0].strip()
            return summary if summary else "Generated docstring."
        
        return "Auto-generated documentation."