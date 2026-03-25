#!/bin/bash

# Script to create a monolith of all Python code in the repository
# Concatenates all .py files into monolith.py with file separators for AI analysis

output="monolith.py"

# Clear the output file
> "$output"

# Find all .py files, excluding __pycache__ directories
find . -name "*.py" -type f -not -path "./*/__pycache__/*" | while read -r file; do
    echo "# ===== File: $file =====" >> "$output"
    cat "$file" >> "$output"
    echo "" >> "$output"
done

echo "Monolith created in $output"