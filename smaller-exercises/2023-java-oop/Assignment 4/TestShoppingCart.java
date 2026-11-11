// Program to capture info and print invoice
// Daniel Schlesinger
// SCHDAN066
// 18 August 2023

import java.util.Scanner;

public class TestShoppingCart {
   public static void main(String[] args) {
      ShoppingCart newCart = new ShoppingCart();
      Scanner input = new Scanner(System.in);
      System.out.println("How many items would you like to add to your Shopping Cart?:");
      int i = input.nextInt();
      if (i == 0) {
         System.out.println("Your Shopping Cart is empty.");
         System.exit(0);
      }
      for (int k = 1; k <= i; k++) {         
         System.out.println("Enter the Product Name:");
         String name = input.next();
         System.out.println("Enter the Quantity:");
         int quantity = input.nextInt();
         System.out.println("Enter the Unit Cost:");
         double unitCost = input.nextDouble();
         Item newItem = new Item(name, quantity, unitCost);
         newCart.item.add(newItem);
      }
      newCart.getDiscount("WELCOME20");
      System.out.println("The Shopping Cart has the following items:");
      newCart.queryCart();
      System.out.println("--- Shopping Cart with all items ---");
      newCart.printInvoice();
   }
}