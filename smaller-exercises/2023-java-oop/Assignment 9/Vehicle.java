public class Vehicle {
   public Student owner;
   public int cylinders;
   public String manufacturer;
   
   public Vehicle(Vehicle other) {
   
   }
   
   public Vehicle(int cylinders, String manufacturer, Student owner) {
      this.cylinders = cylinders;
      this.manufacturer = manufacturer;
      this.owner = owner;
   }
   
   public String toString() {
      return manufacturer + ", " + cylinders + " cylinders, owned by " + owner.getName() + 
      ", a " + owner.getAge() + "-year old " + owner.getGender() + " studying " + 
      owner.getProgramOfStudy() + " at " + owner.getNameOfInstitution() + ". " + 
      owner.getName() + " likes " + owner.getHobbies() + ".";
   }
}