import json
import os

import requests

tooling_modules = [
     {  "name" : "score_cr_checker",
        "module_url": "https://github.com/eclipse-score/tooling/blob/main/cr_checker/MODULE.bazel",
    },
    {   "name": "score_dash_license_checker",
        "module_url": "https://github.com/eclipse-score/tooling/blob/main/dash/MODULE.bazel",
    },
    {   "name": "score_format_checker",
        "module_url": "https://github.com/eclipse-score/tooling/blob/main/format_checker/MODULE.bazel",
    },
    {   "name": "score_python_basics",
        "module_url": "https://github.com/eclipse-score/tooling/blob/main/python_basics/MODULE.bazel",
    },
    {   "name": "score_starpls_lsp",
        "module_url": "https://github.com/eclipse-score/tooling/blob/main/starpls/MODULE.bazel",
    },

]
def get_latest_release_info(repo_url: str):
    """
    Given a GitHub repository URL, returns the latest release version and tarball URL.
    
    Args:
        repo_url (str): GitHub repo URL, e.g., 'https://github.com/org/repo'
    
    Returns:
        tuple: (version tag, tarball URL) or (None, None) on error
    """
    # Extract owner/repo from URL
    try:
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        api_url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
    except Exception as e:
        print(f"Invalid repository URL: {e}")
        return None, None

    # Call GitHub API
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Error fetching release info: {response.status_code} {response.text}")
        return None, None

    data = response.json()
    version = data.get("tag_name")
    tarball_url = data.get("tarball_url")
    
    return version, tarball_url

# Example usage:
#if __name__ == "__main__":
#    repo = "https://github.com/eclipse-score/process_description"
#    version, tar_url = get_latest_release_info(repo)
#    print(f"Latest version: {version}")
#    print(f"Tarball URL: {tar_url}")




def get_actual_versions(modules_path="modules"):
    """
    Scans all subdirectories in the modules folder and extracts the actual version
    from each metadata.json file.

    Args:
        modules_path (str): Path to the modules directory (default is 'modules').

    Returns:
        dict: A dictionary of {module_name: actual_version}
    """
    actual_modules_versions = {}

    for module_name in os.listdir(modules_path):
        module_dir = os.path.join(modules_path, module_name)
        metadata_path = os.path.join(module_dir, "metadata.json")

        if os.path.isdir(module_dir) and os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    versions = metadata.get("versions", [])
                    if versions:
                       actual_modules_versions[module_name] = versions[-1]
                    else:
                       actual_modules_versions[module_name] = None
            except Exception as e:
                print(f"Error reading {metadata_path}: {e}")
                actual_modules_versions[module_name] = None

    return actual_modules_versions

# Example usage:
if __name__ == "__main__":
    results = get_actual_versions("modules")
    for module, version in results.items():
        print(f"{module}: {version}")