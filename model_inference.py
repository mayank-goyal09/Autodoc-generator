import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from the .env file
load_dotenv()

class DocstringGenerator:
    def __init__(self):
        print("[SETUP] Connecting to Hugging Face Serverless Inference API...")
        
        # We use Llama-3.3-70B-Instruct which yields incredible performance on zero-shot code
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
        
        prompt = f"""You are a senior technical writer.
Summarize the following Python function in one short, crisp, professional sentence.
The sentence MUST start with a capitalized present-tense verb (e.g. "Calculates", "Returns", "Validates", "Checks").
Do NOT wrap the output in quotes. Only return the summary sentence.

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
            return "Auto-generated documentation."

        return "Auto-generated documentation."