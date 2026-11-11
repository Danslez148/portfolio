//M. M. Kuttel 2025 mkuttel@gmail.com
package barScheduling;

import java.util.Random;
import java.util.Comparator;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

/*
 Barman Thread class.
 */

public class Barman extends Thread {
	
	private Map<Integer, Long> patronTotalPrepTime = new ConcurrentHashMap<>(); //total prep time for each patron
	private long startTime; // start and end time of the simulation
	private long endTime;

	private List<Long> windowStartTimes = new ArrayList<>(); //start times of each window
	private List<Long> completedOrderTimestamps = new ArrayList<>(); //timestamps of completed orders
	private List<Integer> throughputValues = new ArrayList<>(); //throughput values for each window
	private final long windowSize = 1000; //size of the window in milliseconds
	private final long windowShift = 250; //shift of the window in milliseconds

	private CountDownLatch startSignal;
	private BlockingQueue<DrinkOrder> orderQueue;
	int schedAlg =0;
	int q=10000; //really big if not set, so FCFS
	private int switchTime;
	
	Barman(  CountDownLatch startSignal,int sAlg) {
		//which scheduling algorithm to use
		this.schedAlg=sAlg;
		if (schedAlg==1) this.orderQueue = new PriorityBlockingQueue<>(5000, Comparator.comparingInt(DrinkOrder::getExecutionTime)); //SJF
		else this.orderQueue = new LinkedBlockingQueue<>(); //FCFS & RR
	    this.startSignal=startSignal;
	}
	
	Barman(  CountDownLatch startSignal,int sAlg,int quantum, int sTime) { //overloading constructor for RR which needs q
		this(startSignal, sAlg);
		q=quantum;
		switchTime=sTime;
	}

	public void placeDrinkOrder(DrinkOrder order) throws InterruptedException {
        orderQueue.put(order);
    }
	
	public void run() {
		int interrupts=0;
		try {
			DrinkOrder currentOrder;
			
			startSignal.countDown(); //barman ready
			startSignal.await(); //check latch - don't start until told to do so

			startTime=System.nanoTime()/1000000; //start time in milliseconds;

			if ((schedAlg==0)||(schedAlg==1)) { //FCFS and non-preemptive SJF
				while(true) {
					currentOrder=orderQueue.take();

					int patronID=currentOrder.getPatronID();

					System.out.println("---Barman preparing drink for patron "+ currentOrder.toString());

					patronTotalPrepTime.put(patronID, patronTotalPrepTime.getOrDefault(patronID, 0L) + currentOrder.getExecutionTime()); // adds the current drink's prep time to the total prep time the barman has done for this patron
					System.out.println("Total prep time for patron "+ patronID + " is now "+ patronTotalPrepTime.get(patronID));

					sleep(currentOrder.getExecutionTime()); //processing order (="CPU burst")
					 
					synchronized (completedOrderTimestamps) {
						completedOrderTimestamps.add(System.nanoTime()/1000000); //add the timestamp of the completed order
					}

					System.out.println("---Barman has made drink for patron "+ currentOrder.toString());
					currentOrder.orderDone();

					sleep(switchTime);//cost for switching orders
				}
			}
			else { // RR 
				int burst=0;
				int timeLeft=0;
				System.out.println("---Barman started with q= "+q);

				while(true) {
					System.out.println("---Barman waiting for next order ");
					currentOrder=orderQueue.take();

					int patronID=currentOrder.getPatronID();

					System.out.println("---Barman preparing drink for patron "+ currentOrder.toString() );
					burst=currentOrder.getExecutionTime();
					if(burst<=q) { //within the quantum
						sleep(burst); //processing complete order ="CPU burst"
						System.out.println("---Barman has made drink for patron "+ currentOrder.toString());
						currentOrder.orderDone();

						synchronized (completedOrderTimestamps) {
						completedOrderTimestamps.add(System.nanoTime()/1000000); //add the timestamp of the completed order
					}

						patronTotalPrepTime.put(patronID, patronTotalPrepTime.getOrDefault(patronID, 0L) + burst); //add time worked to the total prep time for this patron
					}
					else {
						sleep(q);
						timeLeft=burst-q;
						System.out.println("--INTERRUPT---preparation of drink for patron "+ currentOrder.toString()+ " time left=" + timeLeft);
						interrupts++;
						currentOrder.setRemainingPreparationTime(timeLeft);
						orderQueue.put(currentOrder); //put back on queue at end

						patronTotalPrepTime.put(patronID, patronTotalPrepTime.getOrDefault(patronID, 0L) + q); // add time worked to the total prep time for this patron
					}
					sleep(switchTime);//switching orders
				}
			}
				
		} catch (InterruptedException e1) {
			endTime=System.nanoTime()/1000000; //end time in milliseconds

			System.out.println("---Barman is packing up ");
			System.out.println("---number interrupts="+interrupts);
			calculateThroughput(); //calculate throughput after all orders are done
			System.out.println("Throughput values for each window: " + throughputValues); //test
		}
	}

	public long getPatronTotalPrepTime(int patronID) {
		return patronTotalPrepTime.getOrDefault(patronID, 0L); //returns the total prep time for this patron
}

	public long calculateTotalActiveTime() {
		return patronTotalPrepTime.values().stream().mapToLong(Long::longValue).sum(); //sum of all prep times for all patrons
	}

	public long calculateTotalTime() {
		return endTime - startTime; //total time of the simulation
	}

	public double calculateUtilization() {
		long totalActiveTime = calculateTotalActiveTime();
		long totalTime = calculateTotalTime();
		return (double) totalActiveTime / totalTime * 100; //utilization percentage
	}

	private void calculateThroughput() {
		long currentWindowStartTime = startTime; //first window start time

		synchronized (completedOrderTimestamps) {
			while (currentWindowStartTime <= endTime) {
				final long windowStart = currentWindowStartTime; // capture the current window start time
				long windowEndTime = currentWindowStartTime + windowSize;
				int throughput = (int) completedOrderTimestamps.stream().filter(timestamp -> timestamp >= windowStart && timestamp < windowEndTime).count(); // find applicable completed orders in the current window and counts them
				throughputValues.add(throughput); //add data to the list
				currentWindowStartTime += windowShift; //shift the window
			}
		}
	}

	public List<Integer> getThroughputValues() {
		return throughputValues; //returns the throughput values for each window
	}

	public List<Long> getWindowStartTimes() {
		List<Long> windowStartTimes = new ArrayList<>();
		long currentWindowStartTime = startTime; //first window start time
		while (currentWindowStartTime <= endTime) {
			windowStartTimes.add(currentWindowStartTime - startTime); //add data to the list
			currentWindowStartTime += windowShift; //shift the window
		}
		return windowStartTimes;
	}
}
