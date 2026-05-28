# Lab 3-1: Secure Coding in Java

## Overview

This lab is the first in a sequence on secure coding. The previous labs in the curriculum focused on bugs that produced wrong answers or crashes; this one focuses on bugs that produce *unauthorized behavior*. The line between the two is thinner than it looks. A program that crashes on bad input is buggy. A program that *does not crash* but lets the user access files they should not, or leaks credentials in its log output, is buggy in a way that is much more dangerous and much harder to detect.

You will work with a small Java program that copies one file to another. It compiles. It runs. For valid inputs it does what its name suggests. It also has at least seven distinct security and reliability problems, ranging from hard-coded secrets to path traversal to resource leaks. None of them produce an error message that says "this is a security flaw." Most of them produce no error message at all; the program simply does the wrong thing more quietly than the program's author imagined.

You will find the flaws by reading the code carefully, by running it against inputs the author did not anticipate, and by refactoring it into a version that is safe by construction. After your own refactor is done, you will compare it to a canonical solution and notice what you missed. A stretch step at the end has you ask Copilot to do the same security review and compare its findings to yours.

The lab is therefore part **adversarial reading exercise** (look at code the way an attacker would, not the way a friendly reviewer would), part **refactoring exercise** (rewrite the code so the flaws cannot be reintroduced), and part **comparison exercise** (your findings vs. the canonical list, your refactor vs. the canonical refactor, your review vs. an AI review).

**This lab is hands-on.** You read and write the code yourself; no AI assistance is needed or expected for the main exercise. The Copilot stretch in Part 7 invites you to compare your analysis to one Copilot produces, but only after you have done the work yourself.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify common security flaws in Java file-handling code: path injection, hard-coded secrets, secrets leaked in logs, public mutable state, missing resource cleanup, sensitive data in exception messages.
2. Demonstrate a path-traversal attack by passing `../` in a path argument and observe what the program does.
3. Demonstrate a same-source-and-destination bug by passing the same path twice and observe the resulting data loss.
4. Refactor a Java class so its fields are private, final, and validated at construction time.
5. Canonicalize a path using `toRealPath()` and check that it lies under a configured base directory before opening it.
6. Use `try-with-resources` to ensure `InputStream` and `OutputStream` instances are always closed, even on exception.
7. Write minimal, non-sensitive error messages that tell the user what they need to fix without leaking server paths, internal class names, or stack traces.
8. Recognize that "the code runs and produces the expected output for typical inputs" is not evidence that the code is safe.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder**.
3. Create a new folder called `security-lab` in your usual workspace location, then open it.
4. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `SECURITY-LAB` at the top.

### Step 1.2: Confirm Java and the Extension Pack are installed

In the VS Code integrated terminal (`` Ctrl+` ``):

```bash
java --version
```

Java 17 or later is required. The lab uses the single-source-file launcher (`java SafeFileCopier.java`), so you do not need a separate `javac` step.

This lab also requires VS Code's **Extension Pack for Java** (Microsoft) for the Run / Debug links above `main`. If you used Lab 2-2 (Java debugging), the pack is already installed. If not, install it now via the Extensions view (`Ctrl+Shift+X`).

### Step 1.3: Create the buggy starter file

In the Explorer, create a new file called `SafeFileCopier.java` and paste in the following code exactly:

```java
import java.io.*;
import java.nio.file.*;

public class SafeFileCopier {
    public static void main(String[] args) throws Exception {
        CopierConfig cfg = new CopierConfig();
        cfg.source = args.length > 0 ? args[0] : "./passwd";
        cfg.dest   = args.length > 1 ? args[1] : "./out.txt";

        String s = System.getProperty("user.dir") + File.separator + cfg.source;
        String d = System.getProperty("user.dir") + File.separator + cfg.dest;

        var in = new FileInputStream(s);
        var out = new FileOutputStream(d);

        in.transferTo(out);

        System.out.println("Copied from " + s + " to " + d + " with key " + CopierConfig.SECRET);
    }
}

class CopierConfig {
    public String source;
    public String dest;
    public static String SECRET = "harDcod3d";
}
```

Save the file.

> **A note on the file structure.** The lab puts `public class SafeFileCopier` first and `class CopierConfig` second. The Java single-source-file launcher uses the *first* top-level type as the launch class, regardless of which one is `public`. Some published examples (including some earlier versions of this lab) declare `CopierConfig` first; that ordering compiles fine with `javac` but fails with `java SafeFileCopier.java` because the launcher will try to run `CopierConfig`. The lab's reordering is a tooling fix, not a security fix; treat both versions as the same buggy code for the purposes of this lab.

### Step 1.4: Create a fake passwd file for the demonstration

Real Unix systems have a sensitive file at `/etc/passwd` that lists user accounts. The lab's default source filename is `./passwd`, which is deliberately suggestive but is a local file in your project, not the system file. Create it:

In the Explorer, create a new file called `passwd` (no extension) and paste:

```
# This is a fake passwd file for the lab.
root:x:0:0:root:/root:/bin/bash
alice:x:1000:1000:alice:/home/alice:/bin/bash
```

Save the file. None of the data here is real; it just looks plausible enough that you will recognize it when you see it leak.

### Step 1.5: Create a lab notebook

Create a file called `notebook.md` in the workspace. Start it with:

```markdown
# Security Lab Notebook

## Part 2: Baseline run

## Part 3: Probe the failure modes

## Part 4: First-pass analysis

## Part 5: Apply your refactor

## Part 6: Compare to the canonical solution

## Part 7: Stretch (Copilot security review)

## Part 8: Reflection
```

Save it.

---

## Part 2: Run the Code (Baseline)

Before you criticize the code, see what it does in the happy case.

### Step 2.1: Run with default arguments

Click **Run** above the `main` method in `SafeFileCopier.java`, or in the terminal:

```bash
java SafeFileCopier.java
```

Expected output (your path prefix will differ):

```
Copied from /home/you/security-lab/./passwd to /home/you/security-lab/./out.txt with key harDcod3d
```

A new file `out.txt` appears in the Explorer. Open it and confirm its contents match the `passwd` file from Step 1.4.

### Step 2.2: Stop and read the output line

The success message is one line, but it contains four pieces of information. Write each one in your notebook:

1. The absolute path to the source file.
2. The absolute path to the destination file.
3. The literal text "with key" followed by...
4. A hard-coded string value from inside the program.

Each of these has a problem. Before you read Part 3, write at least one sentence in your notebook for each: what is the problem with including this piece of information in the success message? Imagine the message is going to be captured by a log aggregator and possibly emailed to an operations team or stored for years.

> **A note on the message.** A "success message" feels like the safest possible kind of output, but in production systems it is one of the most-exfiltrated kinds of output. Logs get scraped, indexed, replicated to backup systems, viewed by support staff who do not need to see paths and credentials, included in screenshots in bug reports, and emailed in incident summaries. Anything that ends up in a log line should be assumed to end up somewhere you did not intend.

Delete the generated `out.txt` before moving on:

```bash
rm out.txt
```

---

## Part 3: Probe the Failure Modes

The code "works" in the sense that the default run produces the right output. The next two steps test the code with inputs the author probably did not have in mind.

### Step 3.1: Path traversal

The first argument is treated as a file path that gets glued onto `System.getProperty("user.dir")`. What happens if the argument contains `..`?

In the terminal:

```bash
java SafeFileCopier.java ../../../etc/hostname ./hostname_stolen.txt
```

Expected output (the path will be longer; this is the structure):

```
Copied from /home/you/security-lab/../../../etc/hostname to /home/you/security-lab/./hostname_stolen.txt with key harDcod3d
```

Now read the generated file:

```bash
cat hostname_stolen.txt
```

You should see the contents of `/etc/hostname` (the name of your machine, perhaps `vm` or your laptop's hostname). The program just happily copied a file that is not even in the lab directory; it is in `/etc/`, a system directory.

The mechanism is straightforward: the code computes `user.dir + "/" + "../../../etc/hostname"` and lets the operating system's path resolution figure out where that ends up. Three `..` segments climb three levels out of the working directory; if your working directory is shallow enough, you land in the root, and `etc/hostname` resolves from there. There is no path validation anywhere in the code; the path is whatever the user typed.

This is called **path traversal** (CWE-22, also known as "directory traversal"). It is one of the oldest and still one of the most commonly exploited classes of web vulnerability. Any program that takes a path from a user and uses it without canonicalization-and-check has this flaw.

Clean up:

```bash
rm hostname_stolen.txt
```

### Step 3.2: Same source and destination

What happens if you pass the same file as both source and destination? The argument check on the second-arg default lets you pick any two paths, including the same one.

```bash
cp passwd test_file.txt
cat test_file.txt
java SafeFileCopier.java test_file.txt test_file.txt
cat test_file.txt
```

Expected:

```
# This is a fake passwd file for the lab.
root:x:0:0:root:/root:/bin/bash
alice:x:1000:1000:alice:/home/alice:/bin/bash
Copied from /home/you/security-lab/test_file.txt to /home/you/security-lab/test_file.txt with key harDcod3d
```

Now look at the file with `cat test_file.txt` again. It should be empty.

What happened: opening `FileOutputStream(s)` truncates the destination to zero bytes immediately, *before* the `FileInputStream` reads anything. The input stream then reads zero bytes (the file is now empty), `transferTo` does nothing, and the program reports success. The original data is gone.

This is a **data integrity bug**, not strictly a security bug, but it has the same shape as one: the code performs an operation that the user almost certainly did not intend, with no warning. In a real backup utility, this single bug could destroy a customer's data permanently.

Clean up:

```bash
rm test_file.txt
```

### Step 3.3: Provoke an exception

What happens if the source file does not exist?

```bash
java SafeFileCopier.java nonexistent_file.txt ./out.txt
```

Expected output:

```
Exception in thread "main" java.io.FileNotFoundException: /home/you/security-lab/nonexistent_file.txt (No such file or directory)
	at java.base/java.io.FileInputStream.open0(Native Method)
	at java.base/java.io.FileInputStream.open(FileInputStream.java:213)
	at java.base/java.io.FileInputStream.<init>(FileInputStream.java:152)
	at java.base/java.io.FileInputStream.<init>(FileInputStream.java:106)
	at SafeFileCopier.main(SafeFileCopier.java:13)
```

The traceback is the third leak in the same lab: it tells the user (or any attacker watching) the working directory, the requested filename, the Java version (implicitly, via the line numbers in `FileInputStream.java`), and the source filename and line number of the calling code. In a real web service, this kind of message would be exactly the kind of detail a reconnaissance step would harvest.

Notice also that the resource cleanup never ran. There are no `try`/`finally` blocks. If the `FileInputStream` succeeded but the `FileOutputStream` failed (file system full, permissions error, etc.), the input file handle would be open until garbage collection ran, potentially holding a file lock that prevents another process from deleting or replacing the file.

---

## Part 4: First-Pass Analysis

Before you start refactoring, write down everything wrong with the code in your notebook. Aim for at least seven distinct issues. For each one, write:

- **The problem** (one sentence).
- **The line(s) where the problem appears.**
- **A specific bad outcome it could produce** (one sentence).

Do this from scratch, looking only at the source code you pasted in Step 1.3 and the demonstrations in Part 3. Do not look at the reference list below until you have written your own.

> **A hint about scope.** "The variable names are bad" is not the kind of issue this lab is about. Focus on issues that an attacker could use to do something the program's author did not intend, or that could cause a non-attacker user to suffer accidental data loss, leaks, or crashes.

### Reference list: the issues this lab is built around

After you have written your own list, compare it to this one. The order is roughly from most-obvious to least-obvious.

| # | Issue | Lines | Why it matters |
|---|-------|-------|----------------|
| 1 | Hard-coded secret (`SECRET = "harDcod3d"`) | `CopierConfig` body | Anyone with read access to the source has the secret. Source-code repositories are not a secure place to store credentials. |
| 2 | Secret printed in success message | Last `println` in `main` | The secret is now in standard output, which will be captured by any log aggregator. |
| 3 | Public mutable fields (`public String source`, `public String dest`) | `CopierConfig` body | Any code anywhere can change the configuration after the validation logic has already used it. |
| 4 | No path canonicalization or validation | The two `String s = ...; String d = ...` lines | Path traversal works (demonstrated in Step 3.1). |
| 5 | No same-source-as-destination check | The two `FileInputStream`/`FileOutputStream` lines | Destination is truncated to empty before source is read (demonstrated in Step 3.2). |
| 6 | No `try-with-resources` for streams | The two `var in = ...; var out = ...` lines | On any exception during the copy, file handles leak. On Windows this can prevent the file from being deleted or replaced. |
| 7 | Unchecked exceptions propagate to the JVM | `throws Exception` on `main` | The JVM prints a full stack trace including absolute paths and JVM internals (demonstrated in Step 3.3). |
| 8 | Sensitive paths echoed in success output | Last `println` in `main` | Even on success, absolute paths are written to stdout, useful for reconnaissance. |
| 9 | Default source `./passwd` is suspicious | First default in `main` | Defaults should be safe and obviously inert; a default that hints at a sensitive file is a sign the author was not thinking adversarially. |
| 10 | No input validation: empty paths, directories instead of files, zero-byte source | None | The code happily copies a directory's bytes (fails partway), or copies a zero-byte file (succeeds, useless). |

If you found more issues than the table, write them down. The list is not exhaustive; it is the issues this lab is built around. Real code reviews routinely find issues that are not on any canonical checklist.

---

## Part 5: Apply Your Refactor

Now you write a safer version of the code. Do this *before* you look at Part 6 (which compares your refactor to the canonical one).

### Step 5.1: Plan the structure

Decide, before you type, how the code should be organized. A workable shape:

- A **configuration class** that parses arguments, validates them, and exposes them through accessors only. Private final fields.
- A **copier class** (or method) that takes a config, validates the paths against a base directory, opens streams with `try-with-resources`, and reports success or a structured error.
- A **main method** that wraps everything in try/catch and converts each exception type to a short, non-sensitive error message and an appropriate exit code.

You do not have to follow this shape, but you should be able to defend whatever shape you choose.

### Step 5.2: Implement

Create a new file `MyRefactor.java` in the workspace and write your refactored version. Aim to address all ten issues from the Part 4 reference list. The acceptance criteria for a passing refactor are:

| Criterion | What it means |
|-----------|---------------|
| No public mutable fields | Configuration object exposes accessors, not raw fields. Fields are `private final`. |
| Paths canonicalized | The source and destination paths are resolved with `Path.toRealPath()` (or `File.getCanonicalFile()`) before opening any stream. |
| Paths checked against a base directory | After canonicalization, both paths must be under a configured allowed base. The default base can be the current directory. |
| Same source and destination rejected | If the canonical source path equals the canonical destination path, the program rejects the operation before opening either stream. |
| `try-with-resources` around streams | Streams are closed on every code path, including exceptions. |
| No hard-coded secret in code | The `SECRET` field is removed entirely. The lab does not need it. |
| No secret or absolute path in success output | The success message names the operation, not the inputs. |
| No stack trace on user-input failures | Main catches expected exceptions and prints a short message. The JVM does not see a `throws Exception` from main. |

The lab does not insist on a specific code shape; it insists on these properties being verifiable in the result. Spend at least 30 minutes on this. If you have not written Java with `Path` and `Files` before, lean on `java.nio.file.Path.toRealPath()`, `java.nio.file.Files.newInputStream`, and `java.nio.file.Files.newOutputStream` rather than the older `java.io.File` API; the modern API gives you better tools for the kind of validation this lab requires.

### Step 5.3: Verify against your acceptance criteria

For each criterion in Step 5.2, write one or two sentences in your notebook explaining which line(s) of your code satisfy it. If you cannot find a line, the criterion is not satisfied; fix it before moving to Part 6.

In particular, test these scenarios on your refactored version:

```bash
# Should succeed
java MyRefactor.java --src passwd --dest out.txt

# Should fail with a short error message, no stack trace
java MyRefactor.java --src ../../../etc/hostname --dest stolen.txt

# Should fail with a short error message
java MyRefactor.java --src passwd --dest passwd --overwrite

# Should fail with a short error message
java MyRefactor.java --src does_not_exist.txt --dest out.txt
```

If your refactor uses positional arguments instead of `--src`/`--dest` flags, that is fine; adjust the commands above. The important thing is that the four scenarios produce the expected outcomes.

Clean up any `out.txt` or `stolen.txt` files created during testing.

---

## Part 6: Compare to the Canonical Solution

The canonical solution is in the file `SafeFileCopierSolution.java`. Open it in the editor (the file is included alongside this lab; create it from the version below if you do not have it yet) and compare it to your refactor.

### Step 6.1: Read the canonical solution

The canonical solution has three top-level classes nested inside `SafeFileCopier`:

- **`AppConfig`**: an immutable data class. Private final fields. Constructed via a static `fromArgs()` factory that parses and validates the command line. Exposes accessors named `source()`, `dest()`, `baseDir()`, `overwrite()` (no JavaBeans `get` prefix, matching the modern record-like style).
- **`Copier`**: contains the `run(AppConfig)` method that does the actual work. Calls `toRealPath()` on the base directory and on both arguments; calls a helper `ensureUnderBase()` that throws `UserInputException` if a path escapes the base; opens streams with `try-with-resources`; verifies that source and destination sizes match after the copy.
- **`UserInputException`**: a custom `RuntimeException` for user-correctable input errors. The catch block in `main` recognizes this exception type specifically and prints a short, user-facing error message; other exception types get their own (also short) messages.

The whole thing is organized around the **fail-fast** principle: invalid input is rejected at the earliest possible point (during config parsing, before any I/O), and the code that does the actual I/O can assume its inputs are valid.

### Step 6.2: Score your refactor against the canonical

For each acceptance criterion in Step 5.2, write a one-line comparison in your notebook:

- "My refactor handled X by doing Y; the canonical does it by doing Z. (Same/different/mine is better/canonical is better.)"

The point of this exercise is not to grade yourself; it is to notice the design moves that the canonical makes that you might not have thought of. Common differences to look for:

- **Custom exception class.** The canonical introduces `UserInputException` to distinguish "the user gave bad input" from "an I/O operation failed mid-way". This lets the catch blocks produce very different messages and exit codes for the two cases.
- **Exit codes.** The canonical's `main` uses different `System.exit()` codes (`0`, `2`, `3`, `1`, `64`) for different failure modes. This is a convention from Unix utilities; downstream scripts can distinguish user errors from I/O errors from "unknown error" without parsing the message text.
- **Integrity check.** The canonical verifies that the destination file size equals the source file size after copying. If they differ (a disk-full mid-copy, a buggy filesystem), the destination is deleted and an error is reported. This is a defense-in-depth move; the underlying `transferTo` should not produce a partial file, but checking provides a clear signal if it ever does.
- **`--overwrite` flag.** The canonical requires an explicit flag to overwrite an existing destination. By default, an existing file is treated as an error rather than silently replaced.

Write in your notebook which of these the canonical did and your refactor did not. None of these are required for a passing refactor (the acceptance criteria in Step 5.2 do not list them), but each one represents a real design move that experienced engineers would recognize.

### Reference: the canonical solution

Save the following code to a file called `SafeFileCopierSolution.java`:

```java
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.*;
import java.util.*;

public final class SafeFileCopierSolution {

    public static void main(String[] args) {
        try {
            AppConfig cfg = AppConfig.fromArgs(args);
            Copier.run(cfg);
            System.out.println("Copy succeeded.");
            System.exit(0);
        } catch (UserInputException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(2);
        } catch (IOException e) {
            System.err.println("I/O error during copy.");
            System.exit(3);
        } catch (Exception e) {
            System.err.println("Unexpected error.");
            System.exit(1);
        }
    }

    public static final class AppConfig {
        private final Path source;
        private final Path dest;
        private final Path baseDir;
        private final boolean overwrite;

        private AppConfig(Path source, Path dest, Path baseDir, boolean overwrite) {
            this.source = source;
            this.dest = dest;
            this.baseDir = baseDir;
            this.overwrite = overwrite;
        }

        public Path source()   { return source; }
        public Path dest()     { return dest; }
        public Path baseDir()  { return baseDir; }
        public boolean overwrite() { return overwrite; }

        public static AppConfig fromArgs(String[] argv) {
            Map<String, String> kv = new HashMap<>();
            boolean overwrite = false;

            for (int i = 0; i < argv.length; i++) {
                switch (argv[i]) {
                    case "--src":
                        requireNext(argv, i, "--src");
                        kv.put("src", argv[++i]);
                        break;
                    case "--dest":
                        requireNext(argv, i, "--dest");
                        kv.put("dest", argv[++i]);
                        break;
                    case "--base":
                        requireNext(argv, i, "--base");
                        kv.put("base", argv[++i]);
                        break;
                    case "--overwrite":
                        overwrite = true;
                        break;
                    case "--help":
                    case "-h":
                        usageAndExit();
                        break;
                    default:
                        throw new UserInputException("Unknown option: " + argv[i]);
                }
            }

            if (!kv.containsKey("src") || !kv.containsKey("dest")) {
                usageAndExit();
            }

            Path base = Paths.get(kv.getOrDefault("base", ".")).normalize();
            Path src  = Paths.get(kv.get("src")).normalize();
            Path dst  = Paths.get(kv.get("dest")).normalize();

            return new AppConfig(src, dst, base, overwrite);
        }

        private static void requireNext(String[] argv, int i, String opt) {
            if (i + 1 >= argv.length) {
                throw new UserInputException("Missing value for " + opt);
            }
        }

        private static void usageAndExit() {
            System.out.println(
                "Usage: java SafeFileCopierSolution --src <path> --dest <path> [--base <dir>] [--overwrite]"
            );
            System.exit(64);
        }
    }

    public static final class Copier {

        public static void run(AppConfig cfg) throws IOException {
            Path baseReal = cfg.baseDir().toRealPath();
            Path srcReal  = ensureUnderBase(cfg.source(), baseReal, "source");
            Path dstReal  = ensureUnderBase(cfg.dest(),   baseReal, "destination");

            if (!Files.exists(srcReal)) {
                throw new UserInputException("Source does not exist.");
            }
            if (!Files.isRegularFile(srcReal)) {
                throw new UserInputException("Source must be a regular file.");
            }
            if (srcReal.equals(dstReal)) {
                throw new UserInputException("Source and destination must differ.");
            }

            Path parent = dstReal.getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }

            if (Files.exists(dstReal) && !cfg.overwrite()) {
                throw new UserInputException("Destination exists. Use --overwrite to replace it.");
            }

            try (InputStream in = Files.newInputStream(srcReal, StandardOpenOption.READ);
                 OutputStream out = Files.newOutputStream(dstReal,
                         cfg.overwrite()
                             ? new OpenOption[]{ StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.WRITE }
                             : new OpenOption[]{ StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE })) {
                in.transferTo(out);
            }

            long s1 = Files.size(srcReal);
            long s2 = Files.size(dstReal);
            if (s1 != s2) {
                try { Files.deleteIfExists(dstReal); } catch (IOException ignored) {}
                throw new IOException("Integrity check failed.");
            }
        }

        private static Path ensureUnderBase(Path candidate, Path baseReal, String label) throws IOException {
            Path resolved = candidate.isAbsolute()
                    ? candidate
                    : baseReal.resolve(candidate);
            Path real;
            try {
                real = resolved.toRealPath();
            } catch (NoSuchFileException nsfe) {
                Path parent = resolved.getParent();
                if (parent == null) {
                    throw new UserInputException("Invalid " + label + " path.");
                }
                real = parent.toRealPath().resolve(resolved.getFileName());
            }
            if (!real.startsWith(baseReal)) {
                throw new UserInputException("The " + label + " path escapes the allowed base directory.");
            }
            return real;
        }
    }

    public static final class UserInputException extends RuntimeException {
        public UserInputException(String message) { super(message); }
    }
}
```

Save the file and verify it on the same four scenarios from Step 5.3:

```bash
# Should print "Copy succeeded."
java SafeFileCopierSolution.java --src passwd --dest out.txt

# Should print "Error: The source path escapes the allowed base directory."
java SafeFileCopierSolution.java --src ../../../etc/hostname --dest stolen.txt

# Should print "Error: Source and destination must differ."
java SafeFileCopierSolution.java --src passwd --dest passwd --overwrite

# Should print "Error: Source does not exist."
java SafeFileCopierSolution.java --src does_not_exist.txt --dest out.txt
```

Clean up any output files created during testing.

---

## Part 7: Stretch: Compare Your Analysis to Copilot's

This part puts a question to Copilot that real engineers ask their AI tools constantly: "is this code secure?" The right framing for the question matters a lot. The Code Generation lab (Lab 1-1) demonstrated that vague prompts produce vague output. Here, you will see the same lesson in a security context.

### Step 7.1: Open Copilot Chat

Open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for full availability notes).

### Step 7.2: First ask, vague prompt

Start a new chat. Attach `SafeFileCopier.java` (the original buggy version) using the paperclip icon or `#`. Send this prompt:

```
Review this Java code.
```

That is the entire prompt. Read the response. In your notebook:

1. Did Copilot mention security at all, or only style/readability?
2. If it did mention security issues, how many of the ten from the Part 4 table did it find?
3. Were there any security issues it identified that you missed?
4. Did it propose fixes, or only identify problems?

### Step 7.3: Second ask, specific prompt

Open a new chat. Attach `SafeFileCopier.java` again. Send this prompt:

```
Review this Java code for security vulnerabilities. For each finding,
provide:

1. The class of vulnerability (e.g., path traversal, hard-coded credentials,
   resource leak, information disclosure).
2. The specific line(s) in the source where the issue is located.
3. A CWE identifier if applicable.
4. The severity (low, medium, high, critical).
5. A short description of how an attacker could exploit the issue.
6. A specific remediation step.

Focus on security. Do not suggest stylistic changes.
```

Read the response. In your notebook:

1. How many of the ten issues did the second prompt elicit?
2. Did the second response include CWE identifiers? For which findings?
3. Did the severity ratings match your intuition? Are any of them wrong (too high, too low)?
4. Were there findings that mentioned vulnerabilities the lab's Part 4 list did not enumerate?

### Step 7.4: Reflect on the difference

Compare the responses to the two prompts. In your notebook, answer:

- Which response was more useful for an actual security review?
- The first response demonstrated what happens when the prompt is vague; the second demonstrated what happens when the prompt names specific deliverables. This is the same lesson Lab 1-1 taught for code generation. Is the lesson the same for security review, or does it apply differently?
- If you were going to put one of these prompts into a `.github/prompts/security-review.prompt.md` file for your team to use as a slash command, which version would you save?

> **What you should observe.** A vague "review this code" prompt typically gets you a mixed response that talks about a couple of obvious issues (hard-coded secrets, often) and a lot of stylistic suggestions. A specific security-focused prompt with structured output requirements typically gets you a longer list of issues with concrete CWE references and remediation suggestions. The difference in usefulness is large, and it costs you only a one-time effort to write the better prompt.
>
> Be careful, though: Copilot is not a substitute for a security audit. Even the better prompt may miss issues that depend on context Copilot does not have (the deployment environment, the threat model, the trust boundary between this code and its callers). It is a useful first-pass tool, not a final assessment.

---

## Part 8: Reflection

Answer in your notebook. These are open-ended; spend at least fifteen minutes.

1. **The category of bug.** Labs 2-1, 2-2, and 2-3 covered bugs that crashed loudly, returned wrong answers silently, and arose between two correct functions. The bugs in this lab are different again: code that runs and produces correct output for typical inputs but is dangerous for atypical ones. Which of the four categories is hardest to catch by reading the code? Which is hardest to catch with unit tests? Why?

2. **The "what if someone" lens.** The lab introduction calls out that secure programming requires asking "what if someone..." for every input. List five such questions for the original code. For each, predict the bad outcome and the smallest code change that would prevent it.

3. **Defense in depth.** The canonical solution does three things to prevent path traversal: `normalize()` (in the config), `toRealPath()` (in the copier), and `startsWith(baseReal)` (the actual check). Why three? What does each one catch that the others miss? Could you argue for fewer (more efficient) or more (more defensive)?

4. **The hard-coded secret as a smell.** The original code's `SECRET` is the value `"harDcod3d"`, which is almost a self-aware joke (it looks like the word "hardcoded" with a number substituted in). Real production hard-coded secrets are often less obvious; common patterns include test credentials forgotten in source, environment defaults in `application.properties`, or signing keys checked in for "convenience." What practices could a team adopt to catch hard-coded secrets before they reach a shared branch?

5. **Error messages and information disclosure.** The original code prints the full source and destination paths in the success message and prints the full stack trace on failure. The canonical solution prints `"Copy succeeded."` on success and `"I/O error during copy."` on failure. These are extreme positions. In your own codebase, where would you draw the line? Are there cases where verbose error messages are appropriate?

6. **The same-file destruction bug.** Of the ten issues in the Part 4 reference list, this one is arguably the most likely to cause real damage in a real deployment. It is not strictly a security issue; it is a data-integrity issue. Are these two categories really distinct, or is "the program destroyed my data without warning" a security issue in a slightly broader definition?

7. **Copilot's blind spots.** Based on Part 7, what kinds of security issues does Copilot reliably find, and what kinds does it miss? In a real team workflow, where would you put Copilot security review in the development cycle (in pre-commit hooks? in pull request review? in periodic batch reviews? in incident response)? Why?

---

## Reference: The Eight Properties of a Safer Refactor

When refactoring code for security, these eight properties (a Java-flavored version of widely-used defensive coding lists) provide a useful checklist:

| Property | What it means |
|----------|---------------|
| **Validated at the boundary** | Untrusted input is checked the moment it enters your code (the argument-parsing step, not the I/O step). |
| **Canonicalized** | Paths, URLs, identifiers are resolved to their real form before being used to make access decisions. |
| **Compared against an allow-list** | After canonicalization, the resulting value is checked against a list of permitted forms, not against a list of forbidden ones. |
| **Immutable after construction** | Configuration objects, value types, and similar internal data cannot be modified after they have been validated. |
| **Closed on every code path** | Resources (file handles, sockets, locks) are released even when an exception is thrown. `try-with-resources` is the Java idiom. |
| **Fails closed** | When in doubt, the program denies the operation rather than allowing it. The default for an unknown configuration is "reject", not "accept". |
| **Minimal in its outputs** | Error messages, success messages, and log lines say only what the recipient needs to know. Stack traces, internal paths, and credentials are not in any output. |
| **Defended in depth** | Multiple independent checks for the same condition. If one is bypassed (because the attacker found a clever trick), the others still apply. |

For the path-traversal flaw alone, the canonical solution applies "validated at the boundary" (config parsing), "canonicalized" (`toRealPath()`), "compared against an allow-list" (`startsWith(baseReal)`), and "fails closed" (the default behavior on a failure is `throw UserInputException`). Four of the eight properties for one flaw is typical; security in depth means each protection backs up the others.

---

## Reference: CWE Identifiers for the Issues in This Lab

The Common Weakness Enumeration (CWE) is a catalog of software weakness types maintained by MITRE. Each entry has a number, a name, and a description; engineers and security researchers use these numbers in vulnerability reports, code review tools, and remediation discussions. The flaws in this lab map to:

| Issue | CWE |
|-------|-----|
| Path traversal (`../`) | CWE-22 "Improper Limitation of a Pathname to a Restricted Directory" |
| Hard-coded secret | CWE-798 "Use of Hard-coded Credentials" |
| Secret leaked in log/output | CWE-532 "Insertion of Sensitive Information into Log File" |
| Resource leak (unclosed streams) | CWE-772 "Missing Release of Resource after Effective Lifetime" |
| Public mutable fields | CWE-485 "7PK - Encapsulation" (also CWE-668 "Exposure of Resource to Wrong Sphere") |
| Stack trace in error output | CWE-209 "Generation of Error Message Containing Sensitive Information" |
| Same source and destination | CWE-410 "Insufficient Resource Pool" (closest fit) or CWE-754 "Improper Check for Unusual or Exceptional Conditions" |

When you write security review reports, citing CWE identifiers makes your findings comparable across teams and across tools, the same way citing PEP numbers in a Python code review or citing a section in IEEE 830 in a requirements review does. CWE-22 is universally understood across the industry; "path injection bug" is understood only by people who happen to use that name.

---

## Reference: When `try-with-resources` Is the Right Tool

`try-with-resources` is the Java idiom for guaranteed resource cleanup. The syntax is:

```java
try (InputStream in = Files.newInputStream(src);
     OutputStream out = Files.newOutputStream(dst)) {
    in.transferTo(out);
}
```

The braces after the resource declarations are the *scope* of the resources; when control leaves the block (normally or via exception), Java calls `close()` on every resource declared in the `try (...)` clause, in reverse order of declaration. This is more reliable than `finally` blocks because:

- You cannot accidentally write a `close()` that swallows the exception from the inner block.
- The compiler enforces that the resource type implements `AutoCloseable`.
- Multiple resources are closed in the correct order automatically.

The original lab's code does not use `try-with-resources` at all. If the `transferTo` call throws an exception (it can, on a disk full or permission error), both `in` and `out` are left dangling. Java's garbage collector will eventually close them via the finalizer, but "eventually" can be minutes or hours later, and on Windows it may prevent another process from deleting or replacing the file. The canonical solution wraps both streams in `try-with-resources`.

A resource that implements `AutoCloseable` should always be opened inside a `try-with-resources`. The exceptions are very narrow: long-lived resources (database connection pools, executor services) that are owned by a higher-level construct and closed during shutdown. For everything else, including every `InputStream`, `OutputStream`, `Reader`, `Writer`, `Connection`, `Statement`, and `ResultSet` in your code, `try-with-resources` is the default.

---

## Troubleshooting

**`error: can't find main(String[]) method in class: CopierConfig`.**
The Java single-source-file launcher uses the *first* top-level type in the file as the launch class. If `class CopierConfig` is declared before `public class SafeFileCopier`, the launcher tries to run `CopierConfig` and fails. Reorder so `public class SafeFileCopier` appears first. The starter in Step 1.3 has the correct order.

**`SafeFileCopier.java` runs but `out.txt` is empty after a same-file test.**
This is the expected behavior of the buggy code, demonstrated in Step 3.2. It is the bug. After Part 5 your refactor should refuse this case with an error.

**The path-traversal test does not produce a stolen file on Windows.**
Windows uses backslash as a path separator, and `..\\..\\..\\Windows\\System32\\drivers\\etc\\hosts` is the typical equivalent. The exact path that escapes the working directory depends on how deep your working directory is. The vulnerability is the same; only the path syntax differs.

**Your refactor compiles but `toRealPath()` throws `NoSuchFileException` when the destination does not exist.**
`toRealPath()` requires the path to exist. For a destination that may not exist yet, canonicalize the parent directory instead and resolve the filename against it. The canonical solution does this in the `ensureUnderBase` helper's catch clause.

**Your refactor's `try-with-resources` does not compile: "incompatible types: java.io.InputStream is not abstract".**
`Files.newInputStream(...)` returns `InputStream`, not the concrete `FileInputStream`. Either change your declared type to `InputStream`, or import the right type. The canonical solution uses the abstract types in declarations.

**Copilot in Part 7 mentions the secret but not the path traversal.**
This is consistent with the lab's expected observation: vague prompts elicit findings only for the most-obvious issues. The remedy is the more-specific prompt in Step 7.3.

**Copilot in Part 7 suggests using `File.getCanonicalFile()` instead of `Path.toRealPath()`.**
Both approaches work. `Path.toRealPath()` is the modern (Java 7+) idiom and integrates with the rest of `java.nio.file`. `File.getCanonicalFile()` is the older `java.io` equivalent. The choice is style, not security; both resolve symlinks and `..` segments before returning.

---

## Further Reading

- **OWASP Top 10** at <https://owasp.org/Top10/>. The most widely-cited list of web application security risks. Path injection appears as "A03:2021 - Injection".
- **CWE Top 25 Most Dangerous Software Weaknesses** at <https://cwe.mitre.org/top25/>. The canonical taxonomy; the CWE identifiers in this lab's reference section all come from here.
- **Secure Coding in Java** (Fred Long et al., Addison-Wesley). The book-length treatment of Java-specific security idioms, including all the issues in this lab and many more.
- **CERT Oracle Secure Coding Standard for Java** at <https://wiki.sei.cmu.edu/confluence/display/java>. A free, well-maintained reference covering the same ground as the book above, in catalog form. Each rule has examples, exceptions, and risk assessments.
- **Java SE Security Documentation** at <https://docs.oracle.com/en/java/javase/21/security/>. The platform reference, including the `java.nio.file` permissions and security manager (mostly historical in Java 21+, but useful context).
- **"The Tangled Web"** (Michal Zalewski, 2011). An older but unsurpassed treatment of how web-app security really works. Chapter 3's discussion of path canonicalization is directly relevant to this lab.
