#!/usr/bin/env python3
"""
Secure secrets management script for the AI Code Explainer application.
This script helps manage API keys and other sensitive information securely.
"""

import os
import sys
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from base64 import b64encode
import json

def generate_key():
    """Generate a new encryption key."""
    return Fernet.generate_key()

def save_key(key, key_file):
    """Save the encryption key securely."""
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.write_bytes(key)
    os.chmod(key_file, 0o600)  # Read/write for owner only

def load_key(key_file):
    """Load the encryption key."""
    try:
        return key_file.read_bytes()
    except FileNotFoundError:
        key = generate_key()
        save_key(key, key_file)
        return key

def encrypt_secrets(secrets, key):
    """Encrypt secrets dictionary."""
    f = Fernet(key)
    return f.encrypt(json.dumps(secrets).encode())

def decrypt_secrets(encrypted_data, key):
    """Decrypt secrets dictionary."""
    f = Fernet(key)
    return json.loads(f.decrypt(encrypted_data))

def save_secrets(secrets, secrets_file, key):
    """Save encrypted secrets to file."""
    encrypted = encrypt_secrets(secrets, key)
    secrets_file.parent.mkdir(parents=True, exist_ok=True)
    secrets_file.write_bytes(encrypted)
    os.chmod(secrets_file, 0o600)  # Read/write for owner only

def load_secrets(secrets_file, key):
    """Load and decrypt secrets from file."""
    try:
        encrypted = secrets_file.read_bytes()
        return decrypt_secrets(encrypted, key)
    except FileNotFoundError:
        return {}

def update_env_file(secrets):
    """Update .env file with decrypted secrets."""
    env_content = []
    for key, value in secrets.items():
        env_content.append(f"{key}={value}")
    
    with open(".env", "w") as f:
        f.write("\n".join(env_content))
    os.chmod(".env", 0o600)  # Read/write for owner only

def main():
    """Main function to manage secrets."""
    # Setup paths
    config_dir = Path.home() / ".config" / "ai-code-explainer"
    key_file = config_dir / "secret.key"
    secrets_file = config_dir / "secrets.enc"

    # Load or generate encryption key
    key = load_key(key_file)

    # Load existing secrets
    secrets = load_secrets(secrets_file, key)

    # Command line interface
    if len(sys.argv) < 2:
        print("Usage:")
        print("  set    - Set new API keys")
        print("  show   - Show current API keys")
        print("  apply  - Apply secrets to .env file")
        sys.exit(1)

    command = sys.argv[1]

    if command == "set":
        print("Enter your API keys (press Enter to keep existing values):")
        
        # OpenAI API Key
        current = secrets.get("OPENAI_API_KEY", "")
        new_key = getpass.getpass(f"OpenAI API Key [{current[:8]}...]: ")
        if new_key:
            secrets["OPENAI_API_KEY"] = new_key

        # Anthropic API Key
        current = secrets.get("ANTHROPIC_API_KEY", "")
        new_key = getpass.getpass(f"Anthropic API Key [{current[:8]}...]: ")
        if new_key:
            secrets["ANTHROPIC_API_KEY"] = new_key

        # Save updated secrets
        save_secrets(secrets, secrets_file, key)
        print("Secrets saved successfully!")

    elif command == "show":
        if not secrets:
            print("No secrets found.")
        else:
            for key, value in secrets.items():
                print(f"{key}: {value[:8]}...")

    elif command == "apply":
        if not secrets:
            print("No secrets found. Please set them first using 'set' command.")
            sys.exit(1)
        update_env_file(secrets)
        print("Applied secrets to .env file!")

if __name__ == "__main__":
    main() 