import ast
import sys
import os
import requests
import base64

import ast
import re

def parse_content(content, file_name, module_name):
    """
    Parse the content of a Python file and generate a markdown document.

    Args:
        content (str): The content of the Python file.
        module_name (str): The name of the module.
    
    Returns:
        str: The markdown content.
    """
    tree = ast.parse(content)
    module = [module_name, file_name]
    module_doc = extract_docstring(tree)

    if file_name == "__init__":
        # Format the title differently for __init__.py
        markdown = f"# Introduction to {module_name}\n\n"
    else:
        markdown = f"# {module[1]}\n\n"
    
    if module_doc:
        markdown += f"{module_doc}\n\n"

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            markdown += format_class(node, module)
        elif isinstance(node, ast.FunctionDef):
            markdown += format_function(node, module)
        elif isinstance(node, ast.AnnAssign) or (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            markdown += format_type_alias(node, module)

    return markdown

def format_class(node, module=None):
    markdown = f"## Class: {node.name}\n\n"
    markdown += f"```python\n{module[0]}.{module[1]}.{node.name}"
    if node.bases:
        base_classes = ", ".join(ast.unparse(base) for base in node.bases)
        markdown += f"({base_classes})"
    markdown += ":\n    ...\n```\n\n"
    markdown += f"{extract_docstring(node)}\n\n"

        # Process methods of the class
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            markdown += format_method(child, module + [node.name])

    return markdown

def format_method(node, module=None):
    # Determine if the method is a class method or an instance method
    method_type = "Instance Method"
    if node.args.args and node.args.args[0].arg != 'self':
        method_type = "Class Method"
    
    markdown = f"### {method_type}: {node.name}\n\n"
    markdown += "```python\n"
    markdown += f"{module[0]}.{module[1]}.{module[2]}.{node.name}("
    
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    
    if node.args.kwonlyargs:
        if not node.args.vararg:
            args.append("*")
        for arg in node.args.kwonlyargs:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
    
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    
    formatted_args = ",\n    ".join(args)
    if len(args) > 1:
        markdown += "\n    " + formatted_args + "\n"
    
    markdown += ")\n```\n\n"
    markdown += f"{extract_docstring(node)}\n\n"
    return markdown


def format_function(node, module=None):
    markdown = f"### Function: {node.name}\n\n"
    markdown += "```python\n"
    markdown += f"{module[0]}.{module[1]}.{node.name}("
    
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    
    if node.args.kwonlyargs:
        if not node.args.vararg:
            args.append("*")
        for arg in node.args.kwonlyargs:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
    
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    
    formatted_args = ",\n    ".join(args)
    if len(args) > 1:
        markdown += "\n    " + formatted_args + "\n"
    else:
        markdown += formatted_args
    
    markdown += "):\n    ...\n```\n\n"
    markdown += f"{extract_docstring(node)}\n\n"
    return markdown

def format_type_alias(node, module=None):
    if isinstance(node, ast.AnnAssign):
        alias_name = node.target.id
        alias_value = ast.unparse(node.annotation)
        docstring = extract_docstring(node)
    elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        alias_name = node.targets[0].id
        alias_value = ast.unparse(node.value)
        docstring = extract_comment_docstring(node)
    else:
        return ""
    
    markdown = f"### Type Alias: {alias_name}\n\n"
    markdown += f"```python\n{alias_name} = {alias_value}\n```\n\n"
    if docstring:
        markdown += f"{docstring}\n\n"
    return markdown

def extract_comment_docstring(node):
    """
    Extracts a comment-based docstring immediately preceding a node.
    
    Args:
        node (ast.AST): The AST node to extract the comment-based docstring for.
    
    Returns:
        str: The extracted comment-based docstring, or None if not found.
    """
    if not hasattr(node, 'lineno'):
        return None
    
    # Read the source file
    with open(node.root.filename, 'r') as file:
        lines = file.readlines()
    
    # Extract comments preceding the node
    comments = []
    for i in range(node.lineno - 2, -1, -1):
        line = lines[i].strip()
        if line.startswith('#'):
            comments.append(line[1:].strip())
        else:
            break
    
    if comments:
        return '\n'.join(reversed(comments))
    return None

def extract_docstring(node):
    docstring = ast.get_docstring(node)
    if docstring:
        lines = docstring.split('\n')
        if len(lines) > 1:
            min_indent = min(len(line) - len(line.lstrip()) for line in lines[1:] if line.strip())
            dedented_lines = [lines[0]] + [line[min_indent:] if line.strip() else '' for line in lines[1:]]
            
            formatted_lines = []
            current_section = None
            pattern = re.compile(r'(\w+)\s*(\((.+?)\))?:\s*(.+)')
            
            for line in dedented_lines:
                lower_line = line.strip().lower()
                if lower_line.startswith(('args:', 'returns:', 'raises:')):
                    current_section = lower_line[:-1]  # remove the colon
                    formatted_lines.append(f"#### {current_section.capitalize()}:\n")
                elif current_section:
                    match = pattern.match(line.strip())
                    if match:
                        name, _, type_, desc = match.groups()
                        if current_section == 'args':
                            formatted_lines.append(f"- `{name}` (`{type_}`): {desc}\n")
                        elif current_section == 'returns':
                            formatted_lines.append(f"- `{type_}`: {desc}\n")
                        elif current_section == 'raises':
                            formatted_lines.append(f"- `{name}`: {desc}\n")
                    else:
                        current_section = None
                        formatted_lines.append(line + '\n')
                else:
                    formatted_lines.append(line + '\n')
            
            return ''.join(formatted_lines)
        return docstring
    return ""

def fetch_github_file_content(repo_owner, repo_name, file_path):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        file_content = base64.b64decode(response.json()['content']).decode('utf-8')
        return file_content
    else:
        print(f"Failed to fetch file content from {url}")
        sys.exit(1)

def fetch_python_files_from_github_directory(repo_owner, repo_name, directory_path):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{directory_path}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch directory listing from {url}")
        sys.exit(1)

    file_urls = []
    for item in response.json():
        if item['type'] == 'file' and item['name'].endswith('.py'):
            file_urls.append(item['path'])
    
    print(f"Found {len(file_urls)} python files in the directory.")
    return file_urls

def upload_file_to_github(repo_owner, repo_name, file_path, content, token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    message = f"Auto-update documentation: {file_path}"
    content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # Check if the file already exists
    response = requests.get(url, headers={"Authorization": f"token {token}"})
    
    data = {
        "message": message,
        "content": content_base64,
        "committer": {
            "name": "github-actions[bot]",
            "email": "github-actions[bot]@users.noreply.github.com"
        }
    }

    if response.status_code == 200:
        data['sha'] = response.json()['sha']

    
    response = requests.put(url, json=data, headers={"Authorization": f"token {token}"})

    if response.status_code in [200, 201]:
        print(f"Successfully uploaded {file_path} to {repo_owner}/{repo_name}")
    else:
        print(f"Failed to upload {file_path} to {repo_owner}/{repo_name}: {response.status_code}")
        print(response.json())

    print("Response status code:", response.status_code)
    print("Response content:", response.json())

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python script.py <main_repo_owner> <main_repo_name> <main_github_directory_path> <docs_repo_owner> <docs_repo_name> <docs_github_directory_path>")
        sys.exit(1)
    
    main_repo_owner = sys.argv[1]
    main_repo_name = sys.argv[2]
    main_github_directory_path = sys.argv[3]
    docs_repo_owner = sys.argv[4]
    docs_repo_name = sys.argv[5]
    docs_github_directory_path = sys.argv[6]

    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    python_files = fetch_python_files_from_github_directory(main_repo_owner, main_repo_name, main_github_directory_path)
    
    for file_path in python_files:
        file_name = os.path.basename(file_path)
        file_name = file_name.replace('.py', '')
        
        file_content = fetch_github_file_content(main_repo_owner, main_repo_name, file_path)
        
        markdown_content = parse_content(file_content, file_name, main_github_directory_path)

        if file_name == '__init__':
            output_file = '0_intro.md'
        else: 
            output_file = f"{file_name}.md"

        upload_file_to_github(docs_repo_owner, docs_repo_name, f"{docs_github_directory_path}/{output_file}", markdown_content, token)
