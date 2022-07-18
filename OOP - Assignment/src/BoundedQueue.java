import java.util.Vector;
import java.util.concurrent.atomic.AtomicBoolean;
class BoundedQueue<T> {
	private int maxSize;
	private Vector<PizzaDelivery> buffer;

	public BoundedQueue () { //Constructor of Queue is responsible of creating a vector 
		buffer = new Vector<PizzaDelivery>(); 
		this.maxSize=12;
	}
	public synchronized void insert(PizzaDelivery item,boolean inProcess) { // Synchronised method responsible of inserting objects one by one.
		if(!inProcess) {
			buffer.add(item);
		}
		else {
			while(buffer.size()>=maxSize) { // this queue has a max limit set to 12 >> if there are more than 12 elements "in queue" the object(the thread) trying to use this insert method will wait 
				try {
					wait();
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			buffer.add(item);
			notifyAll();  
		}
	}
	public synchronized PizzaDelivery extract(AtomicBoolean inProcess)  {  // Synchronised method responsible of extracting objects one by one
		if(!inProcess.get()) {  // Atomic boolean is part of "end of day" protocol- last worker/manger uses this segment in order to wake up all other workers that are "stuck" in wait (expecting for more "work" to come)  
			this.notifyAll(); // wake up any thread stuck in wait
			return null; // return nothing cause you DIDNT extract any object
		}
		else {
			while (buffer.isEmpty() && inProcess.get()) { // as long as the vector is empty AND its still working time >> wait
				try {
					wait();
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			if(!inProcess.get()) {  // when its end of day there are no more "work to come" >> worker will return null  and come out empty handed 
				return null;
			}
			else {
				PizzaDelivery item = buffer.elementAt(0); // in any other case worker will extract the object
				buffer.remove(item);
				notifyAll();
				return item; 
			}
		} 
	}
}