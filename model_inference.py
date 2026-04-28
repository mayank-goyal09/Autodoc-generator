import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from the .env file
load_dotenv()

class DocstringGenerator:
    def __init__(self):
        print("[SETUP] Connecting to Hugging Face Serverless Inference API...")
        
        # Reverting to Llama-3.3 for premium docstring extraction once token permissions are granted
        self.model_name = "meta-llama/Llama-3.3-70B-Instruct"


        
        self.token = os.getenv("HF_TOKEN", None)
        
        if not self.token or self.token == "YOUR_HUGGINGFACE_TOKEN_HERE":
            print("[WARN] HF_TOKEN is missing or default in .env. Using anonymous mode (Strict rate limits).")
            self.token = None
            
        self.client = InferenceClient(model=self.model_name, token=self.token)
        print(f"[READY] Connected to Hugging Face Inference API using {self.model_name}!")

    def predict(self, code_snippet):
        if not code_snippet or not isinstance(code_snippet, str):
            return "No description available."
        
        prompt = f"""You are an expert code documentation engine.
Generate a strict, minimal one-line Python docstring for the provided function according to these rules:

1. DOCUMENT WHAT, NOT HOW: Do NOT describe internal implementation details (e.g. cut "using recursion" or "loops through").
2. DEFINE INPUT CONSTRAINTS: Explicitly state boundary requirements (e.g., "Requires non-negative integer", "Constraint: b != 0").
3. NO FILLER WORDS: Cut phrases like "returns the result of", "given number", "specified amount". Keep it lean.
4. WRITE FOR GUARANTEES: Describe what the function ultimately promises to accomplish.

Good Examples:
- `def factorial(n):` -> "Returns the factorial of n. Requires non-negative integer."
- `def divide(a, b):` -> "Returns the quotient of a divided by b. Constraint: b != 0."
- `def is_prime(n):` -> "Returns True if n is prime, False otherwise. Expects integer."

Code:
{code_snippet.strip()}
"""


        
        try:
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.1,
            )
            
            summary = response.choices[0].message.content.strip()
            
            if summary:
                summary = summary.strip('"\'` #')
                if summary:
                    summary = summary[0].upper() + summary[1:]
                    if not summary.endswith("."):
                        summary += "."
                    return summary
        except Exception as e:
            print(f"[CRASH] Hugging Face Inference failed: {e}")
            return f"Error generating documentation: {str(e)}"


        return "Auto-generated documentation."