"""Analyze unused/redundant code in the codebase."""
import ast
import os
from pathlib import Path
from collections import defaultdict

def find_unused_imports(file_path):
    """Find unused imports in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    
    imports = set()
    used_names = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
    
    unused = []
    for imp in imports:
        if imp not in used_names and imp not in ['src', 'typing', 'datetime', 'pathlib']:
            # Check if it's actually used
            if imp not in content.replace(f'import {imp}', '').replace(f'from {imp}', ''):
                unused.append(imp)
    
    return unused

def analyze_codebase():
    """Analyze the codebase for unused code."""
    issues = []
    
    # Check src files
    src_files = list(Path('src').glob('*.py'))
    
    print("=" * 70)
    print("Code Analysis: Unused/Redundant Code")
    print("=" * 70)
    
    # Manual checks based on grep analysis
    print("\n1. REDUNDANT IMPORTS:")
    print("   - src/scraper.py:99 - Redundant import 'from src.api_client import Yad2ApiClient'")
    print("     (already imported at top)")
    print("   - scrape_city_by_neighborhoods.py:33 - Unused import 'import os'")
    
    print("\n2. UNUSED METHODS:")
    print("   - api_client.py:fetch_listings_for_city() - Convenience method, not used")
    print("   - api_client.py:__enter__() / __exit__() - Context manager, not used")
    
    print("\n3. UNUSED CONSTANTS:")
    print("   - api_client.py:ISRAEL_BBOX - Defined but only used in docstring/test")
    
    print("\n4. MODULE USAGE:")
    print("   - scraper.py: Used by tests but NOT by actual scraper scripts")
    print("     (scrape_city_by_neighborhoods.py and scrape_tel_aviv.py don't use it)")
    print("     NOTE: This is OK - scraper.py is for CLI/future use")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    print("1. Remove redundant import in scraper.py:99")
    print("2. Remove unused import 'os' in scrape_city_by_neighborhoods.py:33")
    print("3. Consider removing fetch_listings_for_city() if not needed")
    print("4. Consider removing context manager methods if not used")
    print("5. Keep scraper.py - it's part of core architecture for CLI")

if __name__ == "__main__":
    analyze_codebase()

