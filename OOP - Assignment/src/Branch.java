import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Vector;
public class Branch {
	private int numOfPizzaGuys;
	private double timeOfWork;
	private int quantityOfCalls;
	private Queue <Call> callQueue ;
	private Queue <Call> managerQueue ;
	private Vector <Thread> threads ;
	private static  MyCounter MyCount;
	private static  MyCounter deliveryCounter;
	private static Queue <Order> schedulerQueue ;
	private static InformationSystem <Order> infoSystem ;
	private static Vector <Employee> EmpList ;
	private static BoundedQueue <PizzaDelivery> deliveryQueue ;

	public Branch(double timeOfWork,int numOfPizzaGuys) { //Constructor of Branch 
		this.quantityOfCalls = 0;
		this.timeOfWork = timeOfWork;
		this.numOfPizzaGuys = numOfPizzaGuys;
		this.callQueue =  new Queue<Call>();
		this.managerQueue =  new Queue<Call>();
		this.threads =  new Vector<Thread>();	
		Branch.deliveryCounter = new MyCounter();
		Branch.deliveryQueue= new BoundedQueue<PizzaDelivery>();
		Branch.MyCount= new MyCounter();
		Branch.infoSystem =  new InformationSystem <Order>();
		Branch.schedulerQueue =  new Queue<Order>();
		Branch.EmpList = new Vector<Employee>();
	}
	public void lifeGenerator (String filePath) { // method is responsible of calling all other generators 
		callGenerator(filePath); 
		clerkGenarator();
		schedulerGenarator();
		kitchenWorkerGenarator();
		pizzaGuyGenarator ();
		managerGenerator();
		threadGenerator();
	}
	public void callGenerator (String filePath) { //method responsible of extracting data from text file and generating a thread calls
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(filePath));
			String line;
			br.readLine();
			int counter = 1;
			while((line = br.readLine())!=null) {// as long as the data file has another line keep going
				Call c = new Call(line, counter,callQueue,managerQueue); // creates a new instance of call
				Thread t = new Thread (c);// making a thread out of it
				threads.add(t); // add thread into threads vector
				this.quantityOfCalls=counter; // count amount of incoming calls
				counter++;
			}
		}
		catch (FileNotFoundException ex) {
			System.out.println("The file was not found.");
		}
		catch (IOException e) {
			System.out.println(e);
		}
		finally {
			try {
				br.close();
			}catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	public void kitchenWorkerGenarator () {//method responsible of generating an instance of kitcheanWorker creating a thread out of it and adds it to thread vector
		for (int i = 1; i <= 3; i++) {
			KitchenWorker sheff = new KitchenWorker("LaSheff "+ i,deliveryQueue,infoSystem,timeOfWork);
			Thread t = new Thread(sheff);
			threads.add(t);
			EmpList.add(sheff); // manager gets a list of all employees to calculate total cost of labour
		}
	}
	public void clerkGenarator () { //method responsible of generating an instance of clerk creating a thread out of it and adds it to thread vector
		for (int i = 0; i < 3; i++) {
			Clerk emp = new Clerk(i,this.quantityOfCalls, callQueue, schedulerQueue,managerQueue,MyCount);
			Thread t = new Thread(emp);
			threads.add(t);
			EmpList.add(emp);
		}
	}
	public void schedulerGenarator () { //method responsible of generating an instance of scheduler creating a thread out of it and adds it to thread vector
		Scheduler Yossi = new Scheduler(schedulerQueue,infoSystem,"Yossi");
		Scheduler Barney = new Scheduler(schedulerQueue,infoSystem,"Barney");
		Thread t1 = new Thread(Yossi);
		Thread t2 = new Thread(Barney);
		threads.add(t1);
		threads.add(t2);
		EmpList.add(Yossi); // manager gets a list of all employees to calculate total cost of labour
		EmpList.add(Barney);
	}
	public void managerGenerator () { //method responsible of generating an instance of manager creating a thread out of it and adds it to thread vector
		Manager manager = new Manager(this.quantityOfCalls,managerQueue,infoSystem,MyCount,deliveryCounter,EmpList);
		Thread t = new Thread(manager);
		t.setPriority(10);
		threads.add(t);
	}
	public void pizzaGuyGenarator () { //method responsible of generating an instance of pizzaGuy creating a thread out of it and adds it to thread vector
		MyCounter pizzaGuys = new MyCounter();
		pizzaGuys.getCounter().set(numOfPizzaGuys);
		for (int i = 0; i < numOfPizzaGuys ; i++) {
			PizzaGuy emp = new PizzaGuy("i",deliveryQueue,deliveryCounter,pizzaGuys);
			Thread t = new Thread(emp);
			threads.add(t);
			EmpList.add(emp);
		}
	}
	public void threadGenerator() { // this method is responsible of "starting work day"
		for (int i = 0; i < threads.size(); i++) {
			threads.get(i).start();
		}
	}
	public int getQuantityOfCalls() {
		return quantityOfCalls;
	}
	public static Queue <Order> getschedulerQueue() {
		return schedulerQueue;
	}
	public static InformationSystem<Order> getInfoSystem() {
		return infoSystem;
	}
	public static BoundedQueue<PizzaDelivery> getDeliveryQueue() {
		return deliveryQueue;
	}
}

