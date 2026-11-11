// Adding money to a total
// Daniel Schlesinger
// SCHDAN066
// 04/08/2023

import java.util.Scanner;

class SumCosts {
   public static void main(String[] args) {
      Scanner keyboard = new Scanner(System.in);
      Currency rand = new Currency("R", "ZAR", 100);
      Money money = new Money("R0", rand);
      String moneyIn = "";
      while (!moneyIn.equals("D") && !moneyIn.equals("Done")) {
         System.out.println("Enter an amount or '[D]one' to print the sum and quit:");
         moneyIn = keyboard.next();
         if (!moneyIn.equals("D") && !moneyIn.equals("Done")) {
            Money addition = new Money(moneyIn, rand);
            money = money.add(addition);
         }              
      }
      System.out.println("Total: " + money);
   }   
}