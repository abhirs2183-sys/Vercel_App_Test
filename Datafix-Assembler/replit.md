# yDatafix - SQL Datafix Package Maker

## Overview
A professional web-based SQL datafix package maker for MS SQL Server and Yardi systems. The application processes .pkg files (plain text format) through a drag-and-drop interface, automatically generating backup queries (DataFixHistory inserts for UPDATE queries, backup tables for DELETE queries), and outputs formatted .pkg files with proper notes sections.

## Current State
- Fully functional Flask web application
- SQL processor handles UPDATE, DELETE, and EXEC queries
- Frontend with dark/light mode theme toggle
- SEO optimized for "yardi sql datafix package maker/generator/creator"

## Project Architecture

### File Structure
```
├── app.py                 # Flask app initialization
├── main.py                # Entry point for gunicorn
├── routes.py              # API routes (upload, feedback)
├── sql_processor.py       # Main SQL query processor
├── case_processor.py      # CASE statement edge case handler
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/styles.css     # All styles (dark/light mode)
│   ├── js/main.js         # Frontend JavaScript
│   └── images/logo.png    # yDatafix logo
├── design_guidelines.md   # UI/UX design specifications
└── feedback.txt           # Feedback storage fallback
```

### Key Features
1. **Drag-and-drop file upload** - Accept .pkg files only
2. **DataFixHistory generation** - Automatic backup INSERT statements
3. **DELETE backup tables** - Creates `tablename_caseid` backup tables
4. **Multi-column UPDATE handling** - Separate DataFixHistory INSERT per column
5. **Theme toggle** - Dark/light mode with localStorage persistence
6. **Feedback system** - Email with file fallback

## Technical Details

### SQL Processing Rules
- DataFixHistory: hycrm IN QUOTES, sTableName in quotes, hForeignKey UNQUOTED
- Foreign key column: `hmyperson` for tenant table, `hmy` for all others
- DELETE queries create both DataFixHistory INSERT and backup table
- Backup table naming: `tablename_caseid`, `tablename_1_caseid` for sequential deletes
- Preserve WHERE clauses exactly - no merging/combining
- Preserve SQL expressions and subqueries as-is

### Input Format
```
Created by: Name
Case#: 12345678
Client Pin: 100067837
Client Name: Company Name
Database: username password dbserver dbname

update tablename set column = value where condition
delete from tablename where condition
exec StoredProcedure param
```

### Output Format
- Filename: `Case#<caseid>#Datafix.pkg`
- Notes section with aligned colons
- DataFixHistory table creation
- DataFixHistory INSERT for each UPDATE column
- DataFixHistory INSERT + backup SELECT INTO for each DELETE
- Original queries preserved at bottom
- Date in MM/DD/YYYY format (IST timezone)

## User Preferences
- Field labeled "User Name" (two words with space)
- Frontend must match provided screenshots exactly
- Color scheme: Cyan (#00d4ff), Navy (#0a1929), Yellow (#ffc107)

## Recent Changes
- 2025-12-10: Initial implementation completed
  - Flask app with routes for upload and feedback
  - SQL processor with UPDATE/DELETE/EXEC handling
  - Frontend matching design screenshots
  - Dark/light mode theme support
