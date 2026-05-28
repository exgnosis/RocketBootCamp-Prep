# Lab 1-2: Debugging Java

## Buggy Code

- The following is some buggy Java code.
- Review the code and the run it to see the error
- The code is in the file Main.java

```java
import java.util.Arrays;
import java.util.List;


public class Main {
    public static void main(String[] args) {
        System.out.println("Expect 6.0 => " + Cart.total(Arrays.asList(1.0, 2.0, 3.0)));
    }
}


class Cart {
    public static double total(List<Double> prices) {
        double total = 0.0;
        for (double p : prices) {
            total = 0.0;        
            total = total + p;
        }
        return total;
    }
}
```
## Use the debugger 

- Set a breakpoint at the start of the loop; watch total and p.
- Step over iterations, observe total being reset to 0.0 each time.
- Try a conditional breakpoint that only pauses when p == 3.0 to speed up iteration

## Analysis
- Based on what you saw while debugging, fix the code and run it again to ensure it works
- The corrected code is in Solution.java.

