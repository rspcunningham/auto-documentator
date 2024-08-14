import ast
import sys
import os
import requests
import base64

import ast
import textwrap

def parse_content(content, module_name):
    """
    Parse the content of a Python file and generate a markdown document.

    Args:
        content (str): The content of the Python file.
        module_name (str): The name of the module.
    
    Returns:
        str: The markdown content.
    """
    tree = ast.parse(content)
    markdown = f"# {module_name}\n\n"
    module_doc = extract_docstring(tree)
    if module_doc:
        markdown += f"{module_doc}\n\n"

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            markdown += format_class(node)
        elif isinstance(node, ast.FunctionDef):
            markdown += format_function(node)

    return markdown

def format_class(node):
    markdown = f"## Class: {node.name}\n\n"
    markdown += f"```python\nclass {node.name}"
    if node.bases:
        base_classes = ", ".join(ast.unparse(base) for base in node.bases)
        markdown += f"({base_classes})"
    markdown += ":\n    ...\n```\n\n"
    markdown += f"{extract_docstring(node)}\n\n"
    return markdown

def format_function(node):
    markdown = f"### Function: {node.name}\n\n"
    markdown += "```python\n"
    markdown += f"def {node.name}("
    
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

import ast
import re

def extract_docstring(node):
    docstring = ast.get_docstring(node)
    if docstring:
        # Preserve original indentation
        lines = docstring.split('\n')
        if len(lines) > 1:
            # Find the minimum indentation (excluding empty lines)
            min_indent = min(len(line) - len(line.lstrip()) for line in lines[1:] if line.strip())
            # Remove exactly this amount of indentation from each line
            dedented_lines = [lines[0]] + [line[min_indent:] if line.strip() else '' for line in lines[1:]]
            
            # Format Args section
            formatted_lines = []
            in_args_section = False
            args_pattern = re.compile(r'(\w+)\s*\((.+?)\):\s*(.+)')
            
            for line in dedented_lines:
                if line.strip().lower().startswith('args:'):
                    in_args_section = True
                    formatted_lines.append(line)
                elif in_args_section:
                    match = args_pattern.match(line.strip())
                    if match:
                        arg_name, arg_type, arg_desc = match.groups()
                        formatted_lines.append(f"    `{arg_name}` (`{arg_type}`):")
                        formatted_lines.append(f"        {arg_desc}")
                    else:
                        in_args_section = False
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)
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
        module_name = file_name.replace('.py', '')
        
        file_content = fetch_github_file_content(main_repo_owner, main_repo_name, file_path)
        
        markdown_content = parse_content(file_content, module_name)
        if file_name == '__init__.py':
            output_file = '0_intro.md'
        else: 
            output_file = file_name.replace('.py', '.md')

        upload_file_to_github(docs_repo_owner, docs_repo_name, f"{docs_github_directory_path}/{output_file}", markdown_content, token)