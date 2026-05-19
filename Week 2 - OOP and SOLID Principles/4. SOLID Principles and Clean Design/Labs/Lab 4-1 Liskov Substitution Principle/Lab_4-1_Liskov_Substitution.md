# Lab 4-1: The Liskov Substitution Principle

## Overview

The **Liskov Substitution Principle (LSP)** is one of the five SOLID principles of object-oriented design. It was articulated by Barbara Liskov in a 1987 keynote and made precise in a 1994 paper with Jeannette Wing. The idea is short to state:

> If S is a subtype of T, then objects of type T in a correct program may be replaced with objects of type S without altering the correctness of that program.

Put another way: a subclass should be able to stand in for its parent class anywhere the parent is used, and the program should still work. If a caller has a `Rectangle` reference, the caller should not have to know or care whether the actual object is a plain `Rectangle` or a `Square` subclass. Whatever guarantees the `Rectangle` interface makes, the `Square` must keep.

LSP is easy to say and surprisingly hard to obey. The canonical violation, and the one you will see in this lab, is so famous it has a nickname: the **Circle-Ellipse problem** (or in our case, the Square-Rectangle problem). The intuition is innocent: "every square is a rectangle, so `Square` should extend `Rectangle`." That sounds right in geometry class. It is also wrong in code, and the bug it produces is subtle: two clients can do the "same" operations to a `Square` and get different answers depending on the order in which they set the width and height.

In this lab you will run a small program that demonstrates the violation, see the bug in the output, then refactor `Square` so that the violation disappears. The fix is unsurprising once you see it, but it requires letting go of the "every square is a rectangle" intuition. The deeper lesson, which the reflection at the end of the lab brings out, is that **inheritance models behavioural compatibility, not real-world taxonomy**. Two things that are the same in the world are not necessarily the same in code, and the test is whether their *behaviour* obeys the same contracts.

The code is provided. Your task is one small refactor.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected. The point is to feel the bug, then feel the fix, and then think about what the fix cost you.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. State the Liskov Substitution Principle from memory.
2. Explain why "every square is a rectangle" is true in geometry but false in code that uses mutable setters.
3. Identify a concrete LSP violation by running a program and reading its output.
4. Refactor a subclass so it no longer violates LSP, and explain what the refactor cost in terms of substitutability.
5. Name at least one alternative design (composition, immutability, separate interfaces) that avoids the violation without inheritance.

---

## Part 1: Set Up the Workspace

### Step 1.1: Confirm you have Java installed

In a terminal:

```bash
java --version
```

Java 11 or later is fine. No records or other modern features are used in this lab.

### Step 1.2: Create the lab directory

```bash
mkdir -p ~/lsp-lab
cd ~/lsp-lab
```

### Step 1.3: Create the starter file

Create a file called `Main.java` and paste in the following code exactly. Do not modify anything yet; in Part 2 you will read it before changing anything.

```java
public class Main {
    // A client that assumes independent setters:
    static int computeArea(Rectangle r) {
        return r.getHeight() * r.getWidth(); // expects unchanged height
    }

    public static void main(String[] args) {
        Rectangle rect = new Rectangle();
        rect.setWidth(5);
        rect.setHeight(10);
        int h1 = computeArea(rect); // expect 50
        System.out.println("Rectangle area for 5x10: " + h1);

        Rectangle sq = new Square(); // subtype used via base type

        sq.setWidth(5);
        sq.setHeight(10);
        int h2 = computeArea(sq);
        System.out.println("First area for square: " + h2);

        sq.setHeight(10);
        sq.setWidth(5);
        h2 = computeArea(sq);
        System.out.println("Second area for square: " + h2);
    }
}

class Rectangle {
    protected int width;
    protected int height;

    public int getWidth()  { return width; }
    public int getHeight() { return height; }

    public void setWidth(int w)  { this.width = w; }
    public void setHeight(int h) { this.height = h; }

    public int area() { return width * height; }
}

class Square extends Rectangle {
    @Override
    public void setWidth(int w) {
        this.width = w;
        this.height = w; // forces equality
    }

    @Override
    public void setHeight(int h) {
        this.height = h;
        this.width  = h; // forces equality
    }
}
```

Save the file.

### Step 1.4: Run the starter to see the violation

```bash
java Main.java
```

Output:

```
Rectangle area for 5x10: 50
First area for square: 100
Second area for square: 25
```

Look at those three lines and let the bug sink in. The first line is fine: a 5 by 10 rectangle has area 50, as expected. But the next two lines are the problem. The "square" variable was given the same operations both times, just in a different order, and the client function `computeArea` got two different answers: 100 and 25.

The client did nothing wrong. The client wrote `computeArea(Rectangle r)` and expects what every reader expects from a `Rectangle`: setting width and height are independent operations. Set the width to 5, then set the height to 10, and the rectangle is now 5 by 10. The client multiplies them and gets 50.

But the actual object is a `Square`, and `Square` has overridden the setters so that each one changes *both* fields. After `sq.setWidth(5); sq.setHeight(10);` the second setter has clobbered the width and the square is now 10 by 10, area 100. After `sq.setHeight(10); sq.setWidth(5);` the second setter clobbers the height instead, the square is 5 by 5, area 25.

This is exactly the situation Liskov's principle forbids. The client wrote correct code against the `Rectangle` contract; substituting a `Square` for the `Rectangle` broke the client's program. Your job in Part 3 is to fix `Square` so this can no longer happen.

### Step 1.5: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your analyses and decisions as you go:

```markdown
# LSP Lab Notebook

## Part 2: Reading the starter

## Part 3: The refactor

## Part 4: Verification

## Part 5: Reflection
```

---

## Part 2: Read the Starter Before You Change It

The bug you just saw is the whole lab in miniature. Before you fix it, you should be able to explain it in your own words. Spend at least 10 minutes on this section.

### Question 2.1: The contract of `Rectangle`

Look at the `Rectangle` class. Without reading the `Square` subclass, write down in your notebook what a caller can expect from `setWidth` and `setHeight`. Specifically:

1. After `r.setWidth(w)`, what is the value of `r.getWidth()`? What is the value of `r.getHeight()`?
2. After `r.setWidth(w); r.setHeight(h);`, what is the value of `r.getWidth()`? What is the value of `r.getHeight()`?
3. Is the order in which you call the two setters supposed to matter, according to the `Rectangle` contract?

These contracts are not written anywhere as code, but they are implicit in the design of `Rectangle`. Every reasonable reader would assume them. The bug appears precisely because `Square` violates them.

### Question 2.2: What `Square` does

Now read the `Square` subclass. Answer in your notebook:

1. What does `Square.setWidth(5)` do to the `width` field? What does it do to the `height` field?
2. Pretend you are a caller who knows only that you have a `Rectangle`. You write `r.setWidth(5); r.setHeight(10);`. If the actual object is a `Rectangle`, you end up with `width=5, height=10`. If it is a `Square`, what do you end up with?
3. The override in `Square` is "logically correct" in the sense that a square always has equal sides. So what specifically is wrong about it from LSP's point of view? (Hint: the problem is not what `Square` does to itself. It is what `Square` does to *callers who think they are talking to a `Rectangle`*.)

### Question 2.3: Why the order matters

The starter's `main` runs the same two setter calls twice, in opposite orders:

```java
sq.setWidth(5);   sq.setHeight(10);   // produces a 10x10 square, area 100
sq.setHeight(10); sq.setWidth(5);     // produces a 5x5 square,   area 25
```

Answer:

1. Walk through both sequences step by step. After each call, what are the values of `width` and `height` inside the `Square`?
2. Why is the dependence on order a *symptom* of the LSP violation, not the violation itself?
3. If the `Rectangle` class had been declared `final` (no subclasses allowed), could this bug exist?

### Question 2.4: What "substitutability" actually means

The principle says objects of type `T` can be replaced with objects of type `S` "without altering the correctness of the program." Answer:

1. Whose "correctness" are we talking about? The `Rectangle`'s? The `Square`'s? Some third party's? (Hint: there is one role we keep mentioning in this lab.)
2. The `computeArea` function in the starter is correct against the `Rectangle` contract. Is it correct against the `Square` contract too? Does the `Square` even *have* a contract that differs from `Rectangle`?
3. LSP is sometimes summarized as "subclass should preserve the *behaviour* the superclass promised." Why is "behaviour" a more accurate word here than "interface" or "method signatures"? (Hint: `Square.setWidth` has the same signature as `Rectangle.setWidth`. That is not enough.)

### Reference: Things you should have noticed

After you write your own answers, check against this list.

**Contract (Q2.1):** A caller of `Rectangle` expects `setWidth` and `setHeight` to be independent: setting one does not change the other. After `r.setWidth(w); r.setHeight(h);` you have `width=w, height=h`, no matter the order. This is not promised in any comment, but it is so obvious from the field names and method names that no reader would expect otherwise.

**Square (Q2.2):** `Square.setWidth(5)` sets both `width=5` and `height=5`. A caller who calls `r.setWidth(5); r.setHeight(10);` on a `Rectangle` reference ends up with `width=10, height=10` if the actual object is a `Square`. The override is "logically correct" for a square in isolation; it is wrong because the caller did not know they were talking to a square. The bug is in the relationship between the subclass and the *caller's expectations of the superclass*, not in the subclass on its own.

**Order (Q2.3):** First sequence: setWidth(5) sets both to 5, then setHeight(10) sets both to 10, giving 10 by 10. Second sequence: setHeight(10) sets both to 10, then setWidth(5) sets both to 5, giving 5 by 5. The order-dependence is a symptom because the underlying violation is that `Square` couples two operations that the `Rectangle` contract said were independent. If `Rectangle` had been declared `final`, nobody could subclass it and this specific bug could not exist; LSP violations require an inheritance relationship in the first place.

**Substitutability (Q2.4):** The correctness in question is the *caller's*. The caller wrote code that is correct against the `Rectangle` contract; the substitution broke it. `Square` does not have a separate contract; by inheriting from `Rectangle` it *promised* to honour the `Rectangle` contract, and it did not. "Behaviour" is more accurate than "interface" because the same method signatures can implement very different behaviours; LSP is about the latter, not the former. This is why LSP cannot be checked by a compiler the way method signatures can.

---

## Part 3: The Refactor

The goal is to make the bug impossible. There are several ways to do that; this lab walks you through the simplest one.

### Step 3.1: Diagnose

Before changing anything, write in your notebook what you think the fix should *not* do, and why:

1. Should the fix change the `Rectangle` class? Why or why not? (Hint: `Rectangle` works correctly; only `Square` violates the contract.)
2. Should the fix change the `computeArea` function? Why or why not? (Hint: `computeArea` is correct against the `Rectangle` contract.)
3. Should the fix change the call sites in `main`? Why or why not?

A good refactor leaves correct code alone and changes only the code that is wrong. The wrong code here is `Square`.

### Step 3.2: The fix

The intuition: a square is not just "a rectangle that happens to be the same width as its height." A square is its own thing, with its own interface. It has a *side*, not a width and a height. So `Square` should expose a `setSide(int s)` method, and should *not* override `setWidth` or `setHeight`.

Make a copy of the starter so you can compare:

```bash
cp Main.java Starter.java
```

Then open `Main.java` and replace the `Square` class with this version:

```java
class Square extends Rectangle {
    public void setSide(int s) {
        super.setHeight(s);
        super.setWidth(s);
    }
}
```

Notice:

1. The `@Override` annotations are gone. `Square` does not override either setter.
2. `Square` calls `super.setHeight` and `super.setWidth` from inside `setSide`. This goes through the inherited `Rectangle` setters, which keep their normal independent behaviour. The `Square` class trusts the `Rectangle` class to set one field at a time.
3. From a caller's point of view: if you have a `Rectangle` reference, you have `setWidth` and `setHeight` and they are still independent. The `Square` class does nothing to interfere.

### Step 3.3: Update `main` to use the new interface

Because `Square` no longer pretends to be substitutable for `Rectangle`, the `main` function that *treats* it as a `Rectangle` no longer makes sense. Replace the `Rectangle sq = new Square();` block with this:

```java
Square sq = new Square(); // declared as Square, not Rectangle
sq.setSide(5);
int h2 = computeArea(sq);
System.out.println("First area for square: " + h2);
```

A few things to notice:

1. The variable is now declared as `Square sq`, not `Rectangle sq`. Callers who want a square ask for a square; callers who want a rectangle ask for a rectangle. The two are no longer interchangeable.
2. `setSide(5)` is the only operation. There is no setWidth/setHeight ambiguity to exploit, so the order-dependence bug cannot occur.
3. The second area block (the one that produced the contradictory "25") is deleted, because the operations that produced the contradiction are no longer possible.
4. The function `computeArea(Rectangle r)` still accepts a `Square` because `Square extends Rectangle`. The substitution still works *for reading*. What changed is that nobody is writing to a `Square` through `Rectangle`'s setters anymore.

The full, finished `Main.java` should look like:

```java
public class Main {
    static int computeArea(Rectangle r) {
        return r.getHeight() * r.getWidth();
    }

    public static void main(String[] args) {
        Rectangle rect = new Rectangle();
        rect.setWidth(5);
        rect.setHeight(10);
        int h1 = computeArea(rect);
        System.out.println("Rectangle area for 5x10: " + h1);

        Square sq = new Square();
        sq.setSide(5);
        int h2 = computeArea(sq);
        System.out.println("First area for square: " + h2);
    }
}

class Rectangle {
    protected int width;
    protected int height;

    public int getWidth()  { return width; }
    public int getHeight() { return height; }

    public void setWidth(int w)  { this.width = w; }
    public void setHeight(int h) { this.height = h; }

    public int area() { return width * height; }
}

class Square extends Rectangle {
    public void setSide(int s) {
        super.setHeight(s);
        super.setWidth(s);
    }
}
```

### Step 3.4: Run the fixed program

```bash
java Main.java
```

The output should be:

```
Rectangle area for 5x10: 50
First area for square: 25
```

Two lines instead of three. The contradictory "second area" is gone because the operations that produced it (calling `Rectangle`'s setters on a `Square`) are no longer in the code.

---

## Part 4: Verify Against the Expected Output

Compare your output to:

```
Rectangle area for 5x10: 50
First area for square: 25
```

If you see exactly that, the refactor worked. If you see anything else, walk through this checklist.

### If your output differs

1. **You still see three lines.** You did not delete the second area block in `main`. The fix requires removing it; the lines `sq.setHeight(10); sq.setWidth(5);` should be gone.

2. **`First area for square: 100` instead of 25.** Your `Square` class is still overriding `setWidth` and `setHeight`. Re-read your new `Square` class; the `@Override` keywords and both setter methods should be gone, replaced with a single `setSide`.

3. **Compile error: `cannot find symbol setSide`.** Either you did not add the `setSide` method to `Square`, or you declared `sq` as `Rectangle sq` instead of `Square sq`. `Rectangle` has no `setSide` method, so the compiler refuses the call.

4. **Compile error: `setSide() in Square cannot override setSide() in Rectangle`.** You probably wrote `@Override` on the `setSide` method by reflex. There is nothing in `Rectangle` for `setSide` to override; remove the annotation.

5. **`First area for square: 0`.** You added a `setSide` method but it does not actually set anything, or you forgot to call `sq.setSide(5)` in `main` before calling `computeArea`. The fields default to zero.

### Walking through the fix

| Step | Code | State after |
|------|------|-------------|
| 1 | `Rectangle rect = new Rectangle();` | `rect`: width=0, height=0 |
| 2 | `rect.setWidth(5);` | `rect`: width=5, height=0 |
| 3 | `rect.setHeight(10);` | `rect`: width=5, height=10 |
| 4 | `computeArea(rect)` | returns 5 * 10 = 50 |
| 5 | `Square sq = new Square();` | `sq`: width=0, height=0 |
| 6 | `sq.setSide(5);` calls `super.setHeight(5)` then `super.setWidth(5)` | `sq`: width=5, height=5 |
| 7 | `computeArea(sq)` | returns 5 * 5 = 25 |

Notice that `computeArea` is exactly the same function it was before, with the same definition. It does not need to know whether its argument is a `Rectangle` or a `Square`. The substitution still works in the read direction. What we gave up was substitutability in the *write* direction: you can no longer mutate a `Square` *as if it were a `Rectangle`*, because doing so was the source of the bug.

---

## Part 5: Reflection

Answer in your notebook. These are open-ended; spend at least 10 minutes.

1. **What the fix cost.** In the starter, `Square` was a true subtype of `Rectangle`: a `Square` could be passed anywhere a `Rectangle` was expected, including to functions that wrote to it through `setWidth`/`setHeight`. In the fix, that is no longer true: `Square` is still a `Rectangle` for reading (it inherits `getWidth`, `getHeight`, `area`) but callers can no longer use the `Rectangle` interface to mutate a `Square`. We *traded* some substitutability for *correctness*. Was that the right trade? When would it not be?

2. **Geometry versus code.** "Every square is a rectangle" is true in geometry. Why is it false (or at least misleading) in code? Articulate the difference between **set-theoretic subtyping** (a square is a special kind of rectangle in the world) and **behavioural subtyping** (a square should support every operation a rectangle supports, with the same guarantees).

3. **An alternative design: immutability.** Imagine `Rectangle` had no setters at all: width and height are set in the constructor and never changed. Could `Square extends Rectangle` then be a true LSP-compliant subtype? Why? (Hint: where in the starter is the contradiction first introduced? Read-only methods, or the setters?)

4. **Another alternative: composition.** Instead of `Square extends Rectangle`, suppose `Square` had a private `Rectangle` field that it delegated to. Sketch what that would look like. Which design is clearer? Which is more flexible?

5. **The deeper rule.** Many of the SOLID principles end up saying versions of the same thing: *"design your subclasses to honour the contracts of their superclasses, not just their signatures."* Where else have you (or could you) hit the same kind of bug? Think about subclasses that override methods to "be more strict" (rejecting inputs the parent accepted), to "be more lenient" (returning fewer guarantees than the parent promised), or to "do extra work" (like firing events the parent didn't fire). Each is a potential LSP violation.

6. **What is missing.** This program is a teaching example, not a real shape library. Three things you would want before shipping it. Name them. (Hints: integer overflow on large dimensions, validation of negative inputs, support for shapes other than rectangles and squares.)

---

## Reference: The Liskov Substitution Principle, Formal Version

Liskov and Wing's 1994 paper gives the precise definition. In informal English it amounts to a set of rules for subtypes:

| Rule | What it means | Example violation |
|------|---------------|-------------------|
| **Preconditions cannot be strengthened** | The subtype cannot demand more of its callers than the supertype did. | A `Rectangle.setWidth` accepts any int; a `Square.setWidth` that throws on negative inputs would violate this if `Rectangle.setWidth` does not. |
| **Postconditions cannot be weakened** | The subtype must guarantee at least what the supertype guaranteed. | If `Rectangle.setWidth(w)` guarantees `getWidth() == w` and *only* width changed, `Square.setWidth(w)` violates this by also changing height. |
| **Invariants must be preserved** | Class invariants of the supertype must still hold. | The `Rectangle` invariant "width and height are independent" is silently broken by `Square`. |
| **History constraint** | The subtype cannot change properties that the supertype said could not change. | If `Rectangle` documents "once set, width changes only via `setWidth`", a `Square` that changes width inside `setHeight` violates this. |

This lab's bug is most directly a violation of the second and third rules. The `Square` weakens the postcondition of `setWidth` (it now also changes height) and breaks the invariant that width and height are independent.

The four rules are not new; they are the same rules that **design by contract** has used since Bertrand Meyer's Eiffel language in the 1980s. LSP is what those rules say specifically about inheritance.

---

## Reference: Common Sources of LSP Violations

LSP violations show up in real codebases in a few recognizable shapes. Recognizing the shape is half the battle.

| Shape | What it looks like | Why it violates LSP |
|-------|-------------------|---------------------|
| **The geometric subclass** | `Square extends Rectangle`, `Circle extends Ellipse`. | The mathematical relationship is "is a special case of," but the code relationship requires "supports every operation of." Mutable setters expose the gap. |
| **The restrictive subclass** | A subclass that throws `UnsupportedOperationException` from inherited methods, like `Collections.unmodifiableList`. | The Liskov-strict view says this is a violation; the pragmatic view (and the JDK's) is that it is a useful trade. |
| **The collection subclass** | `Stack extends Vector` in old Java; `Properties extends Hashtable<Object,Object>`. | The parent has too many methods; the child cannot honour them all and still be sane. |
| **The notification subclass** | A subclass that fires events the parent did not fire, or skips events the parent fired. | History-constraint violation; callers cannot rely on the event sequence. |
| **The optimisation subclass** | A subclass that caches results, then fails to invalidate the cache on a parent method call. | Invariant violation; the cache desynchronizes from the underlying data. |

In all of these, the fix is the same shape: **stop inheriting**. Use composition, use a separate interface, or split the type hierarchy so the subclass relationship is between things that really do share a contract.

---

## Reference: When to Use Inheritance at All

A common piece of modern OO design advice is "prefer composition over inheritance." That is not a ban on inheritance; it is a recognition that inheritance is the strongest possible coupling between two classes, and many use cases that look like inheritance candidates are better served by weaker couplings.

Use inheritance when:

1. The subclass genuinely *is a* specialised supertype, in the behavioural sense, not just the taxonomic sense.
2. You want code reuse *and* polymorphic substitution. (If you want only code reuse, composition is usually simpler.)
3. The supertype was *designed* to be subclassed (it has clearly documented hooks, protected helpers, well-stated invariants).

Use composition when:

1. You want to reuse code but not commit to substitutability.
2. The relationship is "has a" or "is implemented in terms of," not "is a."
3. The supertype was not designed to be subclassed (most classes in most codebases).

A famous expression of this principle is Joshua Bloch's *Effective Java* item "Favor composition over inheritance," which gives a careful worked example of how innocent-looking inheritance can produce LSP violations indirectly, even without a `Square extends Rectangle` smoking gun.

---

## Troubleshooting

**`error: setSide() in Square cannot override setSide() in Rectangle`.**
You added `@Override` to `setSide`. Remove it; `Rectangle` has no `setSide` method, so there is nothing to override.

**`error: cannot find symbol: method setSide(int)` on `Rectangle`.**
You called `setSide` on a variable declared as `Rectangle`. The `Rectangle` type does not know about `setSide`; only `Square` does. Declare the variable as `Square sq` for this call.

**The "Square area for 5x5" is 0.**
The `setSide` method body is empty, or you forgot to call it before calling `computeArea`. Walk through your `setSide` and verify it calls both `super.setHeight` and `super.setWidth`.

**The original three-line output (50, 100, 25) still appears.**
You edited the wrong file, or you saved over `Starter.java` instead of `Main.java`. Make sure you ran `java Main.java` after editing `Main.java`.

**You implemented the fix as a different design and the output is different.**
There is more than one correct fix. If your output is `50` and a *consistent* square area, and the call sites in `main` are not relying on `Rectangle`'s setters to mutate a `Square`, you have probably solved the problem differently and that is fine. The reflection questions are still worth answering.

---

## Further Reading

- **Liskov and Wing, "A Behavioral Notion of Subtyping"** (ACM TOPLAS, 1994). The original formal paper. Dense; the introduction is the most readable part.
- **Robert C. Martin, "The Liskov Substitution Principle"** (1996 paper, later in *Agile Software Development*). The version of LSP that the SOLID acronym popularized. Uses the Rectangle/Square example explicitly.
- **Effective Java, 3rd edition** (Joshua Bloch). Item 18: "Favor composition over inheritance." Concrete worked example of why "obvious" subclassing can violate LSP without anyone noticing.
- **Object-Oriented Software Construction, 2nd edition** (Bertrand Meyer). The chapter on design by contract is the foundation of LSP, and Meyer's discussion of preconditions, postconditions, and invariants is unmatched.
- **"Subtyping vs Inheritance"** (any of several survey articles). The deeper distinction this lab is really about: inheritance is a code-reuse mechanism, subtyping is a substitutability relation, and the language collapses them into one keyword (`extends`) at the cost of letting you make this very bug.
