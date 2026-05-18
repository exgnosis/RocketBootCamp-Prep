# Lab 1-2: Reading Unfamiliar C Code 

## Overview

One of the most useful things you can do with GitHub Copilot is **read code you did not write**. Whether you are joining a new team, picking up a colleague's branch, reviewing a pull request, or just trying to understand an open-source library, the ability to ask an AI assistant "what does this do, and why does it do it that way" is a real productivity multiplier.

In this lab you will work with a single, well-written C program of about 150 lines: a small text statistics utility called `wordcount`. The program is clean, structured, and representative of the kind of C code you might find in any modern Unix-style codebase. You will use Copilot in **Ask mode** to build a complete understanding of how the program works: its overall structure, each function's role, the data flow, the error handling, and the idioms it uses.

You will not modify the code. The goal is to read it, ask the right questions, and end up with a clear mental model.

**Estimated time:** 30 to 40 minutes
**Difficulty:** Beginner

**Prerequisites:**

- Successfully completed lab 6-1 from the previous wee,k, or otherwise have GitHub Copilot set up and working in Ask mode.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Use Copilot in Ask mode to obtain a top-down explanation of an unfamiliar program.
2. Ask focused follow-up questions about individual functions, idioms, and design choices.
3. Distinguish between *what* the code does and *why* the author wrote it that way.
4. Recognize common C idioms: dynamic buffer growth, struct as a return aggregate, error propagation via return codes, single-entry/single-exit functions.
5. Verify Copilot's explanations against the source rather than accepting them on faith.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/wordcount-lab
cd ~/wordcount-lab
code .
```

VS Code opens the empty directory as a workspace. When prompted, click **Yes, I trust the authors**.


### Step 1.2: Create the program file

Copy the provided `wordcount.c` file into the directory, or create a new file called `wordcount.c` and paste the following content into it exactly as shown. Do not modify it. Save the file (`Ctrl+S`).

```c
/*
 * wordcount.c
 *
 * A small text statistics utility. Given a path to a text file, prints
 * the number of lines, words, and characters, the length of the longest
 * line, and the average word length.
 *
 * Build:  gcc -Wall -Wextra -o wordcount wordcount.c
 * Usage:  ./wordcount <path-to-text-file>
 *
 * Exit codes:
 *   0  success
 *   1  usage error
 *   2  file could not be opened
 *   3  out of memory
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define INITIAL_LINE_CAPACITY 128

/*
 * Aggregated statistics for one input file. All counts are non-negative.
 * average_word_length is 0.0 when word_count is 0.
 */
typedef struct {
    long line_count;
    long word_count;
    long char_count;
    long longest_line;
    double average_word_length;
} FileStats;

/*
 * Read one line from `stream` into a dynamically-allocated buffer.
 * The buffer grows as needed and is returned through *line_out.
 * The caller owns the returned buffer and must free() it.
 *
 * Returns the number of characters read (excluding the terminating
 * newline, if any), or -1 on end of file with no characters read,
 * or -2 on allocation failure.
 */
static long read_line(FILE *stream, char **line_out) {
    size_t capacity = INITIAL_LINE_CAPACITY;
    size_t length = 0;
    char *buffer = malloc(capacity);
    int c;

    if (buffer == NULL) {
        return -2;
    }

    while ((c = fgetc(stream)) != EOF && c != '\n') {
        if (length + 1 >= capacity) {
            capacity *= 2;
            char *resized = realloc(buffer, capacity);
            if (resized == NULL) {
                free(buffer);
                return -2;
            }
            buffer = resized;
        }
        buffer[length++] = (char)c;
    }

    if (c == EOF && length == 0) {
        free(buffer);
        *line_out = NULL;
        return -1;
    }

    buffer[length] = '\0';
    *line_out = buffer;
    return (long)length;
}

/*
 * Count the words in a null-terminated string. A "word" is a maximal
 * run of non-whitespace characters. Also adds the total length of all
 * word characters to *total_word_chars so the caller can compute the
 * average word length across an entire file.
 */
static long count_words(const char *line, long *total_word_chars) {
    long words = 0;
    int in_word = 0;
    long word_len = 0;

    for (const char *p = line; *p != '\0'; p++) {
        if (isspace((unsigned char)*p)) {
            if (in_word) {
                words++;
                *total_word_chars += word_len;
                word_len = 0;
                in_word = 0;
            }
        } else {
            in_word = 1;
            word_len++;
        }
    }
    if (in_word) {
        words++;
        *total_word_chars += word_len;
    }
    return words;
}

/*
 * Walk the input file, accumulating statistics into *stats.
 * Returns 0 on success, non-zero on error (see exit codes at top).
 */
static int analyze_file(FILE *input, FileStats *stats) {
    char *line = NULL;
    long line_length;
    long total_word_chars = 0;

    stats->line_count = 0;
    stats->word_count = 0;
    stats->char_count = 0;
    stats->longest_line = 0;
    stats->average_word_length = 0.0;

    while ((line_length = read_line(input, &line)) >= 0) {
        stats->line_count++;
        stats->char_count += line_length;
        if (line_length > stats->longest_line) {
            stats->longest_line = line_length;
        }
        stats->word_count += count_words(line, &total_word_chars);
        free(line);
        line = NULL;
    }

    if (line_length == -2) {
        return 3;
    }

    if (stats->word_count > 0) {
        stats->average_word_length =
            (double)total_word_chars / (double)stats->word_count;
    }

    return 0;
}

/*
 * Print a FileStats to stdout in a fixed, human-readable layout.
 */
static void print_stats(const char *path, const FileStats *stats) {
    printf("File:                %s\n", path);
    printf("Lines:               %ld\n", stats->line_count);
    printf("Words:               %ld\n", stats->word_count);
    printf("Characters:          %ld\n", stats->char_count);
    printf("Longest line:        %ld\n", stats->longest_line);
    printf("Average word length: %.2f\n", stats->average_word_length);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <path-to-text-file>\n", argv[0]);
        return 1;
    }

    const char *path = argv[1];
    FILE *input = fopen(path, "r");
    if (input == NULL) {
        fprintf(stderr, "Error: could not open '%s'\n", path);
        return 2;
    }

    FileStats stats;
    int result = analyze_file(input, &stats);
    fclose(input);

    if (result != 0) {
        fprintf(stderr, "Error: out of memory while reading file\n");
        return result;
    }

    print_stats(path, &stats);
    return 0;
}
```

### Step 1.3: Confirm Copilot is ready

1. Open the Chat view (`Ctrl+Alt+I`).
2. Confirm the model picker reads **Claude Sonnet 4.6**.
3. Switch the chat mode dropdown to **Ask**. You will stay in Ask mode for the entire lab.

### Step 1.4: Open the program in the editor

Click on `wordcount.c` in the file explorer so it becomes Copilot's active-file context. The active editor tab is automatically attached as context to your chat prompts.

---

## Part 2: Top-Down Understanding

Before diving into individual functions, get the big picture. This is the most important habit when reading unfamiliar code: never start at line 1 and read straight through. Start with a high-level summary and drill down only where you need to.

### Question 2.1: What does this program do?

In the Chat view, type:

```
#file:wordcount.c In two short paragraphs, explain what this program does
from the user's point of view. What does it take as input, what does it
output, and what does a typical session look like?
```

**What to look for in the response:**
- A clear statement that it takes a file path as a command-line argument.
- A list of the five statistics it produces (lines, words, characters, longest line, average word length).
- A note that it writes results to stdout and errors to stderr.

Copy the response into your lab notebook. This is your "elevator pitch" understanding of the program. Everything else in this lab refines it.

### Question 2.2: What is the overall structure?

```
What functions does this program define, and how do they call each other?
Draw the call graph in plain text or ASCII art.
```

**What to look for in the response:**
- A list of the five functions: `read_line`, `count_words`, `analyze_file`, `print_stats`, `main`.
- A call graph showing that `main` calls `analyze_file` and `print_stats`; `analyze_file` calls `read_line` and `count_words`.
- A note that `read_line`, `count_words`, `analyze_file`, and `print_stats` are all marked `static`, so they are private to this translation unit.

This call graph is your roadmap. Sketch it in your lab notebook by hand. You will refer back to it.

### Question 2.3: What does each function do, in one sentence?

```
Give a one-sentence description of each function in this program. Do not
explain how they work yet, just what they do.
```

**What to look for in the response:**
- `read_line`: reads one line from a stream into a dynamically-allocated buffer.
- `count_words`: counts whitespace-separated words in a string and also accumulates total word characters.
- `analyze_file`: walks the file line by line and aggregates statistics into a `FileStats`.
- `print_stats`: prints a `FileStats` in a fixed human-readable layout.
- `main`: parses arguments, opens the file, drives the analysis, prints results, returns an exit code.

You now have a complete top-down understanding of the program. Time to drill in.

---

## Part 3: Function-by-Function Deep Dive

For each function below, the lab gives you a focused prompt to ask Copilot. The expected response section tells you what a good answer looks like, so you can judge whether Copilot's explanation matches the code. **If Copilot's explanation does not match the code, the code is what is correct.** Always verify against the source.

### Question 3.1: `read_line` and dynamic buffer growth

```
Explain the read_line function in detail. Walk me through what happens
when the input line is short, when it is exactly INITIAL_LINE_CAPACITY
characters, and when it is very long (say, 10 kilobytes). Also explain
why the function uses both malloc and realloc.
```

**What to look for in the response:**
- For short lines: the initial 128-byte buffer is enough and no resizing happens.
- For lines around 128 bytes: when `length + 1 >= capacity`, the function doubles the capacity with `realloc`.
- For very long lines: the buffer keeps doubling (256, 512, 1024, ...) until it can hold the line. This is the classic "amortized O(1) per character" growth strategy.
- The reason for `malloc` followed by `realloc`: `malloc` allocates the initial buffer; `realloc` is used to grow it because `realloc` preserves the existing contents (a fresh `malloc` would not).

**Verification:** Look at lines around the `capacity *= 2` and `realloc` calls. Confirm Copilot's explanation matches what those lines actually do.

### Question 3.2: The three-way return convention

```
The read_line function returns either a non-negative length, -1, or -2.
What does each return value mean, and why did the author choose this
three-way convention instead of, say, returning 0 on success and -1 on
any error?
```

**What to look for in the response:**
- Non-negative: a line was read (possibly empty, just a newline); the length is the number of characters read.
- -1: end of file reached with no characters read. This is different from a zero-length line because zero-length means "the line was just `\n`," while -1 means "there is no more input at all."
- -2: out-of-memory failure during allocation.
- The reason: the caller needs to distinguish "no more lines, stop the loop normally" from "real error, propagate it up." A single error sentinel cannot carry that distinction.

This is an example of a recurring C idiom: encoding multiple states into the return value of a function that also returns a count.

### Question 3.3: `count_words` and the state machine

```
Walk me through count_words. What state is the function tracking with
the in_word variable, and why is it necessary? What happens for the
following inputs:
  - "hello"
  - "hello world"
  - "   hello   world   "
  - ""
```

**What to look for in the response:**
- `in_word` is a one-bit state machine: "am I currently inside a word, or between words?"
- It is necessary because the function counts *transitions out of a word* as it scans, not characters. Without `in_word`, runs of multiple spaces would each look like word boundaries.
- For `"hello"`: enters in_word at `h`, scans `hello`, hits end of string while still in_word, the trailing `if (in_word)` block counts the word. Result: 1 word.
- For `"hello world"`: counts `hello` at the space, then enters in_word for `world`, end-of-string block counts `world`. Result: 2 words.
- For `"   hello   world   "`: leading and trailing spaces do nothing because `in_word` is 0. The middle space sequence triggers the word count exactly once between words. Result: 2 words.
- For `""`: loop never executes, `in_word` stays 0, end-of-string block does nothing. Result: 0 words.

**Verification:** This is a good place to mentally trace the code. Pick `"hello world"` and walk through the loop one character at a time. Confirm Copilot's trace.

### Question 3.4: The double-pointer trick in `count_words`

```
The count_words function takes a parameter called total_word_chars as a
pointer (long *). Why is this a pointer instead of a return value? What
pattern does this follow, and where else in this program do you see it?
```

**What to look for in the response:**
- The function already returns a value (the word count), so it cannot also return the total characters without an aggregate type.
- The author chose to pass `total_word_chars` as a pointer so the caller can accumulate across multiple calls (one per line) into a single running total.
- This is the C idiom of "in-out parameters": the function reads the current value and writes back an updated value.
- The same pattern appears in `read_line`'s `char **line_out` parameter, which returns the allocated buffer.
- And in `analyze_file`'s `FileStats *stats` parameter, which is filled in by the function.

### Question 3.5: `analyze_file` and the main loop

```
Walk me through analyze_file's main loop. How does it know when to stop?
How does it handle an out-of-memory error mid-file? Why does it set
line to NULL after free(line)?
```

**What to look for in the response:**
- The loop stops when `read_line` returns a negative value (`-1` for EOF or `-2` for OOM).
- The `while ((line_length = read_line(...)) >= 0)` test does both the read and the check in one expression.
- After the loop, the function checks `if (line_length == -2)` and returns error code 3 if an allocation failed.
- `line = NULL` after `free(line)` is defensive programming: it prevents a double-free if the code is later modified. The current loop overwrites `line` on every iteration, but the explicit nulling makes the intent clear and is a habit worth keeping in C.

### Question 3.6: `print_stats` and the const-ness

```
print_stats takes both parameters as const pointers. What does const
mean on each one, and what would change if they were not const?
```

**What to look for in the response:**
- `const char *path` means the function will not modify the characters that `path` points to.
- `const FileStats *stats` means the function will not modify the `FileStats` structure it points to.
- Removing `const` would still compile and run correctly, but it would weaken the function's contract. With `const`, the function declares to its callers (and to the compiler) that it is read-only with respect to its inputs. The compiler will reject any code inside the function that tries to mutate them.
- This is a small example of "encode invariants in the type system" which is a recurring C and C++ theme.

### Question 3.7: `main` and the error flow

```
Walk me through main. List every place where main can return early, what
exit code it returns, and what cleanup happens before the return.
```

**What to look for in the response:**
- Early return with exit code 1: wrong number of arguments. No cleanup needed because nothing has been allocated yet.
- Early return with exit code 2: `fopen` returned NULL. No cleanup needed.
- Early return with exit code 3: `analyze_file` returned non-zero (out of memory). `fclose(input)` has already been called before this check, so the file is closed.
- Normal return with exit code 0: `print_stats` runs to completion, return 0.
- The structure is a classic "structured programming" pattern: each error has a single, clearly-marked exit point, and resources are released in reverse order of acquisition.

---

## Part 4: Design and Idiom Questions

Now that you understand *what* the code does, ask Copilot about *why* it was written this way. These questions are about idiom, style, and design choices.

### Question 4.1: Why a struct return aggregate?

```
analyze_file fills in a FileStats struct rather than returning multiple
values directly. C does not have tuple return types like Python or Go.
What are the alternatives, and why is the struct-out-parameter approach
a good choice here?
```

**What to look for in the response:**
- Alternative 1: return one value and use global variables for the others. Bad: globals make the function non-reentrant and harder to test.
- Alternative 2: take five separate `long *` out parameters. Bad: cluttered signature, easy to mix up at call sites.
- Alternative 3: heap-allocate a struct and return a pointer. Adds an allocation and a `free` for no benefit when the caller has perfectly good stack space.
- The chosen approach (caller-allocated struct, function fills it in) is the C idiom. It is zero-cost, keeps the data together, and the caller controls the lifetime.

### Question 4.2: Static functions

```
Four of the five functions are declared `static`. What does static mean
here, and what would change if it were removed?
```

**What to look for in the response:**
- At file scope, `static` gives a function *internal linkage*, meaning it is not exposed to other translation units. The function is private to `wordcount.c`.
- Without `static`, the function would have external linkage and be callable from any other `.c` file linked into the program.
- This is an information-hiding technique. In a multi-file project, marking helper functions `static` keeps the public surface of each file minimal and prevents accidental coupling.

### Question 4.3: Why the cast to `unsigned char` in `isspace`?

```
In count_words, the call is isspace((unsigned char)*p). Why the cast?
What would happen without it?
```

**What to look for in the response:**
- `isspace` (and the rest of `<ctype.h>`) takes an `int` whose value must be either `EOF` or representable as an `unsigned char`.
- `*p` is a `char`, and on platforms where `char` is signed (most platforms by default), a byte with the high bit set becomes a negative `int` when implicitly promoted.
- Passing a negative value (other than `EOF`) to `isspace` is undefined behavior. The cast to `unsigned char` first ensures the value is in `[0, 255]`, then the implicit promotion to `int` is harmless.
- This is one of the most common subtle bugs in C code that processes non-ASCII bytes. The cast is the standard fix and is recommended by the C standard library documentation.

### Question 4.4: What if the file ends without a newline?

```
What happens if the input file does not end with a newline character?
Does the last line get counted? Walk through the code to justify your
answer.
```

**What to look for in the response:**
- `read_line` reads bytes until either `\n` or `EOF`.
- If the file ends with `"goodbye"` (no trailing newline), `fgetc` returns each character of `"goodbye"`, accumulates them into the buffer, then returns `EOF`.
- The loop exits with `length == 7` and `c == EOF`.
- The check `if (c == EOF && length == 0)` is false (length is 7), so the function falls through to the `buffer[length] = '\0'` line and returns 7.
- The caller (`analyze_file`) sees a non-negative return and processes the line normally.
- On the *next* call, `fgetc` immediately returns EOF, `length` is 0, the function returns -1, and the loop terminates.
- So yes, the final line is counted, even without a trailing newline. This is correct behavior matching `wc(1)`.

### Question 4.5: Could this be simpler?

```
The standard C library has fgets, which reads a line into a fixed-size
buffer. Why didn't the author use fgets instead of writing read_line by
hand?
```

**What to look for in the response:**
- `fgets` requires a fixed maximum line length. If a line in the input is longer than the buffer, `fgets` truncates and the caller has to detect and handle the truncation by checking the last character.
- The author wanted to support arbitrarily long lines without imposing a limit, so they wrote a buffer-growing loop.
- This is a real trade-off. `fgets` is simpler but imposes a maximum line length. A growing buffer handles any input but is more code and uses dynamic allocation.
- For a general-purpose tool that might be pointed at any text file (including pathological ones), the growing-buffer approach is the right call.

---

## Part 5: Verify Your Understanding

You have now built a model of this program through conversation. Test that model against the actual code.

### Step 5.1: Predict the output

Without running the program, predict what it will print for this input:

```
hello world
  goodbye   cruel   world
```

(That is two lines. The first has two words separated by one space. The second has three words separated by multiple spaces, with leading whitespace.)

Write down your predictions for all five statistics in your lab notebook. Be specific: what is the longest-line value? What is the average word length?

### Step 5.2: Verify by running

If you have `gcc` installed, compile and run the program:

```bash
gcc -Wall -Wextra -o wordcount wordcount.c
cat > input.txt <<EOF
hello world
  goodbye   cruel   world
EOF
./wordcount input.txt
```

Compare the output to your predictions. If anything is different, do not assume the program is wrong. Reread the relevant function and figure out which assumption you got wrong. **This is the moment where your understanding becomes real.**

> **Expected output (for reference):**
> ```
> File:                input.txt
> Lines:               2
> Words:               5
> Characters:          37
> Longest line:        26
> Average word length: 5.80
> ```
> Notable: the leading whitespace on line 2 *is* counted in `Characters` and in `Longest line` because both include all bytes. The leading whitespace does *not* contribute to `Words` or `Average word length`. Did your predictions match?

### Step 5.3: A targeted Copilot question

If your prediction was wrong, ask Copilot one final question, copying in the part of the code you misread:

```
I expected this code to do X, but it actually does Y. Where in the code
is the behavior I missed, and what did I misunderstand?
```

This kind of "verify against reality, then ask for explanation" loop is the most powerful use of Copilot. It uses the AI as a tutor rather than as an oracle.

---

## Part 6: Reflection

Answer the following in your lab notebook:

1. **Top-down vs. bottom-up.** This lab structured the analysis from high-level summary (Part 2) down to individual lines (Part 3). What did you gain from going in that order? What would have been different if you had started by reading line 1 of the file straight through?

2. **The role of comments.** This program has substantial header comments on each function describing its contract. How much of your understanding came from those comments, how much from Copilot, and how much from the code itself? In a code review, would you have asked for more, fewer, or different comments?

3. **Verifying Copilot.** Pick one Copilot answer from earlier in the lab and explain, line by line, how you would verify it against the source. What part of the response is grounded in the actual code, and what part is Copilot's general C knowledge being applied?

4. **Prompt patterns.** Across all the questions you asked in this lab, which type of prompt elicited the most useful explanations? Was it the high-level ones, the function-by-function ones, the idiom-oriented "why did the author do it this way" ones, or the prediction-and-verify ones? If you were reading another unfamiliar program tomorrow, what order would you ask the questions in?

5. **When to stop asking.** At what point during the lab did you feel you had "enough" understanding of the program? Could you, right now, write a one-page document explaining this program to a new team member? If yes, do it.

---

## Reference: Useful Patterns for Reading Unfamiliar Code

These prompt patterns are reusable across any language and codebase.

| Pattern | Example wording | When to use |
|---------|-----------------|-------------|
| **Elevator pitch** | "In two paragraphs, explain what this program/file does from the user's point of view." | Always your first question. Reveals whether Copilot understood the high-level intent. |
| **Call graph** | "What functions/classes/methods does this define and how do they call each other? Draw a call graph." | Your roadmap for the rest of the analysis. |
| **One-sentence summaries** | "Give a one-sentence description of each function. Just what it does, not how." | Builds your mental index before you go deep. |
| **Walk-through a specific scenario** | "Walk me through function X when the input is Y. What happens at each step?" | The single most reliable way to test whether Copilot (and you) understand a function. |
| **Why this idiom?** | "Why did the author use X instead of Y here?" | Surfaces design decisions and constraints that are not visible in the code itself. |
| **What if the input is...?** | "What happens if the file is empty? Has one line? Has no trailing newline?" | Forces edge-case reasoning, which is where bugs usually hide. |
| **Predict, then verify** | (After reading): "Predict the output for input X." Then run and compare. | Converts "I think I understand" into actual understanding. |
| **Targeted recovery** | "I expected X but the code does Y. Where did I misunderstand?" | Use after a failed prediction. The most efficient way to learn. |

---

## Troubleshooting

**Copilot's explanation contradicts the code.**
Trust the code, not Copilot. LLMs occasionally generate plausible-sounding explanations that do not match the actual source. If something feels off, pick a specific function or line and ask Copilot to walk through it step by step. If the walk-through still does not match the code, your analysis is correct and Copilot's high-level summary was wrong.

**Copilot's response is generic and not specific to this file.**
Make sure `wordcount.c` is the active editor tab (click it in the explorer), and use the `#file:wordcount.c` reference at the start of your prompt. Without the file context, Copilot may answer about C in general rather than about this specific program.

**Copilot suggests changes to the code in Ask mode.**
Sometimes Copilot will volunteer suggestions like "you could improve this by..." even in Ask mode. That is fine, but it is outside the scope of this lab. Stay focused on understanding what the code does, not what it could be.

**The chat seems to forget what you asked earlier.**
Long chat sessions can lose context as they grow. If Copilot stops referring back to earlier discussion, start a new chat with `/clear` and re-attach the file with `#file:wordcount.c` at the start of your next prompt.

---

## Further Reading

- C Programming Language (Kernighan and Ritchie), Chapter 5: Pointers and Arrays
- Modern C (Jens Gustedt), available free online, for idiomatic modern C style
- GNU coding standards: <https://www.gnu.org/prep/standards/>
- Copilot documentation on the Ask mode: <https://code.visualstudio.com/docs/copilot/chat/chat-modes>
