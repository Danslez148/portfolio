import java.util.*;

public class Rectangle extends Shape {
   private double length;
   private double width;
      
   public Rectangle(String name, String colour, double length, double width) {
      super(name, colour);
      this.length = length;
      this.width = width;
   }
   
   public Rectangle(Rectangle otherRectangle) {
      super(otherRectangle);
      this.length = otherRectangle.length;
      this.width = otherRectangle.width;
   }
 
   public String toString() {
      return super.toString() + " Length " + length + " Width " + width;
   }
}

