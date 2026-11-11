//M. M. Kuttel 2025 mkuttel@gmail.com
package barScheduling;


import java.util.Random;
import java.util.concurrent.CountDownLatch;

/*class for the patrons at the bar*/

public class Patron extends Thread {
	
	private Random random;// for variation in Patron behaviour
	private CountDownLatch startSignal; //all start at once, actually shared
	private Barman theBarman; //the Barman is actually shared though

	private int ID; //thread ID 
	private int numberOfDrinks;

	private long turnaroundTime;
	private long responseTime;
	private long waitingTime;

	private DrinkOrder [] drinksOrder;
	
	Patron( int ID,  CountDownLatch startSignal, Barman aBarman, long seed) {
		this.ID=ID;
		this.startSignal=startSignal;
		this.theBarman=aBarman;
		this.numberOfDrinks=5; // number of drinks is fixed
		drinksOrder=new DrinkOrder[numberOfDrinks];
		if (seed>0) random = new Random(seed);// for consistent Patron behaviour
		else random = new Random();
	}

	//getters for the turnaround, response and waiting times
	public long getTurnaroundTime() {
		return turnaroundTime;
	}
	public long getResponseTime() {
		return responseTime;
	}
	public long getWaitingTime() {
		return waitingTime;
	}
	public int getID() {
		return ID;
	}
	
	
//this is what the threads do	
	public void run() {
		try {
			
			//Do NOT change the block of code below - this is the arrival times
			startSignal.countDown(); //this patron is ready
			startSignal.await(); //wait till everyone is ready
			int arrivalTime = ID*50; //fixed arrival for testing
	        sleep(arrivalTime);// Patrons arrive at staggered  times depending on ID 
			System.out.println("+new thirsty Patron "+ this.ID +" arrived"); //Patron has actually arrived
			//End do not change
			
			long timeArrived = System.nanoTime();
			long[] drinkOrdered = new long[numberOfDrinks];
			long[] drinkReceived = new long[numberOfDrinks];

	        for(int i=0;i<numberOfDrinks;i++) {
	        	drinksOrder[i]=new DrinkOrder(this.ID); //order a drink (=CPU burst)	        
	        	//drinksOrder[i]=new DrinkOrder(this.ID,i); //fixed drink order (=CPU burst), useful for testing
				System.out.println("Order placed by " + drinksOrder[i].toString()); //output in standard format  - do not change this
				theBarman.placeDrinkOrder(drinksOrder[i]);

				drinkOrdered[i] = System.nanoTime(); //record the time the order was placed

				drinksOrder[i].waitForOrder();

				drinkReceived[i] = System.nanoTime(); //record the time the order was received

				System.out.println("Drinking patron " + drinksOrder[i].toString());
				sleep(drinksOrder[i].getImbibingTime()); //drinking drink = "IO"
			}

			System.out.println("Patron "+ this.ID + " completed ");

			long timeFinishedLastDrink = System.nanoTime();//record the time the last drink was finished

			turnaroundTime = (timeFinishedLastDrink - timeArrived)/1000000;//total turnaround time for this patron
			responseTime = (drinkReceived[0] - timeArrived)/1000000;//total response time for this patron
			waitingTime = 0;
			for(int i=0; i<numberOfDrinks;i++) {
				waitingTime = waitingTime + (drinkReceived[i]-drinkOrdered[i]);
			}
			waitingTime = waitingTime/1000000 - theBarman.getPatronTotalPrepTime(this.ID); //total waiting time for this patron


		} catch (InterruptedException e1) {  //do nothing
		}
}
}
	

