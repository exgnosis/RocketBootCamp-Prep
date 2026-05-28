# Lab 4-1: Linux Commands

## Overview

The Linux command line is the closest thing the software industry has to a universal lingua franca. The terminal you open on a Mac, the SSH session you start on an AWS server, the shell inside a Docker container, the build environment in GitHub Actions, the WSL environment on Windows; all of these are running variations of the same handful of commands, with the same flags, the same arguments, the same conventions. Learning these commands well pays back for the rest of your career, regardless of which language you write or which platform you target.

This lab walks you through thirty short exercises that cover the commands you will use every day: navigating the filesystem, creating and reading files, searching for content, checking permissions, and a few utilities for inspecting your environment. The exercises are small (one or two lines each) and independent (later exercises do build on the directory you create in the first, but each one can be tested on its own). The point is volume: you build muscle memory for the everyday commands by typing them yourself, watching them work, and noticing the small details that the man pages do not advertise.

The lab is therefore part **typing exercise** (build the muscle memory), part **noticing exercise** (each command produces output with structure; learn to read that structure), and part **discipline exercise** (try the command on your own before reading the answer).

**This lab is hands-on.** You type the commands yourself; no AI assistance is needed or expected for the main exercises. A short stretch step at the end (Part 7) discusses when asking Copilot for a command is the right move and when it is not.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Navigate the filesystem with `cd`, `pwd`, and `ls`, and understand the difference between absolute and relative paths.
2. Create, copy, move, rename, and remove files and directories.
3. View file contents with `cat`, count lines and words with `wc`, sort and deduplicate with `sort` and `uniq`.
4. Search the filesystem with `find` and search file contents with `grep`.
5. Read and modify file permissions with `ls -l` and `chmod`, and identify your user and group with `whoami` and `id`.
6. Use shell features like wildcards, hidden files, symbolic links, environment variables, and the manual pages.
7. Recognize when a command's output has more structure than it appears to (columns, ordering, trailing whitespace), and read that structure deliberately.

---

## Part 1: Set Up the Workspace

### Step 1.1: Open a terminal

The exercises in this lab all run in a terminal. You have several options depending on your environment:

- **macOS**: open the Terminal app (in `Applications > Utilities`), or use the integrated terminal in VS Code (`` Ctrl+` `` or `View > Terminal`).
- **Linux**: open your distribution's terminal application, or use VS Code's integrated terminal.
- **Windows**: use **Windows Subsystem for Linux** (WSL) and open an Ubuntu terminal, or use VS Code's integrated terminal with a WSL profile selected. The native Windows Command Prompt and PowerShell use different commands and will not work for this lab.

If you are on Windows without WSL installed, follow Microsoft's instructions at <https://learn.microsoft.com/windows/wsl/install> to install it before starting the exercises. WSL takes 5 to 10 minutes to install.

### Step 1.2: Confirm you are in a bash-compatible shell

In the terminal:

```bash
echo "$BASH_VERSION"
```

If you see a version number (something like `5.1.16(1)-release`), you are in `bash` and ready to proceed. If you see nothing (an empty line), you may be in `zsh` (the default on recent macOS) or another shell. Almost all the commands in this lab work identically in `zsh`; the one exception is the `type -a` command in Exercise 25, which behaves slightly differently. The lab calls out where this matters.

### Step 1.3: Create a lab notebook

Create a file called `notebook.md` in your home directory. Run:

```bash
touch ~/notebook.md
```

You will record observations and reflections in this file as you work through the exercises. Open it in your editor of choice (VS Code, vim, nano, etc.); each exercise group below has a small note about what to record.

### Step 1.4: How to use the exercise sections

Each numbered exercise that follows is structured the same way:

- **Problem**: a one-sentence task.
- **Try it yourself**: a place for you to attempt the command before looking at the answer.
- **Solution**: the canonical command (revealed when you peek).
- **Expected output**: what you should see, or what kind of output to expect.
- **Why this matters**: a one-sentence note about when this command is useful in real work.

**The discipline of this lab is "try first, peek second."** For each exercise, attempt the command without reading the Solution. Compare your attempt to the Solution. Note in your notebook the exercises where your first attempt was different from the canonical answer (different flags, different syntax, completely different approach). Those are the ones to remember.

---

## Part 2: Navigation and Listing (Exercises 1-5)

### Exercise 1: Create a sandbox

**Problem:** Create a directory called `linux-lab` in your home folder and change into it.

**Solution:**

```bash
mkdir -p ~/linux-lab
cd ~/linux-lab
```

**Why this matters:** Every Linux project starts with two questions: where will the files live, and where is the shell pointed? `mkdir -p` creates the directory (the `-p` flag means "create parent directories if needed and do not error if the directory already exists"), and `cd` changes the shell's current directory.

---

### Exercise 2: Where am I?

**Problem:** Show the absolute path of your current directory.

**Solution:**

```bash
pwd
```

**Expected output:** A path like `/home/you/linux-lab` (Linux/WSL) or `/Users/you/linux-lab` (macOS).

**Why this matters:** `pwd` ("print working directory") is the first command to type when you are confused about where commands will run. Most file-related commands operate relative to the current directory; if you do not know where that is, you do not know what your commands will do.

---

### Exercise 3: What's here?

**Problem:** List the contents of the current directory.

**Solution:**

```bash
ls -1
```

**Expected output:** Nothing yet (the directory is empty). After Exercise 4 the output will be three lines (`notes`, `projects`, `temp`).

**Why this matters:** `ls` is the most-used command on Linux, second only to `cd`. The `-1` flag (digit one, not letter L) forces one entry per line, which is easier to read than the default columnar layout when you are scripting.

---

### Exercise 4: Make some structure

**Problem:** Create subdirectories `projects`, `notes`, and `temp`.

**Solution:**

```bash
mkdir -p projects notes temp
```

**Verify** with `ls -1`:

```
notes
projects
temp
```

**Why this matters:** `mkdir` accepts multiple arguments and creates all of them in one call. Notice that `ls -1` returns the entries in alphabetical order, not in the order you passed them to `mkdir`.

---

### Exercise 5: Create a couple of files

**Problem:** In `notes`, create empty files `intro.txt` and `todo.txt`.

**Solution:**

```bash
touch notes/intro.txt notes/todo.txt
```

**Verify:**

```bash
ls -l notes
```

**Why this matters:** `touch` does two jobs: if a file does not exist, it creates it with zero bytes; if it does exist, it updates its modification timestamp. The first job is useful for placeholder files; the second is useful for invalidating cached build artifacts.

---

> **Notebook note for Part 2.** After completing exercises 1-5, write in your notebook: which command surprised you, and why? Was it the `-p` flag's "no error if it exists" behavior, the alphabetical sorting of `ls`, or something else?

---

## Part 3: Files and Content (Exercises 6-12)

### Exercise 6: Add text

**Problem:** Put the text *Welcome to Linux* into `notes/intro.txt`.

**Solution:**

```bash
echo "Welcome to Linux" > notes/intro.txt
```

**Why this matters:** The `>` operator redirects standard output to a file, replacing the file's contents if it exists. `>>` (two characters) would *append* instead. The single-character form is destructive; check twice before using it on a file that has content you care about.

---

### Exercise 7: View a file

**Problem:** Display the contents of `notes/intro.txt`.

**Solution:**

```bash
cat notes/intro.txt
```

**Expected output:**

```
Welcome to Linux
```

**Why this matters:** `cat` ("concatenate") prints the contents of one or more files to standard output. For one file, it is essentially "show me this file." For multiple files, it joins them in order. Use `less` instead for large files; it pages instead of dumping.

---

### Exercise 8: Hidden files

**Problem:** Create a hidden file `.hidden` and list all files, including hidden ones.

**Solution:**

```bash
touch .hidden
ls -la
```

**Expected output** (yours will have your username and current date):

```
total 20
drwxr-xr-x  5 you you 4096 May 28 21:37 .
drwxrwxrwt 11 you you 4096 May 28 21:37 ..
-rw-r--r--  1 you you    0 May 28 21:37 .hidden
drwxr-xr-x  2 you you 4096 May 28 21:37 notes
drwxr-xr-x  2 you you 4096 May 28 21:37 projects
drwxr-xr-x  2 you you 4096 May 28 21:37 temp
```

**Why this matters:** Filenames starting with `.` are hidden from default `ls` output, by convention only. The `-a` flag ("all") shows them. The two extra entries `.` and `..` are the current directory and its parent; they exist on every directory by convention.

---

### Exercise 9: Move around

**Problem:** Change into `notes`, list its contents, then return to the lab root.

**Solution:**

```bash
cd notes
ls
cd ..
```

**Why this matters:** `cd ..` moves up one level. `cd -` (a different shortcut) jumps back to wherever you were before the last `cd`. Both are useful when you are bouncing between two directories repeatedly.

---

### Exercise 10: Absolute path

**Problem:** Print the absolute path of the `notes` directory.

**Solution:**

```bash
realpath notes
```

**Expected output:** Something like `/home/you/linux-lab/notes`.

**Why this matters:** A *relative* path (`notes` or `./notes`) is interpreted relative to the current directory; an *absolute* path starts with `/` and is unambiguous. When you write scripts that may be run from different working directories, resolving paths to their absolute form with `realpath` is the safe move.

---

### Exercise 11: Copy a file

**Problem:** Copy `notes/intro.txt` to `temp/intro_copy.txt`.

**Solution:**

```bash
cp notes/intro.txt temp/intro_copy.txt
```

**Verify** with `cat temp/intro_copy.txt`. The copy should have the same contents as the original.

**Why this matters:** `cp` ("copy") takes a source and a destination. To copy a directory and its contents, add `-r` for "recursive". To preserve permissions and timestamps, add `-p` for "preserve".

---

### Exercise 12: Rename a file

**Problem:** Rename `notes/todo.txt` to `notes/tasks.txt`.

**Solution:**

```bash
mv notes/todo.txt notes/tasks.txt
```

**Why this matters:** `mv` ("move") is the rename command on Linux; there is no separate `rename`. A move within a single filesystem is essentially a rename of a directory entry, which is why moving even a huge directory inside the same disk completes instantly.

---

> **Notebook note for Part 3.** Try this: `echo "second line" > notes/intro.txt` (note: `>`, not `>>`). What happened to the original "Welcome to Linux" content? Restore it with `echo "Welcome to Linux" > notes/intro.txt` before continuing. The point is that `>` is destructive; the only protection is care.

---

## Part 4: Structure and Search (Exercises 13-16)

### Exercise 13: Nested directories

**Problem:** Inside `projects`, create `app/src`.

**Solution:**

```bash
mkdir -p projects/app/src
```

**Why this matters:** Without `-p`, `mkdir` would fail if `projects/app` did not yet exist. With `-p`, it creates each missing parent in turn. The "-p" stands for "parents".

---

### Exercise 14: Directory tree

**Problem:** Show the directory layout (top 3 levels).

**Solution:**

```bash
find . -maxdepth 3 -type d
```

**Expected output:**

```
.
./projects
./projects/app
./projects/app/src
./notes
./temp
```

**Why this matters:** `find` is the workhorse tool for "give me a list of files matching a description." The `.` is the directory to start from, `-maxdepth 3` limits how deep to recurse, and `-type d` restricts to directories (not files). Combining these gives you a tree-like view without installing the `tree` command separately.

---

### Exercise 15: Find by name

**Problem:** Find all `.txt` files under the lab directory.

**Solution:**

```bash
find . -type f -name "*.txt"
```

**Expected output:**

```
./notes/intro.txt
./notes/tasks.txt
./temp/intro_copy.txt
```

**Why this matters:** Quoting the glob pattern (`"*.txt"`, not `*.txt`) is important; without quotes, the shell expands the glob *before* passing it to `find`, and `find` may receive the wrong arguments (or none at all, if no files match in the current directory). Always quote glob patterns that are intended for `find` to interpret.

---

### Exercise 16: Find text

**Problem:** Search for the word "Linux" in all files under the lab directory.

**Solution:**

```bash
grep -R "Linux" .
```

**Expected output:**

```
./notes/intro.txt:Welcome to Linux
./temp/intro_copy.txt:Welcome to Linux
```

**Why this matters:** `grep` searches text by line. `-R` (or `-r`) makes it recursive; without it, `grep` does not descend into subdirectories. The output format `path:matching-line` is the convention that every developer eventually learns to skim quickly. For programming work, you will use `grep` constantly to find which file defines what.

---

> **Notebook note for Part 4.** Try `find . -name "intro*"`. What's the difference between this and Exercise 15's pattern? What if you wanted only files modified in the last hour? (Hint: `man find` and search for `-mmin`.)

---

## Part 5: Counts, Sizes, Permissions (Exercises 17-23)

### Exercise 17: Count lines

**Problem:** Show line, word, and byte counts for `notes/intro.txt`.

**Solution:**

```bash
wc notes/intro.txt
```

**Expected output:**

```
 1  3 17 notes/intro.txt
```

The three numbers are lines, words, and bytes in that order; the filename is at the end. For just one of the three, use `-l` (lines), `-w` (words), or `-c` (bytes).

**Why this matters:** `wc` is the right tool for "how big is this file" when you mean lines or words, not bytes. For very large logs, `wc -l` is faster than opening the file in an editor.

---

### Exercise 18: Sort and unique

**Problem:** Create `names.txt` with duplicates, then show unique sorted names.

**Solution:**

```bash
printf "Ada\nBob\nAda\nLinus\nBob\n" > names.txt
sort names.txt | uniq
```

**Expected output:**

```
Ada
Bob
Linus
```

**Why this matters:** `uniq` only collapses *adjacent* duplicate lines, which is why you almost always pipe `sort` into it. `sort -u` does both jobs in one command and is shorter for this common case. Pipelines like this one (`sort | uniq` or `sort -u`) are the heart of Unix-style scripting: small tools that each do one thing, composed with `|`.

---

### Exercise 19: Directory size

**Problem:** Show the total disk usage of the current directory.

**Solution:**

```bash
du -sh .
```

**Expected output:** Something like `36K	.` (the unit is human-readable; small directories will be `K`, larger ones `M` or `G`).

**Why this matters:** `du` ("disk usage") and `df` ("disk free") are the two commands for "where is my disk space going". `du -sh` summarizes; without `-s` it lists every subdirectory. Use this when something fills up your laptop and you do not know what.

---

### Exercise 20: Free space

**Problem:** Display free space for the filesystem.

**Solution:**

```bash
df -h .
```

**Expected output** (yours will look different):

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       100G   45G   55G  45% /
```

**Why this matters:** `df -h` is the first command to run when an operation fails with "no space left on device". The `.` argument tells `df` to report the filesystem containing the current directory.

---

### Exercise 21: Permissions

**Problem:** List permissions for everything in `notes`.

**Solution:**

```bash
ls -l notes
```

**Expected output:**

```
total 4
-rw-r--r-- 1 you you 17 May 28 21:37 intro.txt
-rw-r--r-- 1 you you  0 May 28 21:37 tasks.txt
```

The first column is the permission string: a leading character (`-` for file, `d` for directory, `l` for symlink) followed by three groups of three (read, write, execute for the owner, the group, and everyone else).

**Why this matters:** Every Linux file has owner/group/other permissions plus a user owner and a group owner. The permission string is the most compact way to read this information; learn to scan it.

---

### Exercise 22: Change permissions

**Problem:** Make `notes/intro.txt` readable and writable by you only.

**Solution:**

```bash
chmod 600 notes/intro.txt
```

**Verify:**

```bash
ls -l notes/intro.txt
```

Should show `-rw-------` (owner read/write, group and other nothing).

**Why this matters:** The three-digit octal form (`600`) is the most concise way to set permissions: read=4, write=2, execute=1, summed for each of owner/group/other. `600` is owner-read-write only. `644` is owner-read-write + group/other read. `755` is owner-everything + group/other read-execute (typical for scripts).

---

### Exercise 23: Who am I?

**Problem:** Show your username and user/group IDs.

**Solution:**

```bash
whoami
id
```

**Expected output:** Your username on the first line, and a line like `uid=1000(you) gid=1000(you) groups=1000(you),27(sudo)` on the second.

**Why this matters:** Permission-related debugging usually starts here. "The file is owned by `root` and you are `you`; that is why your write failed." `id` is the more complete answer; `whoami` is the quick version.

---

> **Notebook note for Part 5.** Run `chmod 000 notes/intro.txt`, then try to `cat` it. What error do you get? Restore with `chmod 644 notes/intro.txt`. This is the simplest demonstration of permissions actually being enforced.

---

## Part 6: Links, Environment, Help, Cleanup (Exercises 24-30)

### Exercise 24: Symbolic link

**Problem:** Create `intro.link` pointing to `notes/intro.txt`.

**Solution:**

```bash
ln -s notes/intro.txt intro.link
```

**Verify:**

```bash
ls -l intro.link
```

Should show something like `lrwxrwxrwx 1 you you 15 May 28 21:37 intro.link -> notes/intro.txt`.

**Why this matters:** A symbolic link ("symlink") is a file that contains the path of another file. Reading the link transparently reads the target. Symlinks let you have one file appear in multiple places without duplicating it. The leading `l` in `ls -l` and the `->` notation are the visible signs of a symlink.

---

### Exercise 25: Where is a command?

**Problem:** Show the full path(s) of the `ls` command.

**Solution (bash):**

```bash
type -a ls
```

**Expected output:** Often something like `ls is /usr/bin/ls` or, if your shell has aliased `ls` to add color, `ls is aliased to 'ls --color=auto'` followed by `ls is /usr/bin/ls`.

**Why this matters:** When a command behaves differently than the man page suggests, the cause is often that your shell is using an *alias* (a shortcut that wraps the real command) or a function in your shell config. `type -a` shows every meaning of the name, in order; the first one is what gets executed.

> **A note about shells.** `type -a` is a `bash` builtin. In `zsh` it works similarly. In `dash` and some other minimal shells it does not. If `type -a` fails, try `which -a ls` (which searches the `$PATH` but does not see aliases).

---

### Exercise 26: Environment variables

**Problem:** Print your home directory and list all environment variables.

**Solution:**

```bash
echo "$HOME"
printenv | sort
```

**Why this matters:** Environment variables are the simplest way for a parent process to pass configuration to a child. `$HOME` is your home directory; `$PATH` is the list of directories searched for commands; `$LANG` is your locale. `printenv` lists them all; piping to `sort` makes the long list easier to scan.

---

### Exercise 27: Help and manuals

**Problem:** Show the man page for `ls`, then built-in help for `mkdir`.

**Solution:**

```bash
man ls
mkdir --help
```

`man` opens an interactive pager; press `q` to quit, `/` to search, `n` to find the next match, `Space` to page down.

**Why this matters:** Most Linux commands have both a `man` page (verbose, formal) and a `--help` flag (concise, one screen). The `--help` flag is usually faster when you just want to remember a flag name; `man` is better when you need to understand a command's behavior in depth.

---

### Exercise 28: Wildcards

**Problem:** Copy all `.txt` files from `notes` to `temp`.

**Solution:**

```bash
cp notes/*.txt temp/
```

**Why this matters:** The `*.txt` glob is expanded by the shell *before* `cp` runs, so `cp` actually receives a list of all the matching files as arguments. If no files match, the shell passes the literal `*.txt` to `cp`, which then errors with "No such file or directory". To control this, set `shopt -s nullglob` (so a non-matching glob expands to nothing) or use `find` with `-exec` for safer batch operations.

---

### Exercise 29: Safe remove

**Problem:** Interactively delete `temp/intro_copy.txt`.

**Solution:**

```bash
rm -i temp/intro_copy.txt
```

The `-i` flag means "interactive": `rm` prompts before each deletion. Type `y` to confirm, anything else to skip.

**Why this matters:** `rm` is one of the most dangerous commands on the system because it has no undo. The `-i` flag is the simplest safeguard. Many engineers alias `rm` to `rm -i` in their shell config so that the prompt always appears.

---

### Exercise 30: Cleanup

**Problem:** Delete the entire `linux-lab` directory (with confirmation).

**Solution:**

```bash
cd ~
rm -rI linux-lab
```

`-r` is recursive (descend into directories), `-I` is the "less annoying" interactive flag (prompts once before deleting many files, rather than once per file as `-i` would).

**Why this matters:** The combination `rm -rf /` (with no `-i` or `-I` safeguard) is the canonical "destroy everything" command on Unix. Always be cautious with the `-r` flag; ensure the path is exactly what you intend before pressing Enter. The `-I` flag is a cheap safety net.

---

## Part 7: Stretch: When to Ask Copilot for a Command

GitHub Copilot is in your VS Code chat; you can absolutely ask it "how do I find all files modified in the last hour" and it will give you a `find` invocation. This raises a real question: should you?

Open Copilot Chat (`Ctrl+Alt+I` or `Cmd+Alt+I`). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. Try these three prompts in sequence:

### Prompt A (a command you have just learned)

```
How do I count the number of lines in a file from the Linux command line?
```

You already know the answer (`wc -l filename` from Exercise 17). Compare Copilot's response. Did it give the same command? Did it add useful detail (the `-l` flag, redirecting from stdin, what to do for binary files)? Did it confuse you with unnecessary alternatives?

### Prompt B (a slightly harder thing you have not learned)

```
How do I find all files in the current directory tree that have been
modified in the last hour?
```

Copilot will give you something like `find . -mmin -60`. This is a real `find` flag you have not seen in this lab. Note in your notebook: was the answer correct? Did you trust it without verifying? How could you check?

### Prompt C (a destructive operation)

```
How do I remove every file ending in .log from this entire directory tree?
```

Copilot will give you a `find ... -delete` or `find ... -exec rm` command. Read it carefully before running anything. This is the genre of question where one extra character (a missing dot, an unquoted glob, a misplaced flag) can delete the wrong thing. Whatever Copilot returns:

- Read the command. Do you understand every flag?
- Could you swap `-delete` for `-print` first, run that, and verify the files listed are exactly the ones you want to delete?
- Would you run this command without that verification step?

### The takeaway

There is no universal rule for when to ask Copilot vs. when to type from memory. A useful starting framework:

| Situation | Action |
|-----------|--------|
| Everyday commands you use often | Type from memory. Asking each time slows you down and weakens your retention. |
| A flag you do not remember | Try `command --help \| grep keyword` first. If that does not help, ask Copilot. |
| A new command you have never used | Ask Copilot; then verify by reading the man page for the suggested flags. |
| A destructive operation | Ask Copilot to *describe* what the command will do, run a non-destructive preview first (`-print` instead of `-delete`, `--dry-run` if supported), then run the real command. |

Write in your notebook: which of the three prompts above gave you a clearly correct answer, and which left you uncertain? Did Copilot ever suggest a command you would have considered dangerous?

---

## Part 8: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **The commands you used most.** Across the 30 exercises, which five commands did you use most often? If you had to pick three commands that every junior developer should commit to memory, which would they be, and why?

2. **The flags you keep forgetting.** Which flags surprised you (the `-p` on `mkdir`, the `-R` on `grep`, the `-h` on `df`, the `-I` on `rm`)? Pick the three most useful ones for your typical workflow and write them on a sticky note where you will see them.

3. **The destructive commands.** `rm`, `mv` (when the destination exists), `>` (the redirection that overwrites), `chmod 000`. Which of these has the most damaging potential in your work? What is one practice (an alias, a habit, a verification step) that would protect against it?

4. **The man-page habit.** Did you read any man pages during the lab? If yes, which one was most useful? If no, pick one command from the lab and read its man page now. What did you learn that the exercise did not cover?

5. **Pipes.** Exercise 18 used `sort names.txt | uniq`. The Unix philosophy is "small tools combined with pipes". Look back at the exercises and imagine which two could have been combined with a pipe to do something more interesting (for example, `find . -name "*.txt" | wc -l` to count the number of .txt files). Pick one combination and try it.

6. **Copilot for commands vs. for code.** In earlier labs you used Copilot to generate or analyze code. In Part 7 you used it to recall commands. Was the experience different? Did Copilot make different kinds of mistakes? What does this suggest about where Copilot is most and least valuable?

---

## Reference: The Cheat Sheet

The thirty commands you used in this lab, organized by purpose. Print this section, or copy it to your notebook for later reference.

| Purpose | Command |
|---------|---------|
| Show current directory | `pwd` |
| Change directory | `cd path`, `cd ..`, `cd -`, `cd ~` |
| List files | `ls`, `ls -l`, `ls -la`, `ls -1` |
| Make a directory (and parents) | `mkdir -p path` |
| Make a file (or update timestamp) | `touch file` |
| Remove a file | `rm file`, `rm -i file` |
| Remove a directory tree | `rm -rI dir` |
| Copy a file | `cp src dst`, `cp -r src dst` |
| Move or rename a file | `mv src dst` |
| Show file contents | `cat file`, `less file` |
| Write text to a file (replace) | `echo "text" > file` |
| Append text to a file | `echo "text" >> file` |
| Count lines/words/bytes | `wc file`, `wc -l file` |
| Sort lines | `sort file`, `sort -u file` |
| Show unique adjacent lines | `uniq file` |
| Search file contents | `grep "text" file`, `grep -R "text" dir` |
| Find files by name | `find . -name "pattern"` |
| Find directories | `find . -type d` |
| Show disk usage | `du -sh dir` |
| Show free disk space | `df -h .` |
| Change permissions | `chmod 644 file`, `chmod 755 script` |
| Show user info | `whoami`, `id` |
| Make a symlink | `ln -s target name` |
| Find a command's path | `type -a cmd`, `which cmd` |
| Print environment variable | `echo "$VAR"` |
| List all environment variables | `printenv` |
| Get help on a command | `cmd --help`, `man cmd` |
| Resolve absolute path | `realpath path` |

---

## Reference: Common Pitfalls

Things that bite every new Linux user at least once.

- **`rm` has no undo.** There is no Trash, no Recycle Bin, no "are you sure" by default. Use `-i` or `-I` as a safety net.
- **`>` overwrites; `>>` appends.** They are one character apart and do very different things.
- **`*.txt` is expanded by the shell, not the command.** That means `cp *.txt other_dir/` works only if `*.txt` matches something in the current directory.
- **Spaces in filenames need quotes or escapes.** `cat my file.txt` looks for two files; `cat "my file.txt"` looks for one.
- **`cd` is a shell builtin, not a program.** That is why `cd /tmp` cannot be put inside a script (the script's child shell would `cd` and then exit, leaving the parent shell unchanged). To change directories from a script, `source` the script with `. script.sh` instead of running it.
- **Permissions apply to directories too.** A file you can read can be invisible if its containing directory is unreadable.
- **Hidden files exist by convention only.** `ls -a` shows them. They are not protected; they are just less visible.
- **The current directory is not on `$PATH` by default.** That is why running a script in the current directory requires `./script.sh`, not just `script.sh`. This is a security feature.

---

## Troubleshooting

**`bash: command not found`.**
Either the command is not installed (try `which command` and `apt list --installed 2>/dev/null | grep command-name` on Debian/Ubuntu), or the directory containing it is not on your `$PATH`. On a minimal Docker image many "standard" commands (`vim`, `less`, `tree`, `man`) may not be installed by default.

**The command runs but prints nothing.**
Many commands print nothing on success and only print on error. `mkdir -p existing/path` and `touch existing_file` both succeed silently. The absence of output is usually a good sign.

**`Permission denied`.**
You either lack read/write/execute permission on the file, or you lack execute permission on a directory in the path. Check both with `ls -l file` and `ls -ld containing_dir`. If you need elevated permissions, prefix the command with `sudo`; this prompts for your password and runs the command as root.

**Quoting confusion in `find` and `grep`.**
If a glob pattern argument seems wrong, try wrapping it in single quotes: `find . -name '*.txt'`. Single quotes prevent the shell from expanding anything inside; the literal characters are passed to the command.

**The output looks fine in the terminal but wrong in a file when redirected.**
Some commands detect that their output is not a terminal and change their behavior (no colors, no progress bars, different formatting). `ls` is a famous example; `ls --color=always` forces color even when redirected.

**`type -a` does not work.**
You are in a shell where it is not a builtin. Try `which command` instead; it is less informative (does not see aliases) but works in any POSIX shell.

**You can't get out of `man`.**
Press `q`. (This is the same key as in `less`, `top`, `git diff`, and many other interactive pagers.)

---

## Further Reading

- **The Linux Command Line** (William Shotts), free at <https://linuxcommand.org/tlcl.php>. A 500-page book that goes deep on everything in this lab and much more. Recommended.
- **POSIX Utilities** specification at <https://pubs.opengroup.org/onlinepubs/9799919799/utilities/contents.html>. The formal definition of what every Unix-like system must provide. Useful when you want to know which flags are portable and which are GNU-specific.
- **`man` pages**. The local manual on your machine is the canonical reference. `man man` (the man page about the man command) is a good place to start.
- **explainshell.com** at <https://explainshell.com/>. Paste any shell command and the site annotates each piece with its meaning. Excellent for understanding a snippet you found online.
- **GNU Coreutils manual** at <https://www.gnu.org/software/coreutils/manual/>. The reference for the GNU implementations of `cp`, `mv`, `ls`, `wc`, and the dozens of other small utilities that ship with most Linux distributions.
