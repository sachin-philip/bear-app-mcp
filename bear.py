import sqlite3
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("bear-app-mcp")


def get_bear_database_path():
    """Get the path to Bear's SQLite database."""
    home = os.path.expanduser("~")
    return os.path.join(
        home,
        "Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
    )


@mcp.tool()
async def get_list_of_notes(number_of_notes: int) -> str:
    """Get latest list of notes from the bear app, sorted by updated date.

    Args:
        number_of_notes: Number of notes to return
    """
    db_path = get_bear_database_path()
    if not os.path.exists(db_path):
        return "Error: Bear database not found. Make sure Bear is installed and you're on macOS."

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query to get notes sorted by modification date
        query = """
        SELECT ZTITLE, ZMODIFICATIONDATE
        FROM ZSFNOTE
        WHERE ZTRASHED = 0
        ORDER BY ZMODIFICATIONDATE DESC
        LIMIT ?
        """
        
        cursor.execute(query, (number_of_notes,))
        notes = cursor.fetchall()
        
        result = []
        for title, timestamp in notes:
            # Convert timestamp to readable date
            date = datetime.fromtimestamp(timestamp + 978307200)  # Apple's timestamp adjustment
            result.append(f"{title} (Updated: {date.strftime('%Y-%m-%d %H:%M:%S')})")
        
        conn.close()
        return "\n".join(result) if result else "No notes found."
        
    except sqlite3.Error as e:
        return f"Error accessing Bear database: {str(e)}"


@mcp.tool()
async def get_notes_by_tag(tag: str) -> str:
    """Get all notes that have a specific tag.

    Args:
        tag: The tag to filter notes by (e.g. '#work', '#project')
    """
    db_path = get_bear_database_path()
    if not os.path.exists(db_path):
        return "Error: Bear database not found. Make sure Bear is installed and you're on macOS."

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query to get notes with a specific tag
        query = """
        SELECT DISTINCT n.ZTITLE, n.ZMODIFICATIONDATE
        FROM ZSFNOTE n
        JOIN Z_5TAGS t ON n.Z_PK = t.Z_5NOTES
        JOIN ZSFNOTETAG tag ON t.Z_13TAGS = tag.Z_PK
        WHERE n.ZTRASHED = 0
        AND tag.ZTITLE = ?
        ORDER BY n.ZMODIFICATIONDATE DESC
        """
        
        cursor.execute(query, (tag,))
        notes = cursor.fetchall()
        
        result = []
        for title, timestamp in notes:
            # Convert timestamp to readable date
            date = datetime.fromtimestamp(timestamp + 978307200)  # Apple's timestamp adjustment
            result.append(f"{title} (Updated: {date.strftime('%Y-%m-%d %H:%M:%S')})")
        
        conn.close()
        return "\n".join(result) if result else f"No notes found with tag '{tag}'"
        
    except sqlite3.Error as e:
        return f"Error accessing Bear database: {str(e)}"


@mcp.tool()
async def get_note_summary(note_title: str) -> str:
    """Get the content of a specific note by its title.

    Args:
        note_title: The title of the note to retrieve
    """
    db_path = get_bear_database_path()
    if not os.path.exists(db_path):
        return "Error: Bear database not found. Make sure Bear is installed and you're on macOS."

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query to get note content
        query = """
        SELECT ZTEXT, ZMODIFICATIONDATE
        FROM ZSFNOTE
        WHERE ZTITLE = ?
        AND ZTRASHED = 0
        """
        
        cursor.execute(query, (note_title,))
        note = cursor.fetchone()
        
        if note:
            content, timestamp = note
            date = datetime.fromtimestamp(timestamp + 978307200)  # Apple's timestamp adjustment
            
            # Get the first few lines of the content as a summary
            summary = content.split('\n')[:5]  # Get first 5 lines
            summary_text = '\n'.join(summary)
            
            return f"Note: {note_title}\nLast Updated: {date.strftime('%Y-%m-%d %H:%M:%S')}\n\nContent Preview:\n{summary_text}"
        else:
            return f"No note found with title '{note_title}'"
        
    except sqlite3.Error as e:
        return f"Error accessing Bear database: {str(e)}"


# TODO: Add this back in
# @mcp.tool()
# async def create_note(title: str, content: str, tags: list[str] = None) -> str:
#     """Create a new note in Bear with markdown formatting.

#     Args:
#         title: The title of the new note
#         content: The content of the note in markdown format
#         tags: Optional list of tags to add to the note (e.g. ['#work', '#project'])
#     """
#     db_path = get_bear_database_path()
#     if not os.path.exists(db_path):
#         return "Error: Bear database not found. Make sure Bear is installed and you're on macOS."

#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
        
#         # Get current timestamp (Apple's timestamp format)
#         current_time = int(datetime.now().timestamp() - 978307200)
        
#         # Insert new note
#         cursor.execute("""
#         INSERT INTO ZSFNOTE (
#             ZTITLE, ZTEXT, ZMODIFICATIONDATE, ZCREATIONDATE,
#             ZTRASHED, ZARCHIVED, ZENCRYPTED, ZPINNED
#         ) VALUES (?, ?, ?, ?, 0, 0, 0, 0)
#         """, (title, content, current_time, current_time))
        
#         note_id = cursor.lastrowid
        
#         # Add tags if provided
#         if tags:
#             for tag in tags:
#                 # Check if tag exists
#                 cursor.execute("SELECT Z_PK FROM ZSFNOTETAG WHERE ZTITLE = ?", (tag,))
#                 tag_row = cursor.fetchone()
                
#                 if tag_row:
#                     tag_id = tag_row[0]
#                 else:
#                     # Create new tag if it doesn't exist
#                     cursor.execute("""
#                     INSERT INTO ZSFNOTETAG (ZTITLE, ZMODIFICATIONDATE)
#                     VALUES (?, ?)
#                     """, (tag, current_time))
#                     tag_id = cursor.lastrowid
                
#                 # Link note to tag
#                 cursor.execute("""
#                 INSERT INTO Z_5TAGS (Z_5NOTES, Z_13TAGS)
#                 VALUES (?, ?)
#                 """, (note_id, tag_id))
        
#         conn.commit()
#         conn.close()
        
#         return f"Successfully created note: {title}"
        
#     except sqlite3.Error as e:
#         return f"Error creating note: {str(e)}"


@mcp.tool()
async def delete_note(note_title: str) -> str:
    """Delete a specific note from Bear by marking it as trashed.

    Args:
        note_title: The title of the note to delete
    """
    db_path = get_bear_database_path()
    if not os.path.exists(db_path):
        return "Error: Bear database not found. Make sure Bear is installed and you're on macOS."

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current timestamp (Apple's timestamp format)
        current_time = int(datetime.now().timestamp() - 978307200)
        
        # Update note to mark it as trashed
        cursor.execute("""
        UPDATE ZSFNOTE
        SET ZTRASHED = 1, ZMODIFICATIONDATE = ?
        WHERE ZTITLE = ? AND ZTRASHED = 0
        """, (current_time, note_title))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return f"Successfully deleted note: {note_title}"
        else:
            conn.close()
            return f"No note found with title '{note_title}' or it was already deleted"
        
    except sqlite3.Error as e:
        return f"Error deleting note: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
