import java.util.Scanner;
/**
 * The CarParkSim class contains the main car park simulation method.
 * It creates and manipulates the main objects, and handles user I/O.
 *
 * @author Stephan Jamieson and ...
 * @version 14/7/2019
 */
public class CarParkSim {
        
    public static void main(final String[] args) {
        final Scanner keyboard = new Scanner(System.in);
        // YOUR CODE HERE.
        Clock ourClock = new Clock(new Time("00:00"));
        Register ourRegister = new Register();
        // Declare variables to store a Clock and a Register object, create the relevant objects and assign them. 
        
        System.out.println("Car Park Simulator");
        // YOUR CODE HERE.
        Time startTime = ourClock.examine();
        System.out.println("The current time is " + startTime.toString() + ".");
        // Print current time.
        System.out.println("Commands: advance {minutes}, arrive, depart, quit.");
        System.out.print(">");
        String input = keyboard.next().toLowerCase();
        while (!input.equals("quit")) {
            if (input.equals("advance")) {
                // YOUR CODE HERE.
                int advanceTime = keyboard.nextInt();
                ourClock.advance(new Duration("minute", advanceTime));
                System.out.println("The current time is " + ourClock.examine().toString() + ".");
                // Advance the clock, print the current time.
            }
            else if (input.equals("arrive")) {
                // YOUR CODE HERE.              
                Ticket newTicket = new Ticket(ourClock.examine(), UIDGenerator.makeUID());
                ourRegister.add(newTicket);
                System.out.println("Ticket issued: " + newTicket.toString() + ".");
                // Create a new ticket, add it to the register, print details of ticket issued.
            }
            else if (input.equals("depart")) {
                // YOUR CODE HERE.
                String currentID = keyboard.next();
                if (ourRegister.contains(currentID)) {
                  Ticket currentTicket = ourRegister.retrieve(currentID);
                  Duration stayDuration = currentTicket.age(ourClock.examine());
                  System.out.println("Ticket details: " + currentTicket.toString() + ".");
                  System.out.println("Current time: " + ourClock.examine().toString() + ".");
                  System.out.println("Duration of stay: " + Duration.format(stayDuration, "second") + ".");
                } else {
                  System.out.println("Invalid ticket ID.");
                }
                // Determine if ticket is valid, i.e. in the register.
                // If not, print error message.
                // If yes, retreive it, calculate duration of stay and print it.
            }
            else {
                System.out.println("That command is not recognised.");
                System.out.println("Commands: advance <minutes>, arrive, depart, quit.");
            }            
            System.out.print(">");
            input = keyboard.next().toLowerCase();
        }            
        System.out.println("Goodbye.");
    }

}
