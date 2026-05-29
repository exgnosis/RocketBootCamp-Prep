package calc;

 class Divider {
    // integer division for simplicity; caller is responsible for zero-check
     int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("b must not be zero");
        return a / b;
    }
}