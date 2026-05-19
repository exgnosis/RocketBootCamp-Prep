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
