// Creating a ticket class
// Daniel Schlesinger
// SCHDAN066
// 25 August 2023

public class Ticket {
   public String id;
   public Time issueTime;
   
   public Ticket(Time currentTime, String ID) {
      this.id = ID;
      this.issueTime = currentTime;
   }
   
   public String ID() {
      return this.id;
   }
   
   public Duration age(Time currentTime) {
      return currentTime.subtract(this.issueTime);
   }
   
   public String toString() {
      String stringOut = "Ticket[id=" + id + ", time=" + issueTime.toString() + "]";
      return stringOut;
   }
}