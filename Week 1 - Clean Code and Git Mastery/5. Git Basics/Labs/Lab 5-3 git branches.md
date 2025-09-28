# Lab 3 - Git Branching

- Create a new repository in a director call `gitlab`

```bash
rotech@studentvm:~$ mkdir branchlab
protech@studentvm:~$ cd branchlab
protech@studentvm:~/branchlab$ git init
Initialized empty Git repository in /home/protech/branchlab/.git/
``` 
 
## Part 1: Create a file

- Create a file `branch.txt`
- Open it in any editor and add the line
  - "This is the main branch"
- Or just create it at the command line

```bash
echo "This is the main branch" >> branch.txt
protech@studentvm:~/branchlab$ cat branch.txt
This is the main branch


```
- Commit the file and confirm

```bash
protech@studentvm:~/branchlab$ git add branch.txt
protech@studentvm:~/branchlab$ git commit -m "Add branch.txt to main"
[main (root-commit) c7b2c62] Add branch.txt to main
 1 file changed, 1 insertion(+)
 create mode 100644 branch.txt
protech@studentvm:~/branchlab$ git log
commit c7b2c628e823e3deb7d469bf9d51515635cec6fc (HEAD -> main)
Author: Rocket Student <noone@nowhere.com>
Date:   Sat Sep 27 18:37:00 2025 -0400

    Add branch.txt to main
protech@studentvm:~/branchlab$ 

```

## Part 2: Create a new branch

- Create a new branch
- List the branches
- The one that is marked with an `*` is the one that is currently checked out

```bash
protech@studentvm:~/branchlab$ git branch dev
protech@studentvm:~/branchlab$ git branch
  dev
* main

```

## Part 3: Check out

- Check out the dev branch and modify the `branch.txt` file by adding a line

```bash
protech@studentvm:~/branchlab$ git checkout dev
Switched to branch 'dev'
protech@studentvm:~/branchlab$ echo "This is added in dev" >> branch.txt
protech@studentvm:~/branchlab$ cat branch.txt
This is the main branch
This is added in dev

```

- Commit the changes

```bash
On branch dev
Changes not staged for commit:
 	modified:   branch.txt

protech@studentvm:~/branchlab$ git add branch.txt
protech@studentvm:~/branchlab$ git commit -m "Updated in dev"
[dev df31307] Updated in dev
 1 file changed, 1 insertion(+)
```

- Check the log to see the new commit and that HEAD is pointing to this commit which is the one the branch `dev` is pointing to.

```bash
protech@studentvm:~/branchlab$ git log
commit df3130709b96d99648f0190df3e3c67b2fd42866 (HEAD -> dev)
Author: Rocket Student <noone@nowhere.com>
Date:   Sat Sep 27 18:47:25 2025 -0400

    Updated in dev

commit c7b2c628e823e3deb7d469bf9d51515635cec6fc (main)
Author: Rocket Student <noone@nowhere.com>
Date:   Sat Sep 27 18:37:00 2025 -0400

    Add branch.txt to main

```

## Part 4: Compare branches

- Check out the `main` branch and look at the contents of the file.

```bash
protech@studentvm:~/branchlab$ git checkout main
Switched to branch 'main'
protech@studentvm:~/branchlab$ cat branch.txt
This is the main branch
```

- Check the log to see which commit is being shown in the working directory

```bash
git log
commit c7b2c628e823e3deb7d469bf9d51515635cec6fc (HEAD -> main)
Author: Rocket Student <noone@nowhere.com>
Date:   Sat Sep 27 18:37:00 2025 -0400

    Add branch.txt to main

```

- Notice that the `main` branch does not know about any commits past the one that it is pointing too

- Switch back and forth between the branches so you can confirm the files are different.

## Part 5: Fast Forward Merge

- Make sure you are in the `main` branch

```bash
protech@studentvm:~/branchlab$ git branch
  dev
* main
```

- To merge the `dev` branch into the `main` branch, all we need to do is make `main` point to the same commit as `dev`

- Merge the branches

```bash
protech@studentvm:~/branchlab$ git merge dev
Updating c7b2c62..df31307
Fast-forward
 branch.txt | 1 +
 1 file changed, 1 insertion(+)

```

- Check the log to see the effect of the merge

```bash
protech@studentvm:~/branchlab$ git log
commit df3130709b96d99648f0190df3e3c67b2fd42866 (HEAD -> main, dev)
Author: Rocket Student <noone@nowhere.com>
Date:   Sat Sep 27 18:47:25 2025 -0400

    Updated in dev

commit c7b2c628e823e3deb7d469bf9d51515635cec6fc
Author: Rocket Student <noone@nowhere.com>
Date:   Sat Sep 27 18:37:00 2025 -0400

    Add branch.txt to main

```

- Delete the `dev` branch

```bash
protech@studentvm:~/branchlab$ git branch
  dev
* main
protech@studentvm:~/branchlab$ git branch -d dev
Deleted branch dev (was df31307).
protech@studentvm:~/branchlab$ git branch
* main
protech@studentvm:~/branchlab$ 

```

## End