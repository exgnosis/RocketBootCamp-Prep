public class BankAccount {

    // Mutable: the current state of the account.
    // The state object knows the rules; BankAccount just delegates and provides shared storage.
    Transaction state;
    double balance;

    public BankAccount(double openingBalance) {
        this.balance = openingBalance;
        this.state = (openingBalance < 0) ? new Overdrawn(this) : new Normal(this);
    }

    public void deposit(double amount) {
        if (amount <= 0) {
            System.out.println("Deposit refused: amount must be positive.");
            return;
        }
        state.deposit(amount);
    }

    public void withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("Withdrawal refused: amount must be positive.");
            return;
        }
        state.withdraw(amount);
    }

    public double getBalance() {
        return state.getBalance();
    }

    // The state transition method, called by the state objects themselves.
    void setState(Transaction newState) {
        this.state = newState;
    }

    public static void main(String[] args) {
        BankAccount acct = new BankAccount(100.0);
        System.out.println("--- Account created with opening balance " + acct.getBalance() + " ---");

        acct.deposit(50);
        acct.withdraw(30);
        acct.withdraw(200);
        acct.withdraw(10);
        acct.deposit(40);
        acct.deposit(100);
        acct.withdraw(20);

        System.out.println("--- Final balance: " + acct.getBalance() + " ---");
    }
}

interface Transaction {
    void deposit(double amount);
    void withdraw(double amount);
    double getBalance();
}

class Normal implements Transaction {
    private final BankAccount account;

    Normal(BankAccount account) {
        this.account = account;
    }

    public void deposit(double amount) {
        account.balance += amount;
        System.out.println("Deposit of " + amount + " accepted. Balance: " + account.balance);
    }

    public void withdraw(double amount) {
        account.balance -= amount;
        System.out.println("Withdrawal of " + amount + " accepted. Balance: " + account.balance);
        if (account.balance < 0) {
            account.setState(new Overdrawn(account));
            System.out.println("Account is now OVERDRAWN.");
        }
    }

    public double getBalance() {
        return account.balance;
    }
}

class Overdrawn implements Transaction {
    private final BankAccount account;

    Overdrawn(BankAccount account) {
        this.account = account;
    }

    public void deposit(double amount) {
        account.balance += amount;
        System.out.println("Deposit of " + amount + " accepted while overdrawn. Balance: " + account.balance);
        if (account.balance >= 0) {
            account.setState(new Normal(account));
            System.out.println("Account is back to NORMAL.");
        }
    }

    public void withdraw(double amount) {
        System.out.println("Withdrawal of " + amount + " refused: account is overdrawn.");
    }

    public double getBalance() {
        return account.balance;
    }
}
