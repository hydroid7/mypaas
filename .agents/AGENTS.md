# MyPaas - Application Overview

## Goal

**MyPaas** is a self-hosted Platform as a Service (PaaS) tool that makes it easy to run your own PaaS on a VM or bare metal server. It combines Docker and Traefik to provide:

- Automatic HTTPS via Let's Encrypt certificates
- Secure zero-downtime deployments using Dockerfiles
- Powerful analytics and monitoring for all applications
- A web dashboard for viewing status and analytics
- Simple CLI for both server management and client deployments

The primary goal is to simplify managing your own server while maintaining full control, with your only costs being the VM that the PaaS runs on.

## Architecture

MyPaas consists of **two main components**:

### 1. Server Component (`mypaas.server`)

The server component runs on the PaaS server (your VM or hardware) and provides the infrastructure for hosting applications.

**Location:** `mypaas/server/`

**Modules:**
- `_init.py` - Server initialization and restart functionality
- `_auth.py` - Authentication and public key management
- `_daemon.py` - Daemon process management
- `_deploy.py` - Deployment logic and container management
- `_reboot.py` - Scheduled reboot functionality
- `_stats.py` - Statistics collection and management
- `_traefik.py` - Traefik router initialization and configuration

**Responsibilities:**
- Initialize and configure the PaaS server
- Manage Traefik reverse proxy with automatic HTTPS
- Handle container deployments and updates
- Manage authentication keys
- Collect and provide system statistics
- Schedule and handle server reboots

### 2. Client Component (`mypaas.client`)

The client component runs on your work machine and provides commands to interact with the PaaS server.

**Location:** `mypaas/client/`

**Modules:**
- `_keys.py` - Key initialization, generation, and retrieval
- `_push.py` - Push deployments to the server

**Responsibilities:**
- Generate and manage RSA keys for secure authentication
- Push Dockerfile-based deployments to the server
- Retrieve public keys from the server
- Initialize key storage on the client

### 3. Daemon Component (`mypaas.daemon`)

The daemon runs as a system service on the server and provides the API for client-server communication.

**Location:** `mypaas/daemon/`

**Modules:**
- `__main__.py` - Entry point for the daemon service
- `_api.py` - API endpoints for handling client requests
- `_statsgen.py` - System statistics generation

**Responsibilities:**
- Run as a background service (systemctl)
- Provide HTTP API for push deployments
- Generate and serve system statistics
- Handle authentication and request routing

## Additional Modules

### `mypaas.utils`
Utility functions and helper code used across the application.

### `mypaas.stats`
Statistics-related functionality and data processing.

## How to Use the Project

### Installation

```bash
pip install mypaas
```

### Server Setup

1. **Initialize the server:**
   ```bash
   mypaas server init
   ```

2. **Configure your domain and email** in the generated `mypaas.toml` file

3. **Start the daemon:**
   ```bash
   sudo systemctl start mypaasd
   ```

### Client Usage

1. **Initialize keys on your work machine:**
   ```bash
   mypaas key-init
   ```

2. **Generate a new key pair:**
   ```bash
   mypaas key-gen
   ```

3. **Get the server's public key:**
   ```bash
   mypaas key-get
   ```

4. **Deploy an application:**
   ```bash
   mypaas push
   ```

### Application Configuration

Applications are configured using a Dockerfile with special `mypaas` comments. See the example services in `example_services/` for reference.

### Web Dashboard

After setup, access the dashboard at `https://your-domain.com/mypaas/` to view:
- Application status
- Analytics and traffic statistics
- System information

## Module Structure Summary

```
mypaas/
├── __init__.py           # Main package initialization
├── __main__.py          # CLI entry point
├── client/              # Client component
│   ├── __init__.py      # Client module exports
│   ├── _keys.py         # Key management
│   └── _push.py         # Deployment pushing
├── server/              # Server component
│   ├── __init__.py      # Server module exports
│   ├── _init.py         # Server initialization
│   ├── _auth.py         # Authentication
│   ├── _daemon.py       # Daemon management
│   ├── _deploy.py       # Deployment logic
│   ├── _reboot.py       # Reboot scheduling
│   ├── _stats.py        # Statistics
│   └── _traefik.py      # Traefik configuration
├── daemon/              # Daemon component
│   ├── __init__.py      # Daemon module exports
│   ├── __main__.py      # Daemon entry point
│   ├── _api.py          # API endpoints
│   └── _statsgen.py     # Statistics generation
├── stats/               # Statistics processing
└── utils/               # Utility functions
```

## Example Services

The repository includes example services in `example_services/` that demonstrate different use cases:
- `hello-world/` - Basic web service
- `minimal/` - Minimal service configuration
- `benchmark/` - Performance testing service
- `bad-behaving/` - Service with intentional issues for testing

Each example contains both `server.py` and `client.py` files showing how to structure applications for MyPaas.
