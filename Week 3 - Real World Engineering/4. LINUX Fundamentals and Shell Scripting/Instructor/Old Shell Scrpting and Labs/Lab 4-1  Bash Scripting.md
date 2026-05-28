# Lab 4-1 Bash Scripting

For each of the following sections, write the specified bash script and confirm that it works.

Solutions are in the solutions file `Lab 4-1 Solutions.md`

## Part 1: Script Basics & Variables

Write a Bash script called greet.sh that:
- Defines a variable name with the value "Linux Student".
- Prints Hello, Linux Student!

```bash

#!/bin/bash
# Simple greeting script

name="Linux Student"
echo "Hello, $name!"
```

- Run with
```bash
 bash greet.sh
```

## Part 2: Control Flow & Input

Create a script called check_number.sh that:
- Asks the user to enter a number.
- Checks if the number is positive, negative, or zero. 
- Prints the result.

```bash
#!/bin/bash
# Script to check number type

read -p "Enter a number: " num

if [ $num -gt 0 ]; then
    echo "The number is positive."
elif [ $num -lt 0 ]; then
    echo "The number is negative."
else
    echo "The number is zero."
fi
```

## Part 3: Script Parameters & Error Handling

Create a script divide.sh that:
- Accepts two command-line arguments (numerator and denominator).
- Prints the division result.
- If the denominator is zero, print an error and exit with status 1.

```bash
#!/bin/bash
# Script to divide two numbers safely

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
```

## Part 4: Functions and Scope

Write a script square.sh that:
- Defines a function square() that takes a number as an argument.
- Returns (echoes) the square of the number.
- Calls the function with the number 5.

```bash
#!/bin/bash
# Function to calculate square

square() {
    local num=$1
    echo $(( num * num ))
}

result=$(square 5)
echo "The square of 5 is $result"


```

## Part 5: Loops and File Processing

Write a script list_files.sh that:
- Loops through all .sh files in the current directory.
- Prints each filename along with the number of lines it contains.

```bash
#!/bin/bash
# Loop through .sh files and count lines

for file in *.sh; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "$file has $lines lines."
    fi
done

```

## Part 6: Debugging a Script

Create a script debug_example.sh that:
- Runs with debugging enabled using set -x.
- Defines a variable and prints it.
- Turns debugging off with set +x.

```bash
#!/bin/bash
# Script demonstrating debugging

set -x   # Enable debug mode

msg="Debugging in action"
echo "Message: $msg"

set +x   # Disable debug mode
echo "Script finished."

```

