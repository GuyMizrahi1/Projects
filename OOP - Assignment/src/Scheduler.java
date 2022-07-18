import java.util.concurrent.atomic.AtomicBoolean;

public class Scheduler extends Employee implements Runnable {  // The object implements run method so that it could inherit thread methods
	@SuppressWarnings("unused")
	private String name;	
	private double salary;
	private double workTime;
	private static boolean schedulerDayIsFinished;
	private static AtomicBoolean schedulersAreWorking;
	private static Queue<Order> schedulerQueue;
	private static InformationSystem <Order> infoSystem ;

	public Scheduler (Queue<Order> schedulerQueue, InformationSystem<Order> infoSystem, String Name ) {// that is the constructor that Initialising the object
		this.name = Name;
		this.salary=0;
		Scheduler.schedulerDayIsFinished= false;
		Scheduler.schedulersAreWorking = new AtomicBoolean(true);
		Scheduler.schedulerQueue = schedulerQueue;
		Scheduler.infoSystem = infoSystem;
	}
	public void run(){ //That method is executed the current thread.
		while (!schedulerDayIsFinished) {
			Order o = schedulerQueue.extract(schedulersAreWorking);  // unless he didn't finish his work day he won't stop try to extract new orders-
			if(schedulersAreWorking.get()) {						// -the manger will change that atomicBoolean an than the thread will die.
				giveService(o);
			}
		}
	}
	public void giveService (Order o) { // that method is simulate the time of transform an order into the information system 
		o.setDistance(distanceCalculator(o));
		setWorkTime(o.getDistance()*0.25);
		salary = (getWorkTime()*4);
		try {
			Thread.sleep((long)(getWorkTime()));
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		infoSystem.insert(o);
	}
	public double distanceCalculator (Order o) { // that method calculate the distance by the quantity of words and the value of the first letter as described in the method.
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
	public static void setSchedulerDayIsFinished(boolean schedulerDayIsFinished) {
		Scheduler.schedulerDayIsFinished = schedulerDayIsFinished;
	}
	public void setWorkTime(double workTime) {
		this.workTime = workTime;
	}
	public double getWorkTime() {
		return workTime;
	}
	public static AtomicBoolean getSchedulersWorking() {
		return schedulersAreWorking;
	}
	public double getSalary() {
		return salary;
	}
}