// Student name class definition
// Daniel Schlesinger
// SCHDAN066
// 18/08/2023

public class Student {
   private String firstName;
   private String middleName;
   private String lastName;
   
   public void setNames(String first, String middle, String last) {
      this.firstName = first;
      this.middleName = middle;
      this.lastName = last;
   }
   
   public String getFullName() {
      String initial = Character.toString(middleName.charAt(0));
      return firstName + " " + initial + ". " + lastName;
   }
}