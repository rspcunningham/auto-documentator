# ..*script*

### Function: parse_content

```python
..script.parse_content(
    content,
    file_name,
    module_name
):
    ...
```

Parse the content of a Python file and generate a markdown document.

#### Args:
- `content` (`str`): The content of the Python file.
- `module_name` (`str`): The name of the module.

#### Returns:
- `None`: The markdown content.


### Function: format_class

```python
..script.format_class(
    node,
    module
):
    ...
```



### Function: format_function

```python
..script.format_function(
    node,
    module
):
    ...
```



### Function: extract_docstring

```python
..script.extract_docstring(node):
    ...
```



### Function: fetch_github_file_content

```python
..script.fetch_github_file_content(
    repo_owner,
    repo_name,
    file_path
):
    ...
```



### Function: fetch_python_files_from_github_directory

```python
..script.fetch_python_files_from_github_directory(
    repo_owner,
    repo_name,
    directory_path
):
    ...
```



### Function: upload_file_to_github

```python
..script.upload_file_to_github(
    repo_owner,
    repo_name,
    file_path,
    content,
    token
):
    ...
```



