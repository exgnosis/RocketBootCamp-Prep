
public class Main {
    // A client that assumes independent setters:
    static int computeArea(Rectangle r) {
        return r.getHeight() * r.getWidth(); // expects unchanged height
    }

    public static void main(String[] args) {
        Rectangle rect = new Rectangle();
        rect.setWidth(5);
        rect.setHeight(10);
        int h1 = computeArea(rect); // expect50
        System.out.println("Rectangle are for 5x10: " + h1);

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

