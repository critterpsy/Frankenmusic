#!/bin/bash

output="python_dump.txt"
> "$output"

find . -name "*.py" -type f \
  -not -path "./*/__pycache__/*" \
  -not -path "./.venv/*" \
  -not -path "./venv/*" \
  -not -name "$output" \
| while read -r file; do
    echo "===== File: $file =====" >> "$output"
    cat "$file" >> "$output"
    echo "" >> "$output"
  done

echo "Dump created in $output"