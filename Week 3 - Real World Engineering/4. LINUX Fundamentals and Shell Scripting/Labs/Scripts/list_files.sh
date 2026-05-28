#!/bin/bash
for file in *.sh; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "$file has $lines lines."
    fi
done
