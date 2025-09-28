// Main.java
interface Notifier {
    void send(String msg);
}

class EmailNotifier implements Notifier {
    public void send(String msg) {
        System.out.println("[EMAIL] " + msg);
    }
}

class SmsNotifier implements Notifier {
    public void send(String msg) {
        System.out.println("[SMS] " + msg);
    }
}

// (Optional stretch) Add PushNotifier
class PushNotifier implements Notifier {
    public void send(String msg) {
        System.out.println("[PUSH] " + msg);
    }
}

class NotifierFactory {
    // Factory Method implementation
    static Notifier create(String type) {
        if (type.equalsIgnoreCase("email")) {
            return new EmailNotifier();
        } else if (type.equalsIgnoreCase("sms")) {
            return new SmsNotifier();
        } else if (type.equalsIgnoreCase("push")) {   // optional
            return new PushNotifier();
        }
        return null; // could also throw IllegalArgumentException
    }
}

public class Main {
    public static void main(String[] args) {
        Notifier n1 = NotifierFactory.create("email");
        n1.send("Build finished");      // [EMAIL] Build finished

        Notifier n2 = NotifierFactory.create("sms");
        n2.send("Deploy started");      // [SMS] Deploy started

        Notifier n3 = NotifierFactory.create("push");  // stretch
        n3.send("System update available"); // [PUSH] System update available
    }
}
