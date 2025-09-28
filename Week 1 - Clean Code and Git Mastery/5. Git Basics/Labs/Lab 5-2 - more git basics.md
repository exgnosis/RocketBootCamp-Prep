# Lab 2 - Git Basics Continued

- This lab picks up where the last lab left off.
- You should be located the `lab1` directory

## Part 1: Restoring a file

- Delete the file `file.txt`
- Confirm it's gone.
- Then restore it using `git restore file.txt`
- Confirm it's been restored
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
- Add some random content to `file.txt` in your working directory
- Confirm the changes are there
- Restore the file and confirm your change are gone

```bash
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4
this is line 5

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

- We can also specify the commit that we want to restore from
- First, use `git ll` to get a list of the commits
- _Don't copy the values shown here because yours will be different, that's why you need to list your commits_
- The command is `git restore file.txt --course <hash>`


- Restore `file.txt` as it was in the second commit.
  - In this example that has the code `e5c5b41`

```bash
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab third commit
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

- Now restore the latest version
- Note that if we leave the --source parameter out, it defaults to `HEAD`

```bash
git restore file.txt --source HEAD
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4
```

---

## Part 3: Restoring a Previous Commit

- `git restore` works on individual files
- `get checkout` works on a whole commit
- Checkout the second commit

```bash
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab third commit
* e5c5b41 Second commit
* 0e426de First commit
```
- Counting backwards from `HEAD`, it would be `HEAD~2`
- Check it out

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

- Use the `git ll` command to confirm you are seeing the second commit - note where the HEAD pointer

```bash
protech@studentvm:~/lab1$ git ll
* 31c2ebd (main) Fourth commit
* 06da0ab third commit
* e5c5b41 (HEAD) Second commit
* 0e426de First commit

protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
```

- Now switch back with `git switch -`
  - This resets the working directory to the commit the `main` branch is pointing to

```bash
git switch -
Previous HEAD position was e5c5b41 Second commit
Switched to branch 'main'
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab third commit
* e5c5b41 Second commit
* 0e426de First commit
```

