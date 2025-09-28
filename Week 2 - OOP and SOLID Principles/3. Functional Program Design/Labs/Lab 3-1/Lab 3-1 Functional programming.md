# Lab 3-1 Functional Programming

## Overview

In this lab you will:
- Build stream pipelines using intermediate operations (transformations) and terminal operations (consumption).
- Practice map / filter / distinct / sorted / limit / skip / flatMap / peek.
- Understand laziness: nothing runs until a terminal operation is invoked.

## Procedure

- Rather than write all the code from scratch a started template has been provided. 
- You are just required to fill in the missing code
- The starter code is also in the file `Starter.java` and is shown here

```java
import java.util.*;
import java.util.stream.*;

public class StreamLabStarter {

    // Simple domain record (Java 16+). For Java 8, replace with a small class with getters.
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

        // === 1) names → normalize case, filter those starting with 'a', distinct, sort by length then alpha ===
        List<String> aNames = names.stream()
                // TODO: to lowercase
                // TODO: keep only names starting with 'a'
                // TODO: distinct
                // TODO: sorted by length, then alphabetically
                // TODO: collect to list
                .collect(Collectors.toList());
        System.out.println("1) aNames = " + aNames);

        // === 2) numbers → squares of even numbers, sorted descending, skip first 2, take next 5 ===
        List<Integer> evenSquares = numbers.stream()
                // TODO: map to square
                // TODO: keep even
                // TODO: sort descending
                // TODO: skip first 2
                // TODO: limit to 5
                .collect(Collectors.toList());
        System.out.println("2) evenSquares = " + evenSquares);

        // === 3) sentences → words (flatMap), normalize, distinct, sorted ===
        List<String> vocab = sentences.stream()
                // TODO: split each sentence into words (\\W+), then flatMap to a stream of words
                // TODO: to lowercase
                // TODO: filter non-empty
                // TODO: distinct
                // TODO: sorted
                .collect(Collectors.toList());
        System.out.println("3) vocab = " + vocab);

        // === 4) transactions → categories uppercased, distinct, sorted; also total of large txs ===
        List<String> categories = txs.stream()
                // TODO: map category to upper case
                // TODO: distinct
                // TODO: sorted
                .collect(Collectors.toList());
        System.out.println("4) categories = " + categories);

        // Use peek to debug the pipeline for large transactions
        double bigTotal = txs.stream()
                // TODO: filter tx.amount >= 100
                // TODO: peek to log the id of each large tx
                // TODO: map to amount
                // TERMINAL: sum
                .sum();
        System.out.println("5) bigTotal = " + bigTotal);

        // === 5) Pagination demo with names ===
        int pageSize = 3;
        int pageIndex = 2; // zero-based (page 2 = third page)
        List<String> page = names.stream()
                .map(String::toLowerCase)
                .sorted()
                // TODO: skip pageIndex * pageSize
                // TODO: limit pageSize
                .collect(Collectors.toList());
        System.out.println("6) page = " + page);
    }
}

```

## To Do
- Fill in the TODO items as execute the result
- The full solution is the file `Solution.java`

## Things to note

- Intermediate ops chain transformations; nothing runs until a terminal op (collect, sum) is called.
- flatMap turns a stream of sentences into a flattened stream of words.
- sorted can take a comparator for custom order; combine with distinct for unique, ordered results.
- skip / limit are handy for pagination.
- peek is useful for debugging a live pipeline (don’t use it for side-effects in production