import ast
import sys
import os
import requests
import base64

def extract_docstring(node):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
        docstring = ast.get_docstring(node)
        return docstring if docstring else "No docstring provided."
    return None

def parse_content(content, module_name):
    tree = ast.parse(content)
    
    markdown = f"# {module_name}\n\n"
    
    module_doc = extract_docstring(tree)
    if module_doc:
        markdown += f"{module_doc}\n\n"
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            markdown += f"## Class: {node.name}\n\n"
            markdown += f"```python\nclass {node.name}\n```\n\n"
            markdown += f"{extract_docstring(node)}\n\n"
            
        elif isinstance(node, ast.FunctionDef):
            markdown += f"### Function: {node.name}\n\n"
            markdown += f"```python\ndef {node.name}{ast.unparse(node.args)}\n```\n\n"
            markdown += f"{extract_docstring(node)}\n\n"
    
    return markdown

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