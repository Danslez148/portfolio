// Duration calculation from input
// Daniel Schlesinger
// SCHDAN066
// 04/08/2023

import java.util.Scanner;

class CalculateDuration {
   public static void main(String[] args) {
      Scanner keyboard = new Scanner(System.in);
      System.out.println("Enter time A:");
      Time firstTime = new Time(keyboard.next());
      System.out.println("Enter time B:");
      Time secondTime = new Time(keyboard.next());
      Time elapsed = new Time(secondTime.subtract(firstTime));
      System.out.println("The time " + secondTime + " occurs " + (elapsed.getHours()*60 + elapsed.getMinutes()) + " minutes after the time " + firstTime + ".");
   }
}