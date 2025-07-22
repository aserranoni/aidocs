# aidocs

A CLI tool for managing AI assistant context documentation across development projects.

## Overview

`aidocs` helps developers maintain consistent documentation for AI assistants (like Claude, Gemini, ChatGPT, etc.) across multiple projects. It creates a single source of truth (`aidocs.md`) and automatically manages symlinks to AI-specific files like `CLAUDE.md`, `GEMINI.md`, etc.

## Features

- **Single Source of Truth**: Maintain one `aidocs.md` file per project
- **Automatic Symlinks**: Creates and manages symlinks to AI-specific documentation files
- **Project Discovery**: Find and audit all git repositories for compliance
- **Cross-Platform**: Works on macOS, Windows, and Linux
- **Template System**: Customizable templates for new projects

## Installation

```bash
pip install aidocs
```

## Quick Start

1. **Initial Setup**: Configure aidocs globally
   ```bash
   aidocs setup
   ```

2. **Initialize a Project**: Set up aidocs in your project directory
   ```bash
   cd /path/to/your/project
   aidocs init .
   ```

3. **Edit Documentation**: Open the documentation file for editing
   ```bash
   aidocs edit .
   ```

4. **Check Compliance**: Audit multiple projects for aidocs compliance
   ```bash
   aidocs check /path/to/search
   ```

## Commands

### `aidocs setup`
Initializes the global aidocs configuration directory at `~/.aidocs/` with:
- `config.json`: Configuration file specifying which symlinks to create
- `template.md`: Default template for new `aidocs.md` files

### `aidocs init <project_path>`
Initializes aidocs in a specific project by:
- Creating `aidocs.md` from the template (or preserving existing content)
- Consolidating content from existing AI documentation files
- Creating symlinks as specified in the configuration
- Removing the original files after consolidation

### `aidocs edit <project_path>`
Opens the `aidocs.md` file in your default editor. Respects the `EDITOR` environment variable, with platform-specific fallbacks.

### `aidocs check <search_path>`
Recursively searches for git repositories and reports:
- Missing `aidocs.md` files
- Missing or incorrect symlinks
- Overall compliance status

## Configuration

The global configuration is stored in `~/.aidocs/config.json`:

```json
{
    "symlinks": ["GEMINI.md", "CLAUDE.md"]
}
```

You can customize which symlinks are created by editing this file.

## How It Works

1. **Template**: A master template is stored in `~/.aidocs/template.md`
2. **Real File**: Each project has one `aidocs.md` file containing all documentation
3. **Symlinks**: AI-specific files (like `CLAUDE.md`) are symlinks pointing to `aidocs.md`
4. **Consolidation**: When initializing, existing AI documentation files are merged into `aidocs.md`

## Example Workflow

```bash
# One-time setup
aidocs setup

# For each new project
cd my-awesome-project
aidocs init .

# Edit documentation as needed
aidocs edit .

# Verify compliance across all projects
aidocs check ~/dev
```

## File Structure After Initialization

```
my-project/
├── aidocs.md          # The real documentation file
├── CLAUDE.md -> aidocs.md    # Symlink for Claude
├── GEMINI.md -> aidocs.md    # Symlink for Gemini
└── ... (your project files)
```

## Benefits

- **Consistency**: Same documentation visible to all AI assistants
- **Maintenance**: Update once, applies everywhere
- **Discovery**: Easy auditing of documentation across projects
- **Flexibility**: Customizable templates and symlink configurations
- **Safety**: Preserves existing documentation during migration

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)

## Development

```bash
# Clone the repository
git clone https://github.com/arielserranoni/aidocs.git
cd aidocs

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.