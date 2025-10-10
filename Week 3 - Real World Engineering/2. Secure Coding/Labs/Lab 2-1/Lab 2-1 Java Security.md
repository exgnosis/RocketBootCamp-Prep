# Lab 2-1 Java Security

## Introduction

The following Java code copies the contents of one file to another.
- If the file names are not supplied default values are used.
  - Note: Just make sure the files are located in the root directory of the project or adjust the hard coded path names required.

This Java code compiles and runs, but it is not safe code which means:
- It is not robust: meaning that it's easy to crash by giving it inputs it does not expect.
- This often happens when the code is written to handle one specific case the programmer has in mind, so they don't consider how to handle variations on the original case.
- The code also violates a number of the good design practices covered in this course.
- These violations create potential weaknesses in the design that can be used as an attack surface
- It also doesn't take into account the "what if someone?" cases that need to be considered when secure programming. 


```java
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
```

## Part 1: Analysis

- Review the provided code and see if you can spot the security flaws and other weaknesses
- Run the code with different inputs to see what happens
    - For example, what if the input and output file are the same?
- Make a list of the problems you have found
- Use the hints in the solution in you need help
- You may find other flaws that are not in the hints

---

## Part 2: Refactor

- Rewrite the code so that it no longer is secure.
- A list of suggested refactoring in the solution file.
- Test your code to make sure it still works and is now able to handle the cases that caused it to crash earlier
- Compare your refactoring to the one in the solutions file.

## End
