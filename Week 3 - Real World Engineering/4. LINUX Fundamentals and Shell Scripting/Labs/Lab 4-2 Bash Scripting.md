# Lab 4-2: Bash Scripting

## Overview

Lab 4-1 introduced the Linux commands you type one at a time at the shell prompt. This lab is about composing those commands into scripts that you can run repeatedly, save to source control, and share with teammates. A bash script is just a text file containing the same commands you would type interactively, plus a few extra constructs (variables, conditions, loops, functions) that let it react to its inputs.

Bash scripts are everywhere in software engineering. The deployment automation in most CI/CD pipelines is bash. The setup commands in most Docker containers are bash. The "convenience scripts" in most open-source repositories (`run.sh`, `setup.sh`, `clean.sh`) are bash. Learning the language well enough to read and modify these scripts is a baseline skill for any working engineer, regardless of which language they write their main code in.

This lab walks you through six small scripts, each demonstrating one core feature: variables and string interpolation, control flow, command-line arguments and error handling, functions, loops over files, and debugging. Each script is short (5-15 lines), but each one models a pattern you will see in real production scripts at large companies. You will write each script, run it, observe its output, and then check your work against a canonical version and a set of expected outputs.

The lab is therefore part **typing exercise** (build muscle memory for bash syntax), part **observation exercise** (read script output critically and notice the small things), and part **comparison exercise** (your script vs. the canonical version vs. a Copilot-generated version).

**This lab is hands-on.** You write the scripts yourself; no AI assistance is needed or expected for the main exercises. A short stretch step at the end (Part 8) invites you to compare your scripts to ones Copilot generates from the same problem statements.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Write a bash script with a proper shebang line (`#!/bin/bash`) and run it both with `bash script.sh` and as an executable (`./script.sh` after `chmod +x`).
2. Define variables, interpolate them in double-quoted strings, and explain why double quotes matter.
3. Use `if`/`elif`/`else` for control flow and the `[ ... ]` test syntax for comparing numbers and strings.
4. Read positional command-line arguments (`$1`, `$2`, `$#`) and exit with non-zero status codes to signal errors.
5. Define functions, use `local` to scope variables, and capture function output with `$(...)` command substitution.
6. Iterate over files with a `for` loop and handle the edge cases (no matches, filenames with spaces).
7. Turn on bash's tracing mode (`set -x`) to debug a script line by line, and recognize the difference between standard output and standard error.
8. Identify the most common bash pitfalls (unquoted variables, integer-only arithmetic, no input validation) and write defensive scripts that protect against them.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder

In your terminal:

```bash
mkdir -p ~/bash-lab
cd ~/bash-lab
```

You will create six small scripts in this folder over the course of the lab.

### Step 1.2: Confirm bash is available

```bash
bash --version
```

You should see output starting with `GNU bash, version 5.x` or similar. Bash 4 or later is sufficient for this lab; most modern systems have bash 5.

> **A note for macOS users.** macOS ships with bash 3.2 as `/bin/bash` for licensing reasons. Most of this lab works fine on bash 3.2, but a few modern features (associative arrays, `mapfile`) do not. If you installed a modern bash via Homebrew (`brew install bash`), use `/opt/homebrew/bin/bash` or whatever path `which -a bash` shows for the newer install. The default `/bin/zsh` on recent macOS can also run most of this lab's scripts unchanged because the syntax overlap is large; only Part 2's `read -p` differs (you would use `read "num?Enter a number: "` instead, but the lab uses `bash` explicitly so this issue does not arise).

### Step 1.3: Create a lab notebook

Create `~/bash-lab/notebook.md`:

```bash
touch ~/bash-lab/notebook.md
```

Open it in your editor of choice. You will record observations as you go. Start it with:

```markdown
# Bash Scripting Lab Notebook

## Part 2: Variables (greet.sh)

## Part 3: Control flow (check_number.sh)

## Part 4: Arguments and exit codes (divide.sh)

## Part 5: Functions (square.sh)

## Part 6: Loops over files (list_files.sh)

## Part 7: Debugging (debug_example.sh)

## Part 8: Stretch (Copilot for scripts)

## Part 9: Reflection
```

### Step 1.4: The workflow you will repeat

For each of Parts 2 through 7, you will:

1. Read the problem statement and write the script yourself in your editor.
2. Save the script in `~/bash-lab/`.
3. Run the script and compare its output to the expected output.
4. Read the "design notes" sidebar and the canonical solution. Note any differences in your notebook.

Aim to write each script without looking at the canonical solution first. The point of the lab is to build the muscle memory of typing the syntax; copying from the canonical defeats that.

---

## Part 2: Variables and Strings (greet.sh)

### Step 2.1: The problem

Write a Bash script called `greet.sh` that:

- Defines a variable `name` with the value `"Linux Student"`.
- Prints `Hello, Linux Student!`.

### Step 2.2: Write the script

Create `greet.sh` in `~/bash-lab/`. Write your version before peeking at the canonical below.

### Step 2.3: Run it

```bash
bash greet.sh
```

**Expected output:**

```
Hello, Linux Student!
```

### Canonical solution

```bash
#!/bin/bash
# Simple greeting script

name="Linux Student"
echo "Hello, $name!"
```

### Design notes

- **The shebang line (`#!/bin/bash`).** The first line of a script that starts with `#!` tells the operating system which interpreter to use. When you run the script as `./greet.sh` (rather than `bash greet.sh`), the kernel reads this line and runs `/bin/bash` with your script as its argument. For `bash greet.sh`, the shebang is technically optional, but always include it: it documents the intended interpreter and makes the script directly executable later.
- **No spaces around `=`.** `name="Linux Student"` works; `name = "Linux Student"` does not (bash interprets that as running the program `name` with arguments `=` and `"Linux Student"`). This is one of the most common confusions for engineers coming from other languages.
- **Double quotes interpolate; single quotes do not.** `echo "Hello, $name!"` prints `Hello, Linux Student!`. `echo 'Hello, $name!'` prints `Hello, $name!` literally. When in doubt, use double quotes for strings that contain variables.

### Make it directly executable (stretch)

```bash
chmod +x greet.sh
./greet.sh
```

The `chmod +x` sets the executable bit; the `./` is required because the current directory is not on `$PATH` by default. The output is the same as `bash greet.sh`.

---

## Part 3: Control Flow and User Input (check_number.sh)

### Step 3.1: The problem

Create a script called `check_number.sh` that:

- Asks the user to enter a number.
- Checks whether the number is positive, negative, or zero.
- Prints the result.

### Step 3.2: Write the script

Create `check_number.sh` in `~/bash-lab/`. Try writing your own version first.

### Step 3.3: Run it three times with different inputs

```bash
bash check_number.sh
# Enter 5 at the prompt; expect "The number is positive."

bash check_number.sh
# Enter -3; expect "The number is negative."

bash check_number.sh
# Enter 0; expect "The number is zero."
```

### Canonical solution

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

### Design notes

- **`read -p "prompt: " var`** prompts the user and stores their input in `var`. Without `-p`, you would need a separate `echo` for the prompt.
- **`[ ... ]` is the test command.** Notice the spaces around the brackets: `[ $num -gt 0 ]` works; `[$num -gt 0]` does not. Bash parses the brackets as a program name, so they need spaces around them like any other command.
- **`-gt`, `-lt`, `-eq`, `-ne`, `-ge`, `-le`** are the integer comparison operators. For string comparison, use `=`, `!=`, `<`, `>`. Mixing them up is a frequent source of bugs (string comparison of `"10"` and `"9"` returns "10 is less than 9" because it compares lexicographically).
- **`fi` closes `if`.** Bash control structures use the keyword reversed: `if`/`fi`, `case`/`esac`. (It would have been `do`/`od` for loops if `od` were not already taken by another command, hence `do`/`done`.)

### What happens with non-numeric input?

Try entering `hello` at the prompt:

```bash
bash check_number.sh
```

You will see something like:

```
check_number.sh: line 6: [: hello: integer expression expected
check_number.sh: line 8: [: hello: integer expression expected
The number is zero.
```

The script produces error messages and then incorrectly concludes that "hello" is zero. This is a real bug in the canonical script: it has no input validation. A defensive version would add a check like:

```bash
if ! [[ "$num" =~ ^-?[0-9]+$ ]]; then
    echo "Error: not a number." >&2
    exit 1
fi
```

before the comparisons. Note this in your notebook; the reflection at the end of the lab returns to it.

---

## Part 4: Command-Line Arguments and Exit Codes (divide.sh)

### Step 4.1: The problem

Create a script `divide.sh` that:

- Accepts two command-line arguments (numerator and denominator).
- Prints the division result.
- If the denominator is zero, prints an error and exits with status 1.

### Step 4.2: Write the script

Create `divide.sh` in `~/bash-lab/`. Try your version first.

### Step 4.3: Run it with several inputs

```bash
bash divide.sh 10 2
# Expect: Result: 5

bash divide.sh 10 0
# Expect: Error: Division by zero is not allowed.

bash divide.sh
# Expect: Usage: divide.sh numerator denominator

bash divide.sh 7 3
# Expect: Result: 2  (notice: integer division!)
```

After each run, check the exit code:

```bash
echo $?
```

Successful runs exit with `0`; error cases exit with `1`.

### Canonical solution

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

### Design notes

- **`$#` is the count of arguments.** `$1`, `$2`, etc. are the individual arguments. `$0` is the script's own name. `$@` is all the arguments together.
- **Exit codes are how scripts signal success or failure to their caller.** By convention, exit `0` means success, anything else means some kind of error. Scripts called from CI pipelines, Makefiles, and other scripts all rely on this convention.
- **`$(( ... ))` is bash's arithmetic expansion.** It does integer math. `7 / 3` evaluates to `2`, not `2.333`. There is no floating-point in pure bash; for decimals you would pipe to `bc -l` or use `python3 -c`. Many "weird bash bugs" turn out to be this integer-only behavior.
- **The Usage message uses `$0`.** That makes the usage text reflect whatever name the script was invoked as (`./divide.sh`, `bash divide.sh`, or some symlink), rather than hard-coding "divide.sh".

### What happens with bad inputs?

Try the script with garbage:

```bash
bash divide.sh hello world
```

You will get error messages like `[: hello: integer expression expected` and then the script will still try to do the math (with confusing results). This is the same input-validation gap as in Part 3, and the same defensive guard would fix it. Real production scripts include such guards; teaching examples often omit them for brevity, which is its own lesson.

---

## Part 5: Functions and Scope (square.sh)

### Step 5.1: The problem

Write a script `square.sh` that:

- Defines a function `square()` that takes a number as an argument.
- Returns (echoes) the square of the number.
- Calls the function with the number 5.

### Step 5.2: Write the script

Create `square.sh` in `~/bash-lab/`. Try your version first.

### Step 5.3: Run it

```bash
bash square.sh
```

**Expected output:**

```
The square of 5 is 25
```

### Canonical solution

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

### Design notes

- **Function syntax.** `name() { ... }` defines a function. There is no `function` keyword required (though `function name() { ... }` and `function name { ... }` both work as alternative syntaxes).
- **Arguments use `$1`, `$2` etc. inside the function**, just like the script's own arguments. There is no formal parameter list; `square(num)` is not bash syntax.
- **`local` scopes the variable to the function.** Without `local`, the variable would be global. In a small script this rarely matters; in a large script with many functions, omitting `local` is a way to introduce hard-to-debug action at a distance.
- **`return` in bash returns an exit code, not a value.** The "return value" of a bash function is whatever it writes to standard output, which the caller captures with `$(...)` command substitution: `result=$(square 5)`.
- **`$(...)` runs a command and substitutes its output.** Inside it, the command can be anything: another script, a pipeline, even another `$(...)`. The older `` `...` `` (backticks) syntax does the same thing but does not nest cleanly; modern scripts always use `$(...)`.

---

## Part 6: Loops and File Processing (list_files.sh)

### Step 6.1: The problem

Write a script `list_files.sh` that:

- Loops through all `.sh` files in the current directory.
- Prints each filename along with the number of lines it contains.

### Step 6.2: Write the script

Create `list_files.sh` in `~/bash-lab/`. Try your version first.

### Step 6.3: Run it

```bash
bash list_files.sh
```

**Expected output** (your line counts may differ slightly if you wrote your own versions):

```
check_number.sh has 12 lines.
divide.sh has 12 lines.
greet.sh has 5 lines.
list_files.sh has 7 lines.
square.sh has 8 lines.
```

The files are listed in alphabetical order because shell glob expansion is sorted by default.

### Canonical solution

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

### Design notes

- **`for x in pattern; do ... done`** iterates over the words that `pattern` expands to. `*.sh` is a glob that expands to all matching filenames in the current directory, sorted alphabetically.
- **The `[ -f "$file" ]` test** protects against the case where no files match: when `*.sh` matches nothing, bash leaves the pattern as-is by default, and the loop runs once with `file="*.sh"` (a literal). The `-f` test confirms that the candidate is a regular file that exists. An alternative is `shopt -s nullglob` at the top of the script, which makes non-matching globs expand to nothing.
- **Quotes around `"$file"`.** Without them, a filename like `my report.sh` would be split into two arguments (`my` and `report.sh`) when passed to `wc`. Always quote variables that hold filenames.
- **`wc -l < "$file"` versus `wc -l "$file"`.** Both count lines, but the first redirects the file as input (output is just the number), while the second passes it as an argument (output is "5 greet.sh"). For interpolating into the message, the redirect form is cleaner.

### A common bug

Try this variation: remove the `-f "$file"` check, then run the script in a directory with no `.sh` files. Most likely you get an error like:

```
wc: *.sh: No such file or directory
```

That is the loop running once with the literal pattern. The `[ -f "$file" ]` guard prevents this; `shopt -s nullglob` would be a cleaner global fix.

---

## Part 7: Debugging Scripts (debug_example.sh)

### Step 7.1: The problem

Create a script `debug_example.sh` that:

- Runs with debugging enabled using `set -x`.
- Defines a variable and prints it.
- Turns debugging off with `set +x`.

### Step 7.2: Write the script

Create `debug_example.sh` in `~/bash-lab/`. Try your version first.

### Step 7.3: Run it

```bash
bash debug_example.sh
```

**Expected output** (your output may have the order slightly different; see "Standard output vs. standard error" below):

```
+ msg='Debugging in action'
+ echo 'Message: Debugging in action'
Message: Debugging in action
+ set +x
Script finished.
```

The lines starting with `+` are the debug trace. They show each command after expansion, just before bash runs it. This is the equivalent of "single-step through the script and print each step."

### Canonical solution

```bash
#!/bin/bash
# Script demonstrating debugging

set -x   # Enable debug mode

msg="Debugging in action"
echo "Message: $msg"

set +x   # Disable debug mode
echo "Script finished."
```

### Design notes

- **`set -x` turns on tracing**: every command is printed (with a `+` prefix) before it runs. `set +x` turns it off. The convention `-x` for "set" and `+x` for "unset" is bash-specific and quirky; both flags are valid arguments to `set`.
- **`set -e` is a related and very useful flag.** It makes the script exit immediately if any command fails. Many production scripts start with `set -euo pipefail` at the top: exit on error (`-e`), error on undefined variables (`-u`), and propagate failures through pipelines (`-o pipefail`).
- **Standard output vs. standard error.** The trace lines (`+ msg=...`) go to *stderr*. The script's own `echo` output goes to *stdout*. When both stream to the same terminal, their interleaving depends on terminal buffering; sometimes the trace appears before the line it traces, sometimes after. To see them more cleanly, redirect: `bash debug_example.sh 2>trace.log` puts the trace in a file and only the script's output on the screen.

### A debugging exercise (stretch)

Modify a copy of `divide.sh` from Part 4 to start with `set -x`. Run it with both good and bad inputs. Notice how the trace shows you exactly which `if` branch was taken and what each variable was set to. This is bash's single most useful debugging tool; remember it.

---

## Part 8: Stretch: Copilot for Bash Scripts

You have written six scripts from scratch. Now you will compare your versions to ones Copilot generates from the same problem statements. The interesting question is not "which is better"; the interesting question is what the differences reveal about the gaps in your scripts.

### Step 8.1: Open Copilot Chat

Open VS Code in your `~/bash-lab` folder (`code ~/bash-lab` from the terminal). Open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for the full availability notes).

### Step 8.2: Ask for the same six scripts

For each of the six problem statements (Parts 2 through 7), send Copilot a prompt of the form:

```
Write a Bash script called check_number.sh that:
- Asks the user to enter a number.
- Checks if the number is positive, negative, or zero.
- Prints the result.

Include defensive input validation, a comment header, and proper exit codes.
```

This prompt is similar to what you would type in a real workflow: the problem statement, plus a few professional-quality requirements. For each script Copilot produces, save it to a file (`copilot_check_number.sh`, etc.) alongside your own version.

### Step 8.3: Compare your version to Copilot's

Use VS Code's **Compare Selected** feature to view your version and Copilot's version side by side:

1. In the Explorer, click your `check_number.sh` to select it.
2. `Ctrl+click` (Windows/Linux) or `Cmd+click` (macOS) the corresponding `copilot_check_number.sh`.
3. Right-click either file and choose **Compare Selected**.

For each of the six pairs, write in your notebook:

1. Where did your script and Copilot's agree?
2. Did Copilot include things you missed (input validation, error checking, the shebang line, comments, `set -e` at the top)?
3. Did Copilot include things you would consider unnecessary (extra layers of error handling for problems that can never happen, defensive code that obscures the script's intent)?
4. Are there places where you would prefer your version to Copilot's? Why?

### Step 8.4: The takeaway

The typical pattern with Copilot-generated bash is:

- **Strengths**: Copilot reliably includes the things this lab's canonical examples omit. It adds input validation. It uses `set -euo pipefail`. It quotes variables. It includes a comment header with author, date, and usage.
- **Weaknesses**: Copilot sometimes over-engineers. It may catch errors that cannot occur in the script's actual use case, or use a complex pattern (associative arrays, traps) when a simple one would do.

This means the right use of Copilot for bash is *not* "write a bash script for me, ship it as is." It is "write a bash script for me, then critically review every line and trim what is not needed for my context." The act of reviewing requires you to actually know bash, which is what this lab was for.

---

## Part 9: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **The seven shell idioms.** Across the six scripts you wrote, list the seven shell idioms you used most often (for example: shebang line, variable assignment without spaces, `if/then/fi`, `$(...)` command substitution, `local` inside a function, the `for x in pattern` loop, double-quoted strings with variables). Which of these were new to you, and which felt familiar from other languages?

2. **The input validation gap.** Both `check_number.sh` and `divide.sh` misbehave on non-numeric input. In a real production script, would you add the validation? If yes, how would you decide which inputs to validate and which to trust? If no, what would you rely on instead (the caller's contract, a CI test, a wrapper script)?

3. **`set -euo pipefail`.** Look up what each of the three flags does in `man bash` (search for the `set` builtin). For each one, give an example of a bug it would catch. Are there scripts where you would *not* want these flags on?

4. **Pipelines and redirection.** None of the six scripts in this lab used pipelines (the `|` operator) extensively. From your Linux lab (4-1), you used `sort | uniq` and `grep -R`. Pick one of the six scripts in this lab and imagine rewriting it to use a pipeline. Does the pipeline version end up shorter, clearer, both, or worse?

5. **Bash vs. Python for scripting.** For each of the six scripts in this lab, would you choose bash or Python for the equivalent task in production? Are there scripts where bash is clearly the right choice, and others where Python clearly is? What is the rough threshold (in lines of code, in complexity) where you would switch from bash to Python?

6. **Copilot's value for bash specifically.** Compare your experience of Copilot for bash (Part 8) to your experience of Copilot for code in earlier labs (Java, Python). Was Copilot more or less useful for bash? Did its strengths and weaknesses differ between languages?

7. **The scripts you would actually use.** Of the six scripts in this lab, which one is closest to a script you would actually have in your `~/bin/` directory? Which one is the most "teaching example only" with no real-world counterpart? What is the difference between the two extremes?

---

## Reference: The Bash Idioms Used in This Lab

A summary of the syntax pieces, organized by what they do.

| Idiom | Example | Notes |
|-------|---------|-------|
| Shebang | `#!/bin/bash` | First line; tells the kernel which interpreter to run. |
| Comment | `# This is a comment` | Everything from `#` to end of line. |
| Variable assignment | `name="value"` | No spaces around `=`. |
| Variable interpolation | `echo "Hello, $name"` | Double quotes only; single quotes are literal. |
| Read from stdin | `read -p "Enter: " var` | The `-p` prompt is optional. |
| Positional arguments | `$1`, `$2`, ..., `$@`, `$#` | `$0` is the script name. |
| Test command | `[ "$x" -gt 0 ]` | Spaces around the brackets required. |
| Integer comparison | `-eq -ne -lt -le -gt -ge` | For numbers. |
| String comparison | `=` `!=` `<` `>` | For strings. |
| Arithmetic | `$(( 3 + 4 ))` | Integer only. |
| Command substitution | `result=$(cmd)` | Replaces backticks; nests cleanly. |
| If-then-else | `if [ ... ]; then ... elif ... else ... fi` | Reverse keyword: `fi` ends `if`. |
| For loop | `for f in *.sh; do ... done` | Glob, list of words, or `$@`. |
| Function | `name() { ... }` | No keyword required. |
| Local variable | `local x=1` | Only inside functions. |
| Exit code | `exit 1` | Non-zero for errors. |
| Last command's exit | `$?` | Most recent command's exit status. |
| Tracing on/off | `set -x` / `set +x` | Prints each command before running. |
| Strict mode | `set -euo pipefail` | Recommended for production scripts. |
| Redirect output | `cmd > file` / `cmd >> file` | Overwrite / append. |
| Redirect from file | `cmd < file` | Stdin from file. |
| Stderr | `cmd 2> file` / `cmd 2>&1` | Stream 2 is stderr. |
| Pipeline | `cmd1 \| cmd2` | Stdout of `cmd1` becomes stdin of `cmd2`. |

---

## Reference: Common Bash Pitfalls

Things that bite every bash author at least once.

- **Unquoted variables containing spaces.** `cp $file dest/` breaks if `$file` is `my report.txt`. Always: `cp "$file" dest/`.
- **Spaces around `=` in assignment.** `x=1` works; `x = 1` runs the program `x` with arguments `=` and `1`.
- **Spaces inside `[ ... ]`.** `[ "$x" -gt 0 ]` works; `["$x" -gt 0]` does not.
- **Integer-only arithmetic.** `echo $((1/2))` prints `0`, not `0.5`. For decimals use `bc`, `awk`, or `python3 -c`.
- **String comparison with `-gt`.** `[ "10" -gt "9" ]` works (forces numeric); `[ "10" \> "9" ]` is lexicographic and returns false (because "1" < "9"). Choose the right operator family for the data.
- **Globs that match nothing.** `for f in *.foo; do ...; done` runs once with `f="*.foo"` if no files match. Use `shopt -s nullglob` or test `[ -e "$f" ]`.
- **The script's directory vs. the working directory.** `./config.json` is relative to whatever directory the user was in when they ran the script, not to where the script lives. To reference files next to the script: `"$(dirname "$0")/config.json"` (with a `cd "$(dirname "$0")"` near the top of the script as an even simpler approach).
- **Word splitting and globbing in unexpected places.** Bash performs both on the result of unquoted variable expansions. `rm $files` where `$files="a.txt b.txt *.log"` does what you probably want; `rm $files` where `$files="my report.txt"` does not.
- **The `eval` trap.** Avoid `eval "$user_input"` like the plague. It is a code-injection vulnerability with a friendly face.

---

## Troubleshooting

**`./greet.sh: Permission denied`.**
You did not run `chmod +x greet.sh`, or you did but you are on a filesystem that does not preserve the executable bit (some Windows-mounted-via-WSL setups). Run with `bash greet.sh` instead, which does not require the executable bit.

**`bash: ./greet.sh: /bin/bash^M: bad interpreter: No such file or directory`.**
Your script has CRLF (Windows) line endings, not LF (Unix). The `^M` is the carriage return that the kernel cannot find in the shebang line. Fix it with `dos2unix greet.sh`, or `sed -i 's/\r$//' greet.sh`. If you are editing in VS Code, change the line endings in the bottom-right status bar from CRLF to LF.

**`[: too many arguments` or `[: integer expression expected`.**
A variable in your test is empty or has spaces. `[ $num -gt 0 ]` with an empty `$num` becomes `[ -gt 0 ]`, which has the wrong number of arguments. Quote the variable: `[ "$num" -gt 0 ]`. If `$num` might not be numeric, validate first.

**The script ran but produced no output.**
Many things in bash succeed silently. `mkdir -p existing/path` and `touch file` both work without output. If you expected output, check that you wrote `echo` and not `read`, and that you actually called the function.

**`command not found` for a command you know is installed.**
The current directory is not on `$PATH` by default. To run a script in the current directory, prefix it with `./`. To run a system command, either it should be on `$PATH` (try `which command`) or you should invoke it with an absolute path.

**Tracing output (`+ ...`) appears interleaved with regular output in confusing ways.**
The trace goes to stderr; regular output goes to stdout. The interleaving depends on terminal buffering. To see them cleanly separated: `bash script.sh 2>trace.log` (puts trace in a file).

**Copilot's script uses associative arrays or `mapfile` and macOS bash 3.2 complains.**
macOS ships an old bash. Either install a newer one with `brew install bash`, or ask Copilot to "write this in bash 3.2-compatible syntax". Most production scripts target bash 4+, so this is a macOS-specific quirk.

---

## Further Reading

- **The Bash Reference Manual** at <https://www.gnu.org/software/bash/manual/bash.html>. The canonical, comprehensive reference. Long but well-organized; chapter 3 (Basic Shell Features) and chapter 6 (Bash Features) cover most of this lab.
- **Bash Pitfalls** at <https://mywiki.wooledge.org/BashPitfalls>. A community-curated list of the 50-plus most common bash mistakes, each with an explanation. The "Common Pitfalls" reference above is the short version; this is the long version.
- **ShellCheck** at <https://www.shellcheck.net/>. A static analyzer for shell scripts. Paste any script and it points out problems (quoting issues, deprecated syntax, common mistakes). Run it on your six scripts from this lab.
- **The Linux Command Line** (William Shotts), part 2: "Configuration and the Environment" and part 4: "Writing Shell Scripts". Free at <https://linuxcommand.org/tlcl.php>. The same book recommended in Lab 4-1; the scripting half is a thorough introduction.
- **Pro Bash Programming** (Chris Johnson and Jayant Varma). A book-length treatment for engineers who want to write bash scripts at a level beyond what most online tutorials reach.
