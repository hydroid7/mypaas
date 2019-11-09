import os
import json
import secrets
import getpass
import hashlib

from ._utils import USER_CONFIG_DIR, SERVER_CONFIG_DIR


def add_user(name):
    """ Create (or update) credentials for a user. Credentials consists
    of a key to put on the user's computer, and a user-specified
    passphrase.
    """

    key1 = secrets.token_urlsafe(48)
    hash1 = hashlib.sha256(key1.encode()).hexdigest()

    print(
        "Two keys will be created. The first is meant to register a computer."
    )
    print("To enable, run this on the machine that needs access:")
    print(f"    mypaas add_server server.domain.com {key1}")
    print()
    print("The second is a passphrase to make sure only the user has access.")

    key2 = getpass.getpass(f"Passphrase for {name}: ")
    hash2 = hashlib.sha256(key2.encode()).hexdigest()

    filename = os.path.join(SERVER_CONFIG_DIR, "user_credentials.json")
    nusers = _update_credentials(filename, name, [hash1, hash2])
    print(
        f"Credential hashes stored for {name}. There are now {nusers} users."
    )


def add_server(server_domain, server_key):
    """ Create (or update) credentials for a server running MyPaas. Use
    add_user on the server first to obtain the key.
    """

    filename = (os.path.join(USER_CONFIG_DIR, "server_credentials.json"),)
    _update_credentials(server_domain, server_key)

    print(f"Server key for {server_domain} stored in {filename}")
    print(f"You can now do:")
    print(f"     mypaas push {server_domain}")


def _update_credentials(filename, key, value):
    # Load
    try:
        with open(filename, "rb") as f:
            credentials = json.loads(f.read().decode())
    except (FileNotFoundError, json.JSONDecodeError):
        credentials = {}
    # Update
    credentials[key] = value
    # Save
    with open(filename, "wb") as f:
        f.write(json.dumps(credentials).encode())
    # Return count
    return len(credentials)