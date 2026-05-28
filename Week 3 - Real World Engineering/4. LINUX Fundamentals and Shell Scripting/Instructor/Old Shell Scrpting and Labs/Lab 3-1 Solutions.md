# Lab 3-1 Linux Commands – Navigation and Basic Commands

These are the solutions to the lab exercises

---

## 1. Create a Sandbox
**Problem:** Create a directory called `linux-lab` in your home folder and change into it.  
**Solution:**
```bash
mkdir -p ~/linux-lab
cd ~/linux-lab
```

---

## 2. Where Am I?
**Problem:** Show the absolute path of your current directory.  
**Solution:**
```bash
pwd
```

---

## 3. What’s Here?
**Problem:** List the contents of the current directory.  
**Solution:**
```bash
ls -1
```

---

## 4. Make Some Structure
**Problem:** Create subdirectories `projects`, `notes`, and `temp`.  
**Solution:**
```bash
mkdir -p projects notes temp
```

---

## 5. Create a Couple of Files
**Problem:** In `notes`, create empty files `intro.txt` and `todo.txt`.  
**Solution:**
```bash
touch notes/intro.txt notes/todo.txt
```

---

## 6. Add Text
**Problem:** Put the text *Welcome to Linux* into `notes/intro.txt`.  
**Solution:**
```bash
echo "Welcome to Linux" > notes/intro.txt
```

---

## 7. View a File
**Problem:** Display the contents of `notes/intro.txt`.  
**Solution:**
```bash
cat notes/intro.txt
```

---

## 8. Hidden Files
**Problem:** Create a hidden file `.hidden` and list all files, including hidden ones.  
**Solution:**
```bash
touch .hidden
ls -la
```

---

## 9. Move Around
**Problem:** Change into `notes`, list its contents, then return to the lab root.  
**Solution:**
```bash
cd notes
ls
cd ..
```

---

## 10. Absolute Path
**Problem:** Print the absolute path of the `notes` directory.  
**Solution:**
```bash
realpath notes
```

---

## 11. Copy a File
**Problem:** Copy `notes/intro.txt` to `temp/intro_copy.txt`.  
**Solution:**
```bash
cp notes/intro.txt temp/intro_copy.txt
```

---

## 12. Rename a File
**Problem:** Rename `notes/todo.txt` to `notes/tasks.txt`.  
**Solution:**
```bash
mv notes/todo.txt notes/tasks.txt
```

---

## 13. Nested Directories
**Problem:** Inside `projects`, create `app/src`.  
**Solution:**
```bash
mkdir -p projects/app/src
```

---

## 14. Directory Tree
**Problem:** Show the directory layout (top 3 levels).  
**Solution:**
```bash
find . -maxdepth 3 -type d
```

---

## 15. Find by Name
**Problem:** Find all `.txt` files under the lab directory.  
**Solution:**
```bash
find . -type f -name "*.txt"
```

---

## 16. Find Text
**Problem:** Search for the word “Linux” in all files under the lab directory.  
**Solution:**
```bash
grep -R "Linux" .
```

---

## 17. Count Lines
**Problem:** Show line/word/byte counts for `notes/intro.txt`.  
**Solution:**
```bash
wc notes/intro.txt
```

---

## 18. Sort & Unique
**Problem:** Create `names.txt` with duplicates, then show unique sorted names.  
**Solution:**
```bash
printf "Ada\nBob\nAda\nLinus\nBob\n" > names.txt
sort names.txt | uniq
```

---

## 19. Directory Size
**Problem:** Show the total disk usage of the current directory.  
**Solution:**
```bash
du -sh .
```

---

## 20. Free Space
**Problem:** Display free space for the filesystem.  
**Solution:**
```bash
df -h .
```

---

## 21. Permissions
**Problem:** List permissions for everything in `notes`.  
**Solution:**
```bash
ls -l notes
```

---

## 22. Change Permissions
**Problem:** Make `notes/intro.txt` readable/writable by you only.  
**Solution:**
```bash
chmod 600 notes/intro.txt
```

---

## 23. Who Am I?
**Problem:** Show your username and user/group IDs.  
**Solution:**
```bash
whoami
id
```

---

## 24. Symbolic Link
**Problem:** Create `intro.link` pointing to `notes/intro.txt`.  
**Solution:**
```bash
ln -s notes/intro.txt intro.link
```

---

## 25. Where’s a Command?
**Problem:** Show the full path(s) of the `ls` command.  
**Solution:**
```bash
type -a ls
```

---

## 26. Environment Variables
**Problem:** Print your home directory and list all environment variables.  
**Solution:**
```bash
echo "$HOME"
printenv | sort
```

---

## 27. Help & Manuals
**Problem:** Show the man page for `ls`, then built-in help for `mkdir`.  
**Solution:**
```bash
man ls
mkdir --help
```

---

## 28. Wildcards
**Problem:** Copy all `.txt` files from `notes` to `temp`.  
**Solution:**
```bash
cp notes/*.txt temp/
```

---

## 29. Safe Remove
**Problem:** Interactively delete `temp/intro_copy.txt`.  
**Solution:**
```bash
rm -i temp/intro_copy.txt
```

---

## 30. Cleanup
**Problem:** Delete the entire `linux-lab` directory (with confirmation).  
**Solution:**
```bash
cd ~
rm -rI linux-lab
```

---

## End