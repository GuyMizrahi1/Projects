import java.util.Vector;
public class PizzaDelivery {// That Object is call that transformed into order and now become a PizzaDelivery with the fields that had to change.
	private double distance;
	private double amount;
	private String address;
	private Vector<Pizza> pizzaBox;

	public PizzaDelivery (String address, double distance, double amount){ //The constructor that initialise every PizzaDelivery.
		this.address= address;
		this.distance= distance;
		this.amount= amount;
		this.pizzaBox= new Vector <Pizza>();
	}
	public void createSingleDelivery() { // that method responsible to add each pizza that the kitchenWorker made into the pizza delivery.
		for(int i=0;i<this.amount;i++) {
			this.getPizzaBox().add(new Pizza());
		}
	}
	public Vector<Pizza> getPizzaBox() {
		return pizzaBox;
	}
	public double getDistance() {
		return distance;
	}
	public String getAddress() {
		return address;
	}
}