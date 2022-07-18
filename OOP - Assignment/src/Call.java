import java.util.concurrent.atomic.AtomicBoolean;

public class Call implements Runnable  { // The object implements run method so that it could inherit thread methods
	private int id;
	private int amount;
	private int creditNum;
	private int arrivalTime;
	private double waitigTime;
	private boolean doneCall;
	private AtomicBoolean onGoingCall ;
	private String address;
	private Queue<Call> callQueue;
	
	public Call (String record , int id ,Queue<Call> callQueue,Queue<Call> managerQueue) {// the constructor that initialise every call by the fields that has been in the text file.
		String [] callFields = record.split("\t");
		this.id = id;
		this.doneCall= false;
		this.creditNum = Integer.parseInt(callFields[0]);
		this.amount = Integer.parseInt(callFields[1]);
		this.arrivalTime = Integer.parseInt(callFields[2]);
		this.waitigTime = Double.parseDouble(callFields[3]);
		this.address = callFields[4];
		this.callQueue = callQueue;
		this.onGoingCall= new AtomicBoolean(true);	
	}
	public void run() {  //That method is executed the current thread.
		boolean temp = true;
		while(onGoingCall.get()) {
			try {
				if(temp) {
					Thread.sleep(this.arrivalTime*1000); // the arrival time of each call will simulate by sleep
					callQueue.insert(this);
					temp= false;
				}
			}
			catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}
	public boolean getDoneCall() {
		return doneCall;
	}
	public void setDoneCall(boolean doneCall) {
		this.doneCall = doneCall;
	}
	public int getArrivalTime() {
		return arrivalTime;
	}
	public int getAmount() {
		return amount;
	}
	public int getCreditNum() {
		return creditNum;
	}
	public String getAddress() {
		return address;
	}
	public int getId() {
		return id;
	}
	public double getWaitigTime() {
		return waitigTime;
	}
	public AtomicBoolean getOnGoingCall() {
		return onGoingCall;
	}
	public void setOnGoingCall(AtomicBoolean shouldExit) {
		this.onGoingCall = shouldExit;
	}
}
