//M. M. Kuttel 2024 mkuttel@gmail.com
//Class to represent a swim team - which has four swimmers
package medleySimulation;

import medleySimulation.Swimmer.SwimStroke;
import java.util.Arrays;
import java.util.Comparator;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;


public class SwimTeam extends Thread {
	
	public static StadiumGrid stadium; //shared 
	private Swimmer [] swimmers;
	private int teamNo; //team number 
   public static CountDownLatch[] arrLatch; //created array that has a latch for each stroke for entry to stadium
	public CountDownLatch[] arrLatch2 = new CountDownLatch[3]; // array that has latches for each stroke while relay is going
   
	public static final int sizeOfTeam=4;
	
	SwimTeam( int ID, FinishCounter finish,PeopleLocation [] locArr ) {
		this.teamNo=ID;
		
		swimmers= new Swimmer[sizeOfTeam];
	    SwimStroke[] strokes = SwimStroke.values();  // Get all enum constants
		stadium.returnStartingBlock(ID);
      
      arrLatch = new CountDownLatch[5];
      for (int i = 0; i<5; i++) {
         arrLatch[i] = new CountDownLatch(10); //creates a new countdown latch for each stroke
      }
      
      for (int i=0; i<10; i++) {
            arrLatch[0].countDown(); //gets rid of first latch immediately so backstroke can immediately enter
         }  
      arrLatch[1].countDown();
      arrLatch[4] = new CountDownLatch(11);
      
      for (int i=0; i<3; i++) {
         arrLatch2[i] = new CountDownLatch(1); //initialises array so each stroke has a single countered latch that gets released when the previous swimmer finishes swimming
      }
      
		for(int i=teamNo*sizeOfTeam,s=0;i<((teamNo+1)*sizeOfTeam); i++,s++) { //initialise swimmers in team
			locArr[i]= new PeopleLocation(i,strokes[s].getColour());
	      	int speed=(int)(Math.random() * (3)+30); //range of speeds 
			swimmers[s] = new Swimmer(i,teamNo,locArr[i],finish,speed,strokes[s], arrLatch2); //hardcoded speed for now
		}
	}
	
	
	public void run() {
		try {	
			for(int s=0;s<sizeOfTeam; s++) { //start swimmer threads
				swimmers[s].start();
				
			}
			
			for(int s=0;s<sizeOfTeam; s++) swimmers[s].join();			//don't really need to do this;
			
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
	

