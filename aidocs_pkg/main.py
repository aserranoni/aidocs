#!/usr/bin/env python3
import os
import json
import sys
import subprocess

AIDOCS_DIR = os.path.expanduser("~/.aidocs")
CONFIG_FILE = os.path.join(AIDOCS_DIR, "config.json")
TEMPLATE_FILE = os.path.join(AIDOCS_DIR, "template.md")
REAL_FILENAME = "aidocs.md"

DEFAULT_CONFIG = {
    "symlinks": ["GEMINI.md", "CLAUDE.md"]
}

DEFAULT_TEMPLATE = """
# AI Assistant Instructions

This file is the single source of truth for AI assistant context.
It is symlinked to other files like GEMINI.md and CLAUDE.md.

## Project Overview

(TODO: Describe the project's purpose, goals, and key features.)

## Tech Stack

(TODO: List the main technologies, frameworks, and libraries used.)

## Conventions & Style

(TODO: Outline coding conventions, style guides, and architectural patterns.)

## Getting Started

(TODO: Provide instructions on how to set up the development environment.)

"""

def setup():
    """
    Initializes the ~/.aidocs configuration directory and files.
    
    Creates the global configuration directory at ~/.aidocs/ if it doesn't exist,
    and sets up default configuration and template files.
    
    Files created:
    - config.json: Contains symlink configuration
    - template.md: Default template for new aidocs.md files
    """
    print(f"Ensuring configuration directory exists at {AIDOCS_DIR}...")
    os.makedirs(AIDOCS_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        print(f"Creating default config file at {CONFIG_FILE}...")
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    else:
        print(f"Config file already exists at {CONFIG_FILE}.")

    if not os.path.exists(TEMPLATE_FILE):
        print(f"Creating default template file at {TEMPLATE_FILE}...")
        with open(TEMPLATE_FILE, "w") as f:
            f.write(DEFAULT_TEMPLATE)
    else:
        print(f"Template file already exists at {TEMPLATE_FILE}.")
    print("\nSetup complete. You can edit the master template at:")
    print(TEMPLATE_FILE)

def init(project_path):
    """
    Initializes a project with aidocs.md and symlinks.
    
    Args:
        project_path (str): Path to the project directory to initialize
        
    Creates or updates the aidocs.md file in the specified project directory,
    consolidates content from existing AI documentation files, and creates
    symlinks as specified in the global configuration.
    
    Process:
    1. Checks for existing AI documentation files (CLAUDE.md, GEMINI.md, etc.)
    2. Consolidates their content into aidocs.md
    3. Removes the original files
    4. Creates symlinks pointing to aidocs.md
    """
    print(f"Initializing aidocs in {project_path}...")

    # Create the real file
    real_file_path = os.path.join(project_path, REAL_FILENAME)
    
    # Collect content from existing symlinked files
    combined_content = ""
    files_to_delete = []
    
    
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    symlinks_to_check = config.get("symlinks", [])

    for link_name in symlinks_to_check:
        full_link_path = os.path.join(project_path, link_name)
        if os.path.exists(full_link_path) and not os.path.islink(full_link_path):
            print(f"Found existing file {link_name}. Incorporating its content.")
            
            with open(full_link_path, "r") as f_old:
                combined_content += f"\n\n--- Content from {link_name} ---\n\n"
                combined_content += f_old.read()
            files_to_delete.append(full_link_path)

    initial_content = ""
    if os.path.exists(real_file_path):
        print(f"{REAL_FILENAME} already exists. Appending content if necessary.")
        
        with open(real_file_path, "r") as f_real:
            initial_content = f_real.read()
    else:
        print(f"Creating {REAL_FILENAME}...")
        
        with open(TEMPLATE_FILE, "r") as f_template:
            initial_content = f_template.read()

    final_content = initial_content
    if combined_content:
        final_content += combined_content

    
    with open(real_file_path, "w") as f_real:
        f_real.write(final_content)

    # Delete old files after content has been incorporated
    for file_path in files_to_delete:
        print(f"Deleting old file: {file_path}")
        os.remove(file_path)

    # Create the symlinks
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    symlinks_to_create = config.get("symlinks", [])
    
    original_cwd = os.getcwd()
    try:
        os.chdir(project_path)
        for link_name in symlinks_to_create:
            if os.path.lexists(link_name):
                if os.path.islink(link_name) and os.readlink(link_name) == REAL_FILENAME:
                    print(f"Symlink {link_name} already exists and is correct.")
                else:
                    print(f"Warning: {link_name} already exists but is not the correct symlink. Please remove it and run init again.")
            else:
                print(f"Creating symlink: {link_name} -> {REAL_FILENAME}")
                os.symlink(REAL_FILENAME, link_name)
    finally:
        os.chdir(original_cwd)
    
    print("\nInitialization complete.")

def edit(project_path):
    """
    Opens the real aidocs.md file in the default editor.
    
    Args:
        project_path (str): Path to the project directory containing aidocs.md
        
    Opens the aidocs.md file using:
    1. The EDITOR environment variable if set
    2. Platform-specific defaults (open on macOS, notepad on Windows)
    3. Common Linux editors (xdg-open, nano, vim, vi)
    
    Raises:
        SystemExit: If aidocs.md doesn't exist or no editor is found
    """
    real_file_path = os.path.join(project_path, REAL_FILENAME)
    if not os.path.exists(real_file_path):
        print(f"Error: {REAL_FILENAME} not found in {project_path}.")
        print("Please run 'aidocs init' first.")
        sys.exit(1)

    print(f"Opening {real_file_path} for editing...")
    editor = os.environ.get('EDITOR')
    if editor:
        cmd = [editor, real_file_path]
    elif sys.platform == 'darwin':
        cmd = ['open', '-W', '-t', real_file_path]
    elif sys.platform == 'win32':
        cmd = ['notepad', real_file_path]
    else:
        # Try to find a common editor on Linux
        for editor_name in ["xdg-open", "nano", "vim", "vi"]:
            try:
                process = subprocess.Popen([editor_name, real_file_path])
                process.wait()
                return # Exit after successful launch and wait
            except FileNotFoundError:
                continue
        print("Error: Could not find a default text editor. Please set your EDITOR environment variable.")
        sys.exit(1)
        return

    try:
        process = subprocess.Popen(cmd)
        process.wait()
    except FileNotFoundError:
        print(f"Error: Could not find editor: {cmd[0]}")
        sys.exit(1)

    print("\nFinished editing.")
    # Here is where you would add integration calls, e.g.:
    # print("Notifying other tools...")
    # subprocess.run(["gemini-cli", "--refresh-context", project_path])

def check(search_path):
    """
    Checks for aidocs.md and correct symlinks in git repositories.
    
    Args:
        search_path (str): Path to recursively search for git repositories
        
    Recursively searches the specified path for git repositories and reports:
    - Missing aidocs.md files
    - Missing symlinks (as defined in configuration)
    - Invalid symlinks (not pointing to aidocs.md)
    
    Provides a compliance report showing which repositories need attention.
    """
    print(f"Searching for git repositories in {search_path}...")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    symlinks_to_check = config.get("symlinks", [])

    found_repos = []
    for root, dirs, files in os.walk(search_path):
        if ".git" in dirs:
            found_repos.append(root)
            dirs.remove(".git")

    if not found_repos:
        print("No git repositories found.")
        return

    print(f"Found {len(found_repos)} git repositories.")
    all_compliant = True
    for repo_path in found_repos:
        real_file_path = os.path.join(repo_path, REAL_FILENAME)
        if not os.path.exists(real_file_path):
            all_compliant = False
            print(f"\n- Repository: {repo_path}")
            print(f"  Missing: {REAL_FILENAME}")
            continue

        missing_links = []
        invalid_links = []
        for link_name in symlinks_to_check:
            link_path = os.path.join(repo_path, link_name)
            if not os.path.lexists(link_path):
                missing_links.append(link_name)
            elif not os.path.islink(link_path) or os.readlink(link_path) != REAL_FILENAME:
                invalid_links.append(link_name)
        
        if missing_links or invalid_links:
            all_compliant = False
            print(f"\n- Repository: {repo_path}")
            if missing_links:
                print(f"  Missing symlinks: {', '.join(missing_links)}")
            if invalid_links:
                print(f"  Invalid symlinks: {', '.join(invalid_links)}")

    if all_compliant:
        print("\nAll repositories are compliant.")

def main():
    """
    Main function to parse commands and route to appropriate handlers.
    
    Parses command line arguments and executes the corresponding command:
    - setup: Initialize global configuration
    - init <path>: Initialize aidocs in a project
    - edit <path>: Edit project's aidocs.md file
    - check <path>: Check compliance across repositories
    
    Raises:
        SystemExit: On invalid commands or missing arguments
    """
    if len(sys.argv) < 2:
        print("Usage: aidocs <command> [args]")
        print("Commands:")
        print("  setup")
        print("  init <project_path>")
        print("  edit <project_path>")
        print("  check <search_path>")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "setup":
        setup()
    elif command == "init":
        if len(sys.argv) < 3:
            print("Error: init command requires a project_path argument.")
            sys.exit(1)
        project_path = sys.argv[2]
        init(project_path)
    elif command == "edit":
        if len(sys.argv) < 3:
            print("Error: edit command requires a project_path argument.")
            sys.exit(1)
        project_path = sys.argv[2]
        edit(project_path)
    elif command == "check":
        if len(sys.argv) < 3:
            print("Error: check command requires a search_path argument.")
            sys.exit(1)
        search_path = sys.argv[2]
        check(search_path)
    elif command == "help" or command == "--help" or command == "-h":
        print("Usage: aidocs <command> [args]")
        print("Commands:")
        print("  setup                  Initialize global configuration")
        print("  init <project_path>    Initialize aidocs in a project")
        print("  edit <project_path>    Edit aidocs.md in project")
        print("  check <search_path>    Check compliance recursively")
    else:
        print(f"Unknown command: {command}")
        print("Run 'aidocs help' for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()