import streamlit as st
import os
import sys

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser_engine import extract_functions
from model_inference import DocstringGenerator
from main import inject_docstrings

# Configure the Streamlit page
st.set_page_config(page_title="AutoDoc Hub", page_icon="⚙️", layout="wide")

def load_css():
    st.markdown("""
    <style>
        /* Base background */
        .stApp {
            background: linear-gradient(135deg, #1a1a20 0%, #0f0f11 100%);
            color: #E2E8F0;
        }
        
        /* Titles and text */
        h1, h2, h3, h4, h5, h6, p, .stMarkdown {
            color: #E2E8F0 !important;
        }
        
        .main-title {
            font-size: 3rem !important;
            font-weight: 800 !important;
            background: linear-gradient(90deg, #00E5FF, #B026FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 5s ease infinite;
            background-size: 200% 200%;
            margin-bottom: 0rem !important;
            padding-bottom: 0rem !important;
        }

        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Glassmorphism for Text Areas */
        .stTextArea textarea {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: #E2E8F0 !important;
            padding: 1rem !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            transition: all 0.3s ease-in-out !important;
            font-family: 'Consolas', 'Courier New', monospace !important;
        }

        /* Focus state for Text Areas */
        .stTextArea textarea:focus {
            border-color: #00E5FF !important;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.2) !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
            outline: none !important;
        }
        
        /* Code blocks */
        [data-testid="stCodeBlock"] {
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
        }

        /* Primary Button */
        .stButton > button {
            background: linear-gradient(90deg, #00E5FF, #0088ff) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3) !important;
            width: 100%;
            margin-top: 1rem !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 6px 20px rgba(0, 229, 255, 0.5) !important;
            background: linear-gradient(90deg, #00E5FF, #00b3ff) !important;
        }
        
        .stButton > button:active {
            transform: translateY(1px) scale(0.98) !important;
        }
        
        /* Custom spinner and success messages */
        .stAlert {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            backdrop-filter: blur(10px) !important;
            color: #e2e8f0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

@st.cache_resource
def load_model():
    """Loads the AI model and caches it so it doesn't reload on every interaction."""
    return DocstringGenerator()

st.markdown('<h1 class="main-title">⚙️ AutoDoc Generator Hub</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='color: #a0aec0; font-size: 1.1rem; margin-bottom: 2rem;'>
Welcome to the everyday tool for engineers. Paste your undocumented Python scripts below, 
and the AI will analyze the AST (Abstract Syntax Tree) to inject professional docstrings.
</div>
""", unsafe_allow_html=True)

# Split the layout into two columns for input and output
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Code")
    code_input = st.text_area("Paste your Python code here:", height=400, placeholder="def hello_world():\n    print('hello')")
    generate_btn = st.button("Generate Documentation", type="primary")

with col2:
    st.subheader("Documented Output")
    output_container = st.empty()
    
if generate_btn:
    if not code_input.strip():
        st.warning("Please paste some code first!")
    else:
        # Load the model with a spinner
        with st.spinner("Initializing AI Model..."):
            generator = load_model()
            
        with st.spinner("Analyzing and Documenting..."):
            temp_file = "temp_input.py"
            # Write user input to a temporary file for parsing
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code_input)
                
            functions = extract_functions(temp_file)
            
            if not functions:
                st.info("No functions found that need documenting in the provided code.")
                output_container.code(code_input, language="python")
            else:
                doc_map = {}
                progress_bar = st.progress(0)
                
                # Iterate through functions and generate docstrings
                for idx, func in enumerate(functions):
                    summary = generator.predict(func['content'])
                    doc_map[func['line']] = summary
                    progress_bar.progress((idx + 1) / len(functions))
                
                # Inject the docstrings into a new file
                final_file = inject_docstrings(temp_file, doc_map)
                
                # Read the result
                with open(final_file, "r", encoding="utf-8") as f:
                    documented_code = f.read()
                    
                output_container.code(documented_code, language="python")
                st.success("Documentation successfully generated!")
                
                # Cleanup temporary files
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                if os.path.exists(final_file):
                    os.remove(final_file)
