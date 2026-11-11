import java.util.*;

class Shape {
   private String name;
   private String colour;
   
   public Shape(String name, String colour) {
      this.name = name;
      this.colour = colour;
   }

   public String toString() {
      return name + " " + colour;
   }
}

class Circle extends Shape {
   private double radius;
   
   public Circle(String name, String colour, double radius) {
      super(name, colour);
      this.radius = radius;
   }

   public String toString() {
      return super.toString() + " Radius " + radius;
   }
}

class Rectangle extends Shape {
   private double length;
   private double width;
      
   public Rectangle(String name, String colour, double length, double width) {
      super(name, colour);
      this.length = length;
      this.width = width;
   }
 
   public String toString() {
      return super.toString() + " Length " + length + " Width " + width;
   }
}

class Question3
{   
   public static void main ( String args [] )
   {
      System.out.println (new Shape ("Pentagon", "Blue"));
      System.out.println (new Circle ("Circle", "Purple",  3));
      System.out.println (new Rectangle ("Rectangle", "Red", 6, 8));
   }
}
