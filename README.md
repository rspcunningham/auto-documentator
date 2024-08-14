# auto-documentator

An example workflow is used in `.github/workflows`. 

## Usage

```yaml
    - name: Call Update Documentation Action
      uses: rspcunningham/auto-documentator@main
      with:
        main_repo_owner: 'rspcunningham'
        main_repo_name: 'fpm-py'
        main_github_directory_path: 'fpm_py'
        docs_repo_owner: 'rspcunningham'
        docs_repo_name: 'fpm-py-docs'
        docs_github_directory_path: 'docs/reference'
        token: ${{ secrets.DOCS_TOKEN }}
```

## Authentication

To use, the token passed in must have write access to the DOCUMENTATION repo's contents. If the docs and the module are in the same repo, this can be secrets.GITHUB_TOKEN. Otherwise you must provision a Personal Access Token as follows: 

Creating a Personal Access Token (PAT)

- Go to GitHub Settings.
- Click on developer settings.
- Select fine-grained tokens.
- Generate the token with the appropriate permissions. 
- Copy the token value. 

Adding the PAT to Your Repository Secrets

- Go to your MODULE repository on GitHub.
- Click on Settings.
- Click on Secrets and variables > Actions.
- Click on New repository secret.
- Name the secret (e.g., PAT_TOKEN) and paste the PAT you copied earlier.
- Save the secret.
