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
