# Suggested Plan

## 1: Introduction & Fundamentals

- What is a shell? Why script?
- bash scripting basics: shebang (#!/bin/bash), running scripts
- Variables and simple types (strings, numbers, env vars)

#### Lab:
- Write a “Hello World” script

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Hello, world!"

```
- Create a script that greets a user using $USER and a custom variable

```bash
#!/usr/bin/env bash
set -euo pipefail

GREETING=${1:-"Welcome"}
echo "$GREETING, $USER!"
```

- Run: ./hello.sh

##  2: Control Flow & I/O

- if, else, elif, case
- Loops: for, while, until
- Input/output redirection, pipes, reading from stdin (read)

#### Lab:

Script that checks if a file exists and prints its size

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <path-to-file>" >&2
  exit 2
fi

f=$1
if [[ -f "$f" ]]; then
  # portable way: stat fallback to wc
  if stat --version >/dev/null 2>&1; then
    # GNU stat
    bytes=$(stat -c %s -- "$f")
  else
    # BSD / macOS stat
    bytes=$(stat -f %z -- "$f")
  fi
  echo "File '$f' exists, size: ${bytes} bytes"
else
  echo "File '$f' not found or not a regular file" >&2
  exit 1
fi
```

Script that loops through files in a directory and counts lines

```bash
#!/usr/bin/env bash
set -euo pipefail

dir=${1:-.}
shopt -s nullglob
total=0

for f in "$dir"/*; do
  if [[ -f "$f" ]]; then
    lines=$(wc -l < "$f")
    printf "%s: %d lines\n" "$f" "$lines"
    total=$(( total + lines ))
  fi
done

echo "TOTAL lines in regular files under '$dir': $total"

```

## 3: Functions, Scope, and Arguments

- Functions (myfunc() { … })
- Local vs global variables (local)
- Script parameters: $1, $#, $@, shift

#### Lab:

Script with a function that calculates factorial recursively

```bash
#!/usr/bin/env bash
set -euo pipefail

factorial() {
  local n=$1
  if (( n < 0 )); then
    echo "Error: negative input" >&2
    return 1
  fi
  if (( n <= 1 )); then
    echo 1
  else
    local prev
    prev=$(factorial $(( n - 1 )))
    echo $(( n * prev ))
  fi
}

if [[ $# -ne 1 || ! $1 =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 <nonnegative-integer>" >&2
  exit 2
fi

factorial "$1"

```

Script that accepts a filename as an argument and counts words

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <filename>" >&2
  exit 2
fi

file=$1
if [[ ! -f "$file" ]]; then
  echo "Error: '$file' not found" >&2
  exit 1
fi

# count “words” as sequences of non-space
count=$(wc -w < "$file")
echo "Word count for '$file': $count"

```

## 4: External Commands & Error Handling

- Using grep, awk, sed, cut in scripts
- Capturing exit codes ($?)
- Using set -e, trap for error handling

#### Lab

Script that searches log files for “ERROR” and reports counts

```bash
#!/usr/bin/env bash
set -euo pipefail

logdir=${1:-/var/log}

if [[ ! -d "$logdir" ]]; then
  echo "Error: '$logdir' is not a directory" >&2
  exit 1
fi

echo "Scanning '$lologgdir' for lines containing 'ERROR'…"
# Per-file counts
grep -R --line-number --ignore-case "ERROR" -- "$logdir" 2>/dev/null | awk -F: '
{
  file=$1; counts[file]++
}
END {
  total=0
  for (f in counts) {
    printf("%s: %d\n", f, counts[f])
    total+=counts[f]
  }
  printf("TOTAL ERROR lines: %d\n", total)
}'

```

Script that backs up a folder and exits with an error if it fails

```bash
#!/usr/bin/env bash
set -euo pipefail

# Fail fast on errors; report where failures happen
trap 'echo "Error on line $LINENO"; exit 1' ERR

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <source-dir> <dest-dir>" >&2
  exit 2
fi

src=$1
dst=$2
ts=$(date +%Y%m%d-%H%M%S)

if [[ ! -d "$src" ]]; then
  echo "Error: source '$src' not found" >&2
  exit 1
fi
mkdir -p -- "$dst"

archive="${dst%/}/backup-$(basename "$src")-${ts}.tar.gz"

echo "Creating archive: $archive"
# Use --exclude-vcs to skip .git/.svn; adjust as needed
tar -czf "$archive" --exclude-vcs -C "$(dirname "$src")" "$(basename "$src")"

# Verify archive (list contents)
tar -tzf "$archive" >/dev/null

echo "Backup successful: $archive"


```

##  5: Debugging & Best Practices

- Debugging with bash -x script.sh
- set -u, set -o pipefail
- Echo/print statements for debugging

#### Lab:

Break a script intentionally and debug using set -x

```bash
#!/usr/bin/env bash
# BUGS: missing set flags, unquoted vars, wrong test operator, missing error checks
src=$1
dst=$2
if [ -d $src ]; then
  cp -r $src $dst
  echo Copied $src to $dst
else
  echo Source not found
fi

```

How to debug:
Run with tracing: bash -x broken_copy.sh "My Dir" /tmp/out and observe word-splitting and test failures.

**Fixed**

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <source-dir> <dest-dir>" >&2
  exit 2
fi

src=$1
dst=$2

if [[ -d "$src" ]]; then
  mkdir -p -- "$dst"
  cp -r -- "$src" "$dst/"
  echo "Copied '$src' to '$dst/'"
else
  echo "Error: source '$src' not found" >&2
  exit 1
fi

```

Add error handling to an existing lab script

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "Failed at line $LINENO"; exit 1' ERR

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [directory]" >&2
  exit 2
fi

dir=${1:-.}
if [[ ! -d "$dir" ]]; then
  echo "Error: '$dir' is not a directory" >&2
  exit 1
fi

shopt -s nullglob
total=0
for f in "$dir"/*; do
  [[ -f "$f" ]] || continue
  lines=$(wc -l < "$f" || true)
  printf "%s: %s\n" "$f" "${lines:-0}"
  total=$(( total + (lines:-0) ))
done
echo "TOTAL: $total"

```


## 6: Automation with Cron Jobs

- Scheduling with cron (crontab -e)
- Syntax: * * * * * and @daily, @hourly
- Practical examples: log rotation, backups, report generation

#### Lab:

Write a script that appends timestamped output to a file

```bash
#!/usr/bin/env bash
set -euo pipefail

logfile=${1:-"$HOME/timestamps.log"}
printf "[%s] heartbeat from %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$HOSTNAME" >> "$logfile"

```

Run once: ./timestamp_log.sh ~/my.log

Schedule it with cron to run every minute

```text
Open crontab: crontab -e

Examples (pick one):

Every minute (demo):
* * * * * /full/path/timestamp_log.sh /full/path/cron.log

Hourly
@hourly /full/path/timestamp_log.sh /full/path/cron.log


Daily at 2:30
30 2 * * * /full/path/timestamp_log.sh /full/path/cron.log


```