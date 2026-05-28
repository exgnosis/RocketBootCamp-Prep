// SafeFileCopierSolution.java
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
                // Allow the destination's path to not exist yet; canonicalize the parent instead
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
