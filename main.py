import os
import sys
import traceback

from parser_engine import extract_functions
from model_inference import DocstringGenerator

import argparse

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="AutoDoc Generator: Automatically generate Python docstrings using AI.")
    parser.add_argument(
        "--file", 
        type=str, 
        required=True, 
        help="Path to the Python file you want to document."
    )
    
    # Parse the arguments
    args = parser.parse_args()
    target_file = args.file
    
    if not os.path.exists(target_file):
        print(f"❌ Error: File '{target_file}' not found.")
        return

    try:
        generator = DocstringGenerator()
        print(f"🔍 Analyzing {target_file}...")
        functions = extract_functions(target_file)
        
        if not functions:
            print("ℹ️ No new functions need documenting!")
            return

        # Store documentation: {line_number: docstring_text}
        doc_map = {}
        
        for func in functions:
            print(f"🧠 Processing: {func['name']}...")
            summary = generator.predict(func['content'])
            doc_map[func['line']] = summary
        
        print("🖋️ Injecting docstrings into new file...")
        final_file = inject_docstrings(target_file, doc_map)
        
        print(f"✅ Success! Your documented code is at: {final_file}")

    except Exception as e:
        print("💥 An unexpected error occurred:")
        traceback.print_exc()


def format_docstring(text, indentation="    "):
    """Wraps the AI text in triple quotes and matches indentation."""
    return f'{indentation}"""\n{indentation}{text}\n{indentation}"""'

def inject_docstrings(file_path, documentation_map):
    """
    documentation_map: A dictionary where key is line number, 
    value is the generated docstring.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Sort backwards to keep indices valid during insertion
    for line_num in sorted(documentation_map.keys(), reverse=True):
        doc_text = documentation_map[line_num]
        
        # We need to find the ACTUAL 'def' line because decorators shift lineno
        # Search forward from the reported line number to find the 'def'
        idx = line_num - 1
        while idx < len(lines) and "def " not in lines[idx]:
            idx += 1
            
        if idx >= len(lines): continue # Safety fallback

        current_line = lines[idx]
        indent = " " * (len(current_line) - len(current_line.lstrip()))
        
        # Professional tip: Docstrings go right after the 'def ...:' line
        formatted = format_docstring(doc_text, indent + "    ")
        lines.insert(idx + 1, formatted + "\n")

    output_path = file_path.replace(".py", "_documented.py")
    with open(output_path, "w") as f:
        f.writelines(lines)
    return output_path

if __name__ == "__main__":
    main()