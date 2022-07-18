import java.util.Vector;
import java.util.concurrent.atomic.AtomicBoolean;

public class Manager extends Thread implements Runnable { // The object implements run so that it could inherit thread methods
	private double totalCostOfLabor;
	private boolean bossDayIsfinished;
	private int totalAmountOfCalls;
	private static AtomicBoolean imWorking;
	private static Vector <Employee> EmpList ;
	private static Queue <Call> managerQueue;
	private static InformationSystem<Order> infoSystem; 
	private static MyCounter shardeCounter1;
	private static MyCounter deliveryCounter;

	public Manager (int amoutofcalls,Queue <Call> managerQueue,InformationSystem<Order> infoSystem, MyCounter idCount,MyCounter deliveryCounter,Vector <Employee> EmpList) { //Constructor of manager gets most its parameters from branch when created
		Manager.shardeCounter1=idCount;
		Manager.deliveryCounter=deliveryCounter;
		Manager.managerQueue = managerQueue;
		Manager.infoSystem = infoSystem;
		Manager.imWorking= new AtomicBoolean(true);
		Manager.EmpList= EmpList;
		this.bossDayIsfinished = false;
		this.totalAmountOfCalls=amoutofcalls;
		this.totalCostOfLabor=0;
	}
	public void run() {
		while(!bossDayIsfinished) { 
			Call c = managerQueue.extract(imWorking); // extracting large orders from managerQueue 
			if(imWorking.get()) {
				giveService(c); // method will "give service to customer"
			}
			else if((totalAmountOfCalls - deliveryCounter.getCount()) <= 10 ) { // in case were at the last 10 orders manager will let the pizza guy know by switching lastTen atomic boolean to true
				PizzaGuy.getLastTen().set(true);	
			}
			if ((totalAmountOfCalls - deliveryCounter.getCount()) == 0 ) { // when its end of day>>
				updatedCostOfLabor(); // method will sum all of the working force salary
				
				try {
					workDayFinished(); // let all other workers know that the day is finished
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				dayliReport(); // print all wanted data
				bossDayIsfinished= true; //  getting the manger out of his while loop
			}
			imWorking.set(true); // in order to get the manager out his waiting when a delivery comes back from a drop we changed his atomic boolean to false >>
			//now, were setting it back to true so the manger would go wait for more big orders
		}
	}
	private void dayliReport() { // method is responsible of printing report
		System.out.println("The Daily Cost Of Labor Is: "+totalCostOfLabor +"\n" +
				"The Amount Of Deliveries Is: " + deliveryCounter.getCount() +"\n" +
				"The Daily Profit Is: " +infoSystem.getTotalProfit());
	}
	public void updatedCostOfLabor() { // method is responsible of calculating all of the branch employees
		for(int i=0 ; i<EmpList.size();i++) {
			totalCostOfLabor+=EmpList.elementAt(i).getSalary();
		}
		setTotalCostOfLabor(totalCostOfLabor);
	}
	public void workDayFinished() throws InterruptedException { // by using this method the manger basically enters all the queues with a "fake extract" letting everyone know that its time to go home :) 
		Scheduler.setSchedulerDayIsFinished(true);
		KitchenWorker.setKitchenWorkIsFinished(true);
		PizzaGuy.setPizzaGuyDayIsFinished(true);
		
		Scheduler.getSchedulersWorking().set(false);
		Branch.getschedulerQueue().extract(Scheduler.getSchedulersWorking());
		PizzaGuy.getPizzaGuysAreWorking().set(false);
		while(PizzaGuy.getPizzaGuyCount().getCounter().get()!=0) {
			PizzaGuy.setPizzaGuyDayIsFinished(true);
			PizzaGuy.getPizzaGuysAreWorking().set(false);
		Branch.getDeliveryQueue().extract(PizzaGuy.getPizzaGuysAreWorking());
		}
	}
	public void giveService (Call c) { // method is responsible of giving service to big orders - meaning he is creating instances of orders
		Order o2 = new Order(c,Branch.getschedulerQueue(),infoSystem,shardeCounter1.getAndIncreaseCount());  //>>sets up the new price after discount and inserts it into information system
		o2.setTotalPrice(c.getAmount()*15);
		if(c.getAmount() > 20) {
			o2.setTotalPrice(o2.getTotalPrice() * 0.9);
		}
		o2.setDistance(distanceCalculator(o2));
		try {
			Thread.sleep((long)(2000));
			infoSystem.insert(o2);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		c.setDoneCall(true); // sets the boolean of the call to true >> ending the while of the call instance
		c.getOnGoingCall().compareAndExchange(c.getDoneCall(), false);
	}
	public double distanceCalculator (Order o) {	// exchange the address to distance from the branch by calculation that the Scheduler has.
		int counter=1;
		double letterValue=1;
		for(int i = 0; i < o.getCall().getAddress().length(); i++) {
			if (o.getCall().getAddress().charAt(i) == ' ') {
				counter ++;
			}
		}
		char firstLetter = o.getCall().getAddress().charAt(0);
		if(firstLetter >='a' && firstLetter <='h' || firstLetter >='A' && firstLetter <='H') {
			letterValue = 0.5;
		}else if(firstLetter >= 'i'&& firstLetter <='p' ||firstLetter >='I' && firstLetter <='P') {
			letterValue = 2;
		}else if(firstLetter >= 'q'&& firstLetter <='z' || firstLetter >='Q' && firstLetter <='Z') {
			letterValue = 7;
		}else if(firstLetter >= '1'|| firstLetter <='9') {
			letterValue = (firstLetter-48);
		}
		return (counter + letterValue);
	}
	public static Queue<Call> getManagerQueue() {
		return managerQueue;
	}
	public static AtomicBoolean getImWorking() {
		return imWorking;
	}
	public int getTotalAmountOfCalls() {
		return totalAmountOfCalls;
	}
	public void setTotalCostOfLabor(double totalProfit) {
		this.totalCostOfLabor = totalProfit;
	}
}