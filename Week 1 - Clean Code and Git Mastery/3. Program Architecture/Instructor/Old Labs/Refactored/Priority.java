public enum Priority {
    HIGH(1), MEDIUM(2), LOW(3);

    private final int level;
    Priority(int level) { this.level = level; }
    public int level() { return level; }

    public static Priority fromInt(int n) {
        return switch (n) {
            case 1 -> HIGH;
            case 2 -> MEDIUM;
            case 3 -> LOW;
            default -> throw new IllegalArgumentException("Priority must be 1..3");
        };
    }
}
