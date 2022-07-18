import java.awt.EventQueue;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.border.EmptyBorder;
import javax.swing.JLabel;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JButton;
import java.awt.Color;

@SuppressWarnings("serial")
public class PizzaGui extends JFrame { // By the GUI we can allow users to interact with the java code through graphical icons, by using it the program execute.

	private JPanel contentPane;
	private JTextField timeOfWork;
	private JTextField numOfPizzaGuy;

	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					PizzaGui frame = new PizzaGui();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}
	public PizzaGui() { //// the constructor that initialise the start pane.
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);	 //boot of the pane
		setBounds(100, 100, 450, 300);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		contentPane.setLayout(null);
		setTitle("The Best Virtual Pizza You'll Ever Get");
		
		JLabel lblWelcomToOg = new JLabel("Welcom To O&G Pizza!");//set a title
		lblWelcomToOg.setFont(new Font("Tahoma", Font.BOLD | Font.ITALIC, 25));
		lblWelcomToOg.setBounds(75, 32, 303, 65);
		contentPane.add(lblWelcomToOg);

		JLabel lblKitchenWorkers = new JLabel("Kitchen Workers Working Time");
		lblKitchenWorkers.setFont(new Font("Tahoma", Font.ITALIC, 18));
		lblKitchenWorkers.setBounds(30, 105, 252, 38);
		contentPane.add(lblKitchenWorkers);

		JLabel lblNumberOfPizza = new JLabel("Number Of Pizza Guys");
		lblNumberOfPizza.setFont(new Font("Tahoma", Font.ITALIC, 18));
		lblNumberOfPizza.setBounds(40, 154, 196, 28);
		contentPane.add(lblNumberOfPizza);

		JButton btnNewButton = new JButton("START"); // Link button to start the program
		btnNewButton.setBackground(Color.GREEN);
		btnNewButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				double doub = parseDoubleD(timeOfWork,1.0);
				int num = parseIntI(numOfPizzaGuy,2);
				Branch OG = new Branch(doub,num); 
				OG.lifeGenerator("assignment4_callsData.txt");
			}
		});
		btnNewButton.setFont(new Font("Tahoma", Font.BOLD, 18));
		btnNewButton.setBounds(99, 215, 102, 23);
		contentPane.add(btnNewButton);

		JButton btnNewButton_1 = new JButton("EXIT"); // option to close the pane
		btnNewButton_1.setBackground(Color.RED);
		btnNewButton_1.addActionListener (new ActionListener() {
			 public void actionPerformed (ActionEvent e) {
			  System.exit(0);
			 }
		});
		btnNewButton_1.setFont(new Font("Tahoma", Font.BOLD, 18));
		btnNewButton_1.setBounds(278, 215, 102, 23);
		contentPane.add(btnNewButton_1);
		timeOfWork = new JTextField(); // set a place for input
		timeOfWork.setBounds(292, 117, 86, 20);
		contentPane.add(timeOfWork);
		timeOfWork.setColumns(10);
		numOfPizzaGuy = new JTextField(); // set a place for input
		numOfPizzaGuy.setBounds(292, 161, 86, 20);
		contentPane.add(numOfPizzaGuy);
		numOfPizzaGuy.setColumns(10);  
	}
	public static double parseDoubleD(JTextField doub, double defaultVal) { // set a default variable
        if (doub == null || doub.getText().trim().isEmpty()) 
            return defaultVal;
        else
        	return Double.parseDouble(doub.getText());
	}
	public static int parseIntI(JTextField inti, int defaultVal) { // set a default variable
        if (inti == null || inti.getText().trim().isEmpty()) 
            return defaultVal;
        else
        	return Integer.parseInt(inti.getText());
	}
}