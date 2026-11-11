// list of all parts in a shop
// Daniel Schlesinger
// SCHDAN066
// 29/09/2023

import java.util.Scanner;
import java.util.ArrayList;

public class Question1 {
   public static void main(String[] args) {
      Scanner keyboard = new Scanner(System.in);
      ArrayList<Parts> ourList = new ArrayList<>();
      System.out.println("Welcome to Great International Technology");
      while (true) {
         System.out.println("MENU: add (B)ox, add (S)creen, add (A)ccessories, (D)elete, (L)ist, (Q)uit");
         String next = keyboard.nextLine().toLowerCase();
         switch (next) {
            case "b":
               System.out.println("Enter the serial number");
               String boxNo = keyboard.nextLine();
               System.out.println("Enter the manufacturer");
               String boxManufacturer = keyboard.nextLine();
               System.out.println("Enter the colour");
               String boxColour = keyboard.nextLine();
               System.out.println("Enter the amount of memory (MB)");
               int boxMemory = Integer.parseInt(keyboard.nextLine());
               Box box = new Box(boxNo, boxManufacturer, boxColour, boxMemory);
               ourList.add(box);
               System.out.println("Done");
               break;
            case "s":
               System.out.println("Enter the serial number");
               String screenNo = keyboard.nextLine();
               System.out.println("Enter the manufacturer");
               String screenManufacturer = keyboard.nextLine();
               System.out.println("Enter the colour");
               String screenColour = keyboard.nextLine();
               System.out.println("Enter the screen size in inches");
               int screenSize = Integer.parseInt(keyboard.nextLine());
               Screen screen = new Screen(screenNo, screenManufacturer, screenColour, screenSize);
               ourList.add(screen);
               System.out.println("Done");
               break;
            case "a":
               System.out.println("Enter the serial number");
               String accessoryNo = keyboard.nextLine();
               System.out.println("Enter the manufacturer");
               String accessoryManufacturer = keyboard.nextLine();
               System.out.println("Enter the colour");
               String accessoryColour = keyboard.nextLine();
               Accessory accessory = new Accessory(accessoryNo, accessoryManufacturer, accessoryColour);
               ourList.add(accessory);
               System.out.println("Done");
               break;
            case "d":
               System.out.println("Enter the serial number");
               String removingNo = keyboard.nextLine();
               boolean found = false;
               for (int i = 0; i < ourList.size(); i++) {
                  Parts part = ourList.get(i);
                  if (part.getSerialNumber().equals(removingNo)) {
                     ourList.remove(i);
                     found = true;
                     break;
                     }
                  }
                if (found) {
                  System.out.println("Done");
                } else {
                  System.out.println("Not found");
                }         
                break;
            case "l":
               for (Parts part : ourList) {
                  System.out.println(part.toString());
               }
               System.out.println("Done");
               break;
            case "q":
               System.exit(0);
               break;
            default:
               System.out.println("Invalid choice. Please choose a valid option.");
               break;
            }
        }
   }
}