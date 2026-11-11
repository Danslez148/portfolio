import java.io.File;
import java.io.FileNotFoundException;
//
import java.util.Scanner;
/**
 * See Assignment II Question II
 *
 * @author Stephan Jamieson
 * @version 26/7/2019
 */
public class MarketPlace {
    
    private MarketPlace() {}
    
    private final static Currency RAND = new Currency("R", "ZAR", 100);
    
    
    // Create an instance of Seller with attributes ID, name, location, product, 
    // unit_price and number_of_units
    private static Seller makeSeller(final String data) {
        final Scanner scanner = new Scanner(data.trim());
        scanner.useDelimiter("\\s*,\\s*");
        
        // Add your code here
        
        String ID = scanner.next();
        String Name = scanner.next();
        String Location = scanner.next();
        String Product = scanner.next();
        Money unit_price = new Money(scanner.next(), RAND);
        int number_of_units = scanner.nextInt();
        
        Seller seller = new Seller(ID, Name, Location, Product, unit_price, number_of_units);
        
        return seller;
    }
    
    // Read the contents of CSV file into an array.
    // See the Appendix on page 4 of the Assignment sheet.
    private static Seller[] parseFile(final String fileName) throws FileNotFoundException {
      final Scanner inFile = new Scanner(new File(fileName));
      Seller[] sellers = null;

      if (inFile.hasNextLine()) {
         int numSellers = Integer.parseInt(inFile.nextLine().trim());
         if (numSellers > 0) {
            sellers = new Seller[numSellers];
            for (int index = 0; index < sellers.length; index++) {
                sellers[index] = makeSeller(inFile.nextLine());
            }
         } else {
            System.out.println("The file contains no seller data.");
            inFile.close();  
            return null;     
          }
      } else {
        System.out.println("The file contains no seller data.");
        inFile.close();  
        return null;     
    }
    inFile.close();
    return sellers;
}
    
    public static void main(final String[] args) throws FileNotFoundException {
        final Scanner inKey = new Scanner(System.in);
        System.out.println("Enter the name of a \"Comma Separated Values\" (CSV) file:");
        final Seller[] sellers = parseFile(inKey.nextLine());
        
        // Your Code here
        
        if (sellers == null) {
            return;
        }
        
        System.out.println("Enter the name of a product:");
        String productName = inKey.nextLine();
        System.out.println("Enter the number of units required:");
        int unitsRequired = Integer.parseInt(inKey.nextLine());
        System.out.println("Enter the maximum unit price:");
        Money maxPrice = new Money(inKey.nextLine(), RAND);
        
        boolean found = false;
        
        for (int i = 0; i < sellers.length; i++) {
            if (sellers[i].Product.equalsIgnoreCase(productName) && sellers[i].number_of_units >= unitsRequired && sellers[i].unit_price.compareTo(maxPrice) <= 0) {
               System.out.println(sellers[i].ID + " : " + sellers[i].Name + " in " + sellers[i].Location + " has " + sellers[i].number_of_units + " " + sellers[i].Product + " for " + sellers[i].unit_price + " each.");
               found = true;
            }
        }
        if (found == false) {
            System.out.println("None found.");
        }
        
    }
}
