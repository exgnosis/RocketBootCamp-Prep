# Lab 5-4: Resolving Merge Conflicts in Git

## Overview

In the previous lab you saw the simplest kind of merge: a fast-forward. The receiving branch had not moved since the working branch was created, so Git just slid the pointer forward and the merge was done. No new commit, no decision to make, no chance of trouble.

This lab is about the case where that doesn't work. Two branches start from the same commit but each move forward on their own. When you try to merge them, Git compares both branches against their common ancestor and tries to combine the changes automatically. Most of the time it succeeds (a **three-way merge** with a merge commit). But when both branches have modified the *same line* of the *same file* in different ways, Git refuses to guess. It writes both versions into the file, surrounded by markers, and hands the problem back to you. This is a **merge conflict**, and resolving it is one of the most common things a developer does that has no automated solution.

You will create two branches that edit the same line of a small recipe file in different ways, attempt to merge them, see the conflict markers Git inserts, resolve the conflict in **VS Code** (which Git is configured to use as the default editor in this lab series), stage the resolved file, and finalize the merge commit. By the end you will have a clear procedure to follow whenever a merge conflict appears, and you will understand what `<<<<<<<`, `=======`, and `>>>>>>>` actually mean.

Conflicts feel scary the first few times. The single most important thing to internalize is this: **a conflict is not an error.** Git is working correctly. It is asking you, the human, to make a decision that the algorithm cannot make for you. Once you understand what the markers mean, the resolution is just text editing.

**This lab is hands-on.** You type every command yourself in a terminal and edit a file in VS Code.

**Estimated time:** 30 to 40 minutes
**Difficulty:** Beginner to Intermediate

**Prerequisites:**

- Completion of Labs 5-1, 5-2, and 5-3. You should be comfortable with `git init`, `git add`, `git commit`, `git status`, `git log`, `git branch`, `git checkout`, and `git merge` (fast-forward case).
- Git 2.30 or later.
- The `git ll` alias configured (`log --oneline --graph --decorate --all`).
- The `init.defaultBranch=main` setting.
- VS Code installed and the `code` command available on your `PATH`. Test by running `code --version` in a terminal; you should see version numbers, not "command not found." (On macOS, the `code` command is enabled from inside VS Code under **View > Command Palette > Shell Command: Install 'code' command in PATH**.)
- Git configured to use VS Code as its editor: `git config --global core.editor "code --wait"`. The `--wait` flag is important; without it, Git will think the editor closed instantly and skip your message.

You will create a new repository for this lab. The `branchlab` repository from Lab 5-3 is not needed.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Construct a scenario in which two branches diverge from a common ancestor and modify the same content.
2. Trigger a merge conflict deliberately and read Git's conflict report.
3. Identify the conflict markers `<<<<<<<`, `=======`, and `>>>>>>>` in a file and explain what each one means.
4. Resolve a conflict using VS Code's built-in conflict editor (Accept Current Change, Accept Incoming Change, Accept Both Changes, Compare Changes).
5. Resolve a conflict by hand-editing the markers when the right answer is neither side as-written.
6. Stage the resolved file and finalize the merge commit.
7. Use `git merge --abort` to back out of a merge that is going badly and try a different approach.
8. Read the resulting two-parent merge commit in `git ll` and explain why it has two parents.

---

## Part 1: Create the Lab Repository

### Step 1.1: Create the directory and initialize Git

```bash
mkdir mergelab
cd mergelab
git init
```

Output:

```
Initialized empty Git repository in /home/protech/mergelab/.git/
```

### Step 1.2: Create a small file with multiple lines

Most merge conflicts happen in files that have several lines, only one of which is being changed by each side. We'll use a tiny recipe file:

```bash
cat > recipe.txt << 'EOF'
Pancakes
========
1. Mix 1 cup of flour with 1 tsp of salt.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
EOF
cat recipe.txt
```

Output:

```
Pancakes
========
1. Mix 1 cup of flour with 1 tsp of salt.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

> **Why a `here-document` (`<<` syntax)?** The triple-`>` chevrons (`>>>`) we'll see later in this lab look just like shell redirection from a distance. Using `cat << 'EOF' ... EOF` to write the file makes it harder to confuse Git's conflict markers with shell syntax in your scrollback. Single-quote the marker (`'EOF'`) so the shell does not expand `$` or backticks inside the content.

Stage and commit:

```bash
git add recipe.txt
git commit -m "Add pancake recipe"
```

Output:

```
[main (root-commit) 2380906] Add pancake recipe
 1 file changed, 5 insertions(+)
 create mode 100644 recipe.txt
```

You now have a single commit on `main`. Both your future branches will start from here.

---

## Part 2: Create Divergent Branches

A merge conflict requires that both branches make changes after a common ancestor. The shortest path to that is: create a branch, modify a line, commit; switch back, modify the *same* line differently, commit. Now both branches have moved forward, and neither is an ancestor of the other.

### Step 2.1: Create and switch to the `sweet` branch

You will use the shortcut from the end of Lab 5-3:

```bash
git checkout -b sweet
```

Output:

```
Switched to a new branch 'sweet'
```

Confirm:

```bash
git branch
```

Output:

```
  main
* sweet
```

### Step 2.2: Modify the salt line on the `sweet` branch

A baker who wants sweet pancakes replaces the salt with sugar. Open the file in VS Code:

```bash
code recipe.txt
```

In the editor, find the line that reads:

```
1. Mix 1 cup of flour with 1 tsp of salt.
```

and change it to:

```
1. Mix 1 cup of flour with 2 tbsp of sugar.
```

Save (`Ctrl+S` on Linux/Windows, `Cmd+S` on macOS) and return to the terminal. Verify the change:

```bash
cat recipe.txt
```

Output:

```
Pancakes
========
1. Mix 1 cup of flour with 2 tbsp of sugar.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

Commit:

```bash
git add recipe.txt
git commit -m "Sweeten the pancakes"
```

Output:

```
[sweet f7f3fa1] Sweeten the pancakes
 1 file changed, 1 insertion(+), 1 deletion(-)
```

The `sweet` branch is now one commit ahead of `main`.

### Step 2.3: Switch back to `main` and modify the SAME line differently

```bash
git checkout main
cat recipe.txt
```

Output:

```
Pancakes
========
1. Mix 1 cup of flour with 1 tsp of salt.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

The salt line is back to its original "1 tsp of salt" wording. The change you made on `sweet` is invisible from `main`; it lives on a different branch.

Now a *different* baker (a cook who wants fluffier pancakes, not sweeter ones) modifies the same line. Open the file in VS Code:

```bash
code recipe.txt
```

Find the same line as before:

```
1. Mix 1 cup of flour with 1 tsp of salt.
```

and change it to:

```
1. Mix 1 cup of flour with 1 tbsp of baking powder.
```

Save. Back in the terminal:

```bash
cat recipe.txt
```

Output:

```
Pancakes
========
1. Mix 1 cup of flour with 1 tbsp of baking powder.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

Commit:

```bash
git add recipe.txt
git commit -m "Add baking powder for fluffiness"
```

Output:

```
[main 0836d33] Add baking powder for fluffiness
 1 file changed, 1 insertion(+), 1 deletion(-)
```

### Step 2.4: Look at the divergent graph

```bash
git ll
```

Output:

```
* 0836d33 (HEAD -> main) Add baking powder for fluffiness
| * f7f3fa1 (sweet) Sweeten the pancakes
|/  
* 2380906 Add pancake recipe
```

This is the most important moment in the lab so far. Read the graph carefully.

- There is a common ancestor at the bottom (`2380906`): the original "Add pancake recipe" commit.
- The graph splits into two lines above it. The left line is `main`'s history; the right line is `sweet`'s history.
- Each branch made exactly one commit after the split. Both commits modified the same line of the same file, but to different content.
- HEAD is on `main`.

ASCII picture of the state:

```
       0836d33   <-- HEAD -> main
      /
2380906
      \
       f7f3fa1   <-- sweet
```

Neither branch is an ancestor of the other. A fast-forward merge is not possible. Git will have to perform a real three-way merge, and because both sides changed the same line, that merge is going to conflict.

---

## Part 3: Trigger the Merge Conflict

### Step 3.1: Attempt the merge

You are on `main`. You want to bring `sweet`'s changes in:

```bash
git merge sweet
```

Output:

```
Auto-merging recipe.txt
Fast-forward
```

...is what you would have seen in Lab 5-3. This time, you'll see:

```
Auto-merging recipe.txt
CONFLICT (content): Merge conflict in recipe.txt
Automatic merge failed; fix conflicts and then commit the result.
```

Read every word:

- **`Auto-merging recipe.txt`**: Git tried to merge the file automatically.
- **`CONFLICT (content): Merge conflict in recipe.txt`**: it could not. The `(content)` qualifier means the conflict is about file content, not file structure (a "tree conflict" happens when, for example, one branch deletes a file the other modified).
- **`Automatic merge failed; fix conflicts and then commit the result.`**: Git has stopped halfway. Some changes have been applied; one needs your input.

Your shell prompt may have changed to show the merge state. The merge is "in progress" until you either complete it (commit) or abort it.

### Step 3.2: Check the status

```bash
git status
```

Output:

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   recipe.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

Notice the structure of the message:

- The first line confirms you are still on `main`.
- The next two lines tell you what to do next: either fix and commit, or abort.
- The **Unmerged paths** section lists files where Git could not auto-merge. `both modified` means both branches changed this file.

When in doubt during a merge, `git status` is your map. It tells you which files are unresolved, and once you start fixing them, it tells you which files are still unresolved.

### Step 3.3: Look at the file Git produced

```bash
cat recipe.txt
```

Output:

```
Pancakes
========
<<<<<<< HEAD
1. Mix 1 cup of flour with 1 tbsp of baking powder.
=======
1. Mix 1 cup of flour with 2 tbsp of sugar.
>>>>>>> sweet
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

Look at the conflict block (the section surrounded by `<<<<<<<` and `>>>>>>>`). Git has inserted **conflict markers** to show you exactly what could not be merged:

- **`<<<<<<< HEAD`**: the start of the conflict. Everything between this line and the `=======` is what's in HEAD (the current branch, `main`).
- **`=======`**: the separator between the two versions.
- **`>>>>>>> sweet`**: the end of the conflict. Everything between the `=======` and this line is what's in the other branch (`sweet`).

The lines outside the markers (the `Pancakes` heading at the top and the `2. Add ...` and `3. Cook ...` steps below) were the same in both branches; Git merged those without help. Only the conflicting region is shown.

> **Why seven characters?** The `<<<<<<<` / `=======` / `>>>>>>>` markers are seven characters wide. This is long enough that they are extremely unlikely to appear by accident in any source code or natural text, but short enough to read at a glance. Git uses these exact markers; tools that *interact* with Git (VS Code, IntelliJ, GitHub's web UI) all recognize them.

---

## Part 4: Resolve the Conflict in VS Code

Now you make the decision Git could not make. You have three pieces of information: the version in HEAD (`main`), the version in `sweet`, and the original (which Git did not write into the file, but you remember: "1 tsp of salt"). Your options are:

1. **Take main's version.** Drop the sugar change; keep the baking powder.
2. **Take sweet's version.** Drop the baking powder change; keep the sugar.
3. **Take both.** Combine them: baking powder *and* sugar.
4. **Take neither, write something else.** Revert to salt, or write "buttermilk", or anything you decide.

For this lab, we'll use option 3: a baker who wants fluffy *and* sweet pancakes. Real pancake recipes commonly have both.

### Step 4.1: Open the file in VS Code

```bash
code recipe.txt
```

You should see the file with the conflict markers, and VS Code should be displaying its **merge conflict UI**: small clickable command links above the conflict region that read:

```
Accept Current Change | Accept Incoming Change | Accept Both Changes | Compare Changes
```

(If you don't see these, your VS Code may need the built-in **Git** extension enabled. Go to the Extensions panel and search "Git"; the built-in extension is shipped with VS Code and is on by default.)

The colour-coded blocks are also helpful:

- The **green** highlighted lines (with the heading "Current Change") are HEAD's version: `main`'s line about baking powder.
- The **blue** highlighted lines (with the heading "Incoming Change") are `sweet`'s version: the line about sugar.

These match the markers in the file. "Current" is what HEAD says (between `<<<<<<<` and `=======`). "Incoming" is what the *other* branch says (between `=======` and `>>>>>>>`). Remember the direction: you merged `sweet` *into* `main`, so the change *coming in* is from `sweet`, and the change you *currently* have is from `main`.

### Step 4.2: Try the one-click resolution buttons (then undo)

To see what each button does, click **Accept Current Change**. The conflict markers disappear and you are left with `main`'s version:

```
1. Mix 1 cup of flour with 1 tbsp of baking powder.
```

Undo (`Ctrl+Z` / `Cmd+Z`) to bring the markers back.

Click **Accept Incoming Change**. You get `sweet`'s version:

```
1. Mix 1 cup of flour with 2 tbsp of sugar.
```

Undo to bring the markers back.

Click **Accept Both Changes**. You get both lines, one after the other:

```
1. Mix 1 cup of flour with 1 tbsp of baking powder.
1. Mix 1 cup of flour with 2 tbsp of sugar.
```

That gives you both ingredients, but the result is two lines that both start with `1.`, which is wrong: the recipe should have one "step 1," not two. The buttons are mechanical; they don't know that what you actually want is **one line with both ingredients**. So undo again.

### Step 4.3: Resolve by hand-editing

For most real conflicts, none of the one-click options is exactly right. You delete the markers and write what the file should actually say.

In VS Code, delete the five conflict-marker lines (the `<<<<<<<`, the two ingredient lines, the `=======`, and the `>>>>>>>`) and replace them with a single combined line:

```
1. Mix 1 cup of flour with 1 tbsp of baking powder and 2 tbsp of sugar.
```

The full file should now look like:

```
Pancakes
========
1. Mix 1 cup of flour with 1 tbsp of baking powder and 2 tbsp of sugar.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

Save the file (`Ctrl+S` / `Cmd+S`) and return to the terminal.

### Step 4.4: Confirm the markers are gone

```bash
cat recipe.txt
```

Output:

```
Pancakes
========
1. Mix 1 cup of flour with 1 tbsp of baking powder and 2 tbsp of sugar.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

No `<<<<<<<`, no `=======`, no `>>>>>>>`. If any of these remain, the file is not resolved, and the next step will not complete.

> **A common mistake.** Beginners sometimes leave a stray `=======` in the file. The marker is just text once VS Code is closed, so Git will happily commit it. The result is a file with conflict markers in it that compiles or runs depending on language and luck. Always check `cat` output for `<<<<<<<`, `=======`, and `>>>>>>>` before committing. A pre-commit hook (covered in a later lab) can do this for you automatically.

---

## Part 5: Stage and Commit the Merge

The file is fixed but Git does not yet know that you consider the conflict resolved. You tell it by staging the file.

### Step 5.1: Check the status

```bash
git status
```

Output:

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   recipe.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

The status hasn't changed yet. Git can see that `recipe.txt` was modified, but it does not know whether you have resolved the conflict or just edited around it. The act of `git add` is what marks the file resolved.

### Step 5.2: Stage the resolved file

```bash
git add recipe.txt
git status
```

Output:

```
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
	modified:   recipe.txt
```

Read the first line carefully: **All conflicts fixed but you are still merging.** This is Git's way of saying "good, but you have one more step." The merge is staged; it just isn't committed yet.

### Step 5.3: Complete the merge commit

```bash
git commit
```

VS Code opens a new window or tab with a draft merge message. Git pre-fills a sensible default:

```
Merge branch 'sweet'

# Conflicts:
#       recipe.txt
```

You can edit this if you want a more descriptive message (some teams require this; many do not for the simple case). Lines starting with `#` are comments and will be stripped. For this lab, leave the default. Save the file and close the tab (`Ctrl+W` / `Cmd+W`, or just close the window).

VS Code closes and Git completes the commit:

```
[main 47390fc] Merge branch 'sweet'
```

> **Why does VS Code open?** This is the `core.editor` setting in your Git config. `git commit` without a `-m` flag opens whatever editor is configured. With `core.editor "code --wait"`, VS Code opens and Git waits for the window to close before continuing. Without `--wait`, VS Code would launch and return control immediately, Git would think the editor was done, and your commit message would be empty. This is why the prerequisites checklist mentions `--wait`.
>
> If you prefer to skip the editor and use the default merge message, you can run `git commit --no-edit` instead. That commits immediately with whatever message Git pre-filled.

### Step 5.4: Inspect the result

```bash
git ll
```

Output:

```
*   47390fc (HEAD -> main) Merge branch 'sweet'
|\  
| * f7f3fa1 (sweet) Sweeten the pancakes
* | 0836d33 Add baking powder for fluffiness
|/  
* 2380906 Add pancake recipe
```

This is what a three-way merge looks like in the graph. Notice:

- The new commit (`47390fc`) is at the top. HEAD is on `main`, and `main` is at this new commit.
- The new commit has **two parent lines** (`|\`). One leads back down to `0836d33` (main's previous tip), the other to `f7f3fa1` (sweet's tip).
- Both diverging lines reunite at the common ancestor `2380906`.

The merge commit has two parents. That is the structural fingerprint of a true (non-fast-forward) merge. You can see this directly:

```bash
git log --oneline -n 1
git show --stat HEAD | head -5
```

Output:

```
47390fc Merge branch 'sweet'
commit 47390fc630eb91bace852743ea05b374cbae519f
Merge: 0836d33 f7f3fa1
Author: Rocket Student <[email protected]>
Date:   Tue May 19 13:57:18 2026 +0000
```

The `Merge: 0836d33 f7f3fa1` line is unique to merge commits. Ordinary commits have one parent; merge commits have two (or more, in the rare octopus-merge case).

Confirm the file looks right:

```bash
cat recipe.txt
```

Output:

```
Pancakes
========
1. Mix 1 cup of flour with 1 tbsp of baking powder and 2 tbsp of sugar.
2. Add 1 egg and 1 cup of milk.
3. Cook on a hot griddle.
```

Both the baking powder change and the sugar change are in the file, combined into one sensible line. The merge commit's snapshot includes your resolution exactly as you wrote it.

### Step 5.5: Delete the merged branch

`sweet` has nothing `main` does not, so it can go:

```bash
git branch -d sweet
```

Output:

```
Deleted branch sweet (was f7f3fa1).
```

```bash
git ll
```

Output:

```
*   47390fc (HEAD -> main) Merge branch 'sweet'
|\  
| * f7f3fa1 Sweeten the pancakes
* | 0836d33 Add baking powder for fluffiness
|/  
* 2380906 Add pancake recipe
```

The `(sweet)` label is gone, but the commit `f7f3fa1` remains. It is reachable through `main`'s merge commit, so Git keeps it. Unlike the fast-forward merge in Lab 5-3, **the history records that the merge happened**: the two-parent commit is permanent evidence that two lines of development came together.

---

## Part 6: Aborting a Merge (For Reference)

Sometimes you start a merge, see the conflict, and decide it's not worth resolving right now. Maybe the conflict is huge, maybe you realize you're merging the wrong branch, maybe you just want to think about it. You can back out without consequences.

You don't need to actually run this in your current lab (your merge is already finished). This is a procedure to remember for next time.

If a merge is in progress and you haven't committed yet:

```bash
git merge --abort
```

This resets your working tree to whatever it was before you ran `git merge`. All conflict markers vanish. Your branches go back to their pre-merge tips. It is as if the merge never happened.

`git merge --abort` is safe to run at any point during the merge as long as you haven't yet committed the resolution. After the commit, the merge is part of history; aborting is no longer the right tool. (Use `git reset --hard HEAD~1` to undo the last commit if you really need to, but that's a topic for a later lab.)

---

## Part 7: Reflection

Answer in your notebook (or a scratch file). These are open-ended; spend at least 10 minutes.

1. **Why couldn't Git resolve this automatically?** Git successfully merges most diverging branches without help. What is specifically true about the changes in this lab that prevented automation? Could a smarter merge algorithm have solved it? (Think about whether "fluffier" and "sweeter" express the same intent, or different intents.)

2. **The three-way merge.** A true merge is called a "three-way" merge. What are the three versions Git is comparing? Why isn't the original file (the common ancestor) shown in the conflict markers? Would including it help, or would it just add clutter?

3. **HEAD and "the other one."** During the conflict, the markers said `HEAD` for one side and `sweet` for the other. Why these names? If you had checked out `sweet` first and merged `main` into it, which side would have been labelled `HEAD`?

4. **Resolving the wrong way.** You combined both changes. A different baker might have chosen to take only one side. What goes into that decision? Are there situations where "take both" is wrong because the two changes are *contradictory* (not just different)? Give an example from real code.

5. **The two-parent merge commit.** Unlike the fast-forward merge in Lab 5-3, this merge left a permanent record in the history: a commit with two parents. Some teams love this (it preserves the story of how features came together). Other teams hate it (it clutters the log and makes `git log` harder to read on the main branch). Look up `git merge --squash` and explain in a sentence how it sidesteps the debate.

6. **A merge versus a rewrite.** Suppose, after seeing the conflict, you had run `git merge --abort` and decided instead to rewrite your own change on top of `sweet`'s. That operation is called a **rebase**, and it is the topic of a future lab. From what you already know, what do you think rebase would look like in this scenario? What would the graph look like afterwards, compared to the merge graph you produced?

---

## Reference: The Conflict Markers

| Marker | What it means |
|--------|---------------|
| `<<<<<<< HEAD` | Start of the conflict. Everything below this line until the `=======` is the version from HEAD (the branch you are on). |
| `=======` | Separator. Everything above it is HEAD's side; everything below it is the other branch's side. |
| `>>>>>>> <branch-name>` | End of the conflict. The label after the markers is the name of the branch being merged in (or, in a rebase, the commit hash). |

There is no marker for the common ancestor by default. You can enable a "diff3" style that includes it:

```bash
git config --global merge.conflictStyle diff3
```

After that, a conflict will look like:

```
<<<<<<< HEAD
HEAD's version
||||||| <ancestor commit>
the common ancestor's version
=======
other branch's version
>>>>>>> other-branch
```

Many experienced Git users turn this on permanently. Seeing the ancestor often makes "what changed on each side" obvious at a glance.

---

## Reference: Merge Resolution Commands

| Command | What it does |
|---------|--------------|
| `git merge <branch>` | Merge the named branch into the current branch. May fast-forward, may conflict, may complete cleanly with a merge commit. |
| `git status` | During a merge, lists unresolved files under "Unmerged paths." |
| `git add <file>` | Mark a file as resolved. Stages the current contents. |
| `git commit` | Finalize the merge. Opens the editor pre-filled with a merge message. |
| `git commit --no-edit` | Same as `git commit` but uses the pre-filled message without opening the editor. |
| `git merge --abort` | Cancel the in-progress merge. Working tree restored to pre-merge state. |
| `git diff` | While merging, shows the unresolved conflicts (your file as-is, with markers). |
| `git checkout --ours <file>` | Resolve by keeping HEAD's version of the file wholesale. |
| `git checkout --theirs <file>` | Resolve by keeping the other branch's version wholesale. |
| `git mergetool` | Open an external graphical merge tool (configured via `merge.tool`). VS Code's built-in conflict UI is so good that most people don't bother with `mergetool` anymore. |

---

## Reference: VS Code's Conflict UI

VS Code recognizes Git's conflict markers automatically and displays a small command bar above each conflict region. Each command performs a textual edit and saves it back to the file:

| Command | What it does |
|---------|--------------|
| **Accept Current Change** | Keeps the HEAD side, deletes the other side and the markers. |
| **Accept Incoming Change** | Keeps the other branch's side, deletes the HEAD side and the markers. |
| **Accept Both Changes** | Keeps both sides one after the other, deletes the markers. Often produces nonsense; use only when the two sides truly are independent additions. |
| **Compare Changes** | Opens a side-by-side diff view of the two sides. Doesn't modify the file. Useful for understanding what changed. |

These commands are convenient but not magic. They do not understand your code, your intent, or your business logic. For non-trivial conflicts, do not click; edit the file by hand.

---

## Troubleshooting

**`git commit` opens an editor I don't recognize (vim, nano).**
Your `core.editor` is not set. Run `git config --global core.editor "code --wait"` and try again. (If you are stuck in vim and need to escape: press `Esc`, type `:q!`, press Enter.)

**`git commit` exits immediately with an empty message.**
Your `core.editor` is set to `code` without `--wait`. Run `git config --global core.editor "code --wait"` and try again.

**`git merge sweet` says "Already up to date."**
Either `sweet` is already merged into `main`, or you ran the merge while still on `sweet`. Run `git branch` to confirm you are on `main` (the `*` should be next to `main`).

**`git merge sweet` says "fatal: refusing to merge unrelated histories."**
The two branches don't share a common ancestor. This happens when you import a project from another repo or use the `--orphan` flag. For this lab, that shouldn't happen; check that you created both branches from the same starting commit.

**I committed a file that still has `<<<<<<<` in it.**
Easy mistake. Open the file, remove the markers and any wrong content, run `git add <file>`, then `git commit --amend` to fix the previous commit. Avoid this in the future by running `cat` on the file before committing, or installing a pre-commit hook that scans for conflict markers.

**`git merge --abort` says "fatal: There is no merge to abort."**
Either the merge is already finished (you ran `git commit`), or there was never a merge in progress. `git status` will tell you which.

**VS Code doesn't show the Accept Current/Incoming/Both buttons.**
The built-in Git extension is probably disabled. Open the Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`), search for `@builtin Git`, and make sure it's enabled.

**The conflict markers look ugly and confusing.**
Try `git config --global merge.conflictStyle diff3`. The added "ancestor" section often makes the conflict much easier to understand.

**The merge commit graph in `git ll` looks tangled.**
That's three-way merging working as designed. The "tangle" is the historical record of the divergence. If you want a cleaner graph, look up `git rebase` and `git merge --squash` in a future lab.

**Two of us conflict on the same file every day.**
That's a workflow signal, not a Git problem. Talk to your colleague about who owns which parts of the file, or split the file into pieces each of you can edit independently. Frequent conflicts often mean two people are doing related work without coordinating.

---

## Further Reading

- **Pro Git**, Chapter 3.2: <https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging>. Walks through the same scenario this lab does, in slightly more detail.
- **`git help merge`**: the canonical reference. The "How conflicts are presented" section is short and worth reading once.
- **VS Code's Git documentation**: <https://code.visualstudio.com/docs/sourcecontrol/overview>. Covers the editor's full Git integration, not just conflict resolution.
- **"How to resolve merge conflicts in Git"** (GitHub Docs): <https://docs.github.com/en/get-started/using-git/resolving-merge-conflicts-on-the-command-line>. A second perspective on the same procedure, with screenshots.
- **Mastering Git's diff3 conflict style** (any blog post on the topic): if you find conflict markers hard to read, setting `merge.conflictStyle = diff3` is the single biggest improvement most people make to their merge workflow.

---

## End of Lab 5-4

You may keep your `mergelab` directory for reference or delete it. Subsequent labs do not depend on it.

The next lab in the series covers **rebasing**, which is the other way to bring two branches together. Rebasing avoids the merge commit (and the two-parent graph) at the cost of rewriting history. You will see when each approach is the right tool.
