public class KitchenWorker extends Employee implements Runnable  {  // The object implements run method so that it could inherit thread methods
	private String myName;
	private double salary;
	private double timeOnSinglePizza;
	private	InformationSystem <Order> infoSystem ;
	private static  boolean kitchenWorkIsFinished;
	private static BoundedQueue<PizzaDelivery> deliverQueue;

	public KitchenWorker (String name,BoundedQueue<PizzaDelivery> deliverQueue,InformationSystem<Order> infoSystem,double timeOnSinglePizza) {// that is the constructor that Initialising the object
		this.myName=name;
		this.setSalary(0);
		this.infoSystem= infoSystem;
		this.timeOnSinglePizza=timeOnSinglePizza;
		KitchenWorker.deliverQueue=deliverQueue;
		KitchenWorker.kitchenWorkIsFinished=false;
	}
	public void run() { //That method is executed the current thread.
		while (!kitchenWorkIsFinished) {
			Order o= infoSystem.extract();
			if( o!=null) {
				System.out.println(this.toString() + "\n" + o);
				giveService(o);
			}
		}
	}
	public  String toString() { //override the toString method for the print of the kitchenWorkers
		return "My Name Is: " + myName +","+ " My Current Salary Is: " + (salary+2);
	}
	public void giveService (Order o) {// that method simulate the time of baking every pizza and adding 2 coins for each pizza that he baked
		PizzaDelivery box= new PizzaDelivery(o.getCall().getAddress(),o.getDistance(),o.getCall().getAmount());
		try {
			Thread.sleep((long)(1000.0*(o.getCall().getAmount())*timeOnSinglePizza));
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		this.setSalary(this.getSalary() + 2);
		deliverQueue.insert(box,true);
	}
	public static void setKitchenWorkIsFinished(boolean kitchenWorkIsFinished) {
		KitchenWorker.kitchenWorkIsFinished = kitchenWorkIsFinished;
	}
	public double getSalary() {
		return salary;
	}
	public void setSalary(double d) {
		this.salary = d;
	}
	public String getMyName() {
		return myName;
	}
}