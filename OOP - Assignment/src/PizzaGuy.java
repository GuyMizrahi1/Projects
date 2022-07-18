import java.util.Vector;
import java.util.concurrent.atomic.AtomicBoolean;
public class PizzaGuy extends Employee implements Runnable{ // The object implements run so that it could inherit thread methods
	@SuppressWarnings("unused")
	private String name;
	private int totalTip;
	private int capacity;
	private int amountOfDeliveries;
	private double salary;
	private double dayliyDistance;
	private static boolean  lastTenAssist;
	private Vector<PizzaDelivery> myDeliveries;
	private MyCounter deliveryCounter;
	private static MyCounter pizzaGuyCount;
	private static boolean pizzaGuyDayIsFinished;
	private static AtomicBoolean lastTen;
	private static AtomicBoolean pizzaGuysAreWorking;
	private static BoundedQueue <PizzaDelivery> deliveryQueue;

	public PizzaGuy(String name,BoundedQueue <PizzaDelivery> deliveryQueue,MyCounter deliveryCounter, MyCounter pizzaguycount) { // that is the constructor that Initialising the object
		PizzaGuy.pizzaGuyCount = pizzaguycount;
		PizzaGuy.lastTenAssist = true;
		this.amountOfDeliveries =0;
		this.name = name;
		this.deliveryCounter = deliveryCounter;
		this.capacity = capacityCalaulate();
		this.myDeliveries = new Vector <PizzaDelivery>();
		PizzaGuy.deliveryQueue= deliveryQueue;
		PizzaGuy.pizzaGuyDayIsFinished = false;
		PizzaGuy.lastTen = new AtomicBoolean (false);
		PizzaGuy.pizzaGuysAreWorking = new AtomicBoolean (true);
	}
	public void run() { //That method is executed the current thread.
		while(!pizzaGuyDayIsFinished) {
			if(!getLastTen().get()) {
				settingUpDelivery(capacity);
			}
			if(getLastTen().get() ) {
				settingUpDelivery(1);
			}
		}
		PizzaGuy.pizzaGuysAreWorking.set(false);
		deliveryQueue.extract(pizzaGuysAreWorking);
		pizzaGuyCount.getCounter().decrementAndGet();
	}
	public void settingUpDelivery(int limit) { // that method responsible of announcing the manager the number of orders at the time.
		PizzaDelivery box = null ;
		synchronized(this) {
			for(int i = 0; i < limit; i++) {

				box =deliveryQueue.extract(pizzaGuysAreWorking);

				if(pizzaGuysAreWorking.get() && box!=null) { 
					deliveryCounter.getCounter().incrementAndGet();
					this.getMyDeliveries().add(box);
					Manager.getImWorking().set(false);
					Manager.getManagerQueue().extract(Manager.getImWorking());
					if(lastTen.get())
						break;

				}	
			}
		}
		if(lastTen.get()&&lastTenAssist) {// if there are pizzaGuys that had waited they'll drop their deliveries and start from taking one order at the time
			while (!this.getMyDeliveries().isEmpty()) {
				deliveryQueue.insert(this.myDeliveries.elementAt(0),false);
				deliveryCounter.getCounter().decrementAndGet();
				this.myDeliveries.remove(0);
			}
			lastTenAssist=false;
		}
		if(! myDeliveries.isEmpty()) {
			ride(limit);
		}
	}
	public void ride(int limit) { // that method is responsible to emphasise an actual ride and simulate of sleeping time as they had the time to reach the house.
		double	rideWorkTime = 0;
		double workTime =0;
		for(int i = 0; i < myDeliveries.size(); i++) {
			if(myDeliveries.elementAt(0)!=null)
				workTime = myDeliveries.elementAt(i).getDistance();// the arrival time is equal to the distance because of the speed of 1km/second.
			try {
				this.getMyDeliveries().removeAllElements();
				Thread.sleep((long)(1000*workTime)); // the time it take to the pizzaGuy to drive 
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			int tip =((int)Math.random()*15);
			this.setTotalTip(tip);
			try {
				Thread.sleep((long)(1000)); // the time it take to the pizzaGuy to get the tip.
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			rideWorkTime += workTime;
		}
		this.increaseDayliyDistance(rideWorkTime); // count the whole distance that the pizza guy ride that day.
		amountOfDeliveries++;
		this.setSalary(salaryCalculation());
	}
	public static AtomicBoolean getPizzaGuysAreWorking() {
		return pizzaGuysAreWorking;
	}
	public int capacityCalaulate() { // Initialising the capacity for each pizzaGuy
		int random = (int) (2 + Math.random()*2);
		return random;
	}
	public double salaryCalculation() {// that method is responsible to calculate the each pizzaguy's salary after every drive. 
		double payment = 3*this.getAmountOfDeliveries() + 4*this.getDayliyDistance() + this.getTotalTip();
		return payment;
	}
	public int getTotalTip() {
		return totalTip;
	}
	public void increaseDayliyDistance(double dayliyDistance) {
		this.dayliyDistance += dayliyDistance;
	}
	public void setTotalTip(int tip) {
		this.totalTip += tip;
	}
	public double getSalary() {
		return salary;
	}
	public void setSalary(double salary) {
		this.salary = salary;
	}
	public int getAmountOfDeliveries() {
		return amountOfDeliveries;
	}
	public MyCounter getDeliveryCounter() {
		return deliveryCounter;
	}
	public void setDeliveryCounter(MyCounter deliveryCounter) {
		this.deliveryCounter = deliveryCounter;
	}
	public double getDayliyDistance() {
		return dayliyDistance;
	}
	public Vector<PizzaDelivery> getMyDeliveries() {
		return myDeliveries;
	}
	public static AtomicBoolean getLastTen() {
		return lastTen;
	}
	public static void setPizzaGuyDayIsFinished(boolean pizzaGuyDayIsFinished) {
		PizzaGuy.pizzaGuyDayIsFinished = pizzaGuyDayIsFinished;
	}
	public static MyCounter getPizzaGuyCount() {
		return pizzaGuyCount;
	}
}