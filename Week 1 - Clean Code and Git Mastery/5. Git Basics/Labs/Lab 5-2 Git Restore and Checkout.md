# Lab 5-2: Restoring and Navigating History in Git

## Overview

Lab 5-1 taught you the forward-only basics of Git: how to make commits and read the resulting linear history. Real Git work, though, is rarely forward-only. You will routinely need to **undo** a change you have not yet committed, **recover** a file you accidentally deleted, **inspect** a file as it existed three commits ago, and **move** your entire working tree to a different point in history to see what the project looked like then.

This lab introduces three commands that handle all of these cases: `git restore` (for individual files), `git checkout` (for moving your whole working tree), and `git switch` (for returning to a branch). Along the way you will meet the **detached HEAD** state, which sounds alarming the first time you see it but is actually a useful and safe place to visit.

You will continue working in the `lab1` repository you built in Lab 5-1, using its four-commit history as the backdrop for everything that follows.

**This lab is hands-on.** You type every command yourself. The point is to build confidence with Git's "undo" and "time-travel" commands so they feel routine rather than scary.

**Estimated time:** 30 to 45 minutes
**Difficulty:** Beginner

**Prerequisites:**

- Completion of Lab 5-1. You need the `~/lab1` repository with four commits as your starting point.
- Git 2.30 or later. The `git restore` and `git switch` commands were introduced in Git 2.23 (2019), so anything that recent will work.
- The `git ll` alias from Lab 5-1 (`log --oneline --graph --decorate --all`).

> **Important:** Do not delete your work at the end of this lab. The repository you build here may be used in a later lab.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Restore a deleted or modified file from the most recent commit using `git restore`.
2. Restore a file to the state it had at any specific previous commit, using either a hash or a relative reference like `HEAD~1`.
3. Distinguish between `git restore` (one file) and `git checkout` (whole working tree).
4. Recognize and safely operate in detached HEAD state.
5. Return to your working branch with `git switch -`.
6. Explain what HEAD, a branch reference, and a commit hash each are, and how the three relate.

---

## Part 1: Set Up

### Step 1.1: Locate yourself in the lab directory

If your terminal is still open from Lab 5-1, you should already be in `~/lab1`. If not, navigate back:

```bash
cd ~/lab1
```

Confirm with `pwd`:

```bash
pwd
```

Output:

```
/home/protech/lab1
```

### Step 1.2: Confirm the starting state

Before starting any of the exercises, make sure your repository is in the state you left it in at the end of Lab 5-1: four commits, a clean working tree, and `file.txt` with four lines.

```bash
git ll
```

Expected output (your hashes will differ):

```
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab Third commit
* e5c5b41 Second commit
* 0e426de First commit
```

```bash
git status
```

Expected output:

```
On branch main
nothing to commit, working tree clean
```

```bash
cat file.txt
```

Expected output:

```
This is some text
This is line 2
This is line 3
This is line 4
```

If any of these three checks fails, return to Lab 5-1 and finish it before continuing. Every exercise below assumes you start from this exact state.

---

## Part 2: Restore a File from HEAD

The most common reason to use `git restore` is the most ordinary one: you changed a file (or deleted it) and now you wish you had not. Git's permanent record of every committed version means you can always go back.

### Step 2.1: Delete the file and bring it back

Delete `file.txt` from your working directory:

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

```bash
rm file.txt
ls
```

Output (the directory now appears empty to `ls`, though `.git/` is still there as a hidden directory):

```
(no files listed)
```

The file is gone from the working tree. It is **not** gone from Git: every committed version is still in `.git/objects`. Bring it back:

```bash
git restore file.txt
ls
```

Output:

```
file.txt
```

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

The file is back, exactly as it was at the last commit. **By default, `git restore` copies the file from the commit that HEAD points to.** That is the fourth commit in this repository, which contains all four lines.

### Step 2.2: Restore overwrites uncommitted changes

`git restore` will happily overwrite a file in your working tree, even if the file has changes you have not yet committed. This is sometimes what you want (you want to throw the changes away). It is sometimes a mistake (you wanted to keep them). Be sure which case you are in before running the command.

Add a line to the file and confirm:

```bash
echo "This is line 5" >> file.txt
cat file.txt
```

Output:

```
This is some text
This is line 2
This is line 3
This is line 4
This is line 5
```

Now restore:

```bash
git restore file.txt
cat file.txt
```

Output:

```
This is some text
This is line 2
This is line 3
This is line 4
```

The fifth line is gone. **It was never committed, so Git had no record of it.** This is the most common way new Git users lose work: they had local changes, they ran `git restore` to throw away *some* changes, and Git threw away *all* of them. Always check `git status` and `git diff` before restoring.

> **The two-rule mental model for `git restore`:**
>
> 1. `git restore <file>` discards any *unstaged* changes in your working tree, replacing the file with whatever is in the staging area (or HEAD if nothing is staged).
> 2. `git restore --staged <file>` discards anything you have *staged*, putting it back in the working tree as an unstaged change.
>
> Between the two, you can rewind any not-yet-committed work, in either direction.

---

## Part 3: Restore a File from a Specific Commit

`git restore` is not limited to the current commit. The `--source` flag lets you pick any commit in the history. This is what makes it a time-travel tool for individual files.

### Step 3.1: Restore from a commit by its hash

Get the list of commits so you can pick a hash:

```bash
git ll
```

Output (your hashes will differ):

```
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab Third commit
* e5c5b41 Second commit
* 0e426de First commit
```

Restore the file as it existed at the **second commit**. Use *your* second-commit hash, not the one shown in the lab (yours will be different):

```bash
git restore file.txt --source e5c5b41
cat file.txt
```

Output:

```
This is some text
This is line 2
```

The file now has only two lines, the state it had when you made the second commit. **Your working tree is at a different state than the commit HEAD points to** (which still has four lines). This is fine; Git is just showing you that one file can be moved independently of the rest.

> **You do not need the full hash.** Git accepts any unambiguous prefix. Seven characters is the standard short form. If your repository has thousands of commits and a seven-character prefix becomes ambiguous, Git will tell you and ask for more characters.

### Step 3.2: Use `HEAD~N` for relative references

Typing hashes is error-prone, and they are different every time. Git provides relative references that are much easier to use:

- `HEAD` is the current commit.
- `HEAD~1` is the commit one step before HEAD.
- `HEAD~2` is two steps before HEAD.
- `HEAD~N` is N steps before HEAD, following the first parent.

In your linear four-commit history:

| Reference | Commit |
|-----------|--------|
| `HEAD` | Fourth commit (four lines) |
| `HEAD~1` | Third commit (three lines) |
| `HEAD~2` | Second commit (two lines) |
| `HEAD~3` | First commit (one line) |

Currently `file.txt` is at the second-commit state (two lines, from Step 3.1). Restore it to the third commit instead:

```bash
cat file.txt
```

(Output: two lines, from Step 3.1.)

```bash
git restore file.txt --source HEAD~1
cat file.txt
```

Output:

```
This is some text
This is line 2
This is line 3
```

The file now has three lines, the state it had at the third commit.

### Step 3.3: Walk further back

Restore from the first commit:

```bash
git restore file.txt --source HEAD~3
cat file.txt
```

Output:

```
This is some text
```

One line. This is the state of `file.txt` immediately after your first commit.

### Step 3.4: Return to the latest version

To bring the file back to the state of the most recent commit, you can either run `git restore` with no `--source` flag (the default), or specify `HEAD` explicitly:

```bash
git restore file.txt --source HEAD
cat file.txt
```

Output:

```
This is some text
This is line 2
This is line 3
This is line 4
```

The file is back to its four-line state. Confirm with `git status`:

```bash
git status
```

Output:

```
On branch main
nothing to commit, working tree clean
```

You walked the file backwards through every commit and then forward again. **None of this changed your commit history.** `git ll` will still show the same four commits in the same order. You were only moving the working-tree copy of the file around; the underlying history is immutable.

> **Why is this safe?** Every committed version is in `.git/objects` permanently. `git restore` just looks up the version you ask for and writes it to your working directory. You cannot lose a committed version of a file by running `git restore`. The only thing you can lose is uncommitted work.

---

## Part 4: Move Your Whole Working Tree

`git restore` works on a single file. `git checkout` moves your entire working tree to match a whole commit. Every tracked file is updated to its state at that commit, all at once.

### Step 4.1: Inspect the history again

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

You will move to the **second commit**, which is `HEAD~2` from the current position.

### Step 4.2: Check out the second commit

```bash
git checkout HEAD~2
```

Git prints a substantial message that is worth reading:

```
Note: switching to 'HEAD~2'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at e5c5b41 Second commit
```

This message looks alarming but is purely informational. Git is telling you that you have entered a state called **detached HEAD**, what it means, and how to get out of it. Read every line of the message before continuing.

### Step 4.3: See what detached HEAD looks like

```bash
git ll
```

Output:

```
* 31c2ebd (main) Fourth commit
* 06da0ab Third commit
* e5c5b41 (HEAD) Second commit
* 0e426de First commit
```

Compare this to what `git ll` showed before. **HEAD and `main` are no longer at the same commit.** HEAD is at the second commit, on its own. `main` is still at the fourth commit, where it has always been.

This is what "detached HEAD" means: HEAD is pointing directly at a commit instead of pointing at a branch that points at a commit. Recall from Lab 5-1 that the contents of `.git/HEAD` normally look like `ref: refs/heads/main`, an indirect reference through the branch. In detached HEAD state, `.git/HEAD` contains a raw commit hash instead. Check it now if you want:

```bash
cat .git/HEAD
```

Output (your hash will differ):

```
e5c5b412676f38a5f15fba00af47bc34e648d723
```

Compare the contents of `file.txt`:

```bash
cat file.txt
```

Output:

```
This is some text
This is line 2
```

The whole working tree has moved to the second commit. Not just the file you chose, but every tracked file in the repository.

> **Why is detached HEAD considered scary?** Because **any commits you make while detached are not on a branch.** If you make a commit here, then switch back to `main`, your new commit is still in the object store but no branch points at it. After a while, Git's garbage collector will assume it is orphaned and delete it. The state is not dangerous in itself; it becomes dangerous only if you forget you are in it and do work that you intend to keep. The lab will not do that, so detached HEAD here is harmless. In real work, the cure is to either create a branch immediately (`git switch -c new-branch-name`) or get back to a real branch before doing anything you want to keep.

### Step 4.4: Return to your branch

The Git output message gave you a hint: `git switch -`. The hyphen means "the previous reference", just like `cd -` means "the previous directory":

```bash
git switch -
```

Output:

```
Previous HEAD position was e5c5b41 Second commit
Switched to branch 'main'
```

Confirm HEAD is back on `main`:

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

The `(HEAD -> main)` annotation is back on the fourth commit. Your working tree should also be back to the fourth-commit state:

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

```bash
git status
```

Output:

```
On branch main
nothing to commit, working tree clean
```

You time-travelled to the second commit, looked around, and came back. No changes to the history, nothing lost.

---

## Part 5: Save Your Work

You may use this repository in a later lab. Do not delete it.

Confirm the final state:

```bash
pwd
git status
git ll
cat file.txt
```

You should see:

- Directory `~/lab1`.
- "On branch main / nothing to commit, working tree clean."
- Four commits in the compact log, with `(HEAD -> main)` on the fourth.
- Four lines in `file.txt`.

If all four match, you are done.

---

## Part 6: Reflection

Answer in your notebook (or a scratch file). These are open-ended; spend at least 10 minutes.

1. **`restore` vs `checkout`.** In your own words, what is the difference between `git restore` and `git checkout`? When would you use each? Why does Git make this distinction now, when it did not always (the old `git checkout` could do both jobs)?

2. **The danger of `git restore`.** Restoring a file in your working tree silently throws away any unstaged changes to that file. What habit can protect you from accidentally losing work to a careless `git restore`? (Hint: think about `git status` and `git diff`.)

3. **HEAD as a pointer.** Lab 5-1 showed that `.git/HEAD` normally contains `ref: refs/heads/main`. In Step 4.3 of this lab, you checked it during detached HEAD state and found a raw commit hash instead. What does the change tell you about how Git represents your current position in two different states? Why does that representation matter?

4. **`HEAD~N` and history shape.** `HEAD~1` means "the commit one step before HEAD, following the first parent." Why does the description specify "first parent"? When would a commit have more than one parent, and what would `HEAD~1` mean then? (You will meet this in the merge lab. Speculate now and check later.)

5. **What `git restore --source <hash>` does to `git ll`.** When you restored `file.txt` from `HEAD~3` in Step 3.3, your working tree contained the old version of the file, but `git ll` still showed all four commits unchanged. Why? What is `git restore --source` *not* doing that you might intuitively expect it to do?

6. **The phrase "detached HEAD."** Why is this state called "detached"? What is HEAD detached *from*? Try to give a one-sentence definition that you would explain to a colleague new to Git.

---

## Reference: Restore and Time-Travel Commands

| Command | What it does |
|---------|--------------|
| `git restore <file>` | Replace `<file>` in the working tree with the version from the staging area, or from HEAD if nothing is staged. |
| `git restore --source <commit> <file>` | Replace `<file>` in the working tree with its version at `<commit>`. The commit can be a hash or a relative reference like `HEAD~2`. |
| `git restore --staged <file>` | Unstage `<file>` (move it from "changes to be committed" back to "changes not staged"). |
| `git checkout <commit>` | Move the entire working tree to match `<commit>`. Enters detached HEAD state unless `<commit>` is a branch name. |
| `git switch <branch>` | Move HEAD to a branch. The standard way to move between branches. |
| `git switch -` | Switch to the previously-checked-out branch (like `cd -`). |
| `git switch -c <new-branch>` | Create a new branch starting from the current HEAD and switch to it. The recommended way to "rescue" any commits you make while detached. |

---

## Reference: Relative Commit References

These references work anywhere you can use a commit hash.

| Reference | Means |
|-----------|-------|
| `HEAD` | The current commit. |
| `HEAD~1` | One commit before HEAD, following first parent. |
| `HEAD~N` | N commits before HEAD, following first parent each step. |
| `HEAD^` | The first parent of HEAD (same as `HEAD~1`). |
| `HEAD^2` | The *second* parent of HEAD. Only meaningful for merge commits. |
| `<branch>~N` | Same idea, but starting from a named branch. For example, `main~3` is three commits back from `main`. |

`~` walks back through history. `^` selects between multiple parents at one commit. Most everyday Git work uses only `HEAD~N`.

---

## Reference: HEAD in Two States

| State | `.git/HEAD` contains | What it means |
|-------|---------------------|---------------|
| Attached (normal) | `ref: refs/heads/<branch>` | HEAD points at a branch, which points at a commit. New commits move the branch. |
| Detached | A raw commit hash | HEAD points directly at a commit. New commits move HEAD, but no branch follows. |

You enter detached HEAD state any time you ask Git to put you at a specific commit that is not the tip of a branch: `git checkout <hash>`, `git checkout HEAD~2`, `git checkout <tag>`. You leave it by switching to a branch: `git switch <branch>` or `git switch -`.

---

## Troubleshooting

**`git restore` did not restore the file; it stayed deleted.**
Did you run it from the correct directory? `git restore file.txt` looks for `file.txt` in the current directory. If you `cd`'d into `.git/objects/` from an earlier lab and forgot to `cd ..` back, the command silently does nothing useful. Run `pwd` and confirm you are at `~/lab1` before running restore commands.

**`git restore file.txt --source e5c5b41` says "fatal: could not resolve 'e5c5b41'."**
Your commit hashes are different from the lab's reference. Run `git ll` to see your own hashes and use one of them.

**I made a commit while in detached HEAD state and now I cannot find it.**
The commit is still in `.git/objects`, but no branch points at it, so `git log` does not show it from your current branch. Run `git reflog` to see every position HEAD has been at recently; your detached-HEAD commit will be in that list. To save it, find its hash in the reflog and create a branch: `git branch rescue <hash>`. The branch is now a permanent pointer to your commit.

**`git switch -` says "fatal: invalid reference: -".**
You may not have a previous branch to return to. This happens in detached HEAD state if you never came from a branch (for example, if your first action after `git init` was to check out a specific hash). The fix is to switch by name: `git switch main`.

**`git checkout HEAD~2` says "error: pathspec 'HEAD~2' did not match any file."**
Some older versions of Git used a different argument order. Try `git checkout HEAD~2 --` (with the explicit `--`), which tells Git that `HEAD~2` is a commit reference, not a filename.

**Branch is called `master`, not `main`, in my output.**
Your Git version or configuration uses the older default branch name. Everything in this lab still works; substitute `master` wherever the lab says `main`. To rename your branch to `main` for consistency with the lab text: `git branch -m master main`.

**`git ll` says "ll is not a git command."**
The alias from Lab 5-1 is not configured. Run: `git config --global alias.ll "log --oneline --graph --decorate --all"`.

---

## Further Reading

- **Pro Git** (Scott Chacon and Ben Straub), free online at <https://git-scm.com/book/en/v2>. Chapter 2.4 covers undoing things; Chapter 7.7 covers `reset` and `restore`.
- **`git help restore`**, **`git help checkout`**, **`git help switch`**: the official documentation for each command, with examples.
- **Think Like a Git** (Sam Livingston-Gray), <https://think-like-a-git.net/>. A short read that builds intuition for what HEAD, branches, and detached state actually are.
- **Visualizing Git Concepts with D3**: <https://onlywei.github.io/explain-git-with-d3/>. An interactive sandbox where you can run the commands from this lab and watch the graph change.

---

## End of Lab 5-2

Keep your `lab1` directory.
