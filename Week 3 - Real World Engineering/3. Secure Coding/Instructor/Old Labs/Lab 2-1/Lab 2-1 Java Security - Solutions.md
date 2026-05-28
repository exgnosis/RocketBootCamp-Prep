# Lab 2-1 Java Security

## Hints

- Builds paths from raw user input
- Uses public fields
- Leaks details on errors
- Hard-codes a “secret key”
- Forgets to close streams properly.


## Refactorings

#### Encapsulation & API surface
- Make CopierConfig immutable and its fields private
- Provide a minimal, validated constructor and accessors only as needed
- Avoid public non-final statics

#### Path handling
- Canonicalize and validate input paths before use
- Disallow escaping a permitted base directory 

#### Resource management & failures
- Use try-with-resources
- Handle I/O errors without revealing sensitive paths/values
- Close resources when no longer needed
- Don’t allow exceptions to expose sensitive information

#### No secrets in code or logs

- Remove hard-coded “SECRET”
- If you simulate one, read from a safe configuration source and never print it  never hard-code sensitive info
- Do not log sensitive information outside a trust boundary

#### Input sanity

- Reject empty files, absurd sizes, or binary-to-text misuse if you add modes. 

#### Acceptance criteria 

- Private fields; no public mutable state.
-  Path/Files with toRealPath() (or getCanonicalFile() if you stick to File) and base-dir check.
- Try (InputStream in = …; OutputStream out = …) { … }
- No secrets in source/logs
- Clear, minimal error messages. 
- Unit test (even rudimentary) that proves ../ traversal is blocked.


## Part 3: Solution

- This is very comprehensive solution.
- Check to see how much of your solution resembles this one.
- Remember, the is no "right" answer, but you should see a lot of similarities with your code.
- The code in the file `SafeFileCopierSolution.java`

### Features

- No secrets in code or logs.
- Path traversal blocked
  - Both --src and --dest must resolve under --base after canonicalization
- Resources closed: try-with-resources on streams; no leaks.
- Minimal error messages: no stack traces, no absolute paths echoed back to users.
- Immutable config: AppConfig parses and validates arguments
- Fields are private and final by design (exposed via accessors only).
- Integrity check: optional size check after copy; if it fails, destination is removed.


```java 
// SafeFileCopier.java
// -----------------------------------------------------------------------------
// Usage:
//   javac SafeFileCopier.java
//   java SafeFileCopier --src input/sample.txt --dest output/copied.txt [--base .] [--overwrite]
//
// Notes:
// - Validates that source and destination are both under an allowed base directory.
// - Uses try-with-resources for safe resource management.
// - No secrets in code or logs; minimal, non-sensitive error messages.
// - Clear structure: immutable config + focused utilities.
// -----------------------------------------------------------------------------

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.*;
import java.util.*;

public final class SafeFileCopier {

    // ----------------------------- main entry --------------------------------
    public static void main(String[] args) {
        try {
            AppConfig cfg = AppConfig.fromArgs(args);
            Copier.run(cfg);
            System.out.println("Copy succeeded.");
            System.exit(0);
        } catch (UserInputException e) {
            // user-correctable problem (bad arguments/paths) — concise message
            System.err.println("Error: " + e.getMessage());
            System.exit(2);
        } catch (IOException e) {
            // operational failure, avoid leaking paths or internals
            System.err.println("I/O error during copy.");
            System.exit(3);
        } catch (Exception e) {
            // last-resort catch; do not print stack traces or internals
            System.err.println("Unexpected error.");
            System.exit(1);
        }
    }

    // ----------------------------- config ------------------------------------
    /** Immutable, validated configuration */
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

        /** Parse and minimally validate CLI arguments */
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

            Path base = Paths.get(kv.getOrDefault("base", "."));
            Path src  = Paths.get(kv.get("src"));
            Path dst  = Paths.get(kv.get("dest"));

            // Normalize early (but do canonicalization in validation below)
            base = base.normalize();
            src  = src.normalize();
            dst  = dst.normalize();

            return new AppConfig(src, dst, base, overwrite);
        }

        private static void requireNext(String[] argv, int i, String opt) {
            if (i + 1 >= argv.length) {
                throw new UserInputException("Missing value for " + opt);
            }
        }

        private static void usageAndExit() {
            System.out.println(
                    "Usage: java SafeFileCopier --src <path> --dest <path> [--base <dir>] [--overwrite]\n" +
                            "  --src        Source file path (under base)\n" +
                            "  --dest       Destination file path (under base)\n" +
                            "  --base       Allowed base directory (default: current dir)\n" +
                            "  --overwrite  Overwrite destination if it exists\n"
            );
            System.exit(64); // EX_USAGE style
        }
    }

    // ------------------------------ copier -----------------------------------
    /** Performs safe path validation and copying */
    public static final class Copier {

        public static void run(AppConfig cfg) throws IOException {
            // Canonicalize + enforce base directory policy
            Path baseReal = realPath(cfg.baseDir());
            Path srcReal  = ensureUnderBase(cfg.source(), baseReal, "source");
            Path dstReal  = ensureUnderBase(cfg.dest(),   baseReal, "destination");

            // Validate source
            if (!Files.exists(srcReal)) {
                throw new UserInputException("Source does not exist.");
            }
            if (!Files.isRegularFile(srcReal)) {
                throw new UserInputException("Source must be a regular file.");
            }

            // Prepare destination’s parent directory
            Path parent = dstReal.getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }

            // Handle overwrite policy
            if (Files.exists(dstReal) && !cfg.overwrite()) {
                throw new UserInputException("Destination exists. Use --overwrite to replace it.");
            }

            // Copy using streams with try-with-resources
            final CopyOption[] opts = cfg.overwrite()
                    ? new CopyOption[] { StandardCopyOption.REPLACE_EXISTING }
                    : new CopyOption[] { };

            try (InputStream in = Files.newInputStream(srcReal, StandardOpenOption.READ);
                 OutputStream out = Files.newOutputStream(dstReal,
                         cfg.overwrite() ? new OpenOption[]{ StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.WRITE }
                                 : new OpenOption[]{ StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE })) {
                in.transferTo(out);
            }

            // Optionally, you could verify sizes match (defense-in-depth)
            long s1 = Files.size(srcReal);
            long s2 = Files.size(dstReal);
            if (s1 != s2) {
                // Roll back and fail securely
                try { Files.deleteIfExists(dstReal); } catch (IOException ignored) {}
                throw new IOException("Integrity check failed.");
            }
        }

        /** Resolve a path to its real (canonical) absolute form */
        private static Path realPath(Path p) throws IOException {
            // toRealPath will resolve symlinks; if base may not exist yet, use toAbsolutePath().normalize()
            return p.toRealPath(LinkOption.NOFOLLOW_LINKS);
        }

        /** Ensure 'candidate' is under 'baseReal' after canonicalization */
        private static Path ensureUnderBase(Path candidate, Path baseReal, String label) throws IOException {
            Path real = candidate.isAbsolute()
                    ? candidate.toRealPath(LinkOption.NOFOLLOW_LINKS)
                    : baseReal.resolve(candidate).toRealPath(LinkOption.NOFOLLOW_LINKS);

            if (!isUnder(real, baseReal)) {
                throw new UserInputException("The " + label + " path escapes the allowed base directory.");
            }
            return real;
        }

        /** True if child is equal to or inside base */
        private static boolean isUnder(Path child, Path base) {
            child = child.normalize();
            base  = base.normalize();
            return child.startsWith(base);
        }
    }

    // ------------------------------ errors -----------------------------------
    /** For user-facing, non-sensitive argument/validation problems */
    public static final class UserInputException extends RuntimeException {
        public UserInputException(String message) { super(message); }
    }
}

```

## End