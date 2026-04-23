import ast

def extract_functions(file_path):
    """
    Reads a Python file and extracts ALL function names (including methods) and their code.
    """
    try:
        with open(file_path, "r") as source:
            source_code = source.read()
            tree = ast.parse(source_code)
        
        functions = []
        
        # ast.walk visits every single node (including those inside classes)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Only extract if it doesn't already have a docstring
                if ast.get_docstring(node):
                    continue
                    
                func_code = ast.get_source_segment(source_code, node)
                
                functions.append({
                    "name": node.name,
                    "content": func_code,
                    "line": node.lineno
                })
        
        return functions

    except Exception as e:
        print(f"❌ Error parsing file {file_path}: {e}")
        return []
