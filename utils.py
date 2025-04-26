import os
import sys
import shutil
import json
from datetime import datetime
import pandas as pd

def create_data_directory():
    """Create the data directory if it doesn't exist"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    
    # Ensure the required data files exist
    required_files = {
        "data/menu.txt": "[]",
        "data/sales.txt": "[]",
        "data/inventory.txt": "[]"
    }
    
    for file_path, default_content in required_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(default_content)
            print(f"Created file: {file_path}")

def format_currency(amount):
    """Format a number as currency"""
    return f"₹{float(amount):.2f}"

def format_timestamp(timestamp_str):
    """Format a timestamp string for display"""
    try:
        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d-%b-%Y %I:%M %p')
    except (ValueError, TypeError):
        return timestamp_str

def format_date(date_str):
    """Format a date string for display"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d %b %Y')
    except (ValueError, TypeError):
        return date_str

def get_safe_filename(name):
    """Convert a string to a safe filename"""
    # Replace spaces with underscores and remove special characters
    safe_name = ''.join(c if c.isalnum() else '_' for c in name)
    return safe_name

def create_backup(data_manager):
    """Create a backup of all data files"""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = "data/backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Create timestamp for backup files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup each file
        for file_name in ["menu.txt", "sales.txt", "inventory.txt"]:
            source_path = f"data/{file_name}"
            dest_path = f"{backup_dir}/{timestamp}_{file_name}"
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
        
        return True, f"Backup created successfully at {timestamp}"
    except Exception as e:
        return False, f"Backup failed: {str(e)}"

def restore_backup(backup_timestamp, data_manager=None):
    """Restore data from a backup"""
    try:
        backup_dir = "data/backups"
        
        # Check if files exist
        required_files = [
            f"{backup_dir}/{backup_timestamp}_menu.txt",
            f"{backup_dir}/{backup_timestamp}_sales.txt",
            f"{backup_dir}/{backup_timestamp}_inventory.txt"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                return False, f"Backup file not found: {file_path}"
        
        # Create backup of current data before restoring
        if data_manager:
            create_backup(data_manager)
        
        # Restore each file
        for file_name in ["menu.txt", "sales.txt", "inventory.txt"]:
            source_path = f"{backup_dir}/{backup_timestamp}_{file_name}"
            dest_path = f"data/{file_name}"
            
            shutil.copy2(source_path, dest_path)
        
        return True, "Backup restored successfully"
    except Exception as e:
        return False, f"Restore failed: {str(e)}"

def validate_json_file(file_path):
    """Validate that a file contains valid JSON and fix if possible"""
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            
            # Handle empty file
            if not content:
                with open(file_path, 'w') as f_write:
                    f_write.write('[]')
                return True, "Fixed empty file with empty array"
            
            # Try to parse JSON
            json.loads(content)
            return True, "Valid JSON"
    except json.JSONDecodeError:
        # Try to fix common issues
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            # Reset file with empty array if content is corrupt
            with open(file_path, 'w') as f:
                f.write('[]')
            
            return False, "Invalid JSON, reset with empty array"
        except Exception as e:
            return False, f"Failed to fix JSON: {str(e)}"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"
