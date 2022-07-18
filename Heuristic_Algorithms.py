import copy
import numpy as np
# TODO: if you haven't installed networkx, open the search line in your computer and write cmd,
# then press enter, and then write: pip install networkx, after the installation is done the code would run
import networkx as nx
import math
import random


class Cell:  # In simulate annealing & local beam I chose to implement the every move by an object of cell
    def __init__(self, location, board_len, state):
        self.location = location
        self.board_len = board_len
        self.state = state
        self.optional_moves = []
        self.neighbors = []
        self.parent = None
        self.best_neighbors = []
        self.h = 0
        self.target_in_solution = 0
        self.part_of_the_solution = False
        self.route = []  # those fields helped the route to save the paths of the parents
        self.mom_path = []
        self.dad_path = []
        self.path_by_parents = []

    def __repr__(self):
        return f'({self.location[0]},{self.location[1]})->'

    def get_row(self):
        return self.location[0]

    def get_column(self):
        return self.location[1]

    def get_location(self):
        return self.location

    def get_board_len(self):
        return self.board_len

    def get_state(self):
        return self.state

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)


class Route:  # With that object I chose to implement genetic algorithm by using directions and avoid discontinuity when to routes merge to a new one
    def __init__(self, adam_cell, target_cell):
        self.adam_cell = adam_cell
        self.target_cell = target_cell
        self.current_location = np.array([adam_cell.location[0], adam_cell.location[1]])
        self.fitness = 0
        self.probability_to_be_selected = 0
        self.probabilities = []
        self.mom = None
        self.dad = None
        self.mutation = False
        self.directions_by_parents = [(self.current_location, 1)]
        self.directions = []

    def __repr__(self):
        return f'({self.current_location[0]},{self.current_location[1]})->'


def create_grid(start_board):
    grid = nx.DiGraph()  # Initialize the grid to be directed graph with NetworkX assistance.
    cell_grid = []  # Initialize paths as a 2D list with 0.
    create_edges(grid, cell_grid, start_board)
    create_vertexes(grid, cell_grid, start_board)
    vertexes_to_fictive_cell(grid, cell_grid, start_board)
    return grid, cell_grid


def create_edges(grid, cell_grid, start_board):
    for i in range(len(start_board)):
        cell_grid.append([])
        for j in range(len(start_board)):  # The grid would not contain force fields
            cell = Cell((i, j), len(start_board), start_board[i][j])
            cell_grid[i].append(cell)
            if start_board[i][j] != 1:  # that an agent would consider a path with force field.
                grid.add_node((i, j))


def create_vertexes(grid, cell_grid, start_board):
    for i in range(len(start_board)):
        for j in range(len(start_board)):
            cell = cell_grid[i][j]
            if j < len(start_board) - 1:
                if start_board[i][j] != 1 and start_board[i][j + 1] != 1:
                    right_cell = cell_grid[i][j + 1]
                    cell.add_neighbor(right_cell)
                    right_cell.add_neighbor(cell)
                    grid.add_edges_from([((i, j), (i, j + 1)), ((i, j + 1), (i, j))])
            if i < len(start_board) - 1:
                if start_board[i][j] != 1 and start_board[i + 1][j] != 1:
                    lower_cell = cell_grid[i + 1][j]
                    cell.add_neighbor(lower_cell)
                    lower_cell.add_neighbor(cell)
                    grid.add_edges_from([((i, j), (i + 1, j)), ((i + 1, j), (i, j))])


def vertexes_to_fictive_cell(grid, cell_grid, start_board):
    grid.add_node((len(start_board), len(start_board)))  # Create a vertex that isn't shown on the board
    fictive_cell = Cell((len(start_board), len(start_board)), len(start_board), 0)
    cell_grid.append([fictive_cell])
    for i in range(len(start_board)):  # and connect the lowest row with it by edges.
        if start_board[len(start_board) - 1][i] != 1:
            last_row_cell = cell_grid[len(start_board) - 1][i]
            last_row_cell.add_neighbor(fictive_cell)
            grid.add_edge((len(start_board) - 1, i), (len(start_board), len(start_board)))


# Implement my heuristic between agent and target by Manhattan Distance
def heuristic(node1, node2):
    if node1[0] >= 6 or node2[0] >= 6:  # If the target here is the fictive target
        row = min(node1[0], node2[0])
        return 6 - row  # I would return the heuristic for reaching the bottom of the board
    return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])


def get_shortest_path_by_astar(grid, agent, target):
    try:
        path = nx.astar_path(grid, agent, target, heuristic)  # using A* with NetworkX assistance.
    except:
        path = []
    return path


def get_shortest_path_by_hill_climbing(grid, agent, target):
    final_path = []  # Create a path if exist
    if agent == target:
        return [agent]
    else:
        for k in list(grid.neighbors(agent)):
            my_location = k  # The restart happen here, check all the neighbors
            temp_path = [agent, my_location]
            h = heuristic(my_location, target)
            while h > 0:
                found_step = False
                for l in list(grid.neighbors(my_location)):  # of the agent and from here, execute the hill climbing
                    h_temp = heuristic(l, target)
                    found_step = False
                    if h_temp < h and l not in temp_path:
                        temp_path.append(l)
                        my_location = l
                        h = heuristic(my_location, target)
                        found_step = True
                        break
                if not found_step:
                    break
            if temp_path[len(temp_path) - 1] == target:
                final_path.append(temp_path)
                break
        if len(final_path) > 0:  # Path has found, insert it.
            path = min(final_path)
        else:
            path = []  # If there is no path found the index will be empty
    return path


def get_shortest_path_by_simulated_annealing(agent, target):
    path = [agent.location]
    if not reach_target(agent, target):
        my_location = agent
        optional_move = []
        temperature = 100
        counter = 0
        while True:
            neighbor = random_neighbor(my_location, target)
            if neighbor is not None:
                my_location.h = heuristic(my_location.location, target.location)
                neighbor.h = heuristic(neighbor.location, target.location)
                temperature *= 0.9
                if temperature > 0.001:  # limit the amount of iterations
                    random_prob = round(random.uniform(0, 1), 3)
                    probability = math.exp((my_location.h - neighbor.h) / temperature)  # calculation of the probability
                    if neighbor.h < my_location.h:
                        if counter == 0:
                            optional_move.append((my_location, neighbor, 1))  # local array of possible moves
                            my_location.optional_moves.append(
                                optional_move)  # if we got into the if means it's the last step, therefore i will update the agent field
                        path.append(neighbor.location)
                        my_location = neighbor
                        counter += 1
                        if reach_target(my_location, target):
                            break
                    elif random_prob < probability:  # just if the prob is higher than the random number i'll do that step,
                        if counter == 0:  # as long as the iteration goes the possibility decreased.
                            optional_move.append((my_location, neighbor, round(1 - random_prob, 3)))
                            my_location.optional_moves.append(optional_move)  # insert into the local array of moves
                        path.append(neighbor.location)
                        my_location = neighbor
                        counter += 1
                        continue
                    else:
                        if counter == 0:
                            optional_move.append((my_location, neighbor, random_prob))
                        continue
                else:
                    path.clear()  # If the agent couldn't reach the target after all the iterations it will send an empty path.
                    break
            else:
                path.clear()  # If the agent is surrounded by force fields it would alert that there is no path.
                break
        return path
    else:
        return path


def random_neighbor(my_location, target):  # choose random neighbors from the set of optional neighbors
    if len(my_location.neighbors) != 0:
        for i in range(len(my_location.neighbors)):
            rand = random.choice(my_location.neighbors)
            if rand.location == (rand.board_len, rand.board_len) and rand.location != target.location:
                continue
            else:
                return rand
        return None
    return None


def reach_target(my_location, target):  # simple way to know if i have reached the target by index
    if my_location.location == target.location:
        return True
    else:
        return False


def print_simulated_annealing_probabilities(cell_grid, board, path, tup_agent, tup_next_step, target_by_solution):
    agent = cell_grid[tup_agent[0]][tup_agent[1]]
    if path[0] is not tup_agent:  # means there was usage of the block handler
        actual_start_position = cell_grid[path[0][0]][path[0][1]]
        sec_om = actual_start_position.optional_moves[target_by_solution]
        for i in range(len(sec_om)):
            if sec_om[i][1] == agent:
                next_cell = transfer_tup_to_cell(cell_grid, board, tup_next_step)
                prob = sec_om[i][2]
                sec_om[i] = (agent, next_cell, prob)
        print_probabilities(sec_om, agent)  # prints the probabilities of the first agent in the list
    else:
        om = agent.optional_moves[target_by_solution]
        print_probabilities(om, agent)


def print_probabilities(array, agent):
    for tup in array:
        next_step = tup[1]
        prob = tup[2]
        printed_a_location = '(' + str(agent.location[0] + 1) + ',' + str(agent.location[1] + 1) + ')'
        printed_st_location = '(' + str(next_step.location[0] + 1) + ',' + str(next_step.location[1] + 1) + ')'
        if next_step.location != (agent.board_len, agent.board_len) and next_step.state != 2:
            print('action: ' + printed_a_location + '->' + printed_st_location + '; probability: ' + str(prob))
        else:
            print('action: ' + printed_a_location + '->out' + '; probability: ' + str(prob))


def get_shortest_path_by_local_beam(k, agent, target, cell_grid):
    path = [agent.location]
    all_options = []
    k_options = []
    my_location = agent
    while not reach_target(my_location, target):
        if k_options:  # Empty list is a false value means the first iteration will have different functions
            for i in range(len(k_options)):  # modular way to pick the k neighbors every iteration
                if reach_target(k_options[i], target):
                    final_path = find_path_by_parents(agent, k_options[i])
                    initiate_cells_parents(
                        cell_grid)  # for the next agent that about to get into that function I restarted the parameters that will be irrelevant
                    return final_path
                else:
                    k_neighbors = find_best_neighbors(agent, k_options[i], target,
                                                      k)  # choose the neighbor with the lowest heuristic
                    if k_neighbors:
                        all_options = add_without_duplicates(all_options,
                                                             k_neighbors)  # add the neighbors to all options and avoid duplicates that for the next iteration it wouldn't choose a neighbor than once
        else:  # first iteration
            if all_options:
                k_neighbors = find_best_neighbors(agent, my_location, target, k)
                if k_neighbors:
                    all_options.extend(k_neighbors)
            else:  # first iteration
                k_neighbors = find_best_neighbors(agent, my_location, target, k)
                if k_neighbors:
                    my_location.best_neighbors = k_neighbors
                    all_options.extend(k_neighbors)
                else:
                    return []
        k_options = best_k(k, all_options)
    return path


def best_k(k, all_options):  # choose the best options by heuristic condition
    sorted_options = sorted(all_options, key=lambda cell: cell.h)
    the_k = sorted_options[0:k]
    return the_k


# insert just a legitimate neighbors
def find_best_neighbors(agent, my_location, target, k):
    list_of_neighbors = []
    if len(my_location.neighbors) != 0:
        i = 0
        j = 0
        while i < len(my_location.neighbors):  # update all neighbors heuristic field
            neighbor = my_location.neighbors[i]
            neighbor.h = heuristic(neighbor.location, target.location)
            i += 1
        sorted_neighbors = sorted(my_location.neighbors, key=lambda cell: cell.h)
        while j < len(
                sorted_neighbors):  # add the neighbors until we reach the first k, if there is no k neighbors it will add them all
            neighbor = sorted_neighbors[j]
            if not (neighbor.location == (
            neighbor.board_len, neighbor.board_len) and neighbor.location != target.location):
                if (not neighbor.parent) and (not reach_target(neighbor, agent)):
                    neighbor.parent = my_location
                list_of_neighbors.append(neighbor)
            if len(list_of_neighbors) == k:
                break
            j += 1
    my_location.best_neighbors = list_of_neighbors
    return list_of_neighbors


# make the path by going throw the previous cell
def find_path_by_parents(start_point, my_location):
    path = [my_location.location]
    while not reach_target(start_point, my_location):
        path.insert(0, my_location.parent.location)
        my_location = my_location.parent
    return path


# help avoid duplicates therefore the best k wouldn't considers the best one twice if he was a neighbor of two different cells
def add_without_duplicates(all_options, k_neighbors):
    for cell in k_neighbors:
        if cell not in all_options:
            all_options.append(cell)
    return all_options


def initiate_cells_parents(cell_grid):
    for t_list in cell_grid:
        for cell in t_list:
            cell.parent = None


def print_local_beam_boards(cell_grid, board, tup_agent, agents):
    agent = cell_grid[tup_agent[0]][tup_agent[1]]
    lb = agent.best_neighbors
    temp_lb = []
    counter = 0
    while True:
        if counter == 0:
            for cell in lb:  # make sure there is no other agent in the my considerations
                if not (cell.location == (cell.board_len, cell.board_len)):
                    if (cell not in temp_lb) and (not board[cell.location[0]][cell.location[1]] == 2):
                        cell.parent = agent
                        temp_lb.append(cell)
                else:
                    if cell.best_neighbors:  # empty list means false therefore no one called th fictive node
                        if agent not in cell.best_neighbors:
                            cell.best_neighbors.append(agent)
                    else:
                        cell.best_neighbors.append(agent)
            lb = temp_lb
        if len(lb) == 3:
            break
        elif len(lb) < 3:
            if counter > 0:
                break
            for i in range(len(agents)):
                temp_tup_agent = agents[i]
                temp_agent = transfer_tup_to_cell(cell_grid, board, temp_tup_agent)
                for cell in temp_agent.best_neighbors:
                    if cell.location == (cell.board_len, cell.board_len):  # add the parents of the fictive node
                        if cell.best_neighbors:  # empty list means false
                            if temp_agent not in cell.best_neighbors:
                                cell.best_neighbors.append(temp_agent)
                        else:
                            cell.best_neighbors.append(temp_agent)
                    elif (cell not in lb) and (not board[cell.location[0]][cell.location[1]] == 2):
                        cell.parent = temp_agent
                        lb.append(cell)
            counter += 1
        else:
            lb = lb[0:3]
            break
    print_bag_of_options(lb, board)


def print_bag_of_options(array, board):
    i = 0
    for cell in array:
        temp_board = copy.deepcopy(
            board)  # every iteration i made a copy of the board because i didn't want to change the start board for the prints
        for cell1 in array:
            if not (cell.location == (cell.board_len, cell.board_len)):
                temp_board[cell1.location[0]][cell1.location[
                    1]] = 0  # if one of the considerations was to get oust of the board i've just deleted the last location
        if not (cell.location == (cell.board_len, cell.board_len)):
            temp_board[cell.location[0]][cell.location[1]] = 2  # mark the option considered with agents
            temp_board[cell.parent.location[0]][cell.parent.location[1]] = 0  # delete the last position
        else:
            temp_board[cell.best_neighbors[i].location[0]][cell.best_neighbors[i].location[1]] = 0
        i += 1
        if i == 1:
            print('Board 2a:')  # Prints the title for all the boards with the number of them
        if i == 2:
            print('Board 2b:')  # Prints the title for all the boards with the number of them
        if i == 3:
            print('Board 2c:')  # Prints the title for all the boards with the number of them
        print_local_beam_optional_board(temp_board)


def print_local_beam_optional_board(temp_board):
    title = '   '
    for k in range(len(temp_board)):  # Creates row of labels above the board (not limited to 6X6 board)
        title += (' ' + str(k + 1))
    for i in range(len(temp_board)):  # Prints the board
        line = ''
        if i == 0:
            print(title)
        for j in range(len(temp_board)):
            t = ''
            if temp_board[i][j] == 1:
                t = '@ '
            if temp_board[i][j] == 2:
                t = '* '
            if temp_board[i][j] == 0:
                t = '  '
            line += t
        print(i + 1, ':', line)  # Creates column labels next to the board (not limited to 6X6 board)
    print('_____')


def get_shortest_path_by_genetic_algorithm(agent, target, pop_size, mutation_rate, generations_limitation, start_board):
    path = [agent.location]
    if not reach_target(agent, target):
        population = init_population(agent, target,
                                     pop_size)  # initiate the first population with new object of route that starts with first location on the board
        num_of_generation = 0
        new_population = []
        while num_of_generation < generations_limitation:
            counter = 0
            new_population.clear()
            final_route = next_step_of_evolution(population,
                                                 start_board)  # every generation increase with one direction (to avoid discontinuity i used directions that would add or subtract from the last location)
            if final_route is not None:
                family_paths = family_paths_organizer(
                    final_route)  # when it reach the target it would organize for the parents and for itself the path that used
                return family_paths
            while counter < pop_size:
                parents = find_legit_parents(
                    population)  # if the parents by adding the last direction reached a force fields they wouldn't be legit
                new_born = birth(parents[0], parents[1], start_board)
                rand = random.random()
                if rand < mutation_rate:
                    mutation_formation(new_born,
                                       start_board)  # mutation happened if the random is less than the number i determines
                if son_reach_target(new_born):
                    family_paths = family_paths_organizer(new_born)
                    return family_paths
                new_population.append(new_born)
                counter += 1
            population = copy.copy(new_population)
            num_of_generation += 1
        return [[], [], [], []]
    else:
        return [[path], [path], [], []]  # if there were no step occur


def init_population(agent, target, pop_size):
    population = []  # list with route in every index
    for i in range(pop_size):
        population.append(Route(agent, target))
    return population


def next_step_of_evolution(population, start_board):
    turns = [[1, 0], [-1, 0], [0, 1], [0,
                                       -1]]  # every generation increase with one direction (to avoid discontinuity i used directions that would add or subtract from the last location)
    i = 0
    while i < len(population):
        turn = np.array(random.choice(turns))
        route = population[i]
        next_step = (route.current_location + turn)
        if turn_is_possible(next_step, route.target_cell):  # turn would not be possible if i goes out of the board
            route.directions.append(turn)
            route.current_location = next_step
            if son_reach_target(route):
                return route
            i += 1
            calc_fitness(route, start_board)
    return None


def turn_is_possible(next_step, target_cell):  # turn would not be possible if i goes out of the board
    if next_step[0] == target_cell.board_len and target_cell.location == (target_cell.board_len, target_cell.board_len):
        return True  # turn out of the board would be able just for the target if it is the fictive one
    else:
        if next_step[0] < 0 or next_step[0] > target_cell.board_len - 1:
            return False
        elif next_step[1] < 0 or next_step[1] > target_cell.board_len - 1:
            return False
        else:
            return True


def calc_fitness(route, start_board):  # consider that turn_is_possible() happened already
    if route.current_location[0] == route.target_cell.board_len and route.target_cell.location[
        0] == route.target_cell.board_len:
        route.fitness = 1  # would stop the process but to be on the safe side i added 1 to assure it would be pick to be a parent in the next generation
    elif start_board[route.current_location[0]][route.current_location[1]] == 1:
        route.fitness = 0.000001  # if it reached forcefield i don't want to choose him as a parent
    else:
        route.fitness = fitness_fn(route)  # update the route field


def fitness_fn(
        route):  # calculate by divide 1 by the heuristic, means the closer you are more probability you'll choose
    if route.current_location[0] == route.target_cell.location[0] and \
            route.current_location[1] == route.target_cell.location[1]:
        return 1
    else:
        current_tup = (route.current_location[0], route.current_location[1])
        h = heuristic(current_tup, route.target_cell.location)
        ft = 1 / h
        return ft


def son_reach_target(route):
    if route.current_location[0] == route.target_cell.location[0] and route.target_cell.location[
        1] == route.target_cell.board_len:
        return True
    elif route.current_location[0] == route.target_cell.location[0] and \
            route.current_location[1] == route.target_cell.location[1]:
        return True
    else:
        return False


def transfer_route_to_path(
        route):  # a way to transform the way i implement route into path that the system i made knows how to deal with
    np_current_location = np.array([route.adam_cell.location[0], route.adam_cell.location[1]])
    path = [(np_current_location[0], np_current_location[1])]
    for d in route.directions:
        np_current_location = (np_current_location + d)
        if (np_current_location[0] == route.target_cell.location[0] and route.target_cell.location[
            0] == route.target_cell.board_len) \
                or (np_current_location[0] == route.target_cell.location[0] and np_current_location[1] ==
                    route.target_cell.location[1]):
            np_current_location = [route.target_cell.location[0], route.target_cell.location[1]]
        path.append((np_current_location[0], np_current_location[1]))
    return path


def find_legit_parents(
        population):  # avoid parents standing on forcefields - if the first position have two parents that have just one turn to a forcefield the child would consider a path throw forcefield
    parents = []
    possible_parents = False
    while not possible_parents:
        wheel = make_wheel(population)  # a way to chose two different individuals(routes) from the population
        parents = selection(wheel, 2)
        if parents[0].fitness > 0.000001 or parents[1].fitness > 0.000001:
            possible_parents = True
    return parents


def make_wheel(population):  # store each route from the population in a relative place.
    wheel = []
    total = sum(fitness_fn(p) for p in population)
    top = 0
    for p in population:
        f = fitness_fn(p) / total
        wheel.append((top, top + f, p))
        top += f
    return wheel


def bin_search(wheel, num):  # binary search
    mid = len(wheel) // 2
    low, high, answer = wheel[mid]
    if low <= num <= high:
        return answer
    elif high < num:
        return bin_search(wheel[mid + 1:], num)
    else:
        return bin_search(wheel[:mid], num)


def selection(wheel, n):  # generate n parents from the population
    step_size = 1.0 / n
    answer = []
    r = random.random()
    route = bin_search(wheel, r)  # mom
    route.probability_to_be_selected = round(r, 3)  # save the probability of being chosen for the print
    answer.append(route)
    while len(answer) < n:
        r += step_size
        if r > 1:
            r %= 1
        route = bin_search(wheel, r)  # dad
        route.probability_to_be_selected = round(r, 3)
        answer.append(route)
    return answer


def birth(mom, dad, start_board):
    newborn = Route(mom.adam_cell, mom.target_cell)
    parents = [mom, dad]
    while True:
        counter = 0
        while counter < len(mom.directions):
            if counter < len(mom.directions):
                parent = random.choice(parents)  # choose one of the parents randomly every move
                newborn.directions.append(parent.directions[counter])  # place it in the next place
                newborn.current_location = newborn.current_location + parent.directions[counter]
                if parent == mom:
                    newborn.directions_by_parents.append((newborn.current_location,
                                                          1))  # add the location to an array of the parent for the print at the end
                else:
                    newborn.directions_by_parents.append((newborn.current_location, 2))
                counter += 1
        if dna_combination_success(newborn, start_board):  # check that by merge, the path wasn't threw a forcefield
            newborn.probabilities.append(mom.probability_to_be_selected)
            newborn.probabilities.append(dad.probability_to_be_selected)
            newborn.mom = mom
            newborn.dad = dad
            return newborn
        else:
            newborn.current_location = np.array([newborn.adam_cell.location[0], newborn.adam_cell.location[1]])
            newborn.directions_by_parents.clear()
            newborn.directions.clear()


def mutation_formation(route, start_board):
    turns = [[1, 0], [-1, 0], [0, 1], [0, -1]]
    while True:
        mutation_gene = np.array(random.choice(turns))
        vain_gene_place = random.randrange(
            len(route.directions))  # check a random place to switch a turn with random one
        vain_gene = route.directions.pop(vain_gene_place)
        route.directions.insert(vain_gene_place, mutation_gene)
        if dna_combination_success(route, start_board):  # check the the mutation created a legit path
            route.mutation = True
            break
        else:
            route.directions.pop(vain_gene_place)  # if not, i would brings it back to the way it was and mutate again
            route.directions.insert(vain_gene_place, vain_gene)


# check that the new path didn't go threw forcefields
def dna_combination_success(route, start_board):
    np_current_location = np.array([route.adam_cell.location[0], route.adam_cell.location[1]])
    for d in route.directions:
        np_current_location = (np_current_location + d)
        route.current_location = np_current_location
        if turn_is_possible(np_current_location, route.target_cell):
            calc_fitness(route, start_board)
            if route.fitness > 0.000001:
                continue
            else:
                return False
        else:
            return False
    return True


# organize all the paths into tuples that the rest of the system from the last work would work
def family_paths_organizer(final_route):
    moms_path = []
    dads_path = []
    parents_combination = []
    final_path = transfer_route_to_path(final_route)
    if final_route.mom is not None:
        moms_path = transfer_route_to_path(final_route.mom)
        dads_path = transfer_route_to_path(final_route.dad)
        parents_combination = transfer_np_to_tup(final_route)
    return [final_path, moms_path, dads_path, parents_combination, final_route]


def transfer_np_to_tup(route):
    path_of_tuples = []
    for i in range(len(route.directions_by_parents)):
        path_of_tuples.append(((route.directions_by_parents[i][0][0], route.directions_by_parents[i][0][1]),
                               route.directions_by_parents[i][1]))
    return path_of_tuples


def transfer_tup_to_cell(cell_grid, start_board, tup):
    if tup != 0:
        cell = None
        for i in range(len(start_board)):
            for j in range(len(start_board)):
                if i == tup[0] and j == tup[1]:
                    cell = cell_grid[i][j]
        if tup[0] == len(start_board):
            cell = cell_grid[len(start_board)][0]
        return cell
    else:
        return None


def print_family_boards(start_board, cell_grid):
    for row in range(len(start_board)):
        for column in range(len(start_board)):
            cell = cell_grid[row][column]
            if cell.part_of_the_solution:
                num_of_target = cell.target_in_solution
                for i in range(3):
                    copy_of_start_board = copy.deepcopy(start_board)
                    if i < 2:  # the route of the parents was different from the actual route because I inserted in the tupel from which parent the ture came from
                        if i == 0:
                            print('Starting board ' + str(i) + '(probability of selection from population::<' + str(
                                cell.route.probabilities[0]) + '>):')
                            arrange_genetic_bard(copy_of_start_board, cell.mom_path[num_of_target], 1)
                        if i == 1:
                            print('Starting board ' + str(i) + '(probability of selection from population::<' + str(
                                cell.route.probabilities[1]) + '>):')
                            arrange_genetic_bard(copy_of_start_board, cell.dad_path[num_of_target], 2)
                    else:
                        if cell.route.mutation:
                            print('Result board (mutation happened::<yes>):')
                        else:
                            print('Result board (mutation happened::<no>):')
                        arrange_genetic_bard(copy_of_start_board, cell.path_by_parents[num_of_target], 3)
                    print_genetic_family_board(copy_of_start_board)
                return True


# rearrange the board by numbers that eventually represent the whole route that considered and each step would visualize the parent that it came from
def arrange_genetic_bard(temp_board, path, num):
    for tup in path:
        if num == 1:
            if len(path) > 1:
                if tup[0] != 6:
                    temp_board[tup[0]][tup[1]] = 3
            else:
                temp_board[tup[0][0]][tup[0][1]] = 3
        elif num == 2:
            if len(path) > 1:
                if tup[0] != 6:
                    temp_board[tup[0]][tup[1]] = 4
            else:
                temp_board[tup[0][0]][tup[0][1]] = 4
        else:
            if len(path) > 1:
                if tup[0][0] != 6:
                    if tup[1] == 1:
                        temp_board[tup[0][0]][tup[0][1]] = 3
                    elif tup[1] == 2:
                        temp_board[tup[0][0]][tup[0][1]] = 4
            else:
                if tup[0][1] == 1:
                    temp_board[tup[0][0][0]][tup[0][0][1]] = 3
                elif tup[1] == 2:
                    temp_board[tup[0][0][0]][tup[0][0][1]] = 4


def print_genetic_family_board(temp_board):
    title = '   '
    for k in range(len(temp_board)):  # Creates row of labels above the board (not limited to 6X6 board)
        title += (' ' + str(k + 1))
    for i in range(len(temp_board)):  # Prints the board
        line = ''
        if i == 0:
            print(title)
        for j in range(len(temp_board)):
            t = ''
            if temp_board[i][j] == 1:
                t = '@ '
            if temp_board[i][j] == 2:
                t = '* '
            if temp_board[i][j] == 3:
                t = 'M '  # visual way to see the route is mom's route
            if temp_board[i][j] == 4:
                t = 'D '  # visual way to see the route is mom's route
            if temp_board[i][j] == 0:
                t = '  '
            line += t
        print(i + 1, ':', line)  # Creates column labels next to the board (not limited to 6X6 board)
    print('_____')


def best_moves(agents, targets, paths):
    g = nx.Graph()
    for i in range(len(agents)):  # Initialize the graph to be a bipartite graph, by set the agents in the first
        g.add_node(i)  # vertexes and right after them the targets.
        g.add_node(len(agents) + i)
    for i in range(len(agents)):
        for j in range(len(targets)):
            if len(paths[i][j]) > 0:  # If a path exist add an edge between agent i, target j in the bipartite graph
                g.add_edge(i, len(agents) + j, weight=1 / len(paths[i][j]))  # Adds the edge as a Tuple
    return nx.max_weight_matching(
        g)  # The max weight matching return a subset of edges in which no vertex occurs more than once,
    # I set the weight to be (amount of moves)^-1 to find the minimal matching.


def print_board(board, h, goal_board_number, board_number, search_method):
    if board_number == 1:
        print('Board ' + str(board_number) + ' (starting position):')  # Prints the title for the first board
        board_number += 1
    elif board_number == goal_board_number and goal_board_number > 1:
        print('Board ' + str(board_number) + ' (goal position):')  # Prints the title for the last board
        board_number += 1
    else:
        print('Board ' + str(board_number) + ':')  # Prints the title for all the boards with the number of them
        board_number += 1
    title = '   '
    for k in range(len(board)):  # Creates row of labels above the board (not limited to 6X6 board)
        title += (' ' + str(k + 1))
    for i in range(len(board)):  # Prints the board
        line = ''
        if i == 0:
            print(title)
        for j in range(len(board)):
            t = ''
            if board[i][j] == 1:
                t = '@ '
            if board[i][j] == 2:
                t = '* '
            if board[i][j] == 0:
                t = '  '
            line += t
        print(i + 1, ':', line)  # Creates column labels next to the board (not limited to 6X6 board)
    if board_number == 3 and h > 0 and search_method == 1:  # When the bool is true (means h != -1) the heuristic will show up
        print('Heuristic : ' + str(h))
    print('_____')
    return board_number


# Instead of come around the other agent/agents it would cost less if every one of them will take on step forward
def block_handler(board, cell_grid, path, agents, target, i, h, goal_board_number, board_number, search_method,
                  detail_output):
    start = i
    last_move_fictive = False
    while i < len(path):
        if path[i][0] != len(board) and board[path[i][0]][path[i][1]] == 2:  # Check how many agents are on that path
            i += 1
        elif path[i][0] == len(board):  # Check if the last movement in the path is the fictive location
            last_move_fictive = True
            break
        else:  # If there is no more agents in a row
            break
    finish = i
    while i >= start:
        if last_move_fictive:
            if board_number == 2 and start == 1 and search_method == 5 and detail_output:  # would get in just for the first combination between an agent and target that chose for the actual solution
                cell_agent = transfer_tup_to_cell(cell_grid, board, path[start])
                cell_agent.part_of_the_solution = True
                cell_agent.target_in_solution = target
            if board_number == 2 and start == 1 and search_method == 4 and detail_output:  # a way to see that consideration of steps even if the first one was blocked
                print_local_beam_boards(cell_grid, board, path[i - 1], agents)
            if board_number == 2 and start == 1 and search_method == 3 and detail_output:
                print_simulated_annealing_probabilities(cell_grid, board, path, path[i - 1], path[i],
                                                        target)  # last input 3 refers step out eventually
            board[path[i - 1][0]][path[i - 1][1]] = 0
            board_number = print_board(board, h, goal_board_number, board_number, search_method)
            i -= 1
            last_move_fictive = False
        else:
            if board_number == 2 and start == 1 and search_method == 5 and detail_output:
                cell_agent = transfer_tup_to_cell(cell_grid, board, path[start])
                cell_agent.part_of_the_solution = True
                cell_agent.target_in_solution = target
            if board_number == 2 and start == 1 and search_method == 4 and detail_output:
                print_local_beam_boards(cell_grid, board, path[i - 1], agents)
            if board_number == 2 and start == 1 and search_method == 3 and detail_output:
                print_simulated_annealing_probabilities(cell_grid, board, path, path[i - 1], path[i],
                                                        target)  # last input 2 refers usage of block handler
            board[path[i - 1][0]][path[i - 1][1]] = 0  # Change the last location of the interrupter to empty
            if path[i][0] < len(board) and path[i][1] < len(board):
                board[path[i][0]][path[i][1]] = 2  # Execution of the step right after the last interruption
            board_number = print_board(board, h, goal_board_number, board_number, search_method)
            i -= 1
    return finish, board_number


def print_solution(board, cell_grid, solution, paths, agents, targets, search_method, detail_output):
    h = 0
    start_board = []
    board_number = 1
    goal_board_number = 1
    for pair1 in solution:  # The Tuples of any connection in solution (bipartite graph) were define
        agent = min(pair1)  # that the lower element was the agent, and the higher was the target.
        target = max(pair1) - len(
            paths)  # Subtract the target with len(paths) because I've added it while creating the bipartite graph
        h += heuristic(agents[agent], targets[target])  # Adding Manhattan Distance of every connection to the heuristic
        goal_board_number += len(paths[agent][target]) - 1  # Update the variable that sum the number of movements
    if not detail_output:
        h = -1  # If the bool were False the heuristic wouldn't be more than 0
    for pair1 in solution:
        agent = min(pair1)
        target = max(pair1) - len(paths)
        path = paths[agent][target]  # Define path to be all the moves of the agent to target
        i = 0
        while i < len(path) - 1:
            if board_number == 1:
                start_board = copy.deepcopy(board)
                board_number = print_board(board, h, goal_board_number, board_number, search_method)
            if path[i + 1][0] < len(
                    board):  # Check that the row of the next step isn't len(board) because if so,that's a path to the fictive target.
                if board[path[i + 1][0]][path[i + 1][1]] == 0:
                    if board_number == 2 and i == 0 and search_method == 5 and detail_output:
                        cell_agent = transfer_tup_to_cell(cell_grid, board, path[i])
                        cell_agent.part_of_the_solution = True
                        cell_agent.target_in_solution = target
                    if board_number == 2 and i == 0 and search_method == 4 and detail_output:
                        print_local_beam_boards(cell_grid, board, path[i], agents)
                    if board_number == 2 and i == 0 and search_method == 3 and detail_output:
                        print_simulated_annealing_probabilities(cell_grid, board, path, path[i], path[i + 1], target)
                    board[path[i + 1][0]][path[i + 1][
                        1]] = 2  # If there's no interruption change the next location to be 2, and that one to 0.
                    board[path[i][0]][path[i][1]] = 0
                    board_number = print_board(board, h, goal_board_number, board_number,
                                               search_method)  # Print the board every single move, and update the number of moves occurred.
                    i += 1
                else:  # The only interruption possible is an agent on another agent way (the force fields aren't part of the graph)
                    tup = block_handler(board, cell_grid, path, agents, target, i + 1, h, goal_board_number,
                                        board_number, search_method, detail_output)
                    i = tup[0]  # Return the last step that occurred after the agents switched
                    board_number = tup[1]  # Return how many steps occurred
            else:
                if board_number == 2 and i == 0 and search_method == 5 and detail_output:
                    cell_agent = transfer_tup_to_cell(cell_grid, board, path[i])
                    cell_agent.part_of_the_solution = True
                    cell_agent.target_in_solution = target
                if board_number == 2 and i == 0 and search_method == 4 and detail_output:
                    print_local_beam_boards(cell_grid, board, path[i], agents)
                if board_number == 2 and i == 0 and search_method == 3 and detail_output:
                    print_simulated_annealing_probabilities(cell_grid, board, path, path[i], path[i + 1], target)
                board[path[i][0]][
                    path[i][1]] = 0  # When the next step is len(board) that's a way to the fictive target,
                board_number = print_board(board, h, goal_board_number, board_number,
                                           search_method)  # therefore that move ends by clean that agent up from the board.
                i += 1
    if board_number == 1:
        print_board(board, h, goal_board_number, board_number,
                    search_method)  # In case starting board & goal board are the same.
    if board_number > goal_board_number and search_method == 5:
        print_family_boards(start_board, cell_grid)


def find_agents_and_targets(start_board, final_board):
    agents = []
    targets = []
    for i in range(len(start_board)):
        for j in range(len(start_board)):
            if start_board[i][j] == 2:
                agents.append(
                    (i, j))  # Insert into agents Tuples of an agent that include it's row&column from the start board
            if final_board[i][j] == 2:
                targets.append((i, j))
    while len(agents) > len(targets):  # Creating a new Tuple in a non exist index, as a fictive target,
        targets.append((len(start_board),
                        len(start_board)))  # for every agent that has no target (implementation in the create_grid)
    return agents, targets


def solve_game(grid, cell_grid, start_board, final_board, search_method, detail_output):
    (agents, targets) = find_agents_and_targets(start_board, final_board)
    paths = [[0 for i in range(len(agents))] for j in range(len(targets))]  # Initialize paths as a 2D list with 0.
    path = []
    for i in range(len(agents)):  # The index [i][j] means the path between
        for j in range(len(targets)):  # the agent i and target j represented by Tuples.
            agent = agents[i]
            target = targets[j]
            cell_agent = transfer_tup_to_cell(cell_grid, start_board, agent)
            cell_target = transfer_tup_to_cell(cell_grid, start_board, target)
            if search_method == 1:
                path = get_shortest_path_by_astar(grid, agent, target)  # using A* with NetworkX assistance.
            elif search_method == 2:
                path = get_shortest_path_by_hill_climbing(grid, agent,
                                                          target)  # Returns all optional paths between the agents and targets
            elif search_method == 3:
                path = get_shortest_path_by_simulated_annealing(cell_agent,
                                                                cell_target)  # Returns all optional paths between the agents and targets
            elif search_method == 4:
                path = get_shortest_path_by_local_beam(3, cell_agent, cell_target,
                                                       cell_grid)  # Returns all optional paths between the agents and targets
            elif search_method == 5:
                family_paths = get_shortest_path_by_genetic_algorithm(cell_agent, cell_target, 10, 0.1, 42,
                                                                      start_board)  # Returns all optional paths between the agents and targets
                path = family_paths[0]
                cell_agent.mom_path.append(family_paths[
                                               1])  # add the paths into object cell that is the start of the route in the genetic algorithm
                cell_agent.dad_path.append(family_paths[2])
                cell_agent.path_by_parents.append(family_paths[3])
                if len(family_paths) > 4:
                    cell_agent.route = family_paths[4]
            paths[i][j] = path
    solution = best_moves(agents, targets, paths)  # Returns the best path between every agent to his specific target
    if len(solution) < len(
            agents):  # The only way it would happen is when one of the agents couldn't get to any target,
        print("No path found")  # include the fictive target if was necessary.
    else:
        print_solution(start_board, cell_grid, solution, paths, agents, targets, search_method, detail_output)


# checking that start and goal board are match by comparing the locations of the force fields
def check_valid_input(starting_board1, goal_board1):
    for i in range(len(starting_board1)):
        for j in range(len(starting_board1[i])):
            if starting_board1[i][j] == 1 and goal_board1[i][j] != 1:
                return False
    return True


def find_path(starting_board1, goal_board1, search_method, detail_output):
    is_valid = check_valid_input(starting_board1, goal_board1)
    if not is_valid:
        print("Boards are not valid")
    else:
        grid = create_grid(starting_board1)
        solve_game(grid[0], grid[1], starting_board1, goal_board1, search_method, detail_output)


if __name__ == "__main__":
    # @@@@@@111111@@@@@@
    starting_board = [[2, 0, 2, 0, 2, 0],
                      [0, 0, 0, 2, 1, 2],
                      [1, 0, 0, 0, 0, 0],
                      [0, 0, 1, 0, 1, 0],
                      [2, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0]]
    goal_board = [[2, 0, 2, 0, 0, 0],
                  [0, 0, 0, 2, 1, 2],
                  [1, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 1, 2],
                  [0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0]]

    find_path(starting_board, goal_board, 1, True)

# @@@@@@222222@@@@@@
# starting_board = [[2, 2, 2, 2, 2, 2],
#                   [2, 0, 0, 0, 1, 0],
#                   [2, 0, 0, 0, 0, 0],
#                   [2, 0, 1, 0, 1, 0],
#                   [2, 0, 0, 0, 0, 0],
#                   [2, 0, 0, 0, 0, 0]]
# goal_board = [[0, 0, 0, 0, 0, 2],
#               [0, 0, 0, 0, 1, 2],
#               [0, 0, 0, 0, 0, 2],
#               [0, 0, 1, 0, 1, 2],
#               [0, 0, 0, 0, 0, 2],
#               [2, 2, 2, 2, 2, 2]]
# starting_board = [[2, 2, 2, 2, 2, 2],
#                   [2, 2, 0, 0, 1, 0],
#                   [2, 0, 2, 2, 0, 0],
#                   [2, 2, 1, 0, 1, 0],
#                   [2, 0, 0, 0, 0, 0],
#                   [2, 0, 0, 0, 0, 0]]
# goal_board = [[0, 0, 0, 0, 0, 2],
#               [0, 0, 0, 0, 1, 2],
#               [0, 0, 0, 0, 0, 2],
#               [0, 0, 1, 0, 1, 2],
#               [0, 0, 0, 0, 0, 2],
#               [2, 2, 2, 2, 2, 2]]
# @@@@@@3333333@@@@@@
# starting_board = [[0, 0, 0, 0, 2, 2],
#                   [0, 0, 0, 0, 1, 2],
#                   [0, 0, 0, 0, 1, 0],
#                   [0, 0, 0, 0, 1, 0],
#                   [0, 0, 0, 0, 1, 0],
#                   [0, 0, 0, 0, 1, 1]]
# goal_board = [[0, 0, 0, 0, 2, 0],
#               [0, 0, 0, 0, 1, 2],
#               [0, 0, 0, 0, 1, 0],
#               [0, 0, 0, 0, 1, 0],
#               [0, 0, 0, 0, 1, 0],
#               [0, 0, 0, 2, 1, 1]]
# @@@@@@444444@@@@@@
# starting_board = [[2, 0, 2, 1, 2, 1],
#                   [0, 0, 0, 2, 1, 2],
#                   [1, 0, 0, 0, 0, 0],
#                   [0, 0, 1, 0, 1, 0],
#                   [2, 0, 0, 0, 0, 0],
#                   [0, 1, 0, 0, 0, 0]]
# goal_board = [[2, 0, 2, 1, 0, 1],
#               [0, 0, 0, 2, 1, 2],
#               [1, 0, 0, 0, 0, 0],
#               [0, 0, 1, 0, 1, 2],
#               [0, 0, 0, 0, 0, 0],
#               [0, 1, 0, 0, 0, 0]]
# @@@@@@555555@@@@@@
# starting_board = [[2, 0, 0, 0, 0, 0 ,0 ,0 ,0],
#                   [0, 0, 0, 0, 0, 0 ,0 ,0 ,0],
#                   [0, 0, 0, 0, 0, 0 ,0 ,0 ,0],
#                   [1, 1, 1, 1, 1, 1 ,1 ,1, 1],
#                   [0, 0, 0, 0, 0, 0, 0 ,0 ,0],
#                   [0, 0, 0, 0, 0, 0 ,0 ,0 ,0]]
# goal_board = [[0, 0, 0, 0, 0, 0 ,0 ,0 ,0],
#               [0, 0, 0, 0, 0, 0 ,0 ,0 ,0],
#               [0, 0, 0, 0, 0, 0 ,0 ,0 ,0],
#               [1, 1, 1, 1, 1, 1 ,1 ,1, 1],
#               [0, 0, 0, 0, 0, 0, 0 ,0 ,0],
#               [0, 0, 0, 0, 0, 2 ,0 ,0 ,0]]
# @@@@@@6666666@@@@@@
# starting_board = [[2, 2, 2, 2, 2, 2],
#                   [2, 2, 2, 2, 2, 2],
#                   [2, 2, 2, 2, 2, 2],
#                   [2, 2, 2, 2, 2, 2],
#                   [2, 2, 2, 2, 2, 2],
#                   [2, 2, 2, 2, 2, 0]]
# goal_board = [[0, 2, 2, 2, 2, 2],
#               [2, 2, 2, 2, 2, 2],
#               [2, 2, 2, 2, 2, 2],
#               [2, 2, 2, 2, 2, 2],
#               [2, 2, 2, 2, 2, 2],
#               [2, 2, 2, 2, 2, 2]]
# @@@@@@7777777@@@@@@
# starting_board = [[0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 2]]
# goal_board = [[2, 0, 0, 0, 0, 0],
#               [0, 0, 0, 0, 0, 0],
#               [0, 0, 0, 0, 0, 0],
#               [0, 0, 0, 0, 0, 0],
#               [0, 0, 0, 0, 0, 0],
#               [0, 0, 0, 0, 0, 0]]
# @@@@@@8888888@@@@@@
# starting_board = [[0, 1, 0, 0, 0, 0],
#                   [0, 1, 0, 1, 1, 0],
#                   [0, 1, 0, 1, 0, 0],
#                   [0, 1, 0, 1, 0, 1],
#                   [0, 1, 0, 1, 2, 2],
#                   [0, 0, 0, 1, 2, 2]]
# goal_board = [[2, 1, 0, 0, 0, 0],
#               [0, 1, 0, 1, 1, 0],
#               [2, 1, 2, 1, 0, 0],
#               [0, 1, 0, 1, 0, 1],
#               [0, 1, 0, 1, 0, 0],
#               [0, 0, 0, 1, 0, 0]]
# starting_board = [[0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0],
#          [2, 0, 0, 0, 0, 2]]
# @@@@@@9999999@@@@@@
# goal_board = [[0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 2, 0],
#          [0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0]]
