import java.util.concurrent.atomic.AtomicInteger;

public class MyCounter { // That object assist by counting synchronised
	private AtomicInteger counter;
	
	public MyCounter() {// the constructor that initialise every counter to zero
		this.counter = new AtomicInteger(0);
	}
	public int getCount() {
		return counter.get();
	}
	public int getAndIncreaseCount() {// a method of the class atomicInteger that add 1 to the counter every time you call it.
		return counter.incrementAndGet();
	}
	@Override
	public String toString() {
		return "MyCounter [counter=" + counter + "]";
	}
	public synchronized AtomicInteger getCounter() {
		return counter;
	}
}