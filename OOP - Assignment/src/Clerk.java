import java.util.concurrent.atomic.AtomicBoolean;
public class Clerk extends Employee implements Runnable {
	@SuppressWarnings("unused")
	private int id;
	private double salary;
	private static int amountOfCalls;
	private static  boolean workDayIsFinished;
	private static  AtomicBoolean wereWorking;
	private static Queue<Call> callQueue;
	private static Queue<Order> schedulerQueue;
	private static Queue<Call> managerQueue;
	private static MyCounter shardeCounter2;

	public Clerk (int id,int amountOfCalls, Queue<Call> callQueue,Queue<Order> schedulerQueue,Queue<Call> managerQueue,MyCounter count) { //Constructor of Clerk gets most its parameters from branch when created
		this.id = id;
		this.setSalary(0);
		Clerk.shardeCounter2=count;
		Clerk.workDayIsFinished=false;
		Clerk.wereWorking= new AtomicBoolean(true);
		Clerk.callQueue = callQueue;
		Clerk.schedulerQueue = schedulerQueue;
		Clerk.managerQueue = managerQueue;
		Clerk.amountOfCalls= amountOfCalls;
	}
	public void run() {
		while (!workDayIsFinished) { 
			Call c= callQueue.extract(wereWorking);// extracting calls from callQueue 
			if(wereWorking.get()) { // as long as atomic boolean is true keep giving service
				giveService(c); // method is responsible of making an order out of call
				if(Clerk.amountOfCalls==0) { // when the final call gets treated >> the clerk who did the service has to let the other clerks know that the work is finished 
					Clerk.setWorkDayIsFinished(true);
					wereWorking.compareAndExchange(workDayIsFinished, false); // changing atomic boolean to 
				}
			}
		}
		callQueue.extract(wereWorking);
	}
	public void giveService (Call c) { // method is responsible of giving service - meaning he is creating instances of orders
		if(c.getAmount()<10) {
			try {
				Thread.sleep((long)(c.getWaitigTime()*1000));
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			Order o1 = new Order(c,schedulerQueue,Branch.getInfoSystem(),shardeCounter2.getAndIncreaseCount());
			o1.setTotalPrice(c.getAmount()* 25);
			this.setSalary(this.getSalary() + 2);
			schedulerQueue.insert(o1);
			c.setDoneCall(true); // Clerk sets the call boolean to true>> ending the thread
			c.getOnGoingCall().compareAndExchange(c.getDoneCall(), false);
			Clerk.setAmountOfCalls(amountOfCalls-1);
		}
		else {
			Clerk.setAmountOfCalls(amountOfCalls-1);
			managerQueue.insert(c);

		}
	}
	public double getSalary() {
		return salary;
	}
	public synchronized static void setWorkDayIsFinished(boolean workDayIsFinished) {
		Clerk.workDayIsFinished = workDayIsFinished;
	}
	public static  boolean getfinish() {
		return workDayIsFinished;
	}
	public void setSalary(double salary) {
		this.salary = salary;
	}
	public static int getAmountOfCalls() {
		return amountOfCalls;
	}
	public static void setAmountOfCalls(int amountOfCalls) {
		Clerk.amountOfCalls = amountOfCalls;
	}
}