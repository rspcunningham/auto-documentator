# script

### Function: parse_content

```python
def parse_content(
    content,
    module_name
):
    ...
```

Parse the content of a Python file and generate a markdown document.

Args:
    `content` (`str`):
        The content of the Python file.
    `module_name` (`str`):
        The name of the module.

Returns:
    str: The markdown content.

### Function: format_class

```python
def format_class(node):
    ...
```



### Function: format_function

```python
def format_function(node):
    ...
```



### Function: extract_docstring

```python
def extract_docstring(node):
    ...
```



### Function: fetch_github_file_content

```python
def fetch_github_file_content(
    repo_owner,
    repo_name,
    file_path
):
    ...
```



### Function: fetch_python_files_from_github_directory

```python
def fetch_python_files_from_github_directory(
    repo_owner,
    repo_name,
    directory_path
):
    ...
```



### Function: upload_file_to_github

```python
def upload_file_to_github(
    repo_owner,
    repo_name,
    file_path,
    content,
    token
):
    ...
```



