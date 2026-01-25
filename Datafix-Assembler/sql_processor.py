import re
from datetime import datetime
import pytz

import os  #edited


def log_usage(created_by, case_id):  #edited
    os.makedirs("logs", exist_ok=True)  #edited
    #edited
    with open("logs/usage.txt", "a", encoding="utf-8") as f:  #edited
        f.write(  #edited
            f"{datetime.now()} | Created By: {created_by} | Case#: {case_id}\n"
        )  #edited

def split_where_clause(s):
    result = []
    token = ""

    in_quotes = False
    bracket_depth = 0

    for ch in s:
        # Handle quotes (only outside brackets)
        if ch == '"' and bracket_depth == 0:
            if(not in_quotes and token):
                result.append(token)
                token = ""
            in_quotes = not in_quotes
            token += ch

            # quote just CLOSED → flush token
            if not in_quotes:
                result.append(token)
                token = ""
            continue

        # Handle opening bracket
        if ch == '[' and not in_quotes:
            if(bracket_depth == 0 and token):
                result.append(token)
                token = ""
            bracket_depth += 1
            token += ch
            continue

        # Handle closing bracket
        if ch == ']' and not in_quotes:
            bracket_depth -= 1
            token += ch

            # outermost bracket just CLOSED → flush token
            if bracket_depth == 0:
                result.append(token)
                token = ""
            continue

        # Space splits only when fully free
        if ch == ' ' and not in_quotes and bracket_depth == 0:
            if token:
                result.append(token)
                token = ""
        else:
            token += ch

    # Safety flush
    if token:
        result.append(token)

    return result

def process_pkg_file(content):
    lines = content.strip().split('\n')

    metadata = parse_metadata(lines)
    if 'error' in metadata:
        return metadata
    #log_usage(metadata['created_by'], metadata['case_id'])  #edited
    sql_queries = extract_sql_queries(lines)
    if not sql_queries[0]:
        return {'error': 'No SQL queries found in the file'}

    output = generate_output(metadata, sql_queries)

    return {
        'filename': f"Case#{metadata['case_id']}#Datafix.pkg",
        'content': output,
        'case_id': metadata['case_id'],
        'created_by': metadata['created_by']
    }


def parse_metadata(lines):
    metadata = {
        'created_by': '',
        'case_id': '',
        'client_pin': '',
        'client_name': '',
        'username': '',
        'password': '',
        'db_server': '',
        'db_name': ''
    }

    db_parts = ''

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        line_lower = line_stripped.lower()

        if line_lower.startswith('created by:') or line_lower.startswith(
                'created by :'):
            metadata['created_by'] = extract_value(line_stripped)
        elif line_lower.startswith('case#:') or line_lower.startswith(
                'case# :') or line_lower.startswith('case #:'):
            metadata['case_id'] = extract_value(line_stripped)
        elif line_lower.startswith('client pin:') or line_lower.startswith(
                'client pin :'):
            metadata['client_pin'] = extract_value(line_stripped)
        elif line_lower.startswith('client name:') or line_lower.startswith(
                'client name :'):
            metadata['client_name'] = extract_value(line_stripped)
        elif line_lower.startswith('database:') or line_lower.startswith(
                'database :'):
            db_parts = extract_value(line_stripped).split()
            if len(db_parts) >= 4:
                metadata['username'] = db_parts[0]
                metadata['password'] = db_parts[1]
                metadata['db_server'] = db_parts[2]
                metadata['db_name'] = db_parts[3] if len(
                    db_parts) > 3 else db_parts[2]
            elif len(db_parts) >= 1:
                metadata['db_name'] = db_parts[0]

    if not metadata['case_id']:
        return {'error': 'Case ID not found in the input file'}
    if not metadata['created_by']:
        return {'error': 'Created By not found in the input file'}
    if not metadata['client_pin']:
        return {'error': 'Client Pin not found in the input file'}
    if not metadata['client_name']:
        return {'error': 'Client Name not found in the input file'}
    if len(db_parts) != 4:
        return {'error': 'Incomplete/Missing DB Credentials'}

    return metadata


def extract_value(line):
    if ':' in line:
        return line.split(':', 1)[1].strip()
    return ''


def extract_sql_queries(lines):
    queries = []
    current_query_lines = []
    in_query = False
    blank_pos_set = {-1}
    first_query_pos = -1

    metadata_prefixes = [
        'created by', 'case#', 'case #', 'client pin', 'client name',
        'database:'
    ]

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if (first_query_pos == -1 and in_query):
            first_query_pos = i - 1
        if (line_lower == '' and first_query_pos != -1):
            blank_pos_set.add(i - first_query_pos)

        is_metadata = any(
            line_lower.startswith(prefix) for prefix in metadata_prefixes)
        if is_metadata:
            continue

        if is_sql_statement_start(line_stripped):
            if current_query_lines:
                query_text = '\n'.join(current_query_lines).strip()
                if query_text:
                    queries.append(query_text)
                current_query_lines = []
            current_query_lines.append(line_stripped)
            in_query = True
        elif in_query and line_stripped:
            current_query_lines.append(line_stripped)

    if current_query_lines:
        query_text = '\n'.join(current_query_lines).strip()
        if query_text:
            queries.append(query_text)

    return queries, blank_pos_set


def is_sql_statement_start(line):
    line_lower = line.lower()
    sql_keywords = ['update ', 'delete ', 'exec ', 'execute ']
    return any(line_lower.startswith(kw) for kw in sql_keywords)


def generate_output(metadata, sql_queries):
    ist = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist).strftime('%m/%d/%Y')

    output_lines = []

    output_lines.append('//Notes')
    output_lines.append(f"Client Pin     : {metadata['client_pin']}")
    output_lines.append(f"Client Name    : {metadata['client_name']}")
    output_lines.append(f"User Name      : {metadata['username']}")
    output_lines.append(f"Password       : {metadata['password']}")
    output_lines.append(f"DB Server      : {metadata['db_server']}")
    output_lines.append(f"Instance       : {metadata['db_server']}")
    output_lines.append(f"DB Name        : {metadata['db_name']}")
    output_lines.append('')
    output_lines.append('')
    #output_lines.append('')
    #output_lines.append('')
    #output_lines.append('')
    #output_lines.append('')
    #output_lines.append(f"Created By        : {metadata['created_by']}")
    #output_lines.append(f"Date              : {current_date}")
    #output_lines.append(f"Case#             : {metadata['case_id']}")
    output_lines.append(f"Created By     : {metadata['created_by']}")  #edited
    output_lines.append(f"Date           : {current_date}")  #edited
    output_lines.append(f"Case#          : {metadata['case_id']}")  #edited
    output_lines.append('//End Notes')
    output_lines.append('')
    output_lines.append('')
    output_lines.append('//SQL')
    output_lines.append('GO')
    output_lines.append(
        "If Not Exists (Select Name From SysObjects Where Name = 'DataFixHistory')"
    )
    output_lines.append('        Create Table DataFixHistory')
    output_lines.append('        (')
    output_lines.append(
        '                hMy NUMERIC(18,0) IDENTITY(1,1) Not Null,')
    output_lines.append('                hyCRM NUMERIC (18,0) Not Null,')
    output_lines.append('                sTableName VARCHAR(400) Not Null,')
    output_lines.append('                sColumnName VARCHAR(400) Not Null,')
    output_lines.append('                hForeignKey NUMERIC(18,0) Not Null,')
    output_lines.append('                sNotes VarChar(2000) Not Null,')
    output_lines.append('                sNewValue VARCHAR(100),')
    output_lines.append('                sOldValue VARCHAR(100),')
    output_lines.append('                dtDate DATETIME')
    output_lines.append('        )')
    output_lines.append(
        "Else If Not Exists (Select * From INFORMATION_SCHEMA.COLUMNS Where Table_Name = 'DataFixHistory' and Column_Name = 'sColumnName')"
    )
    output_lines.append(
        '        Alter Table DataFixHistory Add sColumnName VARCHAR(400) Null')
    output_lines.append('')

    delete_table_counts = {}

    for query in sql_queries[0]:
        query_type = get_query_type(query)

        if query_type == 'UPDATE':
            backup_statements = generate_update_backup(query,
                                                       metadata['case_id'])
            for stmt in backup_statements:
                output_lines.append('GO')
                output_lines.append(stmt)
                output_lines.append('')
        elif query_type == 'DELETE':
            table_name = extract_table_from_delete(query)
            if table_name:
                count = delete_table_counts.get(table_name.lower(), 0)
                backup_statements = generate_delete_backup(
                    query, metadata['case_id'], table_name, count)
                delete_table_counts[table_name.lower()] = count + 1
                for stmt in backup_statements:
                    output_lines.append('GO')
                    output_lines.append(stmt)
                    output_lines.append('')

    output_lines.append('GO')
    query_pos = 0
    for query in sql_queries[0]:

        while (query_pos in sql_queries[1]):
            output_lines.append('')
            query_pos += 1

        output_lines.append(query)
        query_pos += 1

    output_lines.append('Go')
    output_lines.append('//End SQL')

    return '\n'.join(output_lines)


def get_query_type(query):
    query_lower = query.strip().lower()
    if query_lower.startswith('update '):
        return 'UPDATE'
    elif query_lower.startswith('delete '):
        return 'DELETE'
    elif query_lower.startswith('exec ') or query_lower.startswith('execute '):
        return 'EXEC'
    return 'UNKNOWN'


def generate_update_backup(query, case_id):
    statements = []

    table_info = extract_update_table_info(query)
    if not table_info:
        return statements

    table_name = table_info['table_name']
    set_clause = table_info['set_clause']
    where_clause = table_info['where_clause']

    column_updates = parse_set_clause(set_clause)

    fk_column = get_foreign_key_column(table_name)
    
    if (where_clause[0] == 'f' or where_clause[0] == 'F'):
        where_list = where_clause.lower()
        where_list = split_where_clause(where_list)
        tbn = table_name.lower()
        index = where_list.index(tbn)
        ln = len(where_list)
        alias_name = tbn
        if (index + 2 < ln and where_list[index + 1] == 'as'):
            alias_name = where_list[index + 2]
        elif (index + 1 < ln and where_list[index + 1] != 'on' and where_list[index + 1] != 'inner' and where_list[index + 1] != 'left' and where_list[index + 1] != 'right' and where_list[index + 1] != 'outer' and where_list[index + 1] != 'join' and where_list[index + 1] != 'full' and where_list[index + 1] != 'from' and where_list[index + 1] != 'where'):
            alias_name = where_list[index + 1]
        if(where_clause and ('join' in where_clause)):
            fk_column = f"{alias_name}.{fk_column}"

    for col_name, new_value in column_updates:
        col_name_ = col_name.split(".")[-1] if "." in col_name else col_name
        stmt = f"Insert into DatafixHistory (hycrm, sTableName, sColumnName, hForeignKey, sNotes, sNewValue, sOldValue, dtdate)\n"
        stmt += f"(Select '{case_id}', '{table_name}', '{col_name_}', {fk_column}, 'Updating {col_name_}', {new_value}, {col_name}, getdate() \n"
        
        if(where_clause and where_clause[0] != 'f' and where_clause[0] != 'F'):
            stmt += f"from {table_name}"
        if where_clause:
            stmt += f" {where_clause}"
        stmt += "\n)"

        statements.append(stmt)

    return statements


# def extract_update_table_info(query):
#     query_single = ' '.join(query.split())

#     where_match = re.search(r'\s+(where\s+.+)$', query_single, re.IGNORECASE)
#     where_clause = where_match.group(1).strip() if where_match else ''

#     if where_clause:
#         query_without_where = query_single[:where_match.start()].strip()
#     else:
#         query_without_where = query_single

#     set_match = re.search(r'update\s+(\w+)\s+set\s+(.+)$', query_without_where,
#                           re.IGNORECASE)
#     if set_match:
#         return {
#             'table_name': set_match.group(1),
#             'set_clause': set_match.group(2).strip(),
#             'where_clause': where_clause
#         }

#     return None


def extract_update_table_info(query):
    query_single = ' '.join(query.split())

    # --- 1. locate UPDATE <table> SET ---
    m = re.search(r'update\s+(\w+)\s+set\s+', query_single, re.IGNORECASE)
    if not m:
        return None

    table_name = m.group(1)
    set_start = m.end()

    # --- 2. find FROM or WHERE at depth 0 ---
    depth = 0
    from_pos = None
    where_pos = None

    for i in range(set_start, len(query_single)):
        c = query_single[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0:
            if query_single[i:i + 5].lower() == 'from ':
                from_pos = i
                break
            elif query_single[i:i + 6].lower() == 'where ':
                where_pos = i
                break

    if from_pos is not None:
        set_clause = query_single[set_start:from_pos].strip()
        where_clause = query_single[from_pos:].strip()

        where_clause_list = where_clause.lower()
        where_clause_list = split_where_clause(where_clause_list)
        tn = table_name.lower()
        if tn in where_clause_list:
            index = where_clause_list.index(tn)
            if (index > 0 and where_clause_list[index - 1] != 'join'
                    and where_clause_list[index - 1] != 'from'):
                if (where_clause_list[index - 1] == 'as' and index > 1):
                    table_name = where_clause_list[index - 2]
                elif (where_clause_list[index - 1] != 'as'):
                    table_name = where_clause_list[index - 1]

    elif where_pos is not None:
        set_clause = query_single[set_start:where_pos].strip()
        where_clause = query_single[where_pos:].strip()
    else:
        set_clause = query_single[set_start:].strip()
        where_clause = ''

    return {
        'table_name': table_name,
        'set_clause': set_clause,
        'where_clause': where_clause
    }


def parse_set_clause(set_clause):
    updates = []
    parts = smart_split_set_clause(set_clause)

    for part in parts:
        part = part.strip()
        if '=' in part:
            eq_pos = find_first_equals(part)
            if eq_pos > 0:
                col_name = part[:eq_pos].strip()
                new_value = part[eq_pos + 1:].strip()
                updates.append((col_name, new_value))
    return updates


def find_first_equals(s):
    for i, char in enumerate(s):
        if char == '=':
            if i > 0 and s[i - 1] in '<>!':
                continue
            if i < len(s) - 1 and s[i + 1] == '=':
                continue
            return i
    return -1


def smart_split_set_clause(set_clause):
    parts = []
    current = []
    paren_depth = 0
    in_string = False
    string_char = None

    i = 0
    while i < len(set_clause):
        char = set_clause[i]

        if not in_string and char in ("'", '"'):
            in_string = True
            string_char = char
            current.append(char)
        elif in_string and char == string_char:
            in_string = False
            string_char = None
            current.append(char)
        elif not in_string and char == '(':
            paren_depth += 1
            current.append(char)
        elif not in_string and char == ')':
            paren_depth -= 1
            current.append(char)
        elif char == ',' and paren_depth == 0 and not in_string:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)

        i += 1

    if current:
        parts.append(''.join(current))

    return parts


def get_foreign_key_column(table_name):
    table_lower = table_name.lower()
    if table_lower == 'tenant' or table_lower == 'vendor':
        return 'hmyperson'
    return 'hmy'


def generate_delete_backup(query, case_id, table_name, count):
    statements = []
    Trd_word_from = False
    
    where_match = re.search(r'\bfrom\b.*$', query, re.IGNORECASE | re.DOTALL)
    where_clause = where_match.group(0) if where_match else ''

    fk_column = get_foreign_key_column(table_name)
    alias_name = table_name
    if (where_clause[0] == 'f' or where_clause[0] == 'F'):
        where_list = where_clause.lower()
        where_list = split_where_clause(where_list)
        if(where_list[2] == 'from'):
            where_list = where_list[2:]
            Trd_word_from = True
            
        tbn = table_name.lower()
        index = where_list.index(tbn)
        ln = len(where_list)
        alias_name = tbn
        if (index + 2 < ln and where_list[index + 1] == 'as'):
            alias_name = where_list[index + 2]
        elif (index + 1 < ln and where_list[index + 1] != 'on' and where_list[index + 1] != 'inner' and where_list[index + 1] != 'left' and where_list[index + 1] != 'right' and where_list[index + 1] != 'outer' and where_list[index + 1] != 'join' and where_list[index + 1] != 'full' and where_list[index + 1] != 'where' and where_list[index + 1] != 'from'):
            alias_name = where_list[index + 1]
        if(where_clause and ('join' in where_clause)):
            fk_column = f"{alias_name}.{fk_column}"

    stmt = f"Insert into DatafixHistory (hycrm, sTableName, sColumnName, hForeignKey, sNotes, sNewValue, sOldValue, dtdate)\n"
    stmt += f"(Select '{case_id}', '{table_name}','',{fk_column}, 'Deleting records','','', getdate() \n"
    if where_clause:
        if(Trd_word_from):
            where_list = where_clause.lower()
            where_list = split_where_clause(where_list)
            where_list = where_list[2:]
            result = " ".join(where_list)
            stmt += f" {result}"
        else:
            stmt += f" {where_clause}"
    stmt += "\n)"
    statements.append(stmt)

    if count == 0:
        backup_table = f"{table_name}_{case_id}"
    else:
        backup_table = f"{table_name}_{count}_{case_id}"
        
    if(where_clause and ('join' in where_clause)):
        backup_stmt = f"select {alias_name}.* into {backup_table}"
    else:
        backup_stmt = f"select * into {backup_table}"
        
    if where_clause:
        if(Trd_word_from):
            where_list = where_clause.lower()
            where_list = split_where_clause(where_list)
            where_list = where_list[2:]
            result = " ".join(where_list)
            backup_stmt += f" {result}"
        else:
            backup_stmt += f" {where_clause}"
    statements.append(backup_stmt)

    return statements


def extract_table_from_delete(query):
    pattern = r'delete\s+(?:from\s+)?(\w+)'
    match = re.search(pattern, query, re.IGNORECASE)
    table_name = ''
    if match:
        table_name = match.group(1)
    else:
        table_name = ''
        
    where_match = re.search(r'\bfrom\b.*$', query, re.IGNORECASE | re.DOTALL)
    where_clause = where_match.group(0) if where_match else ''

    where_clause_list = where_clause.lower()
    where_clause_list = split_where_clause(where_clause_list)
    if(where_clause_list[2] == 'from'):
        where_clause_list = where_clause_list[2:]        
    tn = table_name.lower()
    if tn in where_clause_list:
        index = where_clause_list.index(tn)
        if (index > 0 and where_clause_list[index - 1] != 'join'
                and where_clause_list[index - 1] != 'from'):
            if (where_clause_list[index - 1] == 'as' and index > 1):
                table_name = where_clause_list[index - 2]
            elif (where_clause_list[index - 1] != 'as'):
                table_name = where_clause_list[index - 1]

    if match:
        return table_name
    return None