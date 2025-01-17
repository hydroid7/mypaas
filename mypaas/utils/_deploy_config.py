"""
Reads the deploy configuration from mypaas.toml file.
"""
import os
import toml

default_config = {"ignore": ["__pycache__", "htmlcov", ".git", "node_modules"]}


def deploy_config(path):
    config = default_config
    dockerfile = os.path.abspath(path)
    # Check dockerfile and get directory
    if os.path.isfile(dockerfile):
        directory = os.path.dirname(dockerfile)
    elif os.path.isdir(dockerfile):
        directory = dockerfile
        dockerfile = os.path.join(directory, "Dockerfile")
        if not os.path.isfile(dockerfile):
            raise RuntimeError(f"No Dockerfile found in {directory!r}")
    else:
        raise RuntimeError(f"Given dockerfile not a file nor directory: {dockerfile!r}")

    # Load the deploy configuration file
    try:
        config_path = os.path.join(directory, "mypaas.toml")
        config = toml.load(config_path)
        print(f"✔ Reading config from {config_path}")
    except Exception:
        print("No mypaas.toml found. Proceeding with defaults.")

    config["dockerfile"] = dockerfile
    config["directory"] = directory
    return config