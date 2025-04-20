# Bear App MCP

A Python-based MCP (Machine Control Protocol) interface for Bear, the beautiful, flexible writing app for notes and prose.

## Features

This MCP provides the following tools to interact with Bear:

1. **Get List of Notes**
   - Retrieve the latest notes sorted by update date
   - Specify the number of notes to return
   - Returns note titles with their last update timestamps

2. **Get Notes by Tag**
   - Filter notes by a specific tag
   - Returns all notes with the specified tag, sorted by update date
   - Tags should include the '#' prefix (e.g., '#work')

3. **Get Note Summary**
   - Retrieve the content of a specific note by title
   - Returns the first 5 lines of the note's content
   - Includes the note's last update timestamp

4. **Delete Note**
   - Delete a specific note by title
   - Marks the note as trashed in Bear
   - Returns success/failure message

## Prerequisites

1. Python 3.11
2. Install UV `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Install Dependancy `uv activate && uv install`


### MCP Server Configuration

Add the following to your MCP config:

```jsonc
{
  "mcpServers": {
    "Raindrop": {
      "command": "uv",
      "args": [
        "--directory",
        "<location to project clone>",
        "run",
        "bear.py"
      ],
      "env": {
      }
    }
  }
}
```

## License

MIT License - See LICENSE file for details
