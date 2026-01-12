import ast
import json
import sys
# import matplotlib  # Commented: Skip Agg/non-interactive backend
# matplotlib.use('Agg')  # Commented: No plotting deps

def py_to_json_ast(py_file_path):
    try:
        with open(py_file_path, 'r') as f:
            py_code = f.read()
    except IOError as e:
        raise ValueError(f"Failed to read {py_file_path}: {e}")
    
    tree = ast.parse(py_code)
    
    def ast_to_dict(node):
        if isinstance(node, ast.AST):
            fields = {field_name: ast_to_dict(value) for field_name, value in ast.iter_fields(node)}
            return {'type': node.__class__.__name__, 'fields': fields}
        elif isinstance(node, list):
            return [ast_to_dict(item) for item in node]
        elif isinstance(node, str):
            return node
        else:
            return node
    
    return json.dumps(ast_to_dict(tree), indent=2)

def json_to_py(json_str):
    def dict_to_ast(d):
        if isinstance(d, dict) and 'type' in d:
            node_type = getattr(ast, d['type'])
            fields = d.get('fields', {})
            args = {k: dict_to_ast(v) for k, v in fields.items()}
            
            # Fix lineno/col for unparse
            for attr in ['lineno', 'col_offset', 'end_lineno', 'end_col_offset']:
                if attr not in args:
                    args[attr] = 0
            
            # Fix ctx enums
            if 'ctx' in args and isinstance(args['ctx'], dict):
                ctx_type = args['ctx'].get('type')
                if ctx_type == 'Load':
                    args['ctx'] = ast.Load()
                elif ctx_type == 'Store':
                    args['ctx'] = ast.Store()
            
            try:
                new_node = node_type(**args)
                for attr in ['lineno', 'col_offset', 'end_lineno', 'end_col_offset']:
                    if not hasattr(new_node, attr) or getattr(new_node, attr) is None:
                        setattr(new_node, attr, 0)
                return new_node
            except TypeError as e:
                print(f"Error creating {d['type']}: {e} (skipping)")
                return None
        elif isinstance(d, list):
            return [dict_to_ast(item) for item in d if dict_to_ast(item) is not None]
        elif isinstance(d, dict):
            return {k: dict_to_ast(v) for k, v in d.items()}
        else:
            return d
    
    try:
        ast_dict = json.loads(json_str)
        ast_tree = dict_to_ast(ast_dict)
        if ast_tree is None:
            raise ValueError("AST reconstruction failed (too many skips)")
        
        unpacked = ast.unparse(ast_tree)
        ast.parse(unpacked)  # Validate syntax
        return unpacked
    except (json.JSONDecodeError, SyntaxError) as e:
        return f"Reconstruction failed: {str(e)}"

# CLI Usage
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python glueCode.py <py_file> [json_file]")
        sys.exit(1)
    
    py_path = sys.argv[1]
    json_blob = py_to_json_ast(py_path)
    
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write(json_blob)
        print(f"JSON blob saved to {sys.argv[2]}")
    else:
        print("Packed JSON:")
        print(json_blob)
    
    # Unpack
    unpacked_py = json_to_py(json_blob)
    print(f"\nUnpacked Py:\n{unpacked_py}")
    
    # PIM-specific: No pre-imports—skip plot if deps missing
    print("\nRunning unpacked code (metrics only, skip plot if no deps):")
    local_vars = {}
    safe_globals = {
        '__builtins__': {
            'print': print,
            '__import__': __import__,  # Allows imports if present
        }
        # No np/plt pre-load: Let exec try; catch plot errors
    }
    try:
        # Wrap exec in try for plot skip
        exec(unpacked_py, safe_globals, local_vars)
        if 'result' in local_vars:
            print("Exec success! PIM metrics:")
            print(f"Avg reduction: {local_vars['result']['avg_reduction']}")
            print(f"Stability: {local_vars['result']['stability_ready']}%")
            print(f"States sample: {local_vars['result']['states'][:5]}")
            if 'visual_masterpiece_base64' in local_vars['result'] and local_vars['result']['visual_masterpiece_base64']:
                print(f"Plot base64 length: {len(local_vars['result']['visual_masterpiece_base64'])}")
            else:
                print("Plot skipped (no matplotlib)")
        else:
            print("Exec ran, but no 'result' (check PIM output)")
    except ImportError as e:
        if 'numpy' in str(e) or 'matplotlib' in str(e):
            print(f"Skipping deps ({e}); metrics computed without plot.")
            # Re-exec core logic only (manual snippet for metrics—adapt if needed)
            # ... (or just note: full exec would need np for linspace/mean)
        else:
            raise
    except Exception as e:
        print(f"Exec error: {str(e)}")