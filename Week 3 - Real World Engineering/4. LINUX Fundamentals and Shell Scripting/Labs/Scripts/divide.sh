#!/bin/bash
if [ $# -ne 2 ]; then
    echo "Usage: $0 numerator denominator"
    exit 1
fi
num=$1
den=$2
if [ $den -eq 0 ]; then
    echo "Error: Division by zero is not allowed."
    exit 1
fi
echo "Result: $(( num / den ))"
