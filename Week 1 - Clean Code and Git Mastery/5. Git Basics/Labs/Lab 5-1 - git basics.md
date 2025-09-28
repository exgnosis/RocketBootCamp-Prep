# Lab 5-1 - Git Basics

## Part 1: Verifying git

- Log into your VM
- Create  new directory. In these note we are using `lab1` 
- Locate to the directory you just created
- Check the version of git `git --version`
- Check the configuration
  - You can't make any commits unless you have a name and email recorded since git needs to track who made a commit.
  - The user email is added since name are not going to be unique, but we can often make a reasonable assumption that emails are unique identifies

```bash
protech@studentvm:~$ mkdir lab1
protech@studentvm:~$ cd lab1

protech@studentvm:~/lab1$ git --version
git version 2.34.1

protech@studentvm:~/lab1$ git config --list
user.name=Rocket Student
user.email=noone@nowhere.com
alias.ll=log --oneline --graph --decorate --all
init.defaultbranch=main
core.editor=code --wait
```

---

## Part 2: The git repository

- In the `lab1` directory, create the git repository
- Confirm the `.git/` directory and its contents


```bash
protech@studentvm:~/lab1$ git init
Initialized empty Git repository in /home/protech/lab1/.git/

protech@studentvm:~/lab1$ git status
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)


protech@studentvm:~/lab1$ cd .git
protech@studentvm:~/lab1/.git$ ls -l
total 32
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 branches
-rw-rw-r-- 1 protech protech   92 Sep  2 13:49 config
-rw-rw-r-- 1 protech protech   73 Sep  2 13:49 description
-rw-rw-r-- 1 protech protech   21 Sep  2 13:49 HEAD
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 hooks
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 info
drwxrwxr-x 4 protech protech 4096 Sep  2 13:49 objects
drwxrwxr-x 4 protech protech 4096 Sep  2 13:49 refs

protech@studentvm:~/lab1/.git$ cat HEAD
ref: refs/heads/main
```

- Notice that there are no blobs because there is nothing under version control
- The two directories `info` and `pack` are used by git internally.

```bash
protech@studentvm:~/lab1/.git$ cd  objects
protech@studentvm:~/lab1/.git/objects$ ls -l
total 8
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 info
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 pack

total 0
```

---

## Part 3: First commit

- Check with `git log` to see a history of the commits
- Note: An alias was added to give a graphic representation of the repository `git ll`

```bash
protech@studentvm:~/lab1$ git log
fatal: your current branch 'main' does not have any commits yet
```

- Create a file and add some content and check `git status`
- Note that it is telling you that you have a file in the working directory that is not in the repo.

```bash
protech@studentvm:~/lab1$ echo "This is some text" > file.txt
protech@studentvm:~/lab1$ cat file.txt
This is some text


protech@studentvm:~/lab1$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	file.txt

nothing added to commit but untracked files present (use "git add" to track)
```

- Stage the file using `git add file.txt`
- Rerun `git status`

```bash
protech@studentvm:~/lab1$ git add file.txt
protech@studentvm:~/lab1$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   file.txt
```

- Commit the changes.
- Note that you must add a commit message
- If you run `git log`, the commit shows in the history
- Note the hashcode of the commit
- Note that `git status` tells us that the directory tree is clean
  - This means that the contents of the repository are the same as the working directory

```bash
rotech@studentvm:~/lab1$ git commit -m "First commit"
[main (root-commit) 0e426de] First commit
 1 file changed, 1 insertion(+)
 create mode 100644 file.txt
 
 
protech@studentvm:~/lab1$ git log
commit 0e426deb652fc962293f513d461efdf7fc2cfb19 (HEAD -> main)
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:06:57 2025 -0400

    First commit
    
protech@studentvm:~/lab1$ git status
On branch main
nothing to commit, working tree clean

```

- Add a line to your file and use the same process to commit the changes
- Do this three times in total so that you make three new commits
  - Each time the `file.txt` contents have one more line
- The second commit is shown below

```bash
protech@studentvm:~/lab1$ echo  "This is line 2" >> file.txt
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2

protech@studentvm:~/lab1$ git add file.txt
protech@studentvm:~/lab1$ git commit -m "Second commit"
[main e5c5b41] Second commit
 1 file changed, 1 insertion(+)
 
 
protech@studentvm:~/lab1$ git log
commit e5c5b412676f38a5f15fba00af47bc34e648d723 (HEAD -> main)
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:14:04 2025 -0400

    Second commit

commit 0e426deb652fc962293f513d461efdf7fc2cfb19
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:06:57 2025 -0400

    First commit
    
rotech@studentvm:~/lab1$ git ll
* e5c5b41 (HEAD -> main) Second commit
* 0e426de First commit
```
- Your final result should look like this:

```bash
protech@studentvm:~/lab1$ cat file.txt
This is some text
This is line 2
This is line 3
This is line 4

protech@studentvm:~/lab1$ git log
commit 31c2ebd9ae504b4378d5b80f87ba202a34dd5ec5 (HEAD -> main)
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:18:13 2025 -0400

    Fourth commit

commit 06da0ab052e771d59a43cf8f9bc6e166c439a665
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:17:09 2025 -0400

    third commit

commit e5c5b412676f38a5f15fba00af47bc34e648d723
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:14:04 2025 -0400

    Second commit

commit 0e426deb652fc962293f513d461efdf7fc2cfb19
Author: Rocket Student <noone@nowhere.com>
Date:   Tue Sep 2 14:06:57 2025 -0400

    First commit
    
protech@studentvm:~/lab1$ git ll
* 31c2ebd (HEAD -> main) Fourth commit
* 06da0ab third commit
* e5c5b41 Second commit
* 0e426de First commit

```

- Now check the blog directory
- You will see blobs but your hash codes you see might be different from the ones shown here.
- The hash codes are arranged in a tree to make retrieval faster

```bash
protech@studentvm:~/lab1/.git/objects$ ls -l
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
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 info
drwxrwxr-x 2 protech protech 4096 Sep  2 13:49 pack
```

---

### Do not delete your work, you will be using it in the next lab

---

# End Lab 1
