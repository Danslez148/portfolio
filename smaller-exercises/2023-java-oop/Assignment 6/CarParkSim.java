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
        Currency rand = new Currency("R", "ZAR", 100);
        // YOUR CODE HERE.
        Clock ourClock = new Clock(new Time("00:00"));
        Register ourRegister = new Register();
        TariffTable ourTariffs = new TariffTable(100);
        ourTariffs.addTariff(new TimePeriod(new Duration("minutes", 0), new Duration("minutes", 30)), new Money("R10.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("minutes", 30), new Duration("hours", 1)), new Money("R15.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 1), new Duration("hours", 3)), new Money("R20.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 3), new Duration("hours", 4)), new Money("R30.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 4), new Duration("hours", 5)), new Money("R40.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 5), new Duration("hours", 6)), new Money("R50.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 6), new Duration("hours", 8)), new Money("R60.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 8), new Duration("hours", 10)), new Money("R70.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 10), new Duration("hours", 12)), new Money("R90.00", rand));
        ourTariffs.addTariff(new TimePeriod(new Duration("hours", 12), new Duration("days", 1)), new Money("R100.00", rand));
        // Declare variables to store a Clock and a Register object, create the relevant objects and assign them. 
        
        System.out.println("Car Park Simulator");
        // YOUR CODE HERE.
        Time startTime = ourClock.examine();
        System.out.println("The current time is " + startTime.toString() + ".");
        // Print current time.
        System.out.println("Commands: tariffs, advance {minutes}, arrive, depart, quit.");
        System.out.print(">");
        String input = keyboard.next().toLowerCase();
        while (!input.equals("quit")) {
            if (input.equals("tariffs")) {
               System.out.println(ourTariffs.toString());
            }
            else if (input.equals("advance")) {
                // YOUR CODE HERE.
                int advanceTime = keyboard.nextInt();
                ourClock.advance(new Duration("minute", advanceTime));
                System.out.println("The current time is " + ourClock.examine().toString() + ".");
                // Advance the clock, print the current time.
            }
            else if (input.equals("arrive")) {
                // YOUR CODE HERE.              
                Ticket newTicket = new Ticket(ourClock.examine());
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
                  System.out.println("Cost of stay : " + ourTariffs.getTariff(stayDuration) + ".");
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
