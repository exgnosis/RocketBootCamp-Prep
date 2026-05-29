import calc.*;

public class Main {
    public static void main(String[] args) {
        System.out.println(new Adder().add(2, 3));        // 5
        System.out.println(new Multiplier().multiply(4, 6)); // 24
        System.out.println(new Divider().divide(8, 2));      // 4
    }
}