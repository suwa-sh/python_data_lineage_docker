#!/usr/bin/env python3
import argparse
import csv
import os
import re
import sys
from typing import List, Tuple, Dict

try:
    import sqlparse
except ImportError:
    print("Error: sqlparse is not installed. Please install it using: pip install sqlparse")
    sys.exit(1)


def extract_table_name(sql: str, statement_type: str) -> str:
    """Extract table name from DELETE or TRUNCATE statement"""
    sql = sql.strip()
    
    if statement_type == "TRUNCATE":
        # Pattern: TRUNCATE TABLE [schema.]table_name
        match = re.search(r'TRUNCATE\s+TABLE\s+(?:(\w+)\.)?(\w+)', sql, re.IGNORECASE)
        if match:
            schema = match.group(1)
            table = match.group(2)
            return f"{schema}.{table}" if schema else table
    
    elif statement_type == "DELETE":
        # Pattern 1: DELETE FROM table_name
        match = re.search(r'DELETE\s+FROM\s+(?:(\w+)\.)?(\w+)', sql, re.IGNORECASE)
        if match:
            schema = match.group(1)
            table = match.group(2)
            return f"{schema}.{table}" if schema else table
        
        # Pattern 2: DELETE alias FROM table_name alias (SQL Server style)
        match = re.search(r'DELETE\s+\w+\s+FROM\s+(?:(\w+)\.)?(\w+)\s+\w+', sql, re.IGNORECASE)
        if match:
            schema = match.group(1)
            table = match.group(2)
            return f"{schema}.{table}" if schema else table
    
    return "UNKNOWN"


def extract_where_clause(sql: str) -> str:
    """Extract WHERE clause from DELETE statement"""
    # Find WHERE clause
    match = re.search(r'WHERE\s+(.+?)(?:;|$)', sql, re.IGNORECASE | re.DOTALL)
    if match:
        where_clause = match.group(1).strip()
        # Clean up whitespace
        where_clause = ' '.join(where_clause.split())
        return where_clause
    return "-"


def analyze_sql_file(file_path: str) -> List[Dict[str, str]]:
    """Analyze SQL file and extract DELETE/TRUNCATE statements"""
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse SQL statements
    statements = sqlparse.split(content)
    
    for statement in statements:
        if not statement.strip():
            continue
        
        # Format statement
        formatted = sqlparse.format(statement, strip_comments=True).strip()
        if not formatted:
            continue
        
        # Check if it's DELETE or TRUNCATE
        upper_sql = formatted.upper()
        
        if upper_sql.startswith('DELETE'):
            table_name = extract_table_name(formatted, 'DELETE')
            where_clause = extract_where_clause(formatted)
            results.append({
                'file': os.path.basename(file_path),
                'operation': 'delete',
                'table': table_name,
                'condition': where_clause
            })
        
        elif upper_sql.startswith('TRUNCATE'):
            table_name = extract_table_name(formatted, 'TRUNCATE')
            results.append({
                'file': os.path.basename(file_path),
                'operation': 'truncate',
                'table': table_name,
                'condition': '-'
            })
    
    return results


def write_csv(results: List[Dict[str, str]], output_path: str):
    """Write results to CSV file"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ファイル', 'delete/truncate', 'テーブル', '条件'])
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'ファイル': result['file'],
                'delete/truncate': result['operation'],
                'テーブル': result['table'],
                '条件': result['condition']
            })


def main():
    parser = argparse.ArgumentParser(description='Extract DELETE and TRUNCATE statements from SQL file')
    parser.add_argument('sql_file', help='Path to SQL file')
    parser.add_argument('--output', '-o', help='Output directory (default: current directory)', default='.')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.sql_file):
        print(f"Error: File '{args.sql_file}' not found")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Analyze SQL file
    results = analyze_sql_file(args.sql_file)
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(args.sql_file))[0]
    output_file = os.path.join(args.output, f"{base_name}_delete.csv")
    
    # Write results to CSV
    write_csv(results, output_file)
    
    print(f"Analysis complete. Results written to: {output_file}")
    print(f"Found {len(results)} DELETE/TRUNCATE statements")


if __name__ == '__main__':
    main()