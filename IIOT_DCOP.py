import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as stl
import tqdm


def agent_generator(group_size=30):  # generates agents
    neighborhood = []
    for i in range(group_size):
        neighborhood.append(Agent(i))
    return neighborhood


def neighbor_matching(agents, p):  # essentially builds the graph, meaning who is connected to who
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            if random.random() <= p:
                constraint_table = np.random.randint(1, 10, size=(10, 10))  # creating constraints table
                agents[i].neighbors[agents[j].name] = constraint_table  # passing the same table for both ends
                agents[j].neighbors[agents[i].name] = constraint_table
    return agents


def pick_assignment_and_notify_neighbors(agents):  # method is used at the start of dsa solve
    mail_bucket = []
    for i in range(len(agents)):
        agents[i].variable = random.randint(0, 9)  # choose random assignment for each agent
        for key in agents[i].neighbors:
            mail_bucket.append(Message(agents[i].name, key, agents[i].variable))  # posting messages into bucket
    return mail_bucket


def calculate_cost_vector(message, agent, cost_vector):  # method sums up rows to one vector
    if message.pub < message.sub:  # we want to make sure where always accessing the constraint tables in the same order
        cost_vector += agent.neighbors[message.pub][message.val]
    else:
        cost_vector += np.transpose(agent.neighbors[message.pub][:, message.val])  # transposing col into row
    return cost_vector


def chance_to_change_to_min_assignment(cost_vector, p, agent, total_cost_of_iteration):  # method is used in dsa_solve
    min_assignments = np.where(cost_vector == np.amin(cost_vector))  # finds the indices of the minimal cost
    min_assignment = np.amin(min_assignments)  # takes the lower index
    if random.random() <= p:  # chance to change assignment
        agent.variable = min_assignment
    total_cost_of_iteration = total_cost_of_iteration + cost_vector[agent.variable]  # summing the cost of the current-
    return total_cost_of_iteration  # -assignment


def generate_r(agent):
    # By adding up all the fines for each assignment, it is possible to distinguish what the preferred
    # assignment is, and able to calculate the reduced cost(R)
    min_assignments = np.where(agent.cost_vector == np.amin(agent.cost_vector))  # finds the indices of the minimal cost
    agent.potential_assignment = np.amin(min_assignments)  # takes the lower index
    agent.r = agent.cost_vector[agent.variable] - agent.cost_vector[agent.potential_assignment]


def best_possible_local_reduction(agent, reduce_bucket):
    if agent.r > 0:  # if the R is negative there is no reason to check the reduce_bucket
        greater_then_neighbors = True
        for message in reduce_bucket:
            if agent.name == message.sub:
                if agent.r < message.val:
                    # if there is even one neighbor with greater R, the agent assignment wouldn't change
                    greater_then_neighbors = False
                    break
                if agent.r == message.val:
                    # if there is a neighbor with the same R, the agent with the lower
                    # serial number will change his assignment
                    if agent.name > message.pub:
                        greater_then_neighbors = False
                        break
        if greater_then_neighbors:
            agent.variable = agent.potential_assignment


def solve_dsa(p, agents, iteration_number=0):  # Distributed stochastic algorithm
    cost_per_iteration = np.array([0] * 100)
    mail_bucket = pick_assignment_and_notify_neighbors(agents)  # method is responsible of picking the first assignment
    # randomly and notify all neighbors
    while iteration_number < 100:  # termination condition
        total_cost_of_iteration = 0
        mail_bucket2 = []
        for agent in agents:
            cost_vector = np.array([0] * 10)
            for message in mail_bucket:
                if agent.name == message.sub:  # if any of the messages are addressed to the current agent were looking-
                    cost_vector = calculate_cost_vector(message, agent, cost_vector)  # -at -> sum total cost by row\col
            total_cost_of_iteration = chance_to_change_to_min_assignment(cost_vector, p, agent, total_cost_of_iteration)
            for key in agent.neighbors:  # after the possible change of assignment -> notify all neighbors of current-
                mail_bucket2.append(Message(agent.name, key, agent.variable))  # -assignment
        cost_per_iteration[iteration_number] = total_cost_of_iteration / 2  # collecting data points for the-
        mail_bucket = mail_bucket2  # -requested graph
        iteration_number += 1
    return cost_per_iteration


def solve_mgm(agents, iteration_number=0):
    cost_per_iteration = np.array([0] * 100)
    mail_bucket = pick_assignment_and_notify_neighbors(agents)  # method is responsible of picking the first assignment
    # randomly and notify all neighbors
    while iteration_number < 100:  # termination condition
        total_cost_of_iteration = 0
        reduce_bucket = []
        mail_bucket2 = []
        for agent in agents:
            agent.cost_vector = np.array([0] * 10)
            for message in mail_bucket:
                if agent.name == message.sub:  # if any of the messages are addressed to the current agent were looking
                    agent.cost_vector = calculate_cost_vector(message, agent, agent.cost_vector)  # at,sum total cost
            generate_r(agent)
            for key in agent.neighbors:
                reduce_bucket.append(Message(agent.name, key, agent.r))
        iteration_number += 1   # The first iteration is over when all the reduced costs(R) has been sent.
        for agent in agents:
            best_possible_local_reduction(agent, reduce_bucket)  # select highest R from neighbors,and update assignment
            for key in agent.neighbors:
                mail_bucket2.append(Message(agent.name, key, agent.variable))
            total_cost_of_iteration += agent.cost_vector[agent.variable]
        cost_per_iteration[iteration_number - 1] = total_cost_of_iteration / 2
        cost_per_iteration[iteration_number] = total_cost_of_iteration / 2
        mail_bucket = mail_bucket2
        # Second iteration is over when all the assignments has been sent.
        iteration_number += 1
    return cost_per_iteration


def graph_generator(average_data_dsa1_p1_02, average_data_dsa2_p1_02, average_data_mgm_p1_02, average_data_dsa1_p1_05,
                    average_data_dsa2_p1_05, average_data_mgm_p1_05):  # method gets all data points and assemble 2 sub
    # plots- side by side - as requested.
    stl.use("ggplot")
    Y1 = average_data_dsa1_p1_02
    Y2 = average_data_dsa2_p1_02
    Y3 = average_data_mgm_p1_02
    Z1 = average_data_dsa1_p1_05
    Z2 = average_data_dsa2_p1_05
    Z3 = average_data_mgm_p1_05
    X = list(range(0, 100))
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle('The Average Cost As A Function Of The Number Of Iteration')
    plt.title('P1 = 0.2         VS         P1 = 0.5', x=-0.1)
    ax1.plot(X, Y1, "orange", label="p = 0.7", linewidth=2.2)  # ax1-first plot- p1 = 0.2
    ax1.plot(X, Y2, "black", label="p = 0.4", linewidth=2.2)
    ax1.plot(X, Y3, "green", label="mgm", linewidth=2.2)
    ax2.plot(X, Z1, "orange", label="p = 0.7", linewidth=2.2)  # ax2-second plot- p1 = 0.5
    ax2.plot(X, Z2, "black", label="p = 0.4", linewidth=2.2)
    ax2.plot(X, Z3, "green", label="mgm", linewidth=2.2)
    plt.grid(True, color="Black")
    plt.ylabel("Y - Average Cost")
    plt.xlabel("X - Number Of Iteration")
    plt.legend()
    plt.show()


def graph_operator(p1, dsa1_results=np.array([0] * 100), dsa2_results=np.array([0] * 100),
                   mgm_results=np.array([0] * 100), at_least_10_runs=10):  # solve by 2 different algorithms (dsa/mgm)
    for _ in tqdm.tqdm(range(at_least_10_runs), 'Collecting Data From 10 Random Problems (P1 = ' + str(p1) + ')---->>'):
        agents = neighbor_matching(agent_generator(), p1)
        dsa1_results += np.array(solve_dsa(0.7, agents))  # dsa with p = 0.7
        dsa2_results += np.array(solve_dsa(0.4, agents))  # dsa with p = 0.4
        mgm_results += np.array(solve_mgm(agents))  # mgm
    average_of_data_points_dsa1 = (dsa1_results / 10).tolist()
    average_of_data_points_dsa2 = (dsa2_results / 10).tolist()
    average_of_data_points_mgm = (mgm_results / 10).tolist()
    return average_of_data_points_dsa1, average_of_data_points_dsa2, average_of_data_points_mgm  # returns the average-
    # -data points -> used to plot 3 different lines.


def solve():  # method that runs the whole shebang
    average_data_dsa1_p1_02, average_data_dsa2_p1_02, average_of_data_points_mgm_p1_02 = graph_operator(0.2)
    average_data_dsa1_p1_05, average_data_dsa2_p1_05, average_of_data_points_mgm_p1_05 = graph_operator(0.5)
    graph_generator(average_data_dsa1_p1_02, average_data_dsa2_p1_02, average_of_data_points_mgm_p1_02,
                    average_data_dsa1_p1_05, average_data_dsa2_p1_05, average_of_data_points_mgm_p1_05)


class Agent:
    def __init__(self, name):
        self.name = name
        self.variable = None
        self.neighbors = {}
        self.inbox = None
        self.outbox = None
        self.r = None
        self.potential_assignment = None
        self.cost_vector = None


class Message:
    def __init__(self, pub, sub, val):
        self.pub = pub
        self.sub = sub
        self.val = val


if __name__ == '__main__':
    print('Run Directly')
    solve()
else:
    print("Run From Import")
    solve()
