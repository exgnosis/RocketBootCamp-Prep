//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import java.util.*;
import java.util.stream.*;

public class Solution {

    record Transaction(String id, double amount, String category) {}

    public static void main(String[] args) {
        List<String> names = List.of(
                "Ada", "bob", "ALAN", "Ada", "grace", "linus", "Guido", "ada", "Bjarne"
        );

        List<Integer> numbers = List.of(3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5);

        List<String> sentences = List.of(
                "Functional programming uses functions as values",
                "Streams transform data with map filter and flatMap",
                "Pure functions avoid side effects"
        );

        List<Transaction> txs = List.of(
                new Transaction("t1", 120.00, "GROCERY"),
                new Transaction("t2", 18.50,  "COFFEE"),
                new Transaction("t3", 42.99,  "BOOKS"),
                new Transaction("t4", 220.00, "GROCERY"),
                new Transaction("t5", 9.99,   "COFFEE"),
                new Transaction("t6", 500.00, "ELECTRONICS")
        );

        // 1) names: map → filter → distinct → sorted (by length, then alpha)
        List<String> aNames = names.stream()
                .map(String::toLowerCase)
                .filter(n -> n.startsWith("a"))
                .distinct()
                .sorted(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()))
                .collect(Collectors.toList());
        System.out.println("1) aNames = " + aNames);
        // Example output: [ada]

        // 2) numbers: map (square) → filter (even) → sorted desc → skip 2 → limit 5
        List<Integer> evenSquares = numbers.stream()
                .map(n -> n * n)
                .filter(sq -> sq % 2 == 0)
                .sorted(Comparator.<Integer>naturalOrder().reversed())
                .skip(2)
                .limit(5)
                .collect(Collectors.toList());
        System.out.println("2) evenSquares = " + evenSquares);
        // Example: [36, 16, 4] (depending on input)

        // 3) sentences: flatMap to words → normalize → filter non-empty → distinct → sorted
        List<String> vocab = sentences.stream()
                .flatMap(s -> Arrays.stream(s.split("\\W+")))
                .map(String::toLowerCase)
                .filter(w -> !w.isEmpty())
                .distinct()
                .sorted()
                .collect(Collectors.toList());
        System.out.println("3) vocab = " + vocab);

        // 4) transactions: categories uppercased → distinct → sorted
        List<String> categories = txs.stream()
                .map(tx -> tx.category.toUpperCase(Locale.ROOT))
                .distinct()
                .sorted()
                .collect(Collectors.toList());
        System.out.println("4) categories = " + categories);
        // Example: [BOOKS, COFFEE, ELECTRONICS, GROCERY]

        // 5) large transactions total: filter → peek (debug) → mapToDouble → sum (terminal)
        double bigTotal = txs.stream()
                .filter(tx -> tx.amount >= 100.0)
                .peek(tx -> System.out.println("   large tx: " + tx.id + " $" + tx.amount))
                .mapToDouble(tx -> tx.amount)
                .sum();
        System.out.println("5) bigTotal = " + bigTotal);

        // 6) Pagination demo: lowercase → sorted → skip/limit
        int pageSize = 3;
        int pageIndex = 2; // third page
        List<String> page = names.stream()
                .map(String::toLowerCase)
                .sorted()
                .skip((long) pageIndex * pageSize)
                .limit(pageSize)
                .collect(Collectors.toList());
        System.out.println("6) page = " + page);
    }
}
