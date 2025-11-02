import calc.*;

public class Main {
    public static void main(String[] args) {
        Facade  c = new Facade();
        System.out.println(c.add(2, 3));        // 5
        System.out.println(c.multiply(4, 6)); // 24
        System.out.println(c.divide(8, 2));      // 4
    }
}