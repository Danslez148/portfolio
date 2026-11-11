public class Person {
   String name;
   int age;
   String gender;
   
   public Person(String name, int age, String gender) {
      this.name = name;
      this.age = age;
      this.gender = gender;
   }
   
   public Person(Person other) {
      this.name = other.getName();
      this.age = other.getAge();
      this.gender = other.getGender();
   }
   
   public String getName() {
      return name;
   }
   
   public int getAge() {
      return age;
   }
   
   public String getGender() {
      return gender;
   }
   
   public void setAge(int age) {
      this.age = age;
   }
   
   public void setGender(String gender) {
      this.gender = gender;
   }
   
   public void setName(String name) {
      this.name = name;
   }
}