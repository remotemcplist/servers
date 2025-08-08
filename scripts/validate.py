#!/usr/bin/env python3
"""
Validation script for MCP server YAML files.
"""

import yaml
import sys
import os
from pathlib import Path
from datetime import datetime

# Valid categories
VALID_CATEGORIES = [
    'development', 'data-analysis', 'communication', 'payments',
    'cloud', 'productivity', 'security', 'database', 'ai-ml', 'monitoring'
]

# Valid auth types
VALID_AUTH_TYPES = ['oauth2', 'api-key', 'none']

# Valid verification statuses
VALID_STATUSES = ['verified', 'pending', 'unverified']

# Required fields
REQUIRED_FIELDS = [
    'id', 'name', 'category', 'description', 'maintainer',
    'repository', 'authentication', 'endpoints', 'capabilities',
    'tags', 'active'
]

def validate_server(file_path):
    """Validate a single server YAML file."""
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"Invalid YAML: {e}"]
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate ID format
    if 'id' in data:
        server_id = data['id']
        if not server_id.replace('-', '').isalnum() or server_id != server_id.lower():
            errors.append(f"Invalid ID format: {server_id} (use lowercase and hyphens only)")
    
    # Validate category
    if 'category' in data and data['category'] not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {data['category']} (must be one of {VALID_CATEGORIES})")
    
    # Validate description length
    if 'description' in data:
        desc_len = len(data['description'])
        if desc_len < 50 or desc_len > 200:
            errors.append(f"Description must be 50-200 characters (current: {desc_len})")
    
    # Validate authentication
    if 'authentication' in data:
        auth = data['authentication']
        if 'type' in auth and auth['type'] not in VALID_AUTH_TYPES:
            errors.append(f"Invalid auth type: {auth['type']} (must be one of {VALID_AUTH_TYPES})")
    
    # Validate verification status
    if 'verification' in data:
        verification = data['verification']
        if 'status' in verification and verification['status'] not in VALID_STATUSES:
            errors.append(f"Invalid verification status: {verification['status']}")
    
    # Validate dates
    if 'metrics' in data and 'last_updated' in data['metrics']:
        try:
            datetime.fromisoformat(data['metrics']['last_updated'].replace('Z', '+00:00'))
        except:
            errors.append(f"Invalid date format for last_updated: {data['metrics']['last_updated']}")
    
    # Validate URLs
    if 'repository' in data and 'url' in data['repository']:
        url = data['repository']['url']
        if not url.startswith(('http://', 'https://')):
            errors.append(f"Invalid repository URL: {url}")
    
    if 'endpoints' in data:
        endpoints = data['endpoints']
        if 'production' in endpoints:
            prod_url = endpoints['production']
            if not prod_url.startswith(('ws://', 'wss://', 'http://', 'https://')):
                errors.append(f"Invalid production endpoint: {prod_url}")
    
    return errors

def main():
    """Validate all server files or a specific file."""
    if len(sys.argv) > 1:
        # Validate specific file
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        errors = validate_server(file_path)
        if errors:
            print(f"❌ Validation failed for {file_path}:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print(f"✅ {file_path} is valid!")
    else:
        # Validate all files
        servers_dir = Path(__file__).parent.parent / 'servers'
        if not servers_dir.exists():
            print(f"❌ Servers directory not found: {servers_dir}")
            sys.exit(1)
        
        all_valid = True
        for yaml_file in servers_dir.glob('*.yaml'):
            errors = validate_server(yaml_file)
            if errors:
                all_valid = False
                print(f"❌ {yaml_file.name}:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"✅ {yaml_file.name}")
        
        if not all_valid:
            sys.exit(1)
        else:
            print("\n✅ All server files are valid!")

if __name__ == '__main__':
    main()