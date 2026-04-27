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

@st.cache_resource
def load_model():
    """Loads the AI model and caches it so it doesn't reload on every interaction."""
    return DocstringGenerator()

st.title("⚙️ AutoDoc Generator Hub")
st.markdown("""
Welcome to the everyday tool for engineers. Paste your undocumented Python scripts below, 
and the AI will analyze the AST (Abstract Syntax Tree) to inject professional docstrings.
""")

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
