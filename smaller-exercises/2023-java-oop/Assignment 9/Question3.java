import java.util.*;

public class Question3 {
   public static void main(String[] args){
      Scanner keyboard = new Scanner(System.in);
      String[] s = new String[10];
      System.out.println("Enter the vehicle manufacturer:");
      s[0] = keyboard.nextLine();
      System.out.println("Enter the name of the vehicle owner:");
      s[1] = keyboard.nextLine();
      System.out.println("Enter the owner's gender:");
      s[2] = keyboard.nextLine();
      System.out.println("Enter the owner's programme of study:");
      s[3] = keyboard.nextLine();
      System.out.println("Enter the owner's Institution name:");
      s[4] = keyboard.nextLine();
      System.out.println("Enter the owner's hobbies:");
      s[5] = keyboard.nextLine();
      System.out.println("Enter the owner's age:");
      s[6] = keyboard.nextLine();
      System.out.println("Enter the number of cylinders in the engine:");
      s[7] = keyboard.nextLine();
      System.out.println("Enter the car seating capacity:");
      s[8] = keyboard.nextLine();
      System.out.println("Enter the weight of the car:");
      s[9] = keyboard.nextLine();
      Student owner = new Student(s[1], Integer.parseInt(s[6]), s[2], s[5], s[4], 2023, s[3]);
      Car car = new Car(Integer.parseInt(s[7]), s[0], owner, Integer.parseInt(s[8]), Double.parseDouble(s[9]));
      System.out.println(car.toString());
   }
}