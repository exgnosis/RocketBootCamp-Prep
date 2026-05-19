# Lab 5-1: Git Basics

## Overview

Git is the version control system most professional software is built with. Before you can use it productively (branches, merges, remotes, pull requests, rebases), you need a working mental model of what Git actually does when you type the everyday commands: `init`, `add`, `commit`, `status`, `log`. This lab gives you that mental model by walking through a Git repository from the moment it is created to the moment it has a small linear history, with explicit attention to what changes inside the `.git/` directory at each step.

You will create a directory, initialize a Git repository, make four commits to a single text file, and inspect the internal state of `.git/objects` to see how Git actually stores your work. Along the way you will use `git status`, `git log`, and a custom `git ll` alias to read the state of the repository from three different angles.

**This lab is hands-on.** You type every command yourself in a terminal. The point is to build muscle memory for the everyday Git workflow and to see, with your own eyes, what each command produces.

**Estimated time:** 30 to 45 minutes
**Difficulty:** Beginner

**Prerequisites:**

- Access to the lab VM (or any Linux/macOS environment with Git installed).
- Git 2.30 or later installed (`git --version` should print 2.30.x or higher). The lab's reference output was captured against Git 2.34.
- A text editor of your choice; the lab does not require any specific IDE.
- No prior Git knowledge required. This is the introduction.

> **Important:** Do not delete your work at the end of this lab. The next lab (5-2) uses the repository you create here as its starting point.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Verify a Git installation and configure the user identity Git needs to record commits.
2. Initialize a new Git repository and explain what the contents of `.git/` represent.
3. Use the three-state workflow (working tree, staging area, repository) to move changes through Git.
4. Make a commit and read the resulting history with `git log` and a graphical alias.
5. Inspect `.git/objects` to see how Git stores commits as a content-addressed object store.
6. Use `git status` to read the current state of a repository at any moment.

---

## Part 1: Verify Your Git Installation

Before doing anything else, confirm that Git is installed and configured.

### Step 1.1: Open a terminal and locate yourself

Log into the VM and open the Terminal application.

> **Tip:** Press the up-arrow key in a terminal to cycle through your previous commands. You will be running similar commands many times in this lab; the up-arrow saves significant typing.

### Step 1.2: Create the lab directory

Create a directory called `lab1` and move into it:

```bash
mkdir lab1
cd lab1
```

You will work from inside `lab1` for the rest of this lab. Every command in the lab assumes that is your current directory unless stated otherwise.

### Step 1.3: Check the Git version

```bash
git --version
```

You should see something like:

```
git version 2.34.1
```

Anything 2.30 or later will work for this lab. If `git --version` reports "command not found," install Git through your package manager (`apt install git` on Ubuntu, `brew install git` on macOS) before continuing.

### Step 1.4: Check your Git configuration

Git refuses to record a commit unless it knows who is making it. The name and email recorded in your configuration are baked into every commit, permanently. There is no way to make an "anonymous" commit; this is by design.

Check what Git currently knows about you:

```bash
git config --list
```

You should see at least a `user.name` and `user.email` line. The lab's reference configuration looks like this:

```
user.name=Rocket Student
user.email=noone@nowhere.com
alias.ll=log --oneline --graph --decorate --all
init.defaultbranch=main
core.editor=code --wait
```

If your output is missing any of the first two lines (`user.name` and `user.email`), set them now:

```bash
git config --global user.name "Your Name"
git config --global user.email "[email protected]"
```

The lab uses a name and email as identifiers, not as a public profile. Use something recognizable; if you commit to a real shared repository later, you can change these.

### Step 1.5: Set up the convenience configuration the lab uses

The lab also uses an alias called `git ll` that produces a compact graphical log, and it expects new repositories to default to a `main` branch (not the older default of `master`). 

If these are not showing up in the config listing, then set these now so your output matches the lab's reference:

```bash
git config --global alias.ll "log --oneline --graph --decorate --all"
git config --global init.defaultBranch main
```

Re-run `git config --list` and confirm both new entries are present.

> **Why an alias?** `git log --oneline --graph --decorate --all` is a mouthful. Aliases let you give a long Git command a short nickname; `git ll` is much faster to type and you will use it dozens of times. This is also the canonical way professional developers extend Git: not by replacing it, but by giving familiar shapes to common commands.

---

## Part 2: Create a Git Repository

A Git repository is just a hidden directory called `.git/` inside your project. That directory contains every commit you have ever made, every branch, every tag, all of Git's configuration, and pointers to the current state. Understanding what is inside `.git/`  comprises most of what you need to understand about Git itself.

### Step 2.1: Initialize the repository

From inside `lab1`:

```bash
git init
```

Output:

```
Initialized empty Git repository in /home/protech/lab1/.git/
```

That single command created the `.git/` directory. Nothing else has changed; the directory you are working in is otherwise empty.

### Step 2.2: Confirm there is nothing to commit yet

Ask Git for the current state of your repository:

```bash
git status
```

You should see:

```
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

Three things are worth noting here:

- **`On branch main`** says Git has put you on a branch called `main` (because of the `init.defaultBranch` setting from Part 1).
- **`No commits yet`** says the branch exists in name but has no history.
- **`nothing to commit`** says there are no files in your working directory that Git knows about or that are waiting to be saved.

`git status` is the single most important Git command. Run it whenever you are not sure what state you are in. Get into the habit of running it before and after every other command in this lab; it costs nothing and tells you everything.

### Step 2.3: Look inside `.git/`

The contents of `.git/` are not normally something you read by hand, but for one lab it is worth seeing what is there.

```bash
cd .git
ls -l
```

Output:

```
total 32
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 branches
-rw-rw-r-- 1 protech protech   92 Sep  2 13:49 config
-rw-rw-r-- 1 protech protech   73 Sep  2 13:49 description
-rw-rw-r-- 1 protech protech   21 Sep  2 13:49 HEAD
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 hooks
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 info
drwxrwxr-x 4 protech protech 4096 Sep  2 13:49 objects
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 refs
```

The most important entries for this lab are:

- **`HEAD`**: a pointer to the current branch. Read it directly:

  ```bash
  cat HEAD
  ```

  Output:

  ```
  ref: refs/heads/main
  ```

  HEAD does not point at a commit; it points at the *branch reference*, which points at the latest commit on that branch. This indirection is what makes Git branches lightweight.

- **`objects/`**: the store where every committed file and every commit itself is recorded as a content-addressed blob. You will look inside this directory shortly.

- **`refs/`**: the directory of branch and tag pointers.

- **`config`, `description`, `hooks`, `info`, `branches`**: repository-local configuration, scripts that can run at lifecycle events, and a few other directories Git uses internally. You will not touch them in this lab.

### Step 2.4: Look at the empty object store

```bash
cd objects
ls -l
```

Output:

```
total 8
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 info
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 pack
```

Only two subdirectories, both used by Git internally. **There are no blobs yet** because nothing has been committed. This is the starting state of the object store: empty.

Return to the working directory:

```bash
cd ../..
```

You should be back at `~/lab1` now. Run `pwd` if you are unsure.

---

## Part 3: Make Your First Commit

You will now move a file through Git's three-state workflow:

1. **Working tree**: the files you see and edit in your directory.
2. **Staging area** (also called the *index*): a list of changes you have marked as ready to be committed.
3. **Repository**: the permanent record of commits in `.git/`.

The two transitions are `git add` (working tree → staging) and `git commit` (staging → repository). The pattern is universal: every change you ever record in Git goes through these two steps.

### Step 3.1: Confirm there is no history yet

```bash
git log
```

Output:

```
fatal: your current branch 'main' does not have any commits yet
```

This is not an error in the negative sense; Git is correctly telling you that the branch is empty. This message will not appear again once you have at least one commit.

### Step 3.2: Create a file in the working tree

```bash
echo "This is some text" > file.txt
cat file.txt
```

Output:

```
This is some text
```

You now have one file in your working tree that Git has not seen before. Confirm with `git status`:

```bash
git status
```

Output:

```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	file.txt

nothing added to commit but untracked files present (use "git add" to track)
```

The phrase **"Untracked files"** is Git's way of saying "I see this file exists, but I am not following changes to it." `file.txt` is in your working tree only. The staging area is empty and the repository is empty.

### Step 3.3: Stage the file

```bash
git add file.txt
git status
```

Output:

```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   file.txt
```

The file has moved from "untracked" to "changes to be committed." It is now in the staging area, waiting to become part of the next commit.

> **Why does staging exist?** A commit is meant to be a single coherent change. The staging area lets you build up a commit piece by piece (perhaps from several files, or from only parts of a file using `git add -p`) and inspect what you are about to commit before committing it. New Git users often find staging an extra step; experienced users use it as a tool for crafting clean, focused commits.

### Step 3.4: Commit

```bash
git commit -m "First commit"
```

Output:

```
[main (root-commit) 0e426de] First commit
 1 file changed, 1 insertion(+)
 create mode 100644 file.txt
```

The `-m` flag provides the commit message inline. Without it, Git opens your configured editor to ask for one. **Every commit must have a message.** This is enforced by Git for the same reason commits are tied to an identity: without it, history would be unreadable.

Three things to notice in the output:

- **`(root-commit)`**: this is the first commit on the branch, with no parent. Every other commit you make from here will have at least one parent commit.
- **`0e426de`**: this is the short version of the commit's SHA-1 hash. Your hash will be different from the lab's reference because the hash incorporates your name, email, and the exact timestamp.
- **`1 file changed, 1 insertion(+)`**: a summary of what the commit contains. One new file with one line.

### Step 3.5: Look at the history

```bash
git log
```

Output (your hash and timestamp will differ):

```
commit 0e426deb652fc962293f513d461efdf7fc2cfb19 (HEAD -> main)
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:06:57 2025 -0400

    First commit
```

The phrase `(HEAD -> main)` says: the current HEAD is on the `main` branch, and `main` currently points at this commit. This matches what you saw in `cat .git/HEAD` earlier: HEAD points at the branch, and the branch points at the commit.

### Step 3.6: Confirm the working tree is clean

```bash
git status
```

Output:

```
On branch main
nothing to commit, working tree clean
```

The phrase **"working tree clean"** is one you will see thousands of times. It means: every file in your working directory matches exactly what is recorded in the last commit. There are no changes anywhere, in any of the three states.

---

## Part 4: Build a History

A single commit is not very interesting. You will now add three more commits, one at a time, so the history has some shape to look at.

The pattern for each commit is the same:

1. Change the file (add a new line).
2. `git add file.txt` to stage the change.
3. `git commit -m "..."` to record it.

### Step 4.1: Make the second commit

```bash
echo "This is line 2" >> file.txt
cat file.txt
```

Output:

```
This is some text
This is line 2
```

Note the **`>>`** (two greater-than signs) operator. This *appends* to the file. A single `>` would have *overwritten* it. Get the wrong one and you will have to redo the first step.

Stage and commit:

```bash
git add file.txt
git commit -m "Second commit"
```

Output:

```
[main e5c5b41] Second commit
 1 file changed, 1 insertion(+)
```

This commit shows no `(root-commit)` annotation because it has a parent: the first commit.

Inspect the history with both `git log` and the compact alias:

```bash
git log
```

Output:

```
commit e5c5b412676f38a5f15fba00af47bc34e648d723 (HEAD -> main)
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:14:04 2025 -0400

    Second commit

commit 0e426deb652fc962293f513d461efdf7fc2cfb19
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:06:57 2025 -0400

    First commit
```

```bash
git ll
```

Output:

```
* e5c5b41 (HEAD -> main) Second commit
* 0e426de First commit
```

Same information, two different views. The compact view is much easier to scan once you have more than a few commits.

### Step 4.2: Make the third and fourth commits

Repeat the same pattern two more times. After each commit, run `git ll` to watch the history grow.

```bash
echo "This is line 3" >> file.txt
git add file.txt
git commit -m "Third commit"
```

```bash
echo "This is line 4" >> file.txt
git add file.txt
git commit -m "Fourth commit"
```

### Step 4.3: Verify the final state

After the fourth commit, your file should look like this:

```bash
cat file.txt
```

Output:

```
This is some text
This is line 2
This is line 3
This is line 4
```

And your history should look like this:

```bash
git log
```

Output (your hashes and timestamps will differ):

```
commit 31c2ebd9ae504b4378d5b80f87ba202a34dd5ec5 (HEAD -> main)
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:18:13 2025 -0400

    Fourth commit

commit 06da0ab052e771d59a43cf8f9bc6e166c439a665
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:17:09 2025 -0400

    Third commit

commit e5c5b412676f38a5f15fba00af47bc34e648d723
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:14:04 2025 -0400

    Second commit

commit 0e426deb652fc962293f513d461efdf7fc2cfb19
Author: Rocket Student <[email protected]>
Date:   Tue Sep 2 14:06:57 2025 -0400

    First commit
```

And the compact view:

```bash
git ll
```

Output:

```
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab Third commit
* e5c5b41 Second commit
* 0e426de First commit
```

Four commits, in order, with HEAD pointing at the latest one through the `main` branch. This is the simplest possible history shape: a straight line of commits.

---

## Part 5: Inspect the Object Store

Now that you have a real history, look at what Git stored in `.git/objects/`.

```bash
cd .git/objects
ls -l
```

Output (your directory names will differ, but you will see roughly the same number of entries):

```
total 48
drwxrwxr-x 2 protech protech 4096 Sep  2 14:17 06
drwxrwxr-x 2 protech protech 4096 Sep  2 14:06 0e
drwxrwxr-x 2 protech protech 4096 Sep  2 14:13 22
drwxrwxr-x 2 protech protech 4096 Sep  2 14:18 31
drwxrwxr-x 2 protech protech 4096 Sep  2 14:17 6d
drwxrwxr-x 2 protech protech 4096 Sep  2 14:05 a4
drwxrwxr-x 2 protech protech 4096 Sep  2 14:14 b9
drwxrwxr-x 2 protech protech 4096 Sep  2 14:16 d1
drwxrwxr-x 2 protech protech 4096 Sep  2 14:18 e5
drwxrwxr-x 2 protech protech 4096 Sep  2 14:17 f0
drwxrwxr-x 2 protech protech 4096 Sep  2 14:49 info
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 pack
```

What you are looking at is the **Git object store**.

- Every commit, every snapshot of every file's content, and every tree (Git's representation of a directory) is stored here as an object identified by its SHA-1 hash.
- Hashes are 40 characters long. Git uses the first two characters as the directory name and the remaining 38 as the filename inside that directory. This is purely for filesystem performance: putting tens of thousands of objects in one flat directory is slow on most filesystems, so Git fans them out into 256 buckets.
- The directory names you see (`06`, `0e`, `22`, ...) are the first two characters of each object's hash.

Your four commits should have produced **twelve objects** in total:

- **4 commit objects**, one per commit you made. Each records its tree, its parent, the author, the committer, the timestamp, and the message.
- **4 tree objects**, one per commit. Each represents the state of the working directory at that commit. (In this lab the trees are very simple: each contains a single entry pointing at the current `file.txt` blob.)
- **4 blob objects**, one per distinct version of `file.txt`. Each time you added a new line, the file's content changed, so Git stored a new blob.

But `ls -l` on the objects directory will show **fewer than 12 hash-prefix directories**, typically 10 or 11. The discrepancy is not because Git lost any objects; it is because **two different objects sometimes happen to have hashes starting with the same two characters and therefore share a directory**. With 12 objects and 256 possible two-character prefixes, the chance of at least one such collision is about 22% per pair (the birthday-paradox effect), so it is common to see one or two collisions. Count your own directories and you should find that your number is 10, 11, or 12.

Confirm this for yourself. List one of your directories and see how many files are inside:

```bash
ls -la <one-of-your-directory-names>
```

(Use a directory name from *your* output, not the lab's reference.) Most will contain exactly one file. One or two will contain two files. The directories with two files are the collisions; the two files inside each one are unrelated objects that just happened to hash with the same first two characters.

> **The deeper lesson:** Git is a **content-addressed object store**. The hash of an object is determined entirely by its content. Two files with identical content always produce the same blob hash; Git stores them once. If you committed the exact same file twice (without changing it), the second commit would reference the same blob the first commit did. You will not see deduplication in this lab because every commit changed the file, but it is one of the reasons Git is fast even on large repositories.

Return to the working directory:

```bash
cd ../..
```

You should be back at `~/lab1`.

---

## Part 6: Save Your Work for Lab 5-2

**The next lab uses this repository as its starting point. Do not delete it.**

Confirm before you finish:

```bash
pwd
ls -la
git status
git ll
```

You should see:

- A directory called `lab1`.
- A `.git/` directory and a `file.txt`.
- "On branch main / nothing to commit, working tree clean."
- Four commits in the compact log.

If all four are present, you are done.

---

## Part 7: Reflection

Answer in your notebook (or a scratch file). These are open-ended; spend at least 10 minutes.

1. **The three states.** Working tree, staging area, repository. In your own words, what is each one for? Why does staging exist as a separate step rather than going straight from working tree to commit? Can you imagine a project workflow where staging would be especially valuable?

2. **"Working tree clean."** What exactly does this phrase mean? If you ran `cat file.txt`, then a colleague ran `cat file.txt` after `git checkout` of the same commit, would you see identical content? What would have to be different about the commit message, author, or timestamp for the *commit hashes* to be different even if the file contents are identical?

3. **HEAD is a pointer to a pointer.** `.git/HEAD` contains `ref: refs/heads/main`, not a commit hash directly. Why the indirection? What does this design allow that a direct pointer to a commit would not?

4. **`git status` is your best friend.** You ran it many times in this lab. What information does it give you that `git log` does not? When would you reach for `git log` instead?

5. **Object store inspection.** You found 12 objects total, but fewer than 12 directories under `.git/objects/` because some objects share a two-character hash prefix. What does this tell you about why Git uses the two-character prefix at all? What problem is it solving, and what problem is it *not* solving?

6. **The commit hash.** Every commit has a 40-character SHA-1 hash like `0e426deb652fc962293f513d461efdf7fc2cfb19`. The hash is computed from the commit's contents (tree, parent, author, committer, message). What would happen to the hash if you tried to change the commit message after the fact? What property of the system does this give you?

---

## Reference: The Everyday Git Commands

These five commands cover roughly 80% of day-to-day Git usage. Get them into your fingers.

| Command | What it does |
|---------|--------------|
| `git status` | Show the current state of the working tree, staging area, and branch. Run this constantly. |
| `git add <file>` | Move changes from the working tree into the staging area. |
| `git commit -m "..."` | Record everything in the staging area as a new commit. |
| `git log` | Show the history of commits on the current branch (most recent first). |
| `git ll` (your alias) | Show the same history in compact graphical form. |

You will add roughly five more commands over the next two labs (`git diff`, `git branch`, `git checkout`, `git merge`, `git remote`). Those plus the five above are essentially the working vocabulary of a professional developer using Git.

---

## Reference: Git's Three States

```
+-----------------+         git add          +-----------------+         git commit         +----------------+
|                 |  ---------------------> |                 |  ----------------------> |                |
|  Working Tree   |                          |  Staging Area   |                          |  Repository    |
|  (your files)   |  <--------------------- |   (the index)   |                          |   (.git/)      |
|                 |     git restore         |                 |                          |                |
+-----------------+      --staged           +-----------------+                          +----------------+
```

- **Working tree:** what you see and edit.
- **Staging area:** what Git will record on the next `commit`.
- **Repository:** the permanent history, stored in `.git/`.

`git status` shows you, at any moment, which files are in which state.

---

## Troubleshooting

**`git --version` says "command not found."**
Git is not installed. On Ubuntu/Debian: `sudo apt update && sudo apt install git`. On macOS: `brew install git` (or run `xcode-select --install` to get the Apple-provided version). After installation, close and reopen your terminal.

**`git commit` opens an editor instead of committing.**
You forgot the `-m "..."` flag. Either type a commit message in the editor, save, and quit, or quit without saving (which aborts the commit) and re-run `git commit -m "your message"`. If the editor is unfamiliar (typically Vim), the keystrokes to save-and-quit are `Esc` then `:wq` then Enter; to quit-without-saving, `Esc` then `:q!` then Enter.

**`git commit` says "Please tell me who you are."**
Your `user.name` and `user.email` are not configured. Run the two `git config --global` commands from Step 1.4 of this lab.

**`git status` shows "Untracked files" for files I don't recognize.**
Your text editor may have created hidden files (for example, `.vscode/` directories or `.DS_Store` files on macOS). For this lab you can ignore them. In future labs you will use a `.gitignore` file to tell Git to stop noticing them.

**The branch is called `master`, not `main`.**
Your Git version is older than the default-branch-rename change, or `init.defaultBranch` is not set. Set it now with `git config --global init.defaultBranch main`. For the current repository, you can rename the branch: `git branch -m master main`. Then re-run `git status` to confirm.

**`git ll` says "ll is not a git command."**
The alias is not set. Run `git config --global alias.ll "log --oneline --graph --decorate --all"` and try again.

**I accidentally used `>` instead of `>>` and overwrote the file.**
The working tree change is lost, but the previous commit is fine. Restore the file from the last commit: `git checkout -- file.txt`. Now you are back to the state of the last commit, and you can re-append the new line correctly. This is the most common reason to keep committing often: every commit is a recovery point.

**I made a typo in my commit message.**
If you have not yet made any further commits, fix it with `git commit --amend -m "corrected message"`. If you have moved on, the message is part of the history; rewriting it is possible but more involved (and not part of this lab).

---

## Further Reading

- **Pro Git** (Scott Chacon and Ben Straub), free online at <https://git-scm.com/book/en/v2>. Chapters 1, 2, and 10 cover the same material as this lab and the next two labs at a deeper level.
- **`git help <command>`** for any command (e.g., `git help commit`). The official documentation is thorough and well written; it opens in your pager.
- **Visualizing Git Concepts with D3**: <https://onlywei.github.io/explain-git-with-d3/>. An interactive sandbox for seeing what each Git command does to the object graph.

---

## End of Lab 5-1

Keep your `lab1` directory for the next lab.
