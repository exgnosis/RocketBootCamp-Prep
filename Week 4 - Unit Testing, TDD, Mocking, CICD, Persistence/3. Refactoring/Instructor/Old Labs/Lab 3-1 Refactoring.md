# Lab 4-1: Refactoring Basics

This lab walks you through a simple refactoring to a design patterns

## Part 1: Initial application

- This is a rather simple example, but it illustrates the idea behind refactoring to a pattern.
- Initially we start with a `calc` package
- The idea is that there are a number of computations that are being developed over a period of time.
- The example we are using is just some arithmetic operations
  - But in real life, these may represent very complex calculations
  - Such as different statistical tools or physics calculations
  - The operation is in its own class because there may be a number of supporting sub calculations or intermediate data structures that have to be used

- Each calculation is represented by single public class

```java
package calc;

public class Adder {
    public int add(int a, int b) {
        return a + b;
    }
}


package calc;

public class Multiplier {
    public int multiply(int a, int b) {
        return a * b;
    }
}


package calc;

public class Divider {
    // integer division for simplicity; caller is responsible for zero-check
    public int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("b must not be zero");
        return a / b;
    }
}
```

- And a driver to test the code, this is not in the `calc` package

```java
import calc.*;

public class Main {
    public static void main(String[] args) {
        System.out.println(new Adder().add(2, 3));        // 5
        System.out.println(new Multiplier().multiply(4, 6)); // 24
        System.out.println(new Divider().divide(8, 2));      // 4
    }
}

```

- Create a Java project and run it to ensure that it works. 
- The code is in the `Starter` folder in the Labs directory

### Analysis

There are number of problems with the current design
- It has high coupling
  - Clients access the specific classes directly
  - This means we can't modify the contents of the package without the risk of breaking client dependencies
- The interface is not closed to modification
  - The set of public methods from all the classes in a package form a de facto interface
  - Adding or modifying the classes changes the interface implicitly
- The package is going to be hard to maintain as more functionality is added.


## Part 2: The Refactoring 

The first step is to encapsulate all the computational classes inside the package
- This is easily done by making all the existing calc classes and their methods to have only package visibility.

```java
package calc;

class Adder {
    int add(int a, int b) {
        return a + b;
    }
}


package calc;

class Multiplier {
    int multiply(int a, int b) {
        return a * b;
    }
}


package calc;

class Divider {
    // integer division for simplicity; caller is responsible for zero-check
    int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("b must not be zero");
        return a / b;
    }
}
```

Once the classes are encapsulated into the `calc` package, we create a facade class that acts and an interface to the package.
- It is responsible for making sure the computational objects are instantiated, either at start up or though lazy installation (creating them the first time they are called)
- It provides a stable interface so that clients do not need to know anything about the internals of the `calc` package.
- The facade forwards the messages to the correct computation class and relays the result to the client
  - Note that we can change the methods on the computation class and just make a translation in the facade
  - For example, the method `add()` in Adder is changed to `sum()`
  - The Facade receives and add() message but calls sum() on the Adder object

```java
package calc;

public class Facade {

    // Composition keeps internals swappable/testable
    private final Adder adder;
    private final Multiplier multiplier;
    private final Divider divider;

    // Default constructor wires the package-private implementations.
    public Facade() {
        this(new Adder(), new Multiplier(), new Divider());
    }

    // Visible for testing if you want to swap implementations later
    Facade(Adder adder, Multiplier multiplier, Divider divider) {
        this.adder = adder;
        this.multiplier = multiplier;
        this.divider = divider;
    }

    public int add(int a, int b) {
        return adder.add(a, b);
    }

    public int multiply(int a, int b) {
        return multiplier.multiply(a, b);
    }

    public int divide(int a, int b) {
        return divider.divide(a, b);
    }
}

```

Use the following to test the refactoring

```java
import calc.*;

public class Main {
    public static void main(String[] args) {
        Facade  c = new Facade();
        System.out.println(c.add(2, 3));        // 5
        System.out.println(c.multiply(4, 6)); // 24
        System.out.println(c.divide(8, 2));      // 4
    }
}
```

## Part 3: Challenge

Use the command pattern to make the Facade class able to handle future requests to yet to be implemented computation objects.
- For example, adding an  `arctan()` computation
- This can be done with a new interface that never needs to be modified after, no matter how the objects in the `calc` package are modified

### Hint 
- Turn the function requests into objects
  - These are translated by the Facade into function calls that operate on an array of inputs (we may need different numbers of arguments for different computations)
  - Notice that we only need one method in the interface
  - It is closed of modification but open for extension by increasing the number of types allowed in the parameter
  - Remember to have code that throws an exception if the `operationType` is invalid

```java

public class Facade {
    ...
    int calculate(String operationType, int[] args) {
        ...
        if (operationType == "add") return c.add(args[0], args[1])
                ..
}
```

## End