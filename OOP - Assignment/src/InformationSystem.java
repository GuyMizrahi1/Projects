import java.util.*; 
public class InformationSystem<T> {
	private double totalProfit;
	private  Vector<Order> dataBase;
	private  Vector <Order> threeKmToP;
	private  Vector <Order> eightKmToP;
	private  Vector <Order> eightKmAndAbove;

	public InformationSystem() {  //Constructor of Queue is responsible of creating 4 vectors and sets total profit to 0
		this.dataBase = new Vector <Order>();
		this.threeKmToP = new Vector <Order>();
		this.eightKmToP = new Vector <Order>();
		this.eightKmAndAbove = new Vector <Order>();
		this.totalProfit = 0;
	}
	public synchronized void insert(Order o) { // Synchronised method responsible of inserting objects one by one.
		dataBase.add(o); //any order that is being added first gets saved in database vector
		System.out.println("New Order Arrived " + o.getId());  // after an order gets saved >> we classify them by their distance 
		if(o.getDistance()<=3.0) {
			threeKmToP.add(o); // 
			this.notifyAll();
		}
		else if(o.getDistance()>3.0 && o.getDistance()<=8.0) {
			eightKmToP.add(o);
			this.notifyAll();
		}
		else {
			eightKmAndAbove.add(o);
			this.notifyAll();
		}
		updatedProfit(); // whenever an order gets inserted into our information system we reevaluate the total profit
	}
	public synchronized  Order extract() {  // Synchronised method responsible of extracting objects one by one
		while(dataBase.isEmpty()) { //  at first  kitchen workers wait for incoming orders 
			try {
				this.wait();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
		if(!threeKmToP.isEmpty()) { // they will try to get an order from the threeKmToP first
			Order o = threeKmToP.elementAt(threeKmToP.size()-1);
			threeKmToP.remove(o);

			return o;
		}
		else if(!eightKmToP.isEmpty()) { // than from eightKmToP
			Order o = eightKmToP.elementAt(eightKmToP.size()-1);	
			eightKmToP.remove(o);

			return o;
		}
		else if(!eightKmAndAbove.isEmpty()) { // and finally from eightKmAndAbove
			Order o = eightKmAndAbove.elementAt(eightKmAndAbove.size()-1);
			eightKmAndAbove.remove(o);
			return o;
		}
		return null;
	}
	public void updatedProfit() { // method is responsible of calculating total branch profit
		double totalorderprofit=0;
		for(int i=0 ; i<dataBase.size();i++) {
			totalorderprofit+=dataBase.elementAt(i).getTotalPrice();
		}
		setTotalProfit(totalorderprofit);
	}
	public double getTotalProfit() {
		return totalProfit;
	}

	public void setTotalProfit(double totalProfit) {
		this.totalProfit = totalProfit;
	}
}


