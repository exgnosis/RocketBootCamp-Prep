# Lab 5-1 Notifier using Factory Method

## Learning Objectives

- Understand the Factory Method pattern as a way to create objects without exposing creation logic.
- Learn how factories reduce if/else clutter and make code easier to extend.

## Introduction
- In real-world systems, we often need to create different types of objects that serve the same purpose but work differently.
- For example, a system might send messages by email, SMS, or push notifications. 
- Without patterns, code often looks like this:

```java
if (type.equals("email")) {
    notifier = new EmailNotifier();
} else if (type.equals("sms")) {
    notifier = new SmsNotifier();
}
```

- This works for a few cases, but gets messy when more types are added. 
- Every new type requires changing this block. 
- That breaks the Open/Closed Principle (code should be open for extension, but closed for modification).
- The Factory Method pattern solves this problem by putting object creation in a factory class. 
- The client just asks the factory for a Notifier — it doesn’t care how the object is created.

## Starter Code

- The basic structure has been provided here.
- In this case, the factory has been implemented as a Java Interface, but it can also be implemented as an abstract class or similar construct
- The NotifierFactory has a `create(type)` method that creates a motifer of a concrete type.
- The `main()` method asks for a notifier of a specific type.
- Instead of having a lot of conditional code to execute the notification, the created object encapsulates that notification type logic


- Add in the missing items in the starter code.
- The code is in `Starter.java`
- The solution is in `Solution.java`

```java
// Main.java
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

public class Main {
    public static void main(String[] args) {
        // expected: [EMAIL] Build finished
        Notifier n1 = NotifierFactory.create("email");
        n1.send("Build finished");

        // expected: [SMS] Deploy started
        Notifier n2 = NotifierFactory.create("sms");
        n2.send("Deploy started");
    }
}

```

## End