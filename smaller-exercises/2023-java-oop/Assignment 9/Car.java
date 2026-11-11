public class Car extends Vehicle {
   private int capacity;
   private double weight;
   
   public Car(int cylinders, String manufacturer, Student owner, int capacity, double weight) {
      super(cylinders, manufacturer, owner);
      this.capacity = capacity;
      this.weight = weight;
   }
   
   public Car(Car other) {
      super(other.cylinders, other.manufacturer, other.owner);
      this.capacity = other.capacity;
      this.weight = other.weight;
   }
   
   public String toString() {
      return super.toString() + "\nThe car is a " + this.capacity + 
      "-seater weighing " + weight + " kg";
   }
}