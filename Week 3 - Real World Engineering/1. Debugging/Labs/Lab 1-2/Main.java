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