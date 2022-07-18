public class Order { // That Object is call that transformed into order and will deliver as a PizzaDelivery.
	private int id;
	private double totalPrice;
	private double distance;
	private Call call;
	
	public Order(Call c,Queue <Order> schedulerQueue,InformationSystem <Order> infoSystem, int id) {// the constructor that initialise every order.
		this.call = c;
		this.id = id;
	}
	public void setTotalPrice(double totalPrice) {
		this.totalPrice = totalPrice;
	}
	public double getTotalPrice() {
		return totalPrice;
	}
	public Call getCall() {
		return this.call;
	}
	public double getDistance() {
		return distance;
	}
	public void setDistance(double distance) {
		this.distance = distance;
	}
	public int getId() {
		return id;
	}
	public String toString() { // override the toString method for the print of the orders
		return "Order Number: " + id + " " + "Price: " + totalPrice + " " + "Distance: " + distance + " " +
	"Address: " + call.getAddress()+ " "  + "Credit Number: " +call.getCreditNum();
	}
}