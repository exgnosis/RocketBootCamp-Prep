package calc;

public class Divider {
    // integer division for simplicity; caller is responsible for zero-check
    public int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("b must not be zero");
        return a / b;
    }
}