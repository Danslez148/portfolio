import java.util.*;

public class Shape {
   private String name;
   private String colour;
   
   public Shape(String name, String colour) {
      this.name = name;
      this.colour = colour;
   }
   
   public Shape(Shape otherShape) {
      this.name = otherShape.name;
      this.colour = otherShape.colour;
   }

   public String toString() {
      return name + " " + colour;
   }
}

