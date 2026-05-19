# Lab 5-1: The Factory Method Pattern

## Overview

A **design pattern** is a reusable solution to a class of problem that comes up over and over in object-oriented design. The patterns were catalogued in 1994 by the "Gang of Four" (Gamma, Helm, Johnson, and Vlissides) in *Design Patterns: Elements of Reusable Object-Oriented Software*, a book that is still in print and still relevant today. The book lists 23 patterns; this lab covers one of the most common ones.

The **Factory Method** pattern solves a simple problem: how do you create an object of one of several related types, without the caller having to know which type to create? Without a pattern, the answer almost always starts as a chain of `if/else` or a `switch` statement. That works fine for two or three types. By type five, every place in the codebase that creates such an object has the same `if/else` chain copied into it. By type ten, you have to grep across the whole codebase every time you add a new type. The Factory Method pattern puts the `if/else` in exactly one place, behind a function called `create`, and lets every caller in the rest of the codebase just say `factory.create("email")` without caring what's inside.

In this lab you will work with a small notification system. There is an `EmailNotifier`, an `SmsNotifier`, and the lab walks you through adding a `PushNotifier` as a stretch goal. A `NotifierFactory` class hides the decision of which concrete class to construct. Most of the code is provided. Your job is to implement the one method in the factory that does the actual work, and then to feel how easy or hard it is to extend.

The lab is small. The conversation at the end (when does the pattern earn its keep, when is it overkill, what are the alternatives) is bigger and more useful than the coding part. Do not skip the reflection.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Recognize the Factory Method pattern when you see it and explain what problem it solves.
2. Implement a simple factory in Java that returns a concrete subtype based on a string parameter.
3. State the Open/Closed Principle and identify a place in code where it is, or is not, being followed.
4. Add a new product type to a factory and articulate what changed and what did not.
5. Name at least one alternative to the Factory Method pattern (a map of constructors, dependency injection, an enum with abstract methods) and discuss the tradeoffs.

---

## Part 1: Set Up the Workspace

### Step 1.1: Confirm you have Java installed

In a terminal:

```bash
java --version
```

Java 11 or later is fine. The lab uses no records, streams, or other modern-only features. The single-source-file launcher (`java Starter.java`) is convenient and works on Java 11 and up.

### Step 1.2: Create the lab directory

```bash
mkdir -p ~/factory-lab
cd ~/factory-lab
```

### Step 1.3: Create the starter file

Create a file called `Starter.java` and paste in the following code exactly. Do not modify anything yet; in Part 2 you will read it before changing anything.

```java
public class Starter {
    public static void main(String[] args) {
        // expected: [EMAIL] Build finished
        Notifier n1 = NotifierFactory.create("email");
        n1.send("Build finished");

        // expected: [SMS] Deploy started
        Notifier n2 = NotifierFactory.create("sms");
        n2.send("Deploy started");
    }
}

interface Notifier { void send(String msg); }

class EmailNotifier implements Notifier {
    public void send(String msg) { System.out.println("[EMAIL] " + msg); }
}
class SmsNotifier implements Notifier {
    public void send(String msg) { System.out.println("[SMS] " + msg); }
}

class NotifierFactory {
    // TODO(1): Return EmailNotifier when type equals "email"
    //          Return SmsNotifier when type equals "sms"
    //          Otherwise return null (for now)
    static Notifier create(String type) {
        // TODO
        return null;
    }
}
```

Save the file.

### Step 1.4: Try to run the starter (and see why it fails)

```bash
java Starter.java
```

Output:

```
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "Notifier.send(String)" because "<local1>" is null
	at Starter.main(Starter.java:5)
```

This is the expected "before" state and the reason the lab exists. The factory's `create` method has not been implemented yet, so it returns `null`. The `main` method calls `n1.send(...)` on `null` and the JVM throws `NullPointerException`.

Take a moment to look at the error message. Java 21 includes the name of the null variable in the message (`<local1>`, which corresponds to `n1`). Older Java versions would just say "NullPointerException at Starter.java:5." That added clarity is one of the small quality-of-life improvements in the modern JVM.

Your job in Part 3 is to implement the factory so this NPE goes away and the program prints the expected output.

### Step 1.5: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your analyses, decisions, and observations as you go:

```markdown
# Factory Method Lab Notebook

## Part 2: Reading the starter

## Part 3: The implementation

## Part 4: Verification

## Part 5: The stretch (PushNotifier)

## Part 6: Reflection
```

---

## Part 2: Read the Starter Before You Change It

The factory pattern is short to write but easy to misunderstand. Before you implement the TODO, you should be able to answer the questions below from the source alone. Spend at least 10 minutes on this section.

### Question 2.1: The interface

The file declares a `Notifier` interface with one method:

```java
interface Notifier { void send(String msg); }
```

Answer in your notebook:

1. What does it mean that `EmailNotifier` "implements `Notifier`"? What promise is `EmailNotifier` making to its callers?
2. There are two implementations (`EmailNotifier`, `SmsNotifier`). Their `send` methods print different things. From the perspective of someone holding a `Notifier` variable, does that difference matter? Why or why not?
3. Could you store an `EmailNotifier` and an `SmsNotifier` in the same `List<Notifier>` and loop over them? What would the loop look like?

### Question 2.2: The factory class

Look at `NotifierFactory`. It is a class with one `static` method:

```java
class NotifierFactory {
    static Notifier create(String type) {
        // TODO
        return null;
    }
}
```

Answer:

1. The method is `static`. Why? What would change if it were not? (Hint: think about whether you would ever want two different `NotifierFactory` *instances* with different behaviour.)
2. The return type is `Notifier`, not `EmailNotifier` or `SmsNotifier`. Why is this important? What is the caller given back, and what does the caller *not* know?
3. The `type` parameter is a `String`. List two things that could go wrong with this choice. (Hint: typos, case sensitivity, what happens if someone passes `"Email"` instead of `"email"`.)

### Question 2.3: How `main` uses the factory

The `main` method has two near-identical sequences:

```java
Notifier n1 = NotifierFactory.create("email");
n1.send("Build finished");
```

Answer:

1. Walk through these two lines step by step. What is the type of `n1` from the *compiler's* point of view? What is the runtime type of the object it actually points to?
2. The variable is declared as `Notifier` (the interface), not `EmailNotifier`. Why? What does that buy you? (Hint: imagine `main` is part of a much larger codebase. What changes if the variable type were `EmailNotifier` and someone later wanted to switch to SMS?)
3. The caller never says `new EmailNotifier()` anywhere. Where in the program does that constructor get called? Why is that better than calling it directly from `main`?

### Question 2.4: The Open/Closed Principle

In the lab introduction you read that the Factory Method pattern protects the **Open/Closed Principle**: "code should be open for extension, but closed for modification." Answer:

1. In your own words: what does "open for extension" mean? What does "closed for modification" mean? Why is this a desirable property?
2. Suppose, instead of using the factory, every place in a large codebase that needs a notifier had its own `if/else` block:
   ```java
   if (type.equals("email")) n = new EmailNotifier();
   else if (type.equals("sms")) n = new SmsNotifier();
   ```
   Now you want to add a `PushNotifier`. Which files have to change? Which files would have to change if a factory were used instead?
3. The lab text suggests the Open/Closed Principle is "broken" by the if/else version. Is that quite right? Is the code *worse* because of the duplicated if/else, or just *more painful to change later*? What is the relationship between the two?

### Reference: Things you should have noticed

After you write your own answers, check against this list.

**Interface (Q2.1):** `EmailNotifier implements Notifier` is a promise that `EmailNotifier` provides every method declared in `Notifier`. The compiler enforces the promise. To a caller holding a `Notifier`, the differences between the two implementations *do* matter (one sends email, one sends SMS), but the *interface* the caller programs against is the same. That uniformity is exactly what lets a `List<Notifier>` hold both and a single loop iterate over them.

**Factory class (Q2.2):** `static` because the factory has no per-instance state and there is no reason to construct a `NotifierFactory` object first. Some codebases do use *instance* factories when they want different factories to be configured differently (test mode vs production mode, for example), but for this small example, `static` is the natural choice. The return type is `Notifier` (the interface) so that the caller is intentionally given as little information as possible: just "a thing you can call `.send()` on." This is called **programming to an interface**. The `String` parameter is fragile in two ways: typos go unnoticed by the compiler ("emial" compiles fine but fails at runtime), and the comparison may or may not be case-sensitive depending on whether you use `equals` or `equalsIgnoreCase`. An `enum` would catch typos at compile time but is less flexible.

**How main uses it (Q2.3):** The compile-time type of `n1` is `Notifier`; the runtime type is `EmailNotifier`. This is the everyday case of an interface variable pointing to a concrete instance. Declaring the variable as `Notifier` and not `EmailNotifier` is what lets you change the factory call from `"email"` to `"sms"` without touching the rest of the code. The `new EmailNotifier()` constructor is called inside the factory, exactly once per request, and never directly from `main` or any other caller. The whole rest of the codebase is insulated from the existence of the concrete classes.

**Open/Closed (Q2.4):** "Open for extension" means: you can add new behaviour (new notifier types) without rewriting existing code. "Closed for modification" means: existing, tested code does not change when you add new behaviour. The desirable property is *change isolation*: the smaller the set of files you have to touch to add a feature, the less you risk breaking. With if/else scattered across the codebase, adding a `PushNotifier` requires editing every file that creates a notifier; with a factory, you edit one file. The code is not "worse" in the small (it works), but it scales badly, and the pain of every future change accumulates.

---

## Part 3: Implement the Factory

You will implement one TODO. It's short.

Make a copy of the starter so you can compare:

```bash
cp Starter.java Work.java
```

Then rename the public class inside `Work.java` from `Starter` to `Work` so the file name matches the class name (Java requires this for the public class). Edit `Work.java` from now on; leave `Starter.java` as a reference.

### Step 3.1: Implement `NotifierFactory.create`

Find the `create` method in `NotifierFactory`. Replace its body with:

```java
if (type.equalsIgnoreCase("email")) {
    return new EmailNotifier();
} else if (type.equalsIgnoreCase("sms")) {
    return new SmsNotifier();
}
return null;
```

A few design choices worth noticing as you type it out:

1. **`equalsIgnoreCase`, not `equals`.** A caller who passes `"Email"` or `"EMAIL"` probably means the same thing as `"email"`. Being lenient here is usually the right call. If you want to be strict (and force callers to use exactly one canonical spelling), use `equals` instead.

2. **String literal on the left.** Some style guides recommend writing the comparison as `"email".equalsIgnoreCase(type)` instead of `type.equalsIgnoreCase("email")`. The reason: if `type` is `null`, the first form returns `false` safely; the second throws `NullPointerException`. Both are fine for this lab, but you will see both forms in real codebases.

3. **`return null` for unknown types.** This is what the lab specifies, and it's the simplest. It is not the best design: a caller who passes a typo gets a null back and then crashes on the next line with a `NullPointerException`. In production code, you would either throw `IllegalArgumentException` (forcing the caller to handle the case) or return an `Optional<Notifier>`. The reflection at the end of this lab asks you about that choice.

### Step 3.2: Run and verify

```bash
java Work.java
```

Output:

```
[EMAIL] Build finished
[SMS] Deploy started
```

If this is what you see, the basic lab is done. Move on to the stretch in Part 4, or skip to the reflection in Part 6.

---

## Part 4: Stretch: Add a `PushNotifier`

This is where the Factory Method pattern earns its keep. You are going to add a third notifier type. Before you do, predict in your notebook:

- How many files will you need to edit?
- How many existing lines of code will you need to change?
- How many new lines of code will you write?

Then do the work and see if you were right.

### Step 4.1: Add the `PushNotifier` class

In `Work.java`, after the `SmsNotifier` class declaration, add:

```java
class PushNotifier implements Notifier {
    public void send(String msg) {
        System.out.println("[PUSH] " + msg);
    }
}
```

Three lines. The class implements the same `Notifier` interface.

### Step 4.2: Extend the factory

Find the `create` method again. Add one more `else if`:

```java
} else if (type.equalsIgnoreCase("push")) {
    return new PushNotifier();
}
```

Two lines (plus the closing brace from the existing `else if`).

### Step 4.3: Use it from `main`

In `main`, after the SMS block, add:

```java
Notifier n3 = NotifierFactory.create("push");
n3.send("System update available");
```

Two lines.

Run:

```bash
java Work.java
```

Output:

```
[EMAIL] Build finished
[SMS] Deploy started
[PUSH] System update available
```

### Step 4.4: Count the cost

Look back at your prediction. The full cost of adding a new notifier type was:

| Where | Lines |
|-------|-------|
| New `PushNotifier` class | 5 (including braces) |
| New `else if` in factory | 2 |
| New call in `main` (the actual *use* of the type) | 2 |
| **Total** | **9** |

And critically: the existing `EmailNotifier` class did not change. The existing `SmsNotifier` class did not change. The existing `Notifier` interface did not change. The existing email and SMS sections of `main` did not change. Only one method in one factory class needed extension.

That is the Open/Closed Principle in practice. The code was *open for extension* (you added a new type) and *closed for modification* (you didn't have to edit the type's siblings or the consumers that don't use the new type).

If you had used the if/else pattern instead of the factory, and your `main` had many places that created notifiers, every one of those places would have needed the new `else if`. The cost would have been *N* edits instead of one.

---

## Part 5: Verify Against the Expected Output

Run the finished program one more time:

```bash
java Work.java
```

Your output should match this exactly:

```
[EMAIL] Build finished
[SMS] Deploy started
[PUSH] System update available
```

### If your output differs

1. **`NullPointerException` on the first line.** The factory still returns `null` for `"email"`. You probably forgot to save the file, or your `if` condition is wrong. Check that you wrote `equalsIgnoreCase("email")` and not `equalsIgnoreCase("Email")` (the literal you pass in matters; if `equalsIgnoreCase` finds `"EMAIL"` on one side and `"Email"` on the other, that still matches, but `"emial"` (typo) on either side does not match `"email"`).

2. **`NullPointerException` on the push line.** Your factory does not have the `else if` for `"push"` yet. Re-read Step 4.2.

3. **Output appears in the wrong order, or duplicated.** Java prints in the exact order of the `System.out.println` calls in `main`. If your output is wrong-ordered, look at the order of the `Notifier n... = ...; n.send(...);` blocks in `main`, not at the factory.

4. **Compile error: "class PushNotifier is public, should be declared in a file named PushNotifier.java".** You added the `public` keyword to `PushNotifier` by mistake. In a single-file source-launcher program, only one class can be `public`, and it must match the file name. Remove the `public` from `PushNotifier`.

5. **Compile error: "cannot find symbol PushNotifier".** You added the `else if` to the factory but did not define the `PushNotifier` class itself. Add the class declaration (Step 4.1).

---

## Part 6: Reflection

Answer in your notebook. These are open-ended; spend at least 15 minutes.

1. **The `null` return.** When the factory is given an unknown type (say, `"telegraph"`), it returns `null`. The caller then crashes with `NullPointerException` on the next line. Is that the right design? Three alternatives:
   - **Throw `IllegalArgumentException`** with a message like "Unknown notifier type: telegraph".
   - **Return `Optional<Notifier>`** so the caller is forced to handle the missing case.
   - **Return a `NoOpNotifier`** that silently swallows the call (the "null object" pattern).
   
   For each of these, write one or two sentences about when it is the best choice and when it is the worst.

2. **The `String` parameter.** The factory's parameter is a `String`. Typos like `"emial"` are not caught until the line `n1.send(...)` blows up at runtime. An alternative is to use an `enum`:
   ```java
   enum NotifierType { EMAIL, SMS, PUSH }
   ```
   The factory then takes `NotifierType` instead of `String`. What are the tradeoffs? When would you prefer the `enum` version? When would you prefer the `String`?

3. **The pattern's cost.** This lab is small. Three notifier types, one factory, one `main`. In a program this small, would you actually bother with the Factory Method pattern, or would the `if/else` in `main` be perfectly readable? Where is the inflection point? (Hint: think about how many *callers* of `new EmailNotifier()` there are in the program. With one caller, a factory is overkill. With ten, a factory is mandatory. With three, opinions vary.)

4. **Beyond strings: a map of constructors.** A common alternative in modern Java looks like this:
   ```java
   private static final Map<String, Supplier<Notifier>> registry = Map.of(
       "email", EmailNotifier::new,
       "sms",   SmsNotifier::new,
       "push",  PushNotifier::new
   );
   
   static Notifier create(String type) {
       Supplier<Notifier> ctor = registry.get(type.toLowerCase());
       return (ctor == null) ? null : ctor.get();
   }
   ```
   Read this carefully. What does it gain compared to the if/else version? What does it lose? Would you use this in your code?

5. **Dependency injection.** In a larger application, you often do not call the factory yourself; you ask a *dependency injection container* (Spring, Guice, Dagger) to give you a `Notifier`, and the container decides which implementation. From what you have seen in this lab, can you guess what the container is doing under the hood? How does it relate to the Factory Method pattern?

6. **What is missing?** This program is a teaching example. Three things you would want before deploying it. Name them. (Hints: configuration, retry logic, errors from the underlying transport.)

---

## Reference: The Factory Method Pattern in One Picture

```
       +----------+        creates        +-----------------+
       |  Client  | --------+--------> ?  |   <interface>   |
       +----------+         |              |    Notifier     |
                            |              +-----------------+
                            v                      ^
                  +-------------------+            |
                  |  NotifierFactory  |            |
                  | + create(type)    |            |  implemented by
                  +-------------------+            |
                            |                      |
                            |  picks one of        |
                            v                      |
            +-----------+   +-----------+   +--------------+
            | EmailNot. |   |  SmsNot.  |   |  PushNot.    |
            +-----------+   +-----------+   +--------------+
```

The Client knows two things: the factory, and the interface. It does not know about the concrete classes. The concrete classes know only the interface. The factory is the only thing in the system that knows *all* the concrete classes.

---

## Reference: The Open/Closed Principle

The principle was first stated by Bertrand Meyer in 1988 in *Object-Oriented Software Construction*. Robert C. Martin restated it in 1996 in the form most people know today:

> Software entities (classes, modules, functions) should be open for extension, but closed for modification.

In practice this means:

- When you need to change a program's behaviour, you should be able to do it by *adding* code, not by *editing* existing code.
- Existing code that is tested, debugged, and in production should not have to be reopened just because you want to add a new variation.

The Factory Method pattern is one of the most direct ways to honour this principle. So are the **Strategy** pattern (passing in different behaviours as objects), **Template Method** (subclassing to vary specific steps), and **Decorator** (wrapping existing objects to add behaviour). Most of the Gang of Four patterns are, at root, different applications of the same Open/Closed instinct.

---

## Reference: When the Factory Method Is the Wrong Tool

The pattern is famous and easy to apply, which means it is often *over*-applied. Some warning signs that you have factory-ed something that did not need it:

1. **There is only one concrete class.** A factory that always returns `EmailNotifier` is just an extra layer of indirection. Use `new EmailNotifier()` directly until a second type appears.

2. **The factory's body is the if/else you tried to avoid.** A factory does not eliminate the if/else; it *centralizes* it. If the centralization buys nothing because the factory is the only place that ever creates these objects anyway, you've added a class for no gain.

3. **The factory's `type` parameter comes from a hard-coded literal in the calling code.** If every caller writes `factory.create("email")` and `email` is the only thing they ever pass, you have not reduced coupling; you have moved the construction one level away from where it is needed, with no benefit.

4. **You need different *instances* configured differently.** This is what dependency injection is for. A factory that always returns a fresh object cannot remember configuration; a DI container can.

The pattern is genuinely useful when (a) the type to create is decided by data (a config file, a user choice, a database row), and (b) more than one place in the codebase needs to make that decision.

---

## Reference: Alternatives to the Factory Method

| Approach | When it shines | When it does not |
|----------|---------------|------------------|
| **if/else or switch in the caller** | Two or three types, one or two callers. | Many types, many callers: every change touches every caller. |
| **Factory method (this lab)** | A handful of types, many callers. The classic OO solution. | When you also need configuration, lifecycle, or scopes. |
| **Map of `Supplier<T>` (modern)** | The set of types is dynamic (loaded from a plugin, registered at startup). | Compile-time type safety is weaker. |
| **Enum with abstract methods** | The set of types is small, fixed, and known at compile time. | Adding a new type requires modifying the enum, which is a different kind of "closed." |
| **Dependency injection** | Large applications. The framework manages object lifecycle. | Tiny scripts; learning curve is real. |
| **Reflection / `Class.forName(name).newInstance()`** | Type name is read from a config file, plugin, or database. | Compile-time safety is gone; tooling cannot help you. |

There is no universal right answer. The Factory Method is the *first* alternative to look at when if/else gets out of hand, but it is not the *only* alternative.

---

## Troubleshooting

**`error: can't find main(String[]) method in class: Notifier`.**
You ran `java Starter.java` but the `Notifier` interface is declared at the top of the file. The Java 21 source-launcher uses the *first top-level type* in the file as the launch class. Make sure your `public class Starter` (or `public class Work`) appears *before* the `interface Notifier` declaration in the file.

**`error: class Work is public, should be declared in a file named Work.java`.**
You renamed the public class but did not rename the file. The public class name and the file name must match in Java. Either rename the file to match the class, or rename the class to match the file.

**`NullPointerException: Cannot invoke "Notifier.send(String)"`.**
The factory returned `null`. Either you have not implemented TODO(1) yet, or the string you passed (in `main`) does not match any of the strings the factory recognizes. Add a `System.out.println("type=" + type)` at the top of `create` to see what the factory is being asked for.

**The output appears but the order is wrong, or some lines repeat.**
Java prints in the exact order of `System.out.println` calls. Re-read `main` line by line; the order of output reflects the order of calls there, not anything inside the factory.

**Compile error: "duplicate class: PushNotifier"** (if you have other files in the directory).
Java's source-launcher mode compiles all top-level types in the file *plus* anything visible on the classpath. If you have an old `PushNotifier.class` left over from a previous attempt, delete it: `rm *.class`.

---

## Further Reading

- **Design Patterns: Elements of Reusable Object-Oriented Software** (Gamma, Helm, Johnson, Vlissides, 1994). The original Gang of Four book. The Factory Method chapter is short and worth reading once.
- **Head First Design Patterns, 2nd edition** (Freeman et al.). Friendlier introduction to the same patterns. The chapter on Factory Method and Abstract Factory is the standard recommendation for a first read.
- **Effective Java, 3rd edition** (Joshua Bloch). Item 1: "Consider static factory methods instead of constructors." A different angle on factories: not "select among types" but "give the construction a meaningful name."
- **Refactoring Guru: Factory Method** at <https://refactoring.guru/design-patterns/factory-method>. Free online walkthrough with diagrams, code in several languages, and a discussion of the pattern's pros and cons.
- **Robert C. Martin, "The Open-Closed Principle"** (1996 paper, later in *Agile Software Development*). The article that popularized the OCP name and gave it the form most developers know today.
