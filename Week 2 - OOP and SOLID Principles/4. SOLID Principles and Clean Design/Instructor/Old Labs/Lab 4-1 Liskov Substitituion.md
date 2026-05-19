# Lab 4-1: Liskov Substitution Principle with Rectangle & Square

## Objectives
- This lab demonstrates the LSP
- If S is a subtype of T, then objects of type T in a correct program may be replaced with objects of type S without altering the correctness of that program.
- The lab demonstrates a common violation, the subclass overrides the superclass setters

## Violating code

- First, consider the superclass Rectangle

```java
// Rectangle.java
class Rectangle {
    protected int width;
    protected int height;

    public int getWidth()  { return width; }
    public int getHeight() { return height; }

    public void setWidth(int w)  { this.width = w; }
    public void setHeight(int h) { this.height = h; }

    public int area() { return width * height; }
}

```
- Note specially the `setWidth()` setter

- Now the violating Square code

```java

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

```
- The square class overrides the setWidth() method and changes both the height and width of the square.
- This makes sense cor a square, but not a rectangle

### Run the code

- The following driver demonstrates the violation
- When you run the code, we get two different answers for the area of the square.
- The code is in `Starter.java`

```java
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
```

## Task

- Fix the Square class so that it doesn't violate the LSP
- Hint: have the Square use the concept of a side and then use that to call the superclass constructor.
- A full solution is in the file `Solution.java`