// Program to store all tickets
// Daniel Schlesinger
// SCHDAN066
// 25 August 2023

public class Register {
   public Ticket[] tickets;
   public int numTickets;
   
   public Register() {
      this.tickets = new Ticket[100];
      this.numTickets = 0;
   }
   
   public void add(Ticket ticket) {
      tickets[numTickets] = ticket;
      numTickets += 1;
   }
   
   public boolean contains(String ticketID) {
      boolean contained = false;
      for (int i=0; i<numTickets; i++) {
         if (tickets[i].ID().equals(ticketID)) {
            contained = true;
         }
      }
      return contained;
   }
   
   public Ticket retrieve(String ticketID) {
      int indexOf = 0;
      for (int i=0; i<numTickets; i++) {
         if (tickets[i].ID().equals(ticketID)) {
            indexOf = i;
         } 
      }
      return tickets[indexOf]; 
   }
}