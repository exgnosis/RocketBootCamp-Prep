# Lab 3-1: Functional Programming

## Overview

Functional programming is the discipline of building programs out of **values and functions over values** rather than out of statements that mutate state. The functions are first-class: they can be passed as arguments, returned from other functions, and assembled into pipelines. The values are usually immutable: a transformation produces a new value rather than modifying an existing one. The ideas are old; Lisp (1958) is older than the structured-programming and OOP revolutions, and the modern wave (Haskell, ML, Erlang, and the functional features added to Java, Python, and C#) is mostly a return to those ideas after decades of imperative dominance.

In the structured-programming lab you walked over a list with a `for` loop and made decisions with `if/elif/else`. In the OOP lab you wrapped data and behaviour into objects and sent them messages. In this lab you do neither: you describe a transformation as a **pipeline of operations on a stream**, and the runtime decides how to execute it. You will not write a loop. You will not declare a counter variable. You will not mutate an accumulator. Instead, you will chain operations like `map`, `filter`, `distinct`, `sorted`, `flatMap`, and `limit`, and a final terminal operation like `collect` or `sum` will pull values through the pipeline.

Java is not a "functional language" in the way Haskell is, but Java 8 added streams and lambdas, and Java 16 added records, which together make a recognizably functional style possible. The same techniques work in Python (with comprehensions and `itertools`), C# (with LINQ), and JavaScript (with array methods like `.map`, `.filter`, and `.reduce`). The vocabulary is identical across languages once you learn it here.

Most of the code is already written for you. About fifteen small holes are marked `TODO` across six stream pipelines for you to fill in. Each TODO is one line.

The lab is therefore part **reading exercise** (understand the structure before you change it) and part **implementation exercise** (fill in the operative pieces while preserving the structure). When you are done, you will run the program and compare its output against the expected output for verification.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected. The point is to feel where the design decisions are and to practice making them yourself.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Distinguish between **intermediate** operations (which return a stream and are lazy) and **terminal** operations (which return a result and trigger execution).
2. Use `map`, `filter`, `distinct`, `sorted`, `limit`, `skip`, and `flatMap` in stream pipelines and explain what each one does to the stream.
3. Use `Comparator` chaining (`Comparator.comparingInt(...).thenComparing(...)`) to sort by multiple keys.
4. Use `peek` to debug a live pipeline and explain why `peek` is for debugging only and not for production side effects.
5. Use `mapToDouble` and similar primitive-stream conversions to enable numeric terminal operations like `sum`.
6. Verify your implementation against an expected output.

---

## Part 1: Set Up the Workspace

### Step 1.1: Confirm you have Java 16 or later

In a terminal:

```bash
java --version
```

You need Java 16 or later because the lab uses **records**. Java 21 is recommended.

### Step 1.2: Create the lab directory

```bash
mkdir -p ~/streams-lab
cd ~/streams-lab
```

### Step 1.3: Create the starter file

Create a file called `StreamLabStarter.java` and paste in the following code. Do not modify anything yet; in Part 2 you will read it before changing anything.

```java
import java.util.*;
import java.util.stream.*;

public class StreamLabStarter {

    // Simple domain record (Java 16+). Acts as a tiny immutable value class:
    // the compiler generates the constructor, accessors, equals, hashCode, toString.
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

        // === 1) names: normalize case, filter those starting with 'a',
        //               distinct, sort by length then alphabetically ===
        List<String> aNames = names.stream()
                // TODO: map to lowercase
                // TODO: keep only names starting with 'a'
                // TODO: distinct
                // TODO: sorted by length, then alphabetically
                .collect(Collectors.toList());
        System.out.println("1) aNames = " + aNames);

        // === 2) numbers: squares of even numbers, sorted descending,
        //                 skip first 2, take next 5 ===
        List<Integer> evenSquares = numbers.stream()
                // TODO: map to square
                // TODO: keep even
                // TODO: sort descending
                // TODO: skip first 2
                // TODO: limit to 5
                .collect(Collectors.toList());
        System.out.println("2) evenSquares = " + evenSquares);

        // === 3) sentences: split into words (flatMap), normalize, distinct, sorted ===
        List<String> vocab = sentences.stream()
                // TODO: split each sentence on \\W+, then flatMap to a stream of words
                // TODO: map to lowercase
                // TODO: filter out empty strings
                // TODO: distinct
                // TODO: sorted
                .collect(Collectors.toList());
        System.out.println("3) vocab = " + vocab);

        // === 4) transactions: distinct uppercased categories, sorted ===
        List<String> categories = txs.stream()
                // TODO: map category to upper case
                // TODO: distinct
                // TODO: sorted
                .collect(Collectors.toList());
        System.out.println("4) categories = " + categories);

        // === 5) Use peek to debug the pipeline for large transactions ===
        double bigTotal = txs.stream()
                // TODO: filter tx.amount() >= 100
                // TODO: peek to log the id and amount of each large tx
                // TODO: mapToDouble to amount
                // TERMINAL: sum (already there)
                .sum();
        System.out.println("5) bigTotal = " + bigTotal);

        // === 6) Pagination demo with names ===
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

Save the file.

### Step 1.4: Try to run the starter

Java 21 lets you run a single source file directly:

```bash
java StreamLabStarter.java
```

If you have an older Java that does not support that, compile then run:

```bash
javac StreamLabStarter.java
java StreamLabStarter
```

**The starter does not compile.** You will see two errors:

```
StreamLabStarter.java:64: error: incompatible types: inference variable T has incompatible bounds
                .collect(Collectors.toList());
                        ^
    equality constraints: String
    lower bounds: Transaction
StreamLabStarter.java:74: error: cannot find symbol
                .sum();
                ^
  symbol:   method sum()
  location: interface Stream<Transaction>
```

This is not a mistake in the lab; it is the point. The starter's `categories` pipeline declares the result type as `List<String>` but the TODOs that would turn the stream of `Transaction` into a stream of `String` are missing, so the types do not line up. Likewise the `bigTotal` pipeline calls `.sum()` on a stream of `Transaction`, but `sum()` is only defined on streams of numbers (`IntStream`, `LongStream`, `DoubleStream`).

This is a feature of Java's stream API: each `map`, `filter`, and so on produces a stream whose element type is determined at compile time, and any stage whose type does not match its neighbours is a compile error. In a dynamic language like Python, you would discover the same mistake at runtime (and usually with a less informative error message). In Java the compiler tells you what is wrong and where. Your job in Part 3 is to write the missing stages, after which the program will compile and run.

### Step 1.5: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your analyses, decisions, and observations as you go:

```markdown
# Functional Programming Lab Notebook

## Part 2: Reading the starter

## Part 3: Implementation decisions

## Part 4: Verification

## Part 5: Reflection
```

---

## Part 2: Read the Starter Before You Change It

This is a small program, but stream pipelines have more structure than a casual reader sees on first pass. Before you implement the TODOs, you should be able to answer the questions below from the source alone. Spend at least 15 minutes on this section; do not skip it to get to the coding.

### Question 2.1: Intermediate vs terminal operations

A Java stream pipeline has three parts:

1. A **source** that produces the stream (`names.stream()`, `Arrays.stream(...)`, `IntStream.range(...)`).
2. Zero or more **intermediate operations** that transform the stream (`map`, `filter`, `distinct`, `sorted`, `limit`, `skip`, `flatMap`, `peek`).
3. Exactly one **terminal operation** that consumes the stream and produces a result (`collect`, `sum`, `count`, `forEach`, `findFirst`).

The key rule is that intermediate operations are **lazy**: they record what to do, but they do not actually run until a terminal operation pulls values through the pipeline.

Look at the six pipelines in the starter and answer in your notebook:

1. For each pipeline, identify the source, the intermediate operations (TODOs and any that are already there), and the terminal operation.
2. The fifth pipeline has `.sum()` as its terminal. The other five use `.collect(Collectors.toList())`. Why two different terminals? What does `collect(Collectors.toList())` produce, and what does `sum()` produce?
3. If you wrote a pipeline with no terminal operation, like `names.stream().map(String::toLowerCase).filter(n -> n.startsWith("a"))` and assigned it to a variable, what would happen at run time? Would the names actually be lowercased?

### Question 2.2: What each operation does to the stream

Match each operation to its effect:

| Operation | Effect on the stream |
|-----------|----------------------|
| `map(f)` | ? |
| `filter(p)` | ? |
| `distinct()` | ? |
| `sorted()` / `sorted(comparator)` | ? |
| `limit(n)` | ? |
| `skip(n)` | ? |
| `flatMap(f)` | ? |
| `peek(c)` | ? |

Fill in the right column from memory or by reading the JDK documentation. Be precise: there is a real difference between "filters out duplicates" and "keeps the first occurrence of each value." Most of these have a one-line description; if your description is two sentences, you have probably added something that is not actually in the contract.

### Question 2.3: Method references vs lambdas

The pipelines mix two styles for passing functions:

- **Method reference**: `String::toLowerCase` (already in the starter for pipeline 6).
- **Lambda**: `n -> n.startsWith("a")` (which you will write for pipeline 1).

Answer:

1. What is the relationship between `String::toLowerCase` and the lambda `s -> s.toLowerCase()`? Are they interchangeable?
2. When is each style clearer? (Hint: think about what the lambda does. If it just forwards its argument to a single method, a method reference is usually shorter.)
3. Could pipeline 1's filter be written as a method reference instead of `n -> n.startsWith("a")`? Why or why not?

### Question 2.4: Comparators

Pipeline 1 asks you to sort by length first, then alphabetically as a tiebreaker. The pattern looks like this:

```java
.sorted(Comparator.comparingInt(String::length)
                  .thenComparing(Comparator.naturalOrder()))
```

Answer:

1. What does `Comparator.comparingInt(String::length)` produce? What does it compare?
2. What does `thenComparing(...)` add? When does the tiebreaker activate?
3. If you wanted to sort longest-first, then reverse-alphabetically for ties, how would you change this line? (You do not have to write it; just sketch the change in your notebook.)

### Question 2.5: `flatMap`

Pipeline 3 turns a list of sentences into a list of distinct words. The key step is:

```java
.flatMap(s -> Arrays.stream(s.split("\\W+")))
```

Answer:

1. What is the difference between `map` and `flatMap`? If `map` were used here instead, what type would the resulting stream have?
2. `s.split("\\W+")` returns a `String[]`. What does `Arrays.stream(...)` do with it?
3. The regex `\\W+` matches one or more non-word characters. Why might splitting on `\\W+` produce an empty string at the start of some inputs? (Hint: think about what happens if the input begins with a non-word character. This is why pipeline 3 has a `filter(w -> !w.isEmpty())` step.)

### Question 2.6: Laziness and `peek`

Pipeline 5 uses `peek` to log each large transaction as it flows through the pipeline. Answer:

1. Why is `peek` an *intermediate* operation, not a terminal one? Where does the log line actually get printed if the terminal operation is never called?
2. The Javadoc for `peek` says it is intended primarily for debugging and warns against using it for production side effects. Why? (Hint: think about what happens if the stream is short-circuited by a downstream `limit` or `findFirst`.)
3. If you replaced `peek(...)` with `forEach(...)`, what would change? Would the pipeline still produce a `bigTotal`?

### Reference: Things you should have noticed

After you write your own answers, check against this list.

**Intermediate vs terminal (Q2.1):** Each pipeline has a `.stream()` source, several intermediate operations, and exactly one terminal. `collect(Collectors.toList())` materializes the stream into a `List`. `sum()` reduces a primitive numeric stream to a single number. A pipeline with no terminal operation does nothing at run time; no element ever moves through it. This laziness is what allows the JDK to optimize the execution (it can sometimes fuse operations, short-circuit on `limit`, and so on).

**Operations (Q2.2):**
- `map(f)`: applies `f` to each element; element type may change.
- `filter(p)`: keeps elements where `p` returns true; element count may decrease, type does not change.
- `distinct()`: keeps the first occurrence of each value (using `equals`).
- `sorted()`: returns the elements in natural order, or in a comparator-defined order.
- `limit(n)`: keeps at most the first `n` elements; later ones are not pulled.
- `skip(n)`: discards the first `n` elements; rest pass through.
- `flatMap(f)`: applies `f` to each element where `f` returns a stream, and concatenates the resulting streams.
- `peek(c)`: applies `c` to each element as a side effect, without changing the element.

**Method references (Q2.3):** `String::toLowerCase` and `s -> s.toLowerCase()` are equivalent. Use a method reference when the lambda just forwards arguments to a single method. Pipeline 1's filter cannot easily be a method reference because `startsWith` needs an argument (`"a"`), so the lambda form `n -> n.startsWith("a")` is the natural choice. (You could write `((Predicate<String>) "a"::equals)` if you wanted to match exact equality, but that is a different test.)

**Comparators (Q2.4):** `Comparator.comparingInt(String::length)` builds a comparator that compares strings by their length. `thenComparing(naturalOrder())` adds a tiebreaker: when two strings have equal length, compare them alphabetically. Tiebreakers activate only when the primary comparator returns 0. For longest-first with reverse-alpha tiebreakers: `Comparator.comparingInt(String::length).reversed().thenComparing(Comparator.reverseOrder())`.

**flatMap (Q2.5):** `map` would produce a `Stream<String[]>`, a stream of arrays. `flatMap` flattens it by replacing each array with the elements of that array, producing a `Stream<String>`. `Arrays.stream(...)` converts the `String[]` into a `Stream<String>` for `flatMap` to consume. Empty strings can appear when an input starts with a non-word character (none of these sentences do, but defensive code filters them anyway).

**Peek and laziness (Q2.6):** `peek` is intermediate because it returns a stream. The log line is only printed when a terminal operation pulls elements through the pipeline. `peek` is a debugging tool because its execution timing is implementation-defined and surprising: with `limit`, `peek` only fires for elements that survive the limit; with parallel streams, the order is unpredictable. `forEach` is a terminal operation; replacing `peek` with `forEach` would consume the stream, and the pipeline would no longer have anything left to `sum`.

---

## Part 3: Implement the TODOs

You will implement six stream pipelines. Run the program after each pipeline is complete to confirm progress. Each TODO is one line of code.

Make a copy of the starter so you can compare:

```bash
cp StreamLabStarter.java Work.java
```

Then rename the public class inside `Work.java` from `StreamLabStarter` to `Work` so the file name matches the class name (Java requires this). Edit `Work.java` from now on; leave `StreamLabStarter.java` as a reference.

### Step 3.1: Pipeline 1 (names: lowercase, filter 'a', distinct, sort by length then alpha)

Replace the TODOs in pipeline 1 with these intermediate operations, in order:

```java
.map(String::toLowerCase)
.filter(n -> n.startsWith("a"))
.distinct()
.sorted(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()))
```

**Design hint:** Order matters. If you `distinct()` before `map(toLowerCase)`, then `"Ada"` and `"ada"` count as different strings and both survive `distinct`. Lowercasing first collapses them into one. The general principle is **normalize before deduplicating**.

Run the program. The pipeline 1 line should now output something close to:

```
1) aNames = [ada, alan]
```

You will still see compile errors from the unfinished pipelines below; that's fine. Implement them one by one.

### Step 3.2: Pipeline 2 (numbers: square, keep evens, sort desc, skip 2, take 5)

Replace the TODOs:

```java
.map(n -> n * n)
.filter(sq -> sq % 2 == 0)
.sorted(Comparator.<Integer>naturalOrder().reversed())
.skip(2)
.limit(5)
```

**Design hint:** `sorted` with `Comparator.naturalOrder().reversed()` is the idiomatic way to sort in descending order. You could also write `.sorted((a, b) -> b - a)`, but that breaks on overflow for very large values; `naturalOrder().reversed()` does not.

**Run.** Pipeline 2 should now output:

```
2) evenSquares = [4]
```

That is not a typo; it really is a one-element list. The expected trace in Part 4 explains why.

### Step 3.3: Pipeline 3 (sentences: split into words, lowercase, filter empty, distinct, sort)

Replace the TODOs:

```java
.flatMap(s -> Arrays.stream(s.split("\\W+")))
.map(String::toLowerCase)
.filter(w -> !w.isEmpty())
.distinct()
.sorted()
```

**Design hint:** Note the order: `flatMap` first turns one sentence into many words, then `map` lowercases each word individually. If you tried to lowercase the sentence first you would get the same result here, but for more complex transformations (say, applying a per-word filter) you usually want `flatMap` early so you can operate on individual elements.

Run. Pipeline 3 should print a sorted list of 18 distinct lowercase words.

### Step 3.4: Pipeline 4 (categories: uppercased, distinct, sorted)

Replace the TODOs:

```java
.map(tx -> tx.category().toUpperCase(Locale.ROOT))
.distinct()
.sorted()
```

**Design hint:** Note that `tx.category()` is the accessor generated by the `record` declaration. Records do not give you `tx.category` (no parens) like in Python; the parens are part of the call, and they are not optional. The `Locale.ROOT` argument to `toUpperCase` makes the conversion locale-independent; on some Turkish systems, the default-locale uppercase of "i" is "İ" (with a dot), which can produce mysterious bugs. Use `Locale.ROOT` when you are normalizing for comparison, not for display.

Run. Pipeline 4 should output:

```
4) categories = [BOOKS, COFFEE, ELECTRONICS, GROCERY]
```

### Step 3.5: Pipeline 5 (large transactions, peek debug, sum amounts)

Replace the TODOs:

```java
.filter(tx -> tx.amount() >= 100.0)
.peek(tx -> System.out.println("   large tx: " + tx.id() + " $" + tx.amount()))
.mapToDouble(tx -> tx.amount())
```

**Design hint:** Two things to notice. First, `mapToDouble` (not `map`) is what converts a `Stream<Transaction>` into a `DoubleStream`, which is what supports the `.sum()` terminal. The primitive-stream variants (`IntStream`, `LongStream`, `DoubleStream`) exist so that numeric reductions can avoid boxing every value. Second, the `peek` line will print *during* the stream evaluation, intermixed with the subsequent `System.out.println("5) bigTotal = ...")` output. The peek output lines appear *before* the `5) bigTotal = ...` line because the terminal `sum()` is what triggers them, and `sum()` runs to completion before the next `println`.

Run. You should now see the three large transactions logged by `peek`, followed by the total:

```
   large tx: t1 $120.0
   large tx: t4 $220.0
   large tx: t6 $500.0
5) bigTotal = 840.0
```

### Step 3.6: Pipeline 6 (pagination)

Replace the TODOs:

```java
.skip((long) pageIndex * pageSize)
.limit(pageSize)
```

**Design hint:** The `(long)` cast is defensive: `skip` takes a `long` argument, and the multiplication `pageIndex * pageSize` happens in `int` arithmetic, which can overflow for very large page numbers. Casting one operand to `long` forces the multiplication into `long` arithmetic and avoids the overflow. For small page numbers it makes no difference, but the cast costs nothing and prevents a class of subtle bugs.

Run. Pipeline 6 should output:

```
6) page = [grace, guido, linus]
```

---

## Part 4: Verify Against the Expected Output

Run the finished program:

```bash
java Work.java
```

Your output should match this exactly:

```
1) aNames = [ada, alan]
2) evenSquares = [4]
3) vocab = [and, as, avoid, data, effects, filter, flatmap, functional, functions, map, programming, pure, side, streams, transform, uses, values, with]
4) categories = [BOOKS, COFFEE, ELECTRONICS, GROCERY]
   large tx: t1 $120.0
   large tx: t4 $220.0
   large tx: t6 $500.0
5) bigTotal = 840.0
6) page = [grace, guido, linus]
```

Walk through each pipeline before you congratulate yourself; verifying the output is the same skill as writing the code.

### Pipeline-by-pipeline trace

**Pipeline 1 (`aNames`):** Start with `[Ada, bob, ALAN, Ada, grace, linus, Guido, ada, Bjarne]`. After `toLowerCase`: `[ada, bob, alan, ada, grace, linus, guido, ada, bjarne]`. After `filter(startsWith("a"))`: `[ada, alan, ada, ada]`. After `distinct`: `[ada, alan]`. Sort by length (3 < 4): `[ada, alan]`. Final: `[ada, alan]`.

**Pipeline 2 (`evenSquares`):** Start with `[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]`. Squares: `[9, 1, 16, 1, 25, 81, 4, 36, 25, 9, 25]`. Keep even: `[16, 4, 36]`. Sort descending: `[36, 16, 4]`. Skip 2: `[4]`. Limit 5 (no effect, only 1 left): `[4]`. Final: `[4]`. The one-element result is correct: there are only three even squares to begin with, and skipping the first two leaves only one.

**Pipeline 3 (`vocab`):** Split each sentence on `\W+`, flatten, lowercase, drop empties, dedupe, sort. The 18 distinct words across the three sentences, in alphabetical order, are: and, as, avoid, data, effects, filter, flatmap, functional, functions, map, programming, pure, side, streams, transform, uses, values, with.

**Pipeline 4 (`categories`):** Uppercase each transaction's category, dedupe, sort: `[BOOKS, COFFEE, ELECTRONICS, GROCERY]`. (The categories are already uppercase in the input, but the `toUpperCase` step makes the pipeline robust against mixed-case future inputs.)

**Pipeline 5 (`bigTotal`):** Keep transactions with `amount >= 100`: t1 ($120), t4 ($220), t6 ($500). `peek` prints each one as it flows through. `mapToDouble` extracts the amounts. `sum` adds them: `120 + 220 + 500 = 840.0`.

**Pipeline 6 (`page`):** Lowercase all names, sort: `[ada, ada, ada, alan, bjarne, bob, grace, guido, linus]`. Skip `2 * 3 = 6`: `[grace, guido, linus]`. Limit 3: `[grace, guido, linus]`. Final: `[grace, guido, linus]`. Note that `distinct` is not applied here, so the three duplicate "ada" entries fill the first page; we are paginating the raw list, not the deduplicated one.

### If your output differs

The most common ways for the output to differ:

1. **`aNames` shows duplicates.** You probably called `distinct` before `map(toLowerCase)`. With case-sensitive `distinct`, `"Ada"` and `"ada"` are different. Lowercase first, then `distinct`.
2. **`evenSquares` is empty or much longer.** You probably swapped `map` and `filter`: filtering for even *numbers* and then squaring gives a different set than squaring and then filtering for even *squares*. (In this case they happen to give similar results, but the order is a real design choice; the lab spec says square first.)
3. **`vocab` contains an empty string `""` as its first element.** Your filter for non-empty did not run, or you put it before `flatMap` (where each element is still a whole sentence, never empty). Move the filter after the `flatMap`.
4. **`bigTotal` is the sum of *all* transactions, not just large ones.** You forgot the `filter` step, or your filter has the wrong comparison (`>` instead of `>=`, or comparing to the wrong threshold).
5. **The `peek` lines do not appear.** Either you used `forEach` (which consumes the stream and removes everything downstream) or you put `peek` after `mapToDouble` and expected to see the `Transaction` field. Position matters: `peek` shows whatever the stream's element type is at that point.
6. **`page` is wrong.** Most likely an `int` overflow on the `skip` calculation, but for these small numbers that should not happen; more likely you reversed `skip` and `limit`, which gives a totally different page.

If you cannot find the bug, add a `peek` of your own to inspect what is flowing through a stage:

```java
.peek(x -> System.out.println("DEBUG after filter: " + x))
```

That is exactly what `peek` is for.

---

## Part 5: Reflection

Answer in your notebook. These are open-ended; spend at least 10 minutes.

1. **Loops versus pipelines.** You have written six transformations in this lab and not a single `for` loop. Pick the most complex pipeline (probably pipeline 3 or 5) and rewrite it in your notebook as a `for` loop with explicit collections and mutation. Which is easier to read once you know both styles? Which is easier to debug?

2. **Laziness is a leaky abstraction.** Stream pipelines are lazy: nothing runs until the terminal operation. That sounds neutral, but it has practical consequences. Give an example from this lab where laziness saved work (the pipeline did not process every element). Give an example where laziness might *hurt* you (a hidden bug that only manifests at the terminal operation, far from the operation that caused it).

3. **`peek` is for debugging.** The JDK documentation explicitly says `peek` should not be used for production side effects. But pipeline 5 uses `peek` in what looks like production code (the lab does not throw away the log lines). When does a "debug log" cross the line into a "production side effect"? What is the cleaner way to write pipeline 5 if you actually wanted those logs as a feature?

4. **Why streams are like SQL.** A lot of stream pipelines have shapes that look like SQL queries: `filter` is a `WHERE`, `map` is a column projection, `distinct` is `SELECT DISTINCT`, `sorted` is `ORDER BY`, `limit/skip` is `LIMIT/OFFSET`. Why might the JDK designers have wanted streams to look like SQL? When does the analogy break down? (Hint: `flatMap`.)

5. **Records as functional values.** The `Transaction` record is immutable: once constructed, its fields cannot change. That is a deliberately functional design choice. What would change about the code in pipelines 4 and 5 if `Transaction` were a regular mutable class instead? What would *not* change?

6. **What is missing?** This program is a good demonstration of stream pipelines, but it is not production code. Three things are missing that you would want before deploying it. Name them. (Hints: error handling for empty input, parallelism, money arithmetic.)

---

## Reference: Intermediate vs Terminal Operations

The full list of stream operations is long; here are the ones you are most likely to see.

| Kind | Operation | Returns | Notes |
|------|-----------|---------|-------|
| Intermediate | `map(f)` | `Stream<R>` | Element type may change. |
| Intermediate | `filter(p)` | `Stream<T>` | Element count may decrease. |
| Intermediate | `flatMap(f)` | `Stream<R>` | `f` must return a stream. |
| Intermediate | `distinct()` | `Stream<T>` | Uses `equals` for comparison. |
| Intermediate | `sorted()` / `sorted(cmp)` | `Stream<T>` | Stateful: buffers everything. |
| Intermediate | `limit(n)` | `Stream<T>` | Short-circuits the pipeline. |
| Intermediate | `skip(n)` | `Stream<T>` | Discards the first `n`. |
| Intermediate | `peek(c)` | `Stream<T>` | Debugging only. |
| Terminal | `collect(collector)` | varies | Usually a `List`, `Set`, or `Map`. |
| Terminal | `forEach(c)` | `void` | Order undefined for parallel streams. |
| Terminal | `count()` | `long` | Element count. |
| Terminal | `sum()` (primitive streams only) | `int/long/double` | Numeric reduction. |
| Terminal | `reduce(...)` | varies | General-purpose fold. |
| Terminal | `findFirst()` / `findAny()` | `Optional<T>` | Short-circuits the pipeline. |
| Terminal | `anyMatch(p)` / `allMatch(p)` / `noneMatch(p)` | `boolean` | Short-circuits. |

A few have **short-circuit** semantics: they stop pulling values from upstream as soon as they have what they need. `limit`, `findFirst`, `anyMatch`, `allMatch`, and `noneMatch` all short-circuit. This means an infinite stream can still be safely consumed if you put a `limit` or a short-circuiting terminal somewhere downstream.

A few are **stateful**: they must see (some or all) of the stream before they can produce output. `sorted` is the most expensive: it buffers every element. `distinct` is stateful too (it must remember every value it has seen). For most pipelines this does not matter; for huge streams it can.

---

## Reference: Comparators

The `Comparator` class is a small but powerful API.

| Idiom | What it does |
|-------|--------------|
| `Comparator.naturalOrder()` | Use the natural order of `Comparable` elements. |
| `Comparator.reverseOrder()` | Reverse natural order. |
| `Comparator.comparing(f)` | Sort by the value of `f` (any type). |
| `Comparator.comparingInt(f)` | Sort by an `int` value of `f` (avoids boxing). |
| `cmp.reversed()` | Flip an existing comparator's direction. |
| `cmp.thenComparing(other)` | Add a tiebreaker for equal-keyed elements. |

The most common mistake is writing `(a, b) -> a - b` for "natural ascending order." For `Integer` it works most of the time but overflows on `MAX_VALUE - MIN_VALUE`. Use `Integer.compare(a, b)`, or just `Comparator.naturalOrder()`.

---

## Reference: Records (Java 16+)

A record is shorthand for an immutable data class. This:

```java
record Transaction(String id, double amount, String category) {}
```

is roughly equivalent to a regular class with:

- private final fields `id`, `amount`, `category`
- a public constructor that sets them
- accessor methods `id()`, `amount()`, `category()` (note the parens)
- a sensible `equals()` that compares all three fields
- a sensible `hashCode()` that combines them
- a sensible `toString()` like `Transaction[id=t1, amount=120.0, category=GROCERY]`

You can add methods to a record, and you can add a *compact constructor* for validation, but the fields are always implicitly `final` and the class is always implicitly `final` (you cannot extend it). This makes records a natural fit for the values that flow through stream pipelines: they are immutable, so they can be shared safely across threads, and `distinct` works correctly without you having to think about it.

---

## Reference: Pitfalls in Stream Pipelines

| Pitfall | What goes wrong | How to avoid |
|---------|----------------|--------------|
| Reusing a stream | `IllegalStateException: stream has already been operated upon or closed` | A stream is a one-shot pipeline. Build a new one from the source. |
| Mutating shared state from inside a lambda | Race conditions in parallel streams; surprising results | Use immutable values; if you must accumulate, use `collect` or `reduce`. |
| Forgetting the terminal operation | The pipeline never runs | Always end with `collect`, `sum`, `forEach`, etc. |
| `peek` for side effects | Skipped when downstream short-circuits | Use a terminal operation like `forEach` for real side effects. |
| Sorting an infinite stream | `OutOfMemoryError` (stateful operation) | Don't. Use `limit` first. |
| `int` overflow in `skip` arithmetic | Wrong page returned | Cast to `long` before multiplying. |

---

## Troubleshooting

**`error: cannot find symbol: method sum() ... location: interface Stream<Transaction>`.**
You called `.sum()` on a stream whose element type is not numeric. Add a `mapToDouble(tx -> tx.amount())` (or `mapToInt` / `mapToLong` for integer types) before `.sum()`. Only the primitive-typed streams have `sum`.

**`error: incompatible types: inference variable T has incompatible bounds`.**
The element type at the end of your pipeline does not match the declared type of the variable you are collecting into. Most commonly this is because a `map` step is missing. Trace the type from the source through each intermediate operation; what type does each stage produce?

**`java.lang.IllegalStateException: stream has already been operated upon or closed`.**
You tried to use the same stream twice, perhaps by saving it to a variable and calling two terminal operations. Streams are one-shot. If you need two pipelines from the same data, call `.stream()` twice on the source collection.

**Compile error: `tx.amount` cannot be resolved.**
On a record, the accessor is a method call: `tx.amount()`, not `tx.amount`. The parens are not optional.

**`peek` does not print anything.**
Most likely no terminal operation is consuming the stream, or the terminal operation is short-circuiting before reaching the elements that would have been peeked. Add a `.forEach(x -> {})` temporarily as a known-consuming terminal to verify.

**`Comparator.naturalOrder()` produces a "cannot infer type" error.**
The compiler does not know what type you want. Write `Comparator.<Integer>naturalOrder()` (or whichever type) to tell it explicitly.

**Pipeline 6's pagination produces an empty page for small page indices.**
You probably reversed `skip` and `limit`. `skip` then `limit` gives "elements N+1 through N+pageSize". `limit` then `skip` gives "skip from the first `limit` elements", which is usually not what you want.

---

## Further Reading

- **The Java Tutorials, "Aggregate Operations"** at docs.oracle.com. Authoritative tutorial on streams, current with the latest JDK.
- **Java SE API documentation for `java.util.stream`**. The package-level Javadoc has a clear explanation of intermediate vs terminal, lazy vs eager, and the stateful operations.
- **Modern Java in Action** (Urma, Fusco, Mycroft), 2nd edition. The standard book-length treatment of streams, lambdas, and the functional features of Java.
- **Why Functional Programming Matters** (John Hughes, 1989). A classic paper that argues for higher-order functions and lazy evaluation as the two big ideas of functional programming. Streams are the descendant of both.
- **SQL for Streamers**. Most stream pipelines have direct SQL analogs. If you know SQL well, learning streams is mostly learning a new syntax for ideas you already have; if you do not, working through streams will give you most of the conceptual vocabulary for SQL.
