# Lab 6-3: Refactoring to the State Pattern with GitHub Copilot


## Overview

One of the most common signs of a class that wants to be redesigned is a method full of conditionals that switches on an internal "mode" field. Whenever you see code like `if (state == NORMAL) { ... } else if (state == OVERDRAWN) { ... }` repeated across several methods of the same class, you are looking at a candidate for the **State pattern**. The pattern was catalogued in the 1994 Gang of Four book and remains one of the most useful tools for taming "mode-switching" classes.

In this lab you will start with a Java `BankAccount` class that works correctly but uses internal `int` constants and `if/else` chains to switch between two modes: **normal** (deposits and withdrawals both allowed) and **overdrawn** (no withdrawal allowed; deposits accepted, and the account returns to normal once the balance is non-negative again). You will use GitHub Copilot to first understand why the conditional design is fragile, then drive a three-step refactor that produces a `Transaction` interface and two state classes, `Normal` and `Overdrawn`, that each implement the rules for their own state.

You will work mostly in **Agent mode** because you are making real code changes, but you will switch to **Ask mode** for the explanation and design questions where you want analysis without edits.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Recognize the "conditional smell" that signals the State pattern is appropriate.
2. Use Copilot in Ask mode to identify the design problems in a mode-switching class.
3. Use Copilot in Agent mode to extract an interface and two state implementations from a monolithic class.
4. Verify that a refactor preserves behaviour by exercising the application before and after, comparing output line by line.
5. Articulate the tradeoffs of the State pattern: the new files, the back-reference from state to context, and the placement of transition logic.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder...** (or **File > New Window** first, then **Open Folder...** if you already have another project open).
3. In the dialog, create a new folder called `state-lab` in your usual workspace location, then open it.
4. When VS Code asks "Do you trust the authors of the files in this folder?", click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `STATE-LAB` at the top.

> This lab assumes the **Extension Pack for Java** (Microsoft) is installed in VS Code. It provides the "Run" and "Debug" CodeLens links that appear above `main` methods, the in-editor problems view, and the Debug Console pane. If you do not see "Run | Debug" links above the `main` method in Step 1.4, open the Extensions view (`Ctrl+Shift+X`), search for "Extension Pack for Java" by Microsoft, and install it. Reload VS Code when prompted.

### Step 1.2: Create the starter file

Create a new file called `BankAccount.java` and paste the following content into it exactly as shown. Do not modify it yet. Save the file (`Ctrl+S`).

```java
public class BankAccount {

    // States represented as constants
    private static final int NORMAL = 0;
    private static final int OVERDRAWN = 1;

    private double balance;
    private int state;

    public BankAccount(double openingBalance) {
        this.balance = openingBalance;
        this.state = (openingBalance < 0) ? OVERDRAWN : NORMAL;
    }

    public void deposit(double amount) {
        if (amount <= 0) {
            System.out.println("Deposit refused: amount must be positive.");
            return;
        }
        if (state == NORMAL) {
            balance += amount;
            System.out.println("Deposit of " + amount + " accepted. Balance: " + balance);
        } else if (state == OVERDRAWN) {
            balance += amount;
            System.out.println("Deposit of " + amount + " accepted while overdrawn. Balance: " + balance);
            if (balance >= 0) {
                state = NORMAL;
                System.out.println("Account is back to NORMAL.");
            }
        }
    }

    public void withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("Withdrawal refused: amount must be positive.");
            return;
        }
        if (state == NORMAL) {
            balance -= amount;
            System.out.println("Withdrawal of " + amount + " accepted. Balance: " + balance);
            if (balance < 0) {
                state = OVERDRAWN;
                System.out.println("Account is now OVERDRAWN.");
            }
        } else if (state == OVERDRAWN) {
            System.out.println("Withdrawal of " + amount + " refused: account is overdrawn.");
        }
    }

    public double getBalance() {
        return balance;
    }

    public static void main(String[] args) {
        BankAccount acct = new BankAccount(100.0);
        System.out.println("--- Account created with opening balance " + acct.getBalance() + " ---");

        acct.deposit(50);
        acct.withdraw(30);
        acct.withdraw(200);   // pushes overdrawn
        acct.withdraw(10);    // refused
        acct.deposit(40);     // still overdrawn
        acct.deposit(100);    // back to normal
        acct.withdraw(20);    // accepted again

        System.out.println("--- Final balance: " + acct.getBalance() + " ---");
    }
}
```

### Step 1.3: Confirm Copilot is ready

1. Open the Chat view (`Ctrl+Alt+I`).
2. Confirm the model picker reads **Claude Sonnet 4.6**.
3. Switch the chat mode dropdown to **Ask**. You will start in Ask mode and switch to Agent mode in Part 3.

### Step 1.4: Run the starter from the editor

Before changing anything, confirm that the conditional version actually works. The whole point of refactoring is to preserve behaviour, so you need a baseline you can compare against.

1. With `BankAccount.java` open in the editor, look just above the `public static void main(String[] args)` line. The Java extension renders two clickable text links there: **Run | Debug**.
2. Click **Run**.
3. The **Debug Console** pane opens at the bottom of the window (under the "Debug Console" tab; sibling tabs include "Problems", "Output", and "Terminal"). VS Code compiles the file and runs `main()`. After a moment you should see in the Terminal:

```
--- Account created with opening balance 100.0 ---
Deposit of 50.0 accepted. Balance: 150.0
Withdrawal of 30.0 accepted. Balance: 120.0
Withdrawal of 200.0 accepted. Balance: -80.0
Account is now OVERDRAWN.
Withdrawal of 10.0 refused: account is overdrawn.
Deposit of 40.0 accepted while overdrawn. Balance: -40.0
Deposit of 100.0 accepted while overdrawn. Balance: 60.0
Account is back to NORMAL.
Withdrawal of 20.0 accepted. Balance: 40.0
--- Final balance: 40.0 ---
```

Read this trace carefully. The test data is deliberately chosen to exercise both state transitions:

- After the third operation (`withdraw 200`), the account drops below zero and switches **NORMAL to OVERDRAWN**.
- The next withdrawal (`withdraw 10`) is **refused** because of the state change.
- A small deposit (`deposit 40`) is accepted but does not lift the balance back above zero, so the state stays OVERDRAWN.
- The next deposit (`deposit 100`) does lift it back to positive, so the state switches **OVERDRAWN to NORMAL**.
- The final withdrawal is accepted again, confirming the state has indeed flipped back.

**Save this output as a baseline.** You will compare against it after every refactor step.

1. Select all the program output: click anywhere in the output wind, then press `Ctrl+A` to select, `Ctrl+C` to copy. (Some VS Code themes do not visually indicate the selection; the copy still works.)
2. In the Explorer panel, click the **New File** icon next to the folder name (or use **File > New File**) and name the new file `baseline.txt`.
3. Paste (`Ctrl+V`) the copied output into `baseline.txt` and save (`Ctrl+S`).

The refactored version is supposed to produce **exactly the same output** in `baseline.txt`. If at any point in Part 3 the new output diverges, you will see the difference immediately by comparing the new output against `baseline.txt`.

> **The Run-and-Compare procedure.** You will use this procedure after every refactor step in Part 3. It uses VS Code's built-in "Compare Selected" feature to do what a `diff` command would do at a terminal.
>
> 1. Make sure `BankAccount.java` is saved (look for the white dot next to the tab name; if you see one, press `Ctrl+S`).
> 2. Click **Run** above the `main` method in `BankAccount.java`.
> 3. In the Debug Console, `Ctrl+A` then `Ctrl+C` to copy all output.
> 4. Create a new file named `stepN.txt` (for the current step number) in the Explorer panel.
> 5. Paste the output into the new file and save.
> 6. In the Explorer, click `baseline.txt` to select it. Then `Ctrl+click` (Windows/Linux) or `Cmd+click` (macOS) on `stepN.txt` so both files are selected.
> 7. Right-click either of the selected files and choose **Compare Selected**.
>
> VS Code opens a side-by-side diff view. If the panels are identical (no red or green highlighting anywhere), the refactor preserved behaviour. If there are highlighted differences, the refactor changed behaviour and you need to investigate before continuing.

### Step 1.5: Create a lab notebook file

Create a new file `findings.md` in the workspace. You will record your analyses and Copilot's responses here as you go. Start it with:

```markdown
# State Pattern Refactor Notebook

## Part 2: Diagnosis

## Part 3: Refactoring

## Part 4: Design questions

## Part 5: Verification
```

Save it.

---

## Part 2: Diagnose the Problems (Ask Mode)

Before you change a single line of code, you need to understand precisely what is wrong with it. Like the previous Copilot lab, the goal of Part 2 is to get Copilot to articulate the diagnosis in its own words so you (and Copilot) have a shared understanding of the target shape.

Make sure `BankAccount.java` is the active editor tab and you are in **Ask** mode.

### Question 2.1: First-pass critique

In the Chat view, type:

```
#file:BankAccount.java This class works correctly but the design has
known weaknesses. List every design problem you can see, name the
principle being violated for each, and explain in one sentence why
each one would matter as the codebase grows.
```

**What to look for in the response:**

- **Type code instead of polymorphism.** The `state` field is an `int` with two values represented as `int` constants. The `deposit` and `withdraw` methods both have to `if/else` on this field. Adding a third state (say, `FROZEN`) means editing every method.
- **Same conditional duplicated across methods.** Both `deposit` and `withdraw` switch on `state` in the same way. The compiler cannot warn you if one method handles a state that another forgets.
- **Mixed responsibilities in one class.** `BankAccount` is doing the bookkeeping (tracking the balance), the rules of each state (what deposit and withdraw do in each state), and the transitions (when to switch). These are three things, not one.
- **Implicit state machine, no explicit transitions.** The state transitions happen as side effects of `deposit` and `withdraw`. A reader has to scan the whole class to find every place where `state = OVERDRAWN` or `state = NORMAL` appears, then reconstruct the state diagram in their head.
- **No type-safety on state values.** `state = 7` would compile and run. Only the convention of using `NORMAL` and `OVERDRAWN` constants protects against invalid states.

Copy the response into your notebook under Part 2.

### Question 2.2: Sketch the target architecture

```
The classic refactor for code like this is the State pattern. Sketch
what the State pattern version of this BankAccount would look like.
Name each class and interface, list its responsibilities in one
sentence, and say what each one depends on.

In particular, where should the rules for each state live? Where should
the transitions (deciding when to switch states) live? Why?
```

**What to look for in the response:**

- A **`Transaction` interface** (or `AccountState`, depending on what Copilot proposes) with the three operations: `deposit`, `withdraw`, `getBalance`.
- A **`Normal` class** that implements `Transaction`. Its `deposit` and `withdraw` methods know the rules for the normal state.
- An **`Overdrawn` class** that implements `Transaction`. Its `deposit` and `withdraw` methods know the rules for the overdrawn state.
- A **`BankAccount` class (the context)** that holds a reference to the current state and delegates calls to it. It also owns the shared data (the balance).
- **Transition logic lives inside the state classes**, not in `BankAccount`. The `Normal.withdraw` method is the place that knows "if this withdrawal makes the balance negative, switch to Overdrawn." The `Overdrawn.deposit` method is the place that knows "if this deposit brings the balance back to non-negative, switch to Normal."
- **State classes hold a reference back to the `BankAccount`** so they can ask the context to swap them out for a different state. This is a deliberate circular reference and is the standard form of the State pattern.

> **A note on naming.** The user-facing lab specifies the interface should be called `Transaction`. That is unusual: many State pattern examples use `AccountState` or just `State`. Copilot may suggest either of those names; gently ask it to use `Transaction` per the spec. Naming the interface after what it *does* (transactions) rather than after what it *is* (a state) is a defensible choice; it just is not the textbook default.

### Question 2.3: Why is it worth it?

```
Refactoring takes time. Without writing any code yet, list three concrete
benefits the State pattern version would have over the current
conditional version, and one concrete cost.

For the benefits, give scenarios where the difference is visible: a new
feature, a bug, a test, something I would actually do as a developer.
```

**What to look for in the response:**

- **Benefit 1 (adding a new state is local):** Suppose you wanted to add a `FROZEN` state where neither deposits nor withdrawals are allowed. With the conditional version, you have to edit both `deposit` and `withdraw` to add a new `else if` branch. Forget one and you have a silent bug. With the State pattern, you write one new file (`Frozen.java`) that implements `Transaction` and the compiler tells you every method you need.
- **Benefit 2 (states can be tested in isolation):** You can write a unit test for `Normal.withdraw(50)` directly without first putting a `BankAccount` into the right state by sending it a sequence of operations. Each state class becomes independently testable.
- **Benefit 3 (the state diagram is the file list):** The set of states is the set of files implementing `Transaction`. Anyone reading the project can see at a glance what modes the account can be in.
- **Cost:** Three or four files instead of one, with a small amount of indirection. For a class with two states and two operations, this is arguably overkill. The pattern earns its keep when there are more states (three, four, five) or more operations (transfer, freeze, close, mature, etc).

---

## Part 3: Drive the Refactor (Agent Mode)

You now know what you want. Time to make it happen.

Switch the chat mode dropdown to **Agent**. Each edit will appear as a Keep / Undo diff that you review before accepting.

You will execute the refactor in three steps. After each step, run the program to confirm it still compiles and behaves correctly. **Do not skip the run step.** A refactor that changes the output is not a refactor; it is a bug.

### Step 3.1: Extract the `Transaction` interface

In Agent mode, type:

```
#file:BankAccount.java I want to refactor this in three steps to use the
State pattern. Step 1 of 3:

1. Create a new interface called Transaction (in BankAccount.java, as a
   non-public top-level type) with these three methods:
     void deposit(double amount);
     void withdraw(double amount);
     double getBalance();

The interface name MUST be Transaction, not State or AccountState.

Do NOT yet create the Normal or Overdrawn implementations. Do NOT yet
change BankAccount itself. The class should still compile and behave
identically. The Transaction interface will not yet be used; it will
just be present in the file, ready for step 2.

Show me the diff.
```

Press Enter. Copilot will propose adding the interface to the file.

**Review carefully:**
- The interface should be a non-public top-level type (so it can live in the same file as `BankAccount`).
- The three method signatures must match exactly.
- `BankAccount` itself should not change.

**Run to confirm nothing has changed:**

Apply the **Run-and-Compare procedure** (see the boxed note in Step 1.4): click **Run**, copy the Debug Console output into a new file `step1.txt`, then `Ctrl+click` to select both `baseline.txt` and `step1.txt` in the Explorer and choose **Compare Selected**.

The diff view should show **no highlighted differences** (the two panels should look identical). If it does not, undo the changes and try again.

> **Why is this step first?** Even though the interface is not yet used, adding it now makes step 2 mechanical: the state classes have a clear contract to implement. If you started by creating the state classes first, you would either be designing the interface implicitly (by what the classes happen to do) or doing two things in one step.

### Step 3.2: Create the `Normal` and `Overdrawn` state classes

```
Step 2 of 3: Create the two state classes.

1. In BankAccount.java, add a non-public class Normal that implements
   Transaction. Its constructor takes a BankAccount parameter (the
   context) and stores it as a private final field. Its methods should
   implement the rules for the NORMAL state, as currently expressed in
   the if (state == NORMAL) branches of BankAccount.

2. Similarly, add a non-public class Overdrawn that implements
   Transaction, taking a BankAccount in its constructor, implementing
   the rules from the if (state == OVERDRAWN) branches.

3. The state classes need to be able to swap themselves out. Add a
   package-private method setState(Transaction newState) to BankAccount
   that simply assigns the new state to a state field. (This method
   will be wired up in step 3; for now BankAccount has no state field
   to assign to. Leave the body as a TODO comment for now, or have it
   throw UnsupportedOperationException, your choice.)

4. To access the balance from the state classes, give BankAccount a
   package-private double field called `balance` (you may need to
   rename or relax the visibility of the existing private field). The
   state classes will read and write to this field directly.

5. Do NOT yet change deposit, withdraw, or getBalance in BankAccount.
   The existing conditional code should still be running the show. The
   Normal and Overdrawn classes are written but unused. The program
   should still produce identical output.

Show diffs and run the program to confirm the output is unchanged.
```

Press Enter. Copilot will propose:

- A new class `Normal` implementing `Transaction` with three methods.
- A new class `Overdrawn` implementing `Transaction` with three methods.
- A new `setState` method on `BankAccount` (still unused).
- Visibility change for the `balance` field.

Review each diff carefully. Pay particular attention to:

- **Does each state class transition correctly?** `Normal.withdraw` should call `account.setState(new Overdrawn(account))` when the new balance is negative. `Overdrawn.deposit` should call `account.setState(new Normal(account))` when the new balance is non-negative. If these transitions are missing or wrong, the pattern will not work in step 3.
- **Does each state class print the same messages as the original?** "Deposit of X accepted." / "Withdrawal of X accepted." / "Account is now OVERDRAWN." / "Account is back to NORMAL." / "Withdrawal of X refused: account is overdrawn." / "Deposit of X accepted while overdrawn." The lab will verify behavioural equivalence at the end, so the print statements need to match. If Copilot has rewritten any of them ("Insufficient funds" instead of "refused"; "Account is overdrawn" instead of "is now OVERDRAWN"; etc.), undo and retry, or fix them by hand.

**Run to confirm nothing has changed yet:**

Apply the **Run-and-Compare procedure** with a new file `step2.txt`. The diff view should show **no highlighted differences**. The state classes exist but are not yet called, so the program should still behave exactly as before.

### Step 3.3: Wire `BankAccount` to delegate to the state object

```
Step 3 of 3: Replace the conditional code in BankAccount with delegation
to the state object.

1. Add a Transaction state field to BankAccount.
2. In the BankAccount constructor, initialize state to either
   new Normal(this) or new Overdrawn(this) based on the opening balance,
   matching the existing behaviour (overdrawn if negative, normal
   otherwise).
3. Replace the body of deposit(double amount) with input validation
   (amount > 0 check) followed by a single call: state.deposit(amount).
4. Replace the body of withdraw(double amount) similarly.
5. Replace the body of getBalance() with: return state.getBalance().
   (Or just: return balance. Either is fine since the balance field is
   shared. But going through the state is the strictly more
   pattern-faithful version.)
6. Remove the now-unused NORMAL and OVERDRAWN constants and the `state`
   int field (which has been replaced by the state object field of the
   same name; if naming conflicts, rename the int constants away).
7. Complete the setState method body to actually assign the new state.

After this step, BankAccount should be substantially smaller. Show
diffs and then run the program to confirm the output is unchanged.
```

Press Enter and review the diffs.

**Apply the Run-and-Compare procedure** with a new file `step3.txt`. The diff view should show **no highlighted differences**. If it does, the refactor has changed behaviour. The most common causes are:

- A print statement was reworded by Copilot.
- The transition condition is slightly different (`>` instead of `>=`, or vice versa).
- The order of `setState` and `println` was swapped, changing the order of output lines.

Look at the highlighted differences in the diff view and fix the offending code before you continue.

The refactor is complete. You should now have:

- A `BankAccount` class with three short methods that delegate to the state object.
- A `Transaction` interface.
- A `Normal` class.
- An `Overdrawn` class.

All in `BankAccount.java`, or split across separate files if you prefer (Copilot will offer the option).

---

## Part 4: Design Questions (Ask Mode)

Switch back to **Ask** mode. The refactor is done; now you reflect on what it produced.

### Question 4.1: Where does the transition logic live?

```
#file:BankAccount.java

In the refactored version, which class decides when the account
transitions from Normal to Overdrawn? Which class decides when it
transitions back? Are these decisions in the right place? What would
the alternatives be, and what would they cost?
```

**What to look for in the response:**

- **`Normal.withdraw` decides** when to switch to Overdrawn.
- **`Overdrawn.deposit` decides** when to switch back to Normal.
- **This is the right place** because each state knows the conditions under which its own operations can drive the account out of that state. Putting the transitions in `BankAccount` would mean `BankAccount` has to inspect the balance after every operation and choose a state, which is *almost* the same logic, but split across two places.
- **Alternative 1:** A separate state-machine class that watches transitions externally. This is heavier; it's what you would do if transitions could be triggered by many different events (time passing, external signals) rather than just by the operations themselves.
- **Alternative 2:** A finite-state machine library (Spring Statemachine, Squirrel). For a two-state machine this is huge overkill; for a ten-state workflow with guards and side effects, it pays for itself.

### Question 4.2: The back-reference from state to context

```
#file:BankAccount.java

Each state class (Normal, Overdrawn) holds a reference back to the
BankAccount it belongs to. This is a circular reference: the account
holds the state, the state holds the account. Why is this design
considered acceptable here? Are there alternatives that avoid the
circularity?
```

**What to look for in the response:**

- The circularity is acceptable because both objects have the same lifetime: a state object only makes sense for a particular account, and an account is never without a state. There is no risk of "an Overdrawn from another account" appearing where it should not.
- **Alternative 1: pass the context on each method call.** Instead of `Normal(account)`, have `Normal.deposit(account, amount)`. This makes `Normal` stateless and shareable as a singleton. It also means the interface signature gets longer. Some textbooks prefer this for purity; most production code prefers the back-reference for ergonomics.
- **Alternative 2: pass only the data the state needs (not the whole account).** `Normal.deposit(balanceRef, amount, transitionCallback)`. This is the most decoupled design but it requires more glue at the call site and obscures intent.
- The back-reference is the standard form in Gamma et al's original presentation of the pattern.

### Question 4.3: What if Copilot suggested singletons?

```
Some implementations of the State pattern make Normal and Overdrawn
singletons (one instance each, shared across all accounts) because the
state classes themselves have no per-account data. In our version,
they do have per-account data: the back-reference to the BankAccount.

Compare the two approaches. Which one would you prefer for this
application? What would each one look like if you wanted to add a
third state, Frozen, that has its own behaviour?
```

**What to look for in the response:**

- **Singleton approach:** `Normal.INSTANCE` and `Overdrawn.INSTANCE`. State methods take the account as a parameter. Smaller memory footprint (one instance shared across all accounts). Cleaner if states have no per-account data.
- **Per-account instance approach (what this lab built):** Each account has its own `Normal` or `Overdrawn` instance with a back-reference. Slightly more memory (one extra object per account). Methods are simpler because they can read and write the back-referenced fields directly.
- For our application, **per-account instances are easier to read and write**. The methods don't need to thread the account through every signature.
- Adding `Frozen` is the same amount of work either way: one new file, three methods. The choice between singleton and per-instance is orthogonal to the choice of whether to use the State pattern at all.

### Question 4.4: Where would you add a feature?

```
Suppose I want to add three features. For each one, tell me exactly
which files (or classes) I would need to modify, and which would not
change. Explain why.

Feature A: a transfer(BankAccount other, double amount) method that
  moves money from this account to another.
Feature B: a third state, Frozen, that rejects both deposits and
  withdrawals. Initially the account is created normally and can only
  enter the Frozen state via a freeze() method.
Feature C: an audit log that records every transition with a timestamp.
```

**What to look for in the response:**

- **Feature A (transfer):** Add a `transfer` method to `BankAccount`. It will call `withdraw` on this account and `deposit` on the other, delegating to the state objects. **No changes** to `Normal`, `Overdrawn`, or `Transaction`. The pattern's payoff: the new operation is built on top of the existing state-aware operations.
- **Feature B (Frozen state):** Add a new `Frozen` class implementing `Transaction`. Add a `freeze()` method to `BankAccount` that calls `setState(new Frozen(this))`. **No changes** to `Normal` or `Overdrawn` (unless you want one of them to be able to enter Frozen via some other trigger). The compiler will *not* warn you if `Frozen` doesn't implement all three methods, because of course it must, but the moment you add a fourth method to `Transaction`, the compiler will tell you about all three state classes that need to implement it. This is the substitutability payoff.
- **Feature C (audit log):** Either add logging in each state class's transition site (small spread but very localized), or change `setState` in `BankAccount` to log on every transition (one place, one log call). The second is usually better because it captures *every* transition uniformly without each state class having to remember to log.

The contrast with the original conditional `BankAccount` is sharp: features A, B, and C in the conditional version would each have required surgery on the same `deposit`/`withdraw`/whatever methods.

---

## Part 5: Verify Your Understanding

You have built a model of how the refactored application is organized. Test that model.

### Step 5.1: Predict before you run

Without running the code, predict what the program will print for this constructor call followed by these operations:

```java
BankAccount acct = new BankAccount(-10.0);  // starts overdrawn!
acct.withdraw(5);
acct.deposit(5);
acct.deposit(20);
acct.withdraw(15);
```

Write your prediction in your notebook. Be specific: which lines say "accepted," which say "refused," and where do the state-transition messages appear?

### Step 5.2: Run it

Modify the `main` method in `BankAccount.java` to use these operations, save the file, and click **Run** above `main`. The output appears in the Debug Console.

Compare the output to your prediction. If anything is different, do not assume the program is wrong. Re-read the relevant state class and figure out what you got wrong about the rules.

### Step 5.3: Behavioural equivalence with the original

Revert `main` back to the original test sequence (or copy the test from the starter code) and save the file. Apply the **Run-and-Compare procedure** one more time, saving the new output into a file called `final.txt` and comparing it to `baseline.txt` via **Compare Selected**.

The diff view should show **no highlighted differences**. If it does, **the refactor has introduced a behavioural difference**. Use Copilot in Ask mode to find it. Paste the highlighted-differing lines from the diff view into the chat:

```
The original conditional version produces this output: [paste from baseline.txt].
The refactored State pattern version produces this output: [paste from final.txt].
The two should be identical but they differ on these lines: [paste the differing lines].
What is the most likely cause of each difference, and how would I fix it?
```

### Step 5.4: A small extension

Now that the architecture is in place, try adding **Feature B from Question 4.4 (a `Frozen` state)**. Use Copilot in Agent mode and a single well-formed prompt:

```
Add a Frozen state to BankAccount.

1. Create a new non-public class Frozen that implements Transaction.
   - Frozen.deposit refuses with: "Deposit refused: account is frozen."
   - Frozen.withdraw refuses with: "Withdrawal refused: account is frozen."
   - Frozen.getBalance returns the current balance (frozen accounts can
     still be queried).
   - Frozen has no automatic transitions back to other states.
2. Add a public void freeze() method to BankAccount that transitions
   the account to the Frozen state.
3. Add a public void unfreeze() method to BankAccount that transitions
   the account back to Normal (or to Overdrawn if balance < 0).
4. Update main to test the freeze/unfreeze flow at the end of the
   existing test sequence. Show me what the new expected output looks
   like.

Do NOT change Normal, Overdrawn, the Transaction interface, or the
existing deposit/withdraw methods on BankAccount. The new feature
should be additive only.

Show diffs.
```

Notice that this change is purely additive: the existing state classes do not change, the existing methods do not change, the interface does not change. **This is what the State pattern buys you.**

---

## Part 6: Reflection

Answer the following in your lab notebook:

1. **Refactoring vs rewriting.** This lab refactored the original code in three small steps, running the program after each step to confirm identical output. You could instead have read the original once and written the State pattern version from scratch. What did the incremental approach gain you? What did it cost? When would you choose one over the other?

2. **What did you let Copilot decide?** Across the three refactor steps, what choices were yours and what did Copilot fill in? Did you specify that state classes should hold a back-reference, or did Copilot suggest it? Did you specify per-account state instances or singletons? Does it matter for the outcome?

3. **The role of the baseline comparison.** Each refactor step ended with a Compare Selected diff against the saved baseline output. Why did the lab insist on this, even when the change seemed safe? What does the diff catch that a code review or Copilot diff review would not?

4. **The output format.** Both versions print messages like "Deposit of 50.0 accepted." Some teams would consider those debug logs and remove them in production, returning a status object instead. How would you refactor the print statements out of the state classes without losing the ability to debug? (Hint: dependency injection, listeners, events.)

5. **Where the pattern ends.** The State pattern works well when transitions are driven by the operations themselves (deposit triggers Normal-from-Overdrawn). It works less well when transitions are driven by *time* (an account auto-freezes after 90 days of inactivity) or by *external events* (a fraud alert from elsewhere in the system). What pattern would you reach for in those cases? (Hint: look up "event sourcing" or "Spring Statemachine" or "AWS Step Functions.")

6. **When to stop.** This lab refactored a two-state, two-operation class into the State pattern. Was that worth it? At what point would you have decided "the conditional version is fine, leave it alone"? Where do you draw the line for a real project?

---

## Reference: The State Pattern in One Picture

```
                +----------------+
                |  BankAccount   |    <-- the Context
                |  (the context) |
                |                |
                |  balance       |
                |  state ---------+----+
                |                |    |
                |  deposit()     |    |  delegates to state.deposit()
                |  withdraw()    |    |
                |  getBalance()  |    |
                |  setState()    |    |
                +----------------+    |
                                      v
                          +-----------------------+
                          |  <interface>          |
                          |  Transaction          |
                          +-----------------------+
                          |  deposit(amount)      |
                          |  withdraw(amount)     |
                          |  getBalance()         |
                          +-----------------------+
                              ^             ^
                              |             |
                       +-----------+   +------------+
                       |  Normal   |   |  Overdrawn |
                       +-----------+   +------------+
                       | account-+ |   | account--+ |
                       +-----------+   +------------+
                              |              |
                              +------+-------+
                                     |
                              back-reference
                              to the context
```

The context holds the state. The state holds the context. Operations delegate from context to state. State transitions happen inside state methods, which call `context.setState(...)` to swap themselves out for a different state object.

---

## Reference: Conditional Smell to State Pattern Checklist

The State pattern is the right tool when the following are all true:

| Sign | Meaning |
|------|---------|
| Multiple methods of one class have the same `if/else` (or `switch`) on a "mode" field. | Each branch is the implementation of one state. The branches are tangled together in a single method instead of organized by state. |
| Adding a new mode requires touching every method. | The class is mode-oblivious; modes are encoded as data, not types. |
| The transitions between modes happen as side effects of the operations themselves. | A state-driven system. (If transitions are driven by external events, consider a state-machine library instead.) |
| The state is mutually exclusive: at any moment, exactly one mode is in effect. | Classic State pattern fits. (If multiple modes can be active at once, consider Strategy or a combination of patterns.) |
| Each mode has a small, focused set of rules. | Each state class will be small and readable. (If a state class is hundreds of lines, you have more than one state hidden inside.) |

If any of these is *not* true, reach for a different tool. State is one of several patterns that handle "things that vary"; Strategy, Visitor, and the various FSM libraries each cover different shapes of variation.

---

## Reference: Useful Prompt Patterns for Pattern-Based Refactoring

| Pattern | Example wording | When to use |
|---------|-----------------|-------------|
| **Name the pattern explicitly** | "Refactor this to use the State pattern as described by the Gang of Four book." | Copilot has been trained on a lot of pattern literature; using the name unlocks the right idiom. |
| **Specify identifier names** | "The interface MUST be called Transaction, not State." | Copilot has strong defaults (`State`, `AccountState`). Override them up front. |
| **Specify the file layout** | "Put everything in one file as non-public top-level types." | Otherwise Copilot may scatter classes across files unprompted. |
| **Save the baseline output and compare** | (Not a prompt, a habit.) Save the program's output as `baseline.txt`, then run, copy, and **Compare Selected** after every step. | Catches behaviour drift instantly, before it compounds. |
| **One step at a time** | "Step N of M: do exactly this. Do NOT do anything from later steps." | The single most important prompt pattern for refactoring. Big-bang refactors fail. |
| **Constrain to additive changes** | "Do NOT change classes X, Y, Z. The new feature should be additive only." | Tests whether the architecture really does isolate the change. If Copilot insists on touching X, Y, or Z, the architecture is not done. |

---

## Troubleshooting

**Copilot named the interface `State` instead of `Transaction`.**
Undo the diff and re-send the prompt with stronger wording: "The interface MUST be called Transaction. Not State, not AccountState. Use the exact word Transaction." Copilot's training data is heavily biased toward the textbook name; you may have to insist twice.

**Copilot made `Normal` and `Overdrawn` singletons instead of per-account instances.**
Both designs work for this lab. If you want the per-account version (which is what the lab assumes), undo the diffs and add to your prompt: "Each state class should take a BankAccount parameter in its constructor and store it as a private final field. Do NOT make these classes singletons; each BankAccount should have its own Normal and Overdrawn instances."

**Red error underlines appear after step 2 because `setState` is called but does not exist yet.**
Copilot may try to call `setState` from inside `Normal.withdraw` or `Overdrawn.deposit` before you have added the method to `BankAccount`. Hover over the underlined call to confirm the error message, then check the **Problems** pane (`Ctrl+Shift+M`) for a complete list. The fix is in step 2's instructions: add the stub `setState` method to `BankAccount` first (even with a TODO body), then write the state classes. Or, switch the order: do step 2's BankAccount changes first, then the state classes.

**The code compiles cleanly but the output differs from the baseline.**
The single most common cause is a reworded print message. In the Compare Selected diff view, look at the highlighted lines: one side shows the original wording, the other shows what Copilot generated. Either rewrite the state class's print statement to match the original, or update `baseline.txt` if you genuinely intend the new wording.

**The code compiles cleanly, the output matches, but the program enters an infinite loop or stack overflow.**
A state method is calling itself recursively (e.g., `Normal.deposit` calls `account.deposit(amount)` which delegates back to `Normal.deposit`). The state methods should manipulate `account.balance` directly, not call back through the context's deposit/withdraw methods.

**Copilot put each class in its own file even though I asked for a single file.**
Either accept the multi-file layout (it is arguably cleaner for production code, since each public type would normally be in its own file anyway) or reject the diffs and re-send the prompt: "Put all classes in BankAccount.java as non-public top-level types. Do NOT create separate files."

**You ended up with a circular import.**
For a single-file refactor like this one, circular imports are not possible (everything is in one file). If you split across files and hit one, look at the dependency: state classes should import `Transaction` and reference `BankAccount` as a constructor parameter; `BankAccount` should import `Transaction` and instantiate the state classes. There is no need for state classes to be in a separate package; if you put them in one, the import direction must run state → context, not the reverse.

---

## Further Reading

- *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides), 1994. The original State pattern is chapter 5.8. A short, dense chapter.
- *Refactoring* (Martin Fowler), 2nd edition. Chapter 11 covers "Replace Type Code with State/Strategy," which is exactly the refactoring in this lab.
- *Head First Design Patterns* (Freeman et al), 2nd edition. The State pattern chapter uses a vending machine, which is the other classic example.
- *Refactoring Guru: State Pattern*: <https://refactoring.guru/design-patterns/state>. Free online walkthrough with diagrams and code in several languages.
- GitHub Copilot documentation on Agent mode: <https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode>
- *Domain Modeling Made Functional* (Scott Wlaschin). Chapter 6 covers state machines in a functional setting, which is useful for thinking about the difference between "data with mode" and "type with case."
