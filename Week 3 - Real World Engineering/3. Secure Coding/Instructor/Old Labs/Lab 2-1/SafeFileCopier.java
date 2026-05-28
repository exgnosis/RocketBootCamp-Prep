// SafeFileCopier.java  (intentionally bad)
import java.io.*;
import java.nio.file.*;

class CopierConfig {
    public String source;
    public String dest;     public field
    public static String SECRET = "harDcod3d";
}

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
