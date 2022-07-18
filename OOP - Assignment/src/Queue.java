import java.util.Vector;
import java.util.concurrent.atomic.AtomicBoolean;
public class Queue<T> { 
	private Vector<T> buffer;
	
	public Queue() { //Constructor of Queue is responsible of creating a vector 
		buffer = new Vector <T>();
	}
	public synchronized void insert(T t) { // Synchronised method responsible of inserting objects one by one.
		buffer.add(t);
		this.notifyAll(); 
	}
	public synchronized  T extract(AtomicBoolean inProcess) { // Synchronised method responsible of extracting objects one by one
		if(!inProcess.get()) { // Atomic boolean is part of "end of day" protocol- last worker/manger uses this segment in order to wake up all other workers that are "stuck" in wait (expecting for more "work" to come)  
			this.notifyAll(); // wake up any thread stuck in wait
			return null;}  // return nothing cause you DIDNT extract any object
		else {
			while(buffer.isEmpty()&&inProcess.get()) { // as long as the vector is empty AND its still working time >> wait
				try {
					this.wait();
				} catch (InterruptedException e) {
					e.printStackTrace();
				}}
			if(!inProcess.get()) { // when its end of day there are no more "work to come" >> worker will return null  and come out empty handed 
				return null;
			}
			else { // in any other case worker will extract the object
				T t = buffer.elementAt(0);
				buffer.remove(0);
				return t;
			}
		}
	}
}
