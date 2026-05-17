# Lab 5-2 - Git Basics Continued

- This lab picks up where the last lab left off.
- You should be located in the `lab1` directory
- "If you closed your terminal, navigate back with cd ~/lab1.

## Part 1: Restoring a file

- Delete the file `file.txt` with `rm file.txt`
- Confirm it's gone by running `ls`
- Then restore it using `git restore file.txt`
- Confirm it's been restored, also with `ls`
- By default, it is restored from the commit that is referenced by `HEAD`

```bash
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4

protech@studentvm:~/lab1$ rm file.txt
protech@studentvm:~/lab1$ ls

protech@studentvm:~/lab1$ git restore file.txt
protech@studentvm:~/lab1$ ls
file.txt

protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4
```

- The `restore` command will overwrite the file if it already exists in the working directory
- Add some random content to `file.txt` in your working directory (e.g., `echo "this is line 5" >> file.txt`)
- Confirm the changes are there
- Restore the file and confirm your changes are gone

```bash
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4
This is line 5

protech@studentvm:~/lab1$ git restore file.txt

protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4
```

### 

---

## Part 2: Restoring from different commit

-- We can also specify the commit that we want to restore from
- The command is `git restore file.txt --source <hash>`
- First, use `git ll` to get a list of the commits and pick the hash you want
- _Don't copy the values shown here, yours will be different. That's why you need to list your own commits._
- Restore `file.txt` as it was in the second commit (in this example, `e5c5b41`)


```bash
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab Third commit
* e5c5b41 Second commit
* 0e426de First commit

protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4

protech@studentvm:~/lab1$ git restore file.txt --source e5c5b41
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
```

- Now restore from the third commit.
- This time, note that it is the commit just before HEAD
  - We specify "HEAD - 1" as `HEAD~1`
- Restore from the third commit using `HEAD~1`
- Confirm the contents

```bash
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4

protech@studentvm:~/lab1$ git restore file.txt --source HEAD~1

protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3


```
- Now restore from the first commit using `HEAD~3`
- Confirm the contents

```bash
protech@studentvm:~/lab1$ git restore file.txt --source HEAD~3
protech@studentvm:~/lab1$ cat file.txt
This is some text
```

- Now restore file.txt to the latest committed version
- Note that if we leave the --source parameter out, it defaults to `HEAD`

```bash
protech@studentvm:~/lab1$ git restore file.txt --source HEAD
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4
```

---

## Part 3: Restoring a Previous Commit

- `git restore` works on individual files
- `git checkout` switches your entire working directory to match a whole commit
- We're going to check out the second commit, which will change the state of every tracked file
- 
```bash
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab Third commit
* e5c5b41 Second commit
* 0e426de First commit
```
- Counting backwards from `HEAD`, it would be `HEAD~2`
- Check it out with `git checkout HEAD~2`
- Note that you are now in "detached HEAD" state, which means that `HEAD` is not pointing to a branch, but directly to a commit

```bash
protech@studentvm:~/lab1$ git checkout HEAD~2
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

- Use `git ll` and notice that `HEAD` is now pointing at the second commit, while `main` is still pointing at the fourth commit
- This is what "detached HEAD" means
  - `HEAD` is no longer tied to a branch

```bash
protech@studentvm:~/lab1$ git ll
* 31c2ebd (main) Fourth commit
* 06da0ab Third commit
* e5c5b41 (HEAD) Second commit
* 0e426de First commit

protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
```

- Now switch back with `git switch -`
  - The `-` means "the previous branch" — like `cd -` in bash
  - This resets the working directory to whatever commit `main` is pointing to
  
```bash
protech@studentvm:~/lab1$ git switch -
Previous HEAD position was e5c5b41 Second commit
Switched to branch 'main'
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab Third commit
* e5c5b41 Second commit
* 0e426de First commit
```

---

### Do not delete your work, you may use it in a future lab

---

# End Lab 5-2