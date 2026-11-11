// Class construction exercise
// Daniel Schlesinger
// SCHDAN066
// 10/08/2023

import java.util.Scanner;

class TestSeller {
   public static void main(String[] args) {
   Scanner keyboard = new Scanner(System.in);
   Currency rand = new Currency("R", "ZAR", 100);
   System.out.println("Please enter the details of the seller.");
   System.out.print("ID: ");
   String ID = keyboard.nextLine();
   System.out.print("Name: ");
   String Name = keyboard.nextLine();
   System.out.print("Location: ");
   String Location = keyboard.nextLine();
   System.out.print("Product: ");
   String Product = keyboard.nextLine();
   System.out.print("Price: ");
   Money unit_price = new Money(keyboard.nextLine(), rand);
   System.out.print("Units: ");
   int number_of_units = Integer.parseInt(keyboard.nextLine());
   Seller newseller = new Seller(ID, Name, Location, Product, unit_price, number_of_units);
   System.out.println("The seller has been successfully created:");
   System.out.println("ID of the seller: " + newseller.ID);
   System.out.println("Name of the seller: " + newseller.Name);
   System.out.println("Location of the seller: " + newseller.Location);
   System.out.println("The product to sell: " + newseller.Product);
   System.out.println("Product unit price: " + newseller.unit_price);
   System.out.println("The number of available units: " + newseller.number_of_units);
   }
}