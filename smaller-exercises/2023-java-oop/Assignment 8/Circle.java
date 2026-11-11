import java.util.*;

public class Circle extends Shape {
   private double radius;
   
   public Circle(String name, String colour, double radius) {
      super(name, colour);
      this.radius = radius;
   }
   
   public Circle(Circle otherCircle) {
      super(otherCircle);
      this.radius = otherCircle.radius;
   }

   public String toString() {
      return super.toString() + " Radius " + radius;
   }
}