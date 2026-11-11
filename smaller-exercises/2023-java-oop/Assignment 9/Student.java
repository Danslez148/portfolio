public class Student extends Person {
   private int yearOfStudy;
   private String hobbies;
   private String nameOfInstitution;
   private String programOfStudy;
   
   public Student(String name, int age, String gender, String hobbies, String nameOfInstitution, int yearOfStudy, String programOfStudy) {
      super(name, age, gender);
      this.yearOfStudy = yearOfStudy;
      this.hobbies = hobbies;
      this.nameOfInstitution = nameOfInstitution;
      this.programOfStudy = programOfStudy;
   }
   
   public Student(Student other) {
      super(other.getName(), other.getAge(), other.getGender());
   }
   
   public int getYearOfStudy() {
      return yearOfStudy;
   }
   
   public String getHobbies() {
      return hobbies;
   }
   
   public String getNameOfInstitution() {
      return nameOfInstitution;
   }
   
   public String getProgramOfStudy() {
      return programOfStudy;
   }
   
   public void setHobbies(String hobbies) {
      this.hobbies = hobbies;
   }
   
   public void setNameOfInstitution(String nameOfInstitution) {
      this.nameOfInstitution = nameOfInstitution;
   }
   
   public void setProgramOfStudy(String programOfStudy) {
      this.programOfStudy = programOfStudy;
   }
   
   public void setYearOfStudy(int yearOfStudy) {
      this.yearOfStudy = yearOfStudy;
   }
}