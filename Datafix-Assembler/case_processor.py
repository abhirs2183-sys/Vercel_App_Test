"""
CASE statement processor module for SQL datafix packages.
Handles edge cases with CASE WHEN expressions in UPDATE SET clauses.
"""
import re

def process_case_statement(value_expression):
    """
    Process a CASE statement expression and return it as-is.
    CASE statements should be preserved exactly without evaluation.
    """
    return value_expression

def contains_case_statement(expression):
    """
    Check if an expression contains a CASE statement.
    """
    return bool(re.search(r'\bCASE\b', expression, re.IGNORECASE))

def extract_case_columns(case_expression):
    """
    Extract column names referenced in a CASE expression.
    This is useful for understanding dependencies.
    """
    columns = []
    
    when_pattern = r'WHEN\s+(\w+)'
    columns.extend(re.findall(when_pattern, case_expression, re.IGNORECASE))
    
    then_pattern = r'THEN\s+(\w+)'
    columns.extend(re.findall(then_pattern, case_expression, re.IGNORECASE))
    
    else_pattern = r'ELSE\s+(\w+)'
    columns.extend(re.findall(else_pattern, case_expression, re.IGNORECASE))
    
    keywords = {'case', 'when', 'then', 'else', 'end', 'null', 'and', 'or', 'not', 'is', 'in', 'like'}
    columns = [c for c in columns if c.lower() not in keywords]
    
    return list(set(columns))

def validate_case_syntax(case_expression):
    """
    Basic validation of CASE statement syntax.
    Returns True if syntax appears valid, False otherwise.
    """
    case_count = len(re.findall(r'\bCASE\b', case_expression, re.IGNORECASE))
    end_count = len(re.findall(r'\bEND\b', case_expression, re.IGNORECASE))
    
    if case_count != end_count:
        return False
    
    if not re.search(r'\bWHEN\b', case_expression, re.IGNORECASE):
        return False
    
    if not re.search(r'\bTHEN\b', case_expression, re.IGNORECASE):
        return False
    
    return True

def format_case_for_backup(case_expression, column_name):
    """
    Format a CASE expression for use in DataFixHistory backup.
    The expression is used as sNewValue, preserving the SQL expression.
    """
    return case_expression
