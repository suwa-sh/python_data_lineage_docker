#!/usr/bin/env python3
import argparse
import os
import re
import sys
from typing import List, Tuple, Dict
from collections import OrderedDict

try:
    import sqlparse
    from sqlparse import sql, tokens as T
except ImportError:
    print("Error: sqlparse is not installed. Please install it using: pip install sqlparse")
    sys.exit(1)


class SQLSplitter:
    def __init__(self):
        self.ddl_statements = []
        self.cte_statements = []
        self.temp_table_statements = []
        self.subquery_statements = []
        self.main_statement = ""
        self.statement_counter = 0
        
    def is_ddl_statement(self, statement: str) -> bool:
        """Check if statement is DDL (CREATE TABLE/VIEW/INDEX, ALTER, DROP)"""
        # Remove comments and normalize
        cleaned = sqlparse.format(statement, strip_comments=True)
        upper_stmt = cleaned.strip().upper()
        
        # Exclude temporary tables
        if self.is_temp_table_creation(cleaned):
            return False
            
        ddl_keywords = ['CREATE TABLE', 'CREATE VIEW', 'CREATE INDEX', 'CREATE UNIQUE INDEX',
                        'ALTER TABLE', 'DROP TABLE', 'DROP VIEW', 'DROP INDEX']
        return any(upper_stmt.startswith(keyword) for keyword in ddl_keywords)
    
    def is_temp_table_creation(self, statement: str) -> bool:
        """Check if statement creates a temporary table"""
        upper_stmt = statement.strip().upper()
        # Check for various temporary table patterns
        temp_patterns = [
            r'CREATE\s+(?:GLOBAL\s+|LOCAL\s+)?TEMP(?:ORARY)?\s+TABLE',
            r'CREATE\s+TABLE\s+#',  # SQL Server temp table
            r'CREATE\s+TABLE\s+\w+\s+AS\s+SELECT',  # CTAS that might be temporary
        ]
        for pattern in temp_patterns:
            if re.search(pattern, upper_stmt):
                return True
        return False
    
    def extract_cte_from_statement(self, statement: str) -> Tuple[str, str]:
        """Extract CTE (WITH clause) from statement and return (cte, remaining_statement)"""
        parsed = sqlparse.parse(statement)[0]
        
        # Find WITH token
        with_idx = None
        for i, token in enumerate(parsed.tokens):
            if token.ttype is T.Keyword.CTE and token.value.upper() == 'WITH':
                with_idx = i
                break
        
        if with_idx is None:
            return "", statement
        
        # Find the main query start (SELECT, INSERT, UPDATE, DELETE after CTE)
        main_query_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        main_query_idx = None
        paren_depth = 0
        
        for i in range(with_idx + 1, len(parsed.tokens)):
            token = parsed.tokens[i]
            
            if isinstance(token, sql.Parenthesis):
                continue
            elif token.ttype in (T.Punctuation,) and token.value == '(':
                paren_depth += 1
            elif token.ttype in (T.Punctuation,) and token.value == ')':
                paren_depth -= 1
            elif paren_depth == 0 and token.ttype is T.Keyword.DML and token.value.upper() in main_query_keywords:
                main_query_idx = i
                break
        
        if main_query_idx is None:
            return "", statement
        
        # Extract CTE part
        cte_tokens = parsed.tokens[with_idx:main_query_idx]
        cte_statement = ''.join(str(t) for t in cte_tokens)
        
        # Extract remaining part
        remaining_tokens = parsed.tokens[main_query_idx:]
        remaining_statement = ''.join(str(t) for t in remaining_tokens)
        
        return cte_statement.strip(), remaining_statement.strip()
    
    def extract_outer_subqueries(self, statement: str) -> Tuple[List[str], str]:
        """Extract outermost subqueries that can be moved to separate files"""
        subqueries = []
        modified_statement = statement
        
        # Manual parsing approach for better control
        lines = statement.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            upper_line = line.upper()
            
            # Look for JOIN ( or FROM ( patterns
            if ('JOIN (' in upper_line or 'FROM (' in upper_line):
                # Find the complete subquery block
                paren_count = line.count('(') - line.count(')')
                subquery_start = i
                subquery_lines = [line]
                j = i + 1
                
                # Continue until we close all parentheses
                while j < len(lines) and paren_count > 0:
                    subquery_lines.append(lines[j])
                    paren_count += lines[j].count('(') - lines[j].count(')')
                    j += 1
                
                # Extract the subquery content and alias
                full_subquery = '\n'.join(subquery_lines)
                
                # Extract SELECT content and alias more simply
                # Find the SELECT content between parentheses
                select_start = full_subquery.upper().find('SELECT')
                if select_start == -1:
                    result_lines.extend(subquery_lines)
                    i = j
                    continue
                    
                # Find closing paren and alias
                last_line = subquery_lines[-1]
                paren_pos = last_line.rfind(')')
                if paren_pos == -1:
                    result_lines.extend(subquery_lines)
                    i = j
                    continue
                    
                # Extract alias after closing paren
                after_paren = last_line[paren_pos+1:].strip()
                alias_parts = after_paren.split()
                if not alias_parts:
                    result_lines.extend(subquery_lines)
                    i = j
                    continue
                    
                alias = alias_parts[0]
                
                # Extract SELECT content
                select_content = full_subquery[select_start:full_subquery.rfind(')')]
                
                # Check if complex enough
                complexity_keywords = ['JOIN', 'GROUP BY', 'HAVING', 'UNION', 'ORDER BY']
                if any(keyword in select_content.upper() for keyword in complexity_keywords):
                    # Create WITH clause statement
                    with_statement = f"-- Extracted subquery as CTE: {alias}\nWITH {alias} AS (\n{select_content.strip()}\n)"
                    subqueries.append(with_statement)
                    
                    # Replace with simple reference
                    if 'JOIN' in upper_line:
                        result_lines.append(f"JOIN {alias}")
                    else:
                        result_lines.append(f"FROM {alias}")
                    
                    i = j
                    continue
                
                # If not extracted, keep original
                result_lines.extend(subquery_lines)
                i = j
            else:
                result_lines.append(line)
                i += 1
        
        modified_statement = '\n'.join(result_lines)
        return subqueries, modified_statement
    
    def split_sql_file(self, content: str) -> Dict[str, List[str]]:
        """Split SQL content into categorized statements"""
        # Parse all statements
        statements = sqlparse.split(content)
        
        results = {
            'ddl': [],
            'temp_tables': [],
            'cte': [],
            'subqueries': [],
            'main': []
        }
        
        for statement in statements:
            if not statement.strip():
                continue
            
            formatted = sqlparse.format(statement, strip_comments=False)
            
            # Check if it's temporary table creation first
            if self.is_temp_table_creation(formatted):
                results['temp_tables'].append(formatted)
                continue
                
            # Then check if it's DDL
            if self.is_ddl_statement(formatted):
                results['ddl'].append(formatted)
                continue
            
            # Check for CTE
            cte_part, remaining = self.extract_cte_from_statement(formatted)
            if cte_part:
                results['cte'].append(cte_part)
                formatted = remaining
            
            # Extract outer subqueries (simplified for now)
            subqueries, formatted = self.extract_outer_subqueries(formatted)
            if subqueries:
                results['subqueries'].extend(subqueries)
            
            # What's left goes to main
            if formatted.strip():
                results['main'].append(formatted)
        
        return results
    
    def write_split_files(self, results: Dict[str, List[str]], output_dir: str, base_name: str):
        """Write split SQL to numbered files"""
        os.makedirs(output_dir, exist_ok=True)
        
        file_counter = 1
        written_files = []
        
        # Write DDL statements
        for stmt in results['ddl']:
            filename = f"{base_name}_{file_counter:02d}.sql"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"-- File: {filename}\n")
                f.write(f"-- Type: DDL\n\n")
                f.write(stmt)
                if not stmt.rstrip().endswith(';'):
                    f.write(';')
                f.write('\n')
            written_files.append(filename)
            file_counter += 1
        
        # Write temporary table creations
        for stmt in results['temp_tables']:
            filename = f"{base_name}_{file_counter:02d}.sql"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"-- File: {filename}\n")
                f.write(f"-- Type: Temporary Table\n\n")
                f.write(stmt)
                if not stmt.rstrip().endswith(';'):
                    f.write(';')
                f.write('\n')
            written_files.append(filename)
            file_counter += 1
        
        # Write CTEs (they'll be referenced in main)
        cte_references = []
        for stmt in results['cte']:
            filename = f"{base_name}_{file_counter:02d}.sql"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"-- File: {filename}\n")
                f.write(f"-- Type: CTE (Common Table Expression)\n")
                f.write(f"-- Note: This will be combined with main query\n\n")
                f.write(stmt)
                f.write('\n')
            written_files.append(filename)
            cte_references.append(filename)
            file_counter += 1
        
        # Write subqueries (as WITH clauses)
        for stmt in results['subqueries']:
            filename = f"{base_name}_{file_counter:02d}.sql"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"-- File: {filename}\n")
                f.write(f"-- Type: Extracted Subquery (CTE)\n\n")
                f.write(stmt)
                # WITH clauses don't end with semicolon
                f.write('\n')
            written_files.append(filename)
            file_counter += 1
        
        # Write main file
        main_filename = f"{base_name}_main.sql"
        main_filepath = os.path.join(output_dir, main_filename)
        with open(main_filepath, 'w', encoding='utf-8') as f:
            f.write(f"-- File: {main_filename}\n")
            f.write(f"-- Type: Main Query\n")
            
            if cte_references:
                f.write(f"-- References CTEs from: {', '.join(cte_references)}\n")
            
            f.write("\n")
            
            # Write all main statements
            for stmt in results['main']:
                f.write(stmt)
                if not stmt.rstrip().endswith(';'):
                    f.write(';')
                f.write('\n\n')
        
        written_files.append(main_filename)
        
        return written_files


def main():
    parser = argparse.ArgumentParser(description='Split SQL file into components')
    parser.add_argument('sql_file', help='Path to SQL file')
    parser.add_argument('output_dir', help='Output directory')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.sql_file):
        print(f"Error: File '{args.sql_file}' not found")
        sys.exit(1)
    
    # Read SQL file
    with open(args.sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get base name
    base_name = os.path.splitext(os.path.basename(args.sql_file))[0]
    output_subdir = os.path.join(args.output_dir, base_name)
    
    # Split SQL
    splitter = SQLSplitter()
    results = splitter.split_sql_file(content)
    
    # Write split files
    written_files = splitter.write_split_files(results, output_subdir, base_name)
    
    print(f"SQL file split into {len(written_files)} files in: {output_subdir}")
    print(f"Files created: {', '.join(sorted(written_files))}")


if __name__ == '__main__':
    main()