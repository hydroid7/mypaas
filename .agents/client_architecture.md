# MyPaas Client Architecture and Workflow

## Overview

The **client component** of MyPaas (`mypaas.client`) runs on your work machine and provides the command-line interface for interacting with your PaaS server. It handles authentication, deployment packaging, and secure communication with the server.

This document explains how the client part works, its architecture, and the workflow from setup to deployment.

---

## Core Responsibilities

The client component handles:

1. **Key Management** - RSA key pair generation, storage, and retrieval
2. **Authentication** - Secure communication with the server using digital signatures
3. **Deployment Packaging** - Creating deployment packages from local directories
4. **Server Communication** - Secure HTTP communication with the daemon API
5. **Configuration** - Reading deployment configuration from `mypaas.toml`

---

## Module Structure

```
mypaas/client/
├── __init__.py          # Module exports and imports
├── _keys.py            # Key management (generation, storage, retrieval)
└── _push.py            # Deployment pushing to server

mypaas/utils/
├── _deploy_config.py   # Deployment configuration reading
└── _crypto.py          # Cryptographic operations (RSA keys, signing, encryption)
```

---

## Command Line Interface

The client CLI provides the following commands (accessed via `mypaas` without `server` prefix):

### Available Commands

| Command | Description | Module |
|---------|-------------|--------|
| `key-init` | Initialize key setup for this machine | `_keys.py` |
| `key-gen` | Generate a new RSA keypair (for CI/CD) | `_keys.py` |
| `key-get` | Get the public key for this machine | `_keys.py` |
| `push` | Push a deployment to the server | `_push.py` |
| `help` | Show client help | `__main__.py` |
| `version` | Show MyPaas version | `__main__.py` |

### Command Usage Examples

```bash
# Initialize client keys
mypaas key-init

# Generate a new keypair for CI/CD
mypaas key-gen

# Get public key to add to server
mypaas key-get

# Push deployment to server
mypaas push admin.mydomain.com ./myapp

# Show help
mypaas help

# Show version
mypaas version
```

---

## Key Management System (`_keys.py`)

### Overview
The key management system is the foundation of secure client-server communication. It uses RSA key pairs for authentication and digital signatures for request verification.

### Key File Locations

| File | Purpose | Default Location |
|------|---------|------------------|
| Private Key | Client's secret key | `~/.ssh/mypaas_rsa` |
| Standard SSH Key | Alternative private key | `~/.ssh/id_rsa` |
| Key Proxy | Points to actual key file | `~/.ssh/mypaas_rsa` |

### Key Types

1. **Default Key (`~/.ssh/mypaas_rsa`)**
   - Primary key file for MyPaas
   - Can be password-protected
   - Created by `key-init` command

2. **Standard SSH Key (`~/.ssh/id_rsa`)**
   - Existing SSH key can be reused
   - Selected via `key-init` menu

3. **Proxy Key File**
   - Text file containing `file:///path/to/actual/key`
   - Allows flexible key location while maintaining consistent interface

### `key_init()` Function

Interactive setup for client authentication:

#### Process Flow
1. **Check Current Status**
   - Attempts to read existing key from default location
   - Displays current key file in use or error if none exists

2. **Present Options**
   ```
   0. Keep as it is
   1. Generate a new RSA keypair (and store it in '~/.ssh/mypaas_rsa')
   2. Use an existing RSA key file
   3. Use the standard RSA key '~/.ssh/id_rsa'
   ```

3. **Handle User Choice**

   **Option 0: Keep as is**
   - No changes made
   - Uses existing key configuration

   **Option 1: Generate new keypair**
   - Creates new 2048-bit RSA key pair
   - Prompts for passphrase (recommended)
   - Saves encrypted private key to `~/.ssh/mypaas_rsa`
   - Overwrites existing key only with explicit confirmation

   **Option 2: Use existing RSA key file**
   - Prompts for path to existing private key
   - Validates file existence
   - Creates proxy file pointing to the specified key

   **Option 3: Use standard SSH key**
   - Uses `~/.ssh/id_rsa` if it exists
   - Creates proxy file pointing to standard SSH key

### `key_gen()` Function

Generates a passwordless RSA keypair for CI/CD environments:

#### Process Flow
1. **Generate Keypair**
   - Creates new 2048-bit RSA key pair
   - No passphrase (for automation)

2. **Copy Private Key**
   - Displays security warning about private key
   - Copies private key to clipboard (with newlines replaced by underscores)
   - Waits for user to paste key to destination
   - Clears clipboard after pasting

3. **Copy Public Key**
   - Copies public key to clipboard
   - Displays public key on screen
   - Shows fingerprint for identification

### `key_get()` Function

Retrieves the public key corresponding to the client's private key:

#### Process Flow
1. **Load Private Key**
   - Calls `get_private_key()` to load the private key
   - Handles passphrase prompt if key is encrypted

2. **Extract Public Key**
   - Derives public key from private key

3. **Display and Copy**
   - Copies public key to clipboard
   - Prints public key to console
   - Displays fingerprint for identification
   - Shows instructions for adding to server

### `get_private_key()` Function

Loads the private key for authentication:

#### Process Flow
1. **Check Environment Variable**
   - Looks for `MYPAAS_PRIVATE_KEY` environment variable
   - If set, uses the value directly (for CI/CD)

2. **Load from File**
   - Calls `get_key_filename_and_text()` to get key location and content

3. **Handle Encryption**
   - If key contains "ENCRYPTED", prompts for passphrase
   - Otherwise, uses empty passphrase

4. **Parse and Return**
   - Parses key text using `PrivateKey.from_str()`
   - Returns PrivateKey object

### `get_key_filename_and_text()` Function

Resolves the actual key file location and content:

#### Process Flow
1. **Check Default Location**
   - Reads from `~/.ssh/mypaas_rsa`

2. **Handle Proxy Files**
   - If content starts with `file://`, follows the reference
   - Reads from the referenced file

3. **Validate and Return**
   - Ensures file exists
   - Returns filename and key text

---

## Cryptographic Operations (`_crypto.py`)

### Overview
The crypto module provides RSA key management, signing, and encryption using the `cryptography` library.

### Classes

#### `PrivateKey` Class

**Purpose:** Manages RSA private keys for signing and decryption.

**Methods:**

- `generate(size=2048)` - Creates new RSA key pair
- `from_str(s, password)` - Loads private key from string
- `to_str(password)` - Serializes private key to string
- `get_id()` - Returns key fingerprint (last 10 chars of public key)
- `get_public_key()` - Returns corresponding PublicKey object
- `sign(data)` - Signs data with private key (returns base64-encoded signature)
- `decrypt(encrypted_data)` - Decrypts data with private key

**Key Formats Supported:**
- PEM format (with or without encryption)
- OpenSSH format

#### `PublicKey` Class

**Purpose:** Manages RSA public keys for verification and encryption.

**Methods:**

- `from_str(s)` - Loads public key from string (MyPaas format)
- `to_str()` - Serializes public key to URL-safe string
- `get_id()` - Returns key fingerprint (last 10 chars)
- `verify_data(signature, data)` - Verifies digital signature
- `encrypt(data)` - Encrypts data with public key

**Public Key Format:**
- Prefix: `rsa-pub-`
- Encoding: Base64 URL-safe encoding of DER-formatted key

### Security Features

1. **Key Generation**
   - 2048-bit RSA keys
   - Public exponent: 65537
   - Backend: cryptography's default backend

2. **Signing**
   - Algorithm: RSA-PSS with SHA-256
   - Padding: MGF1 with SHA-256
   - Salt length: Maximum

3. **Encryption**
   - Algorithm: RSA-OAEP with SHA-256
   - Padding: MGF1 with SHA-256

4. **Key Serialization**
   - Private keys: PEM format, PKCS8 encoding
   - Public keys: DER format, PKCS1 encoding
   - Encryption: Best available encryption for private keys

---

## Deployment Configuration (`_deploy_config.py`)

### Overview
Reads deployment configuration from `mypaas.toml` file in the project directory.

### `deploy_config(path)` Function

#### Process Flow
1. **Set Defaults**
   ```python
   default_config = {"ignore": ["__pycache__", "htmlcov", ".git", "node_modules"]}
   ```

2. **Resolve Path**
   - If `path` is a file, uses it as Dockerfile
   - If `path` is a directory, looks for `Dockerfile` inside
   - Validates Dockerfile existence

3. **Load Configuration**
   - Looks for `mypaas.toml` in the project directory
   - If found, loads and merges with defaults
   - If not found, uses defaults only

4. **Return Configuration**
   - Adds `dockerfile` and `directory` to config
   - Returns complete configuration dict

### Configuration File Format (`mypaas.toml`)

```toml
# Example mypaas.toml
[ignore]
# Directories to ignore when creating deployment package
ignore = ["__pycache__", "htmlcov", ".git", "node_modules", "venv"]
```

### Configuration Structure

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| `ignore` | list | Directories to exclude from deployment | `[