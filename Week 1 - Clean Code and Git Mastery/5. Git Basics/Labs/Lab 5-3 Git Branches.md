# Lab 5-3: Branching and Fast-Forward Merging in Git

## Overview

Branches are the feature of Git that makes parallel work possible. A branch is essentially a sticky note pointing at one commit; you can have any number of them at any time, and switching between them is nearly instantaneous because Git just moves the working tree to whatever commit the chosen sticky note points at. This is the mechanic behind almost every team workflow you will encounter (feature branches, release branches, hotfix branches, pull requests, GitHub Flow, GitFlow, trunk-based development) and it is the single most important thing to understand after the basic commit cycle.

This lab walks you through the simplest possible branch story: create a fresh repository, make one commit on `main`, create a `dev` branch off `main`, commit something different on `dev`, switch between the two and confirm the working tree changes, then bring `dev`'s changes back into `main` with a **fast-forward merge**. By the end you will have a clear mental model of what a branch is, what HEAD does when you switch, and what "fast-forward" actually means.

Conflicts, true (three-way) merges, and remote-branch workflows come in later labs. The point of this lab is the simplest case, walked through cleanly.

**This lab is hands-on.** You type every command yourself in a terminal.

**Estimated time:** 30 to 40 minutes
**Difficulty:** Beginner

**Prerequisites:**

- Completion of Labs 5-1 and 5-2. You should be comfortable with `git init`, `git add`, `git commit`, `git status`, `git log`, `git restore`, and `git checkout`.
- Git 2.30 or later.
- The `git ll` alias configured (`log --oneline --graph --decorate --all`).
- The `init.defaultBranch=main` setting.

You will create a new repository for this lab. The `lab1` repository from the previous two labs is not needed.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Create a new branch with `git branch` and switch to it with `git checkout` or `git switch`.
2. List all branches and identify the currently checked-out branch.
3. Make commits on a branch and explain how the branch pointer moves as you do.
4. Switch between branches and observe the working tree change to match each branch's tip commit.
5. Merge one branch into another in the **fast-forward** case and explain why this case is special.
6. Delete a branch that has been merged.
7. Read `git ll` output to see the relationship between branches, HEAD, and commits at any moment.

---

## Part 1: Create the Lab Repository

### Step 1.1: Create the directory and initialize Git

```bash
mkdir branchlab
cd branchlab
git init
```

Output:

```
Initialized empty Git repository in /home/protech/branchlab/.git/
```

If your output says `master` anywhere, your `init.defaultBranch` setting is not configured. Either set it now (`git config --global init.defaultBranch main`) and re-run `git init`, or substitute `master` for `main` everywhere in the lab.

### Step 1.2: Create and commit a file on `main`

Create a file with one line of content:

```bash
echo "This is the main branch" > branch.txt
cat branch.txt
```

Output:

```
This is the main branch
```

Stage and commit:

```bash
git add branch.txt
git commit -m "Add branch.txt to main"
```

Output:

```
[main (root-commit) c7b2c62] Add branch.txt to main
 1 file changed, 1 insertion(+)
 create mode 100644 branch.txt
```

Confirm with the log:

```bash
git log
```

Output (your hash and timestamp will differ):

```
commit c7b2c628e823e3deb7d469bf9d51515635cec6fc (HEAD -> main)
Author: Rocket Student <[email protected]>
Date:   Sat Sep 27 18:37:00 2025 -0400

    Add branch.txt to main
```

Your repository now has a single commit on the `main` branch. HEAD and `main` both point at that commit. The graph is just a dot:

```
* main / HEAD
```

---

## Part 2: Create a New Branch

A new branch in Git is created with `git branch <name>`. This command makes a new pointer to the current commit. It does **not** switch to the new branch; you have to do that separately. (We will look at the combined "create-and-switch" shortcut at the end of this lab.)

### Step 2.1: Create the `dev` branch

```bash
git branch dev
```

The command produces no output. That is normal; most Git commands that succeed without surprises stay quiet.

### Step 2.2: List the branches

```bash
git branch
```

Output:

```
  dev
* main
```

Two things to notice:

- Both branches exist. The repository now has two pointers, both aimed at the same commit.
- The `*` next to `main` means `main` is the currently checked-out branch. HEAD still points at `main`. Creating a branch does not switch to it.

Look at the graph:

```bash
git ll
```

Output:

```
* c7b2c62 (HEAD -> main, dev) Add branch.txt to main
```

Both branches and HEAD are at the same commit, displayed in the parentheses. They are different sticky notes pointing at the same dot.

> **A branch is cheaper than you think.** In Git, a branch is literally a single file on disk: `.git/refs/heads/dev` contains the 40-character hash of the commit `dev` points at. Creating a branch takes microseconds and consumes 40 bytes. In older version control systems (SVN, Perforce) a branch involved copying the entire codebase to a new location. The "branches are cheap" principle is what makes Git's everyday workflow possible: you make branches casually, throw most of them away, and never think about cost.

---

## Part 3: Make a Commit on the Other Branch

### Step 3.1: Check out the `dev` branch

```bash
git checkout dev
```

Output:

```
Switched to branch 'dev'
```

> **`git checkout` vs `git switch`.** Both commands switch branches. `git switch dev` does the same thing as `git checkout dev` and is the modern preferred command (introduced in Git 2.23 in 2019). The older `git checkout` was overloaded with too many jobs, which is why Git eventually split its uses into `git switch` (move between branches) and `git restore` (recover files). Both still work. This lab uses `git checkout` to match the kind of output you will see in older tutorials and existing codebases, but you can substitute `git switch` everywhere and the lab will work identically.

Confirm the switch:

```bash
git branch
```

Output:

```
* dev
  main
```

The `*` is now on `dev`. HEAD has moved with you; it now points at `dev` rather than `main`.

### Step 3.2: Modify the file on `dev`

Add a line to `branch.txt`:

```bash
echo "This is added in dev" >> branch.txt
cat branch.txt
```

Output:

```
This is the main branch
This is added in dev
```

Check the state:

```bash
git status
```

Output:

```
On branch dev
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   branch.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

`git status` always tells you which branch you are on. Get into the habit of reading the first line. When you are juggling multiple branches, it is your reminder of where you are.

### Step 3.3: Commit the change

```bash
git add branch.txt
git commit -m "Updated in dev"
```

Output:

```
[dev df31307] Updated in dev
 1 file changed, 1 insertion(+)
```

Notice the `[dev df31307]` prefix. Git is telling you the commit was added to the `dev` branch. This is `dev`'s new tip; `main`'s tip is still where it was.

### Step 3.4: Inspect the graph

```bash
git ll
```

Output:

```
* df31307 (HEAD -> dev) Updated in dev
* c7b2c62 (main) Add branch.txt to main
```

This is the most important moment in the lab. Read it carefully.

- There are two commits.
- `main` points at the original commit (`c7b2c62`).
- `dev` points at the new commit (`df31307`).
- HEAD points at `dev`.
- The new commit's parent is the original commit. The graph forms a straight line.

ASCII picture of the state:

```
  c7b2c62 ---- df31307
   (main)       (HEAD -> dev)
```

The two branches are now at different commits. `dev` is one commit ahead of `main`.

---

## Part 4: Switch Between Branches

The most striking thing about branches in Git is what happens to your working tree when you switch between them. The file on disk changes to match the branch's tip commit, instantly.

### Step 4.1: Switch to `main`

```bash
git checkout main
```

Output:

```
Switched to branch 'main'
```

Now look at the file:

```bash
cat branch.txt
```

Output:

```
This is the main branch
```

**The second line is gone.** Not because Git deleted it from the repository (the `dev` commit still exists, untouched), but because `main` does not include that change. Your working tree has been rewritten to match `main`'s tip.

Run `git log`:

```bash
git log
```

Output:

```
commit c7b2c628e823e3deb7d469bf9d51515635cec6fc (HEAD -> main)
Author: Rocket Student <[email protected]>
Date:   Sat Sep 27 18:37:00 2025 -0400

    Add branch.txt to main
```

Plain `git log` shows only the commits reachable from the current branch. From `main`, that is exactly one commit. The `dev` commit is invisible to this view, even though it still exists.

For the complete picture across all branches, use `git ll` (which uses the `--all` flag from your alias):

```bash
git ll
```

Output:

```
* df31307 (dev) Updated in dev
* c7b2c62 (HEAD -> main) Add branch.txt to main
```

Now both branches show. `main` (with HEAD) is at the older commit, `dev` is at the newer one.

> **Why `git log` and `git ll` show different things.** Plain `git log` walks backwards from HEAD, following parent pointers, and stops when it runs out. From `main`, it only sees one commit because `main` has no further history. From `dev`, it would see both. `git log --all` (which is what `git ll` runs) looks at every branch and tag and shows every commit that is reachable from any of them. When you want "what does the world look like," use `git ll`. When you want "what is my branch's story," use plain `git log`.

### Step 4.2: Switch back and forth to confirm

To really feel this, switch a few times and watch the file change each time:

```bash
git checkout dev
cat branch.txt
```

Two lines.

```bash
git checkout main
cat branch.txt
```

One line.

```bash
git checkout dev
cat branch.txt
```

Two lines.

Your working tree is not a separate concept from your branches. **The working tree is whatever the current branch's tip says it should be.** Switching branches rewrites the working tree atomically.

Before continuing, make sure you are back on `main`:

```bash
git checkout main
git branch
```

Output:

```
  dev
* main
```

---

## Part 5: Fast-Forward Merge

The point of working on a branch is usually to bring its changes back. The simplest case is when the receiving branch (`main` here) has not moved since the working branch (`dev`) was created. In that case Git can do a **fast-forward merge**: it simply moves `main` forward to where `dev` is, without creating a new merge commit.

### Step 5.1: Confirm the starting state

You should be on `main`. The graph should look like this:

```bash
git ll
```

Output:

```
* df31307 (dev) Updated in dev
* c7b2c62 (HEAD -> main) Add branch.txt to main
```

Visually:

```
  c7b2c62 ---- df31307
   (HEAD ->     (dev)
    main)
```

`main` is one commit behind `dev`. There is a single straight line of commits, and `main`'s tip is on that line. This is the configuration that allows a fast-forward merge.

### Step 5.2: Run the merge

```bash
git merge dev
```

Output:

```
Updating c7b2c62..df31307
Fast-forward
 branch.txt | 1 +
 1 file changed, 1 insertion(+)
```

Read every word:

- **`Updating c7b2c62..df31307`**: Git is telling you what the merge does. It updates the current branch from the first hash to the second.
- **`Fast-forward`**: this is the *kind* of merge. Git recognized that `main` was an ancestor of `dev`, so no new merge commit was needed; it just moved `main`'s pointer forward.
- **`branch.txt | 1 +`**: a summary of the changes that were folded in. One file, one new line.

### Step 5.3: Inspect the result

```bash
git ll
```

Output:

```
* df31307 (HEAD -> main, dev) Updated in dev
* c7b2c62 Add branch.txt to main
```

Both branches now point at the same commit, and HEAD is on `main`. The graph is exactly what it would have looked like if you had made both commits on `main` directly. **There is no record of the branch in the history.** Git did not preserve any indicator that there ever was a `dev` branch.

Confirm the file looks right:

```bash
cat branch.txt
```

Output:

```
This is the main branch
This is added in dev
```

The line added on `dev` is now part of `main`.

> **Why is "fast-forward" called that?** Because Git did not have to compute a merge at all. With both branches on a single line and `main` behind `dev`, the only thing to do is fast-forward `main`'s pointer to catch up. No new commit, no chance of conflict, no merge algorithm runs. The other kind of merge ("three-way" or "true" merge, where both branches have diverged) is the topic of the next lab.

### Step 5.4: Delete the merged branch

`dev` no longer has anything `main` does not. It has served its purpose. Delete it:

```bash
git branch
```

Output:

```
  dev
* main
```

```bash
git branch -d dev
```

Output:

```
Deleted branch dev (was df31307).
```

```bash
git branch
```

Output:

```
* main
```

Only `main` remains. The dot-file `.git/refs/heads/dev` is gone. The commit it pointed at is still in the object store, reachable from `main` (since `main` now includes it).

> **`-d` vs `-D`.** `git branch -d <branch>` is a safety check: it only deletes the branch if its commits are reachable from another branch. If you tried to delete `dev` while it still had commits not on `main`, Git would refuse and tell you to use `-D` (capital D) if you really mean it. **`-D` is irreversible (within reason); it deletes the branch pointer immediately, and if no other ref points at the commits, Git's garbage collector eventually removes them.** Use `-d` by default and let Git protect you.

---

## Part 6: A Useful Shortcut

The two-step "create branch, then check it out" pattern is so common that Git has a shortcut. The next time you want a new branch and want to switch to it immediately:

```bash
git checkout -b new-branch-name
```

Or, using the modern equivalent:

```bash
git switch -c new-branch-name
```

Both create a new branch starting at the current HEAD and switch to it in one step. You will use this constantly in real work; the two-step `git branch <name>` followed by `git checkout <name>` is mostly useful for understanding what is happening.

You do not need to run this shortcut in this lab. Just know it exists for next time.

---

## Part 7: Reflection

Answer in your notebook (or a scratch file). These are open-ended; spend at least 10 minutes.

1. **What is a branch, really?** Lab 5-1 showed that `.git/HEAD` is a tiny file containing a pointer. Inside `.git/refs/heads/`, you will find one tiny file per branch. Open one with `cat .git/refs/heads/main`. What does it contain? Given that, why does Git documentation describe a branch as "a movable pointer to a commit"?

2. **The working tree follows the branch.** In Part 4 you watched the file content change every time you switched branches. Where is each version of the file stored? When you ran `git checkout dev`, what did Git actually do to make the working tree match? (Hint: it did not "find the changes" and re-apply them.)

3. **Why fast-forward is "special."** A fast-forward merge produces no merge commit, no record of which branch the changes came from, and no chance of conflict. In what circumstances might you *want* a merge commit even though a fast-forward is possible? (Look up `git merge --no-ff` if you are curious.)

4. **`git log` vs `git ll`.** You saw that plain `git log` only shows commits reachable from the current branch. When would you reach for plain `git log` instead of `git ll`? Give a concrete situation where each is the right tool.

5. **The cost of a branch.** A branch in Git is a 40-byte file. In Subversion, a branch was a full copy of the project. What does the difference in cost change about how teams use branches in their daily work? Why is "let me try this on a branch" a routine sentence in Git but was rare in older systems?

6. **The disappearing dev branch.** After the fast-forward merge in Part 5, no trace remained in the history that a `dev` branch ever existed. For a tiny example like this lab, that is fine. For a real feature branch worked on for two weeks by three developers, would it be fine? What would you give up by losing that information, and how might a team choose to preserve it?

---

## Reference: Branching Commands

| Command | What it does |
|---------|--------------|
| `git branch` | List all local branches; mark the current one with `*`. |
| `git branch <name>` | Create a new branch at the current HEAD. Does not switch. |
| `git branch -d <name>` | Delete a branch (safe: refuses if it has commits not in any other branch). |
| `git branch -D <name>` | Force-delete a branch (irreversible if no other ref points at the commits). |
| `git checkout <branch>` | Switch HEAD to the named branch. Working tree updates to match. |
| `git switch <branch>` | Same as `git checkout <branch>`, but newer and clearer. |
| `git checkout -b <name>` | Create a new branch and switch to it in one step. |
| `git switch -c <name>` | Same as `git checkout -b <name>`, but newer and clearer. |
| `git merge <branch>` | Merge the named branch into the current branch. May fast-forward, may create a merge commit, may conflict. |

---

## Reference: What Lives Where on Disk

For a repository with branches `main` and `dev`, `.git/` contains:

```
.git/
    HEAD                          contains: "ref: refs/heads/<current-branch>"
    refs/
        heads/
            main                  contains: 40-char commit hash
            dev                   contains: 40-char commit hash
        tags/                     (empty unless you have tags)
    objects/
        <hash>/<rest-of-hash>     the commits, trees, and blobs
    config
    ...
```

Every branch is a single file under `refs/heads/`. Every commit is an immutable object under `objects/`. HEAD is a pointer to whichever branch you are currently on. Everything else in Git is built on top of these three things.

You can prove this to yourself. From your `branchlab` directory, after the merge:

```bash
cat .git/HEAD
cat .git/refs/heads/main
ls .git/refs/heads/
```

The HEAD file should point at `refs/heads/main`. The `main` file should contain the hash of the latest commit. The `heads/` directory should contain only `main` (since you deleted `dev`).

---

## Troubleshooting

**`git branch` shows `master`, not `main`.**
Your `init.defaultBranch` is not configured. Set it with `git config --global init.defaultBranch main` for future repositories. For the current one, rename the branch: `git branch -m master main`.

**`git checkout dev` says "error: pathspec 'dev' did not match any file."**
The branch was not created. Run `git branch dev` first, then `git checkout dev`. Or do both at once with `git checkout -b dev`.

**`git commit` after `echo "..." >> branch.txt` says "nothing to commit, working tree clean."**
You forgot to `git add branch.txt` first. Or you accidentally used `>` instead of `>>` and overwrote the file with the *same* content (no change to detect). Re-run with `>>` to append.

**`git merge dev` says "Already up to date."**
You ran the merge while still on the `dev` branch, or `main` has already been merged. Run `git branch` to confirm which branch you are on; you should see `* main`.

**`git merge dev` opens an editor instead of merging immediately.**
Your Git configuration has `merge.ff = false` set, which forces every merge to create a new merge commit (even fast-forwardable ones). The editor is asking for the commit message. For this lab, type a message, save, and quit; or set `merge.ff = true` in your config to restore the default fast-forward behaviour.

**`git branch -d dev` says "branch 'dev' is not fully merged."**
Either you have not run the merge yet (do Part 5 first), or you switched off `main` and are trying to delete `dev` from a branch that doesn't include `dev`'s commits. Run `git checkout main` first, then `git merge dev`, then `git branch -d dev`.

**The `(HEAD -> main, dev)` annotation in `git ll` confuses you.**
It means "this commit has three pointers aimed at it: HEAD, the branch `main`, and the branch `dev`." After a fast-forward merge, both branches are at the same commit, and HEAD is on `main`. After you delete `dev`, only `(HEAD -> main)` will remain.

---

## Further Reading

- **Pro Git**, Chapter 3: <https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell>. The single best introduction to how branches work internally.
- **`git help branch`** and **`git help merge`**: the canonical references.
- **Learn Git Branching** (interactive): <https://learngitbranching.js.org/>. A visual sandbox that lets you run branching and merging commands and see the graph change. Excellent for building intuition.
- **A Successful Git Branching Model** (Vincent Driessen, 2010): <https://nvie.com/posts/a-successful-git-branching-model/>. The original "GitFlow" article. Useful to understand even if your team uses a simpler model, because every team's workflow is some variation on this.
- **Trunk-based Development**: <https://trunkbaseddevelopment.com/>. The modern alternative to GitFlow, used by Google, Facebook, and most large engineering organizations.

---

## End of Lab 5-3

You may keep your `branchlab` directory for reference or delete it. Subsequent labs do not depend on it.
