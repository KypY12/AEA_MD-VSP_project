import random

import numpy as np
from tqdm import tqdm


class Ant3:
    def __init__(self,
                 m,
                 n,
                 cost_matrix,
                 depot_capacities,
                 pheromone_matrix,
                 ant_params: tuple):

        self.m = m
        self.n = n
        self.cost_matrix = cost_matrix
        self.inverse_div_cost_matrix = 1 / (self.cost_matrix + 1e-10)  # avoid zero cost division
        self.depot_capacities = np.array(depot_capacities)

        self.global_pheromone_matrix = pheromone_matrix
        self.local_pheromone_matrix = np.zeros(pheromone_matrix.shape)

        self.tau_0, self.alpha, self.beta, self.phi, self.q_0, self.teleport_factor = ant_params

        self.unvisited = list(range(cost_matrix.shape[0]))

        # the ant always starts from the depot
        # but a new vehicle is used (counted) every time the ant is returning to the depot
        # self.depot_visits = 0
        self.depot_visits = np.array([0 for _ in range(self.m)])

        self.solution = []
        self.solution_cost = -1

    def get_local_pheromone_matrix(self):
        return self.local_pheromone_matrix

    def get_solution(self):
        return self.solution

    def get_solution_cost(self):
        return self.solution_cost

    def get_global_pheromone_matrix(self):
        return self.global_pheromone_matrix

    def set_global_pheromone_matrix(self, matrix):
        self.global_pheromone_matrix = matrix

    def __get_node_neighbours__(self, node, current_depot):
        neighbours = []
        for unvisited_node in self.unvisited:
            if self.cost_matrix[node, unvisited_node] != -1:
                neighbours.append(unvisited_node)

        if node != current_depot:
            neighbours = [current_depot] + neighbours[self.m:]

        return neighbours

    def __choose_argmax_heuristic__(self, current_node, current_neighbours):
        products = []
        for neigh in current_neighbours:
            neigh_product = (self.global_pheromone_matrix[current_node, neigh] ** self.alpha) * \
                            (self.inverse_div_cost_matrix[current_node, neigh] ** self.beta)
            products.append(neigh_product)

        argmax_index = 0
        for index, neigh_product in enumerate(products):
            if neigh_product > products[argmax_index]:
                argmax_index = index

        return current_neighbours[argmax_index]

    def __choose_aco_heuristic__(self, current_node, current_neighbours):

        products = []
        for neigh in current_neighbours:
            neigh_product = (self.global_pheromone_matrix[current_node, neigh] ** self.alpha) * \
                            (self.inverse_div_cost_matrix[current_node, neigh] ** self.beta)
            products.append(neigh_product)

        products_sum = sum(products)

        probabilities = []
        for neigh_product in products:
            probabilities.append(neigh_product / products_sum)

        cumulative_probabilities = np.cumsum(probabilities)
        cumulative_probabilities[-1] = 1.0

        selected_neigh = 0
        random_number = np.random.rand()
        for index, cumulative_prob in enumerate(cumulative_probabilities):
            if random_number <= cumulative_prob:
                selected_neigh = index
                break

        return current_neighbours[selected_neigh]

    def __reduce_vehicles_near_depot__(self, solution):

        for depot_index in range(self.m):

            # Find all trips that enter the depot directly (in_trips)
            in_nodes = []
            for row_index in range(self.m, solution.shape[0]):
                if solution[row_index, depot_index] == 1:
                    in_nodes.append(row_index)

            # Find all the trips that leave the depot directly (out_trips)
            out_nodes = []
            for col_index in range(self.m, solution.shape[1]):
                if solution[depot_index, col_index] == 1:
                    out_nodes.append(col_index)

            output_used = []
            # For each in_trip and out_trip
            for in_index, in_node in enumerate(in_nodes):
                for out_index, out_node in enumerate(out_nodes):
                    # if there is a feasible arc between the in_trip and the out_trip
                    if self.cost_matrix[in_node, out_node] != -1 and out_node not in output_used:
                        # Remove old arcs to/from depot
                        solution[in_node, depot_index] = 0
                        solution[depot_index, out_node] = 0

                        # Add new arc between the
                        solution[in_node, out_node] = 1

                        output_used += [out_node]

                        # Remove one vehicle
                        self.depot_visits[depot_index] -= 1
                        # Go to the next in_trip
                        break

        return solution

    def __get_circuits_paths__(self, solution):

        depots_circuits = []
        for depot_index in range(self.m):

            current_depot_circuits = []
            for start_index in range(solution.shape[1]):

                # If it is a starting index
                if solution[depot_index, start_index] == 1:

                    circuit = []
                    current = start_index

                    while current != depot_index:
                        circuit += [current]
                        current = np.where(solution[current] == 1)[0][0]
                        # for index in range(solution.shape[1]):
                        #     if solution[current, index] == 1:
                        #         current = index
                        #         break

                    current_depot_circuits += [circuit]

            depots_circuits += [current_depot_circuits]

        return depots_circuits

    def __reduce_vehicles_by_same_depot_circuits_joins__(self, solution, depot_circuits):

        changes_are_made = False

        for depot_index in range(self.m):

            current_circuits = depot_circuits[depot_index]
            random.shuffle(current_circuits)
            used_circuits = []

            for circuit_index in range(len(current_circuits)):

                if circuit_index not in used_circuits:
                    found = False
                    current = current_circuits[circuit_index]
                    current_start = current[0]
                    current_end = current[-1]

                    for other_index in range(len(current_circuits)):

                        if other_index != circuit_index and other_index not in used_circuits:

                            other = [depot_index]
                            other += current_circuits[other_index]
                            other += [depot_index]
                            # other = current_circuits[circuit_index]

                            for node_index in range(len(other) - 1):
                                other_node = other[node_index]
                                other_next_node = other[node_index + 1]

                                if self.cost_matrix[other_node, current_start] != -1 and \
                                        self.cost_matrix[current_end, other_next_node] != -1:
                                    # Remove the other circuit edge
                                    solution[other_node, other_next_node] = 0

                                    # print("ceva")

                                    # Remove depot edges to current circuit
                                    solution[depot_index, current_start] = 0
                                    solution[current_end, depot_index] = 0

                                    # Add the 2 new edges (join the two circuits)
                                    solution[other_node, current_start] = 1
                                    solution[current_end, other_next_node] = 1

                                    used_circuits += [circuit_index, other_index]
                                    found = True
                                    changes_are_made = True
                                    self.depot_visits[depot_index] -= 1

                                    break

                        if found:
                            break

        return solution, changes_are_made

    def __search_and_join_circuit__(self, depot_index,
                                    other_depot,
                                    depots_circuits,
                                    used_circuits,
                                    circuit_index,
                                    current_start,
                                    current_end,
                                    solution):

        other_circuits = depots_circuits[other_depot]

        for other_index in range(len(other_circuits)):

            if (other_index != circuit_index or other_depot != depot_index) and \
                    other_index not in used_circuits:

                other = [other_depot]
                other += other_circuits[other_index]
                other += [other_depot]

                for node_index in range(len(other) - 1):
                    other_node = other[node_index]
                    other_next_node = other[node_index + 1]

                    if self.cost_matrix[other_node, current_start] != -1 and \
                            self.cost_matrix[current_end, other_next_node] != -1:
                        # Remove the other circuit edge
                        solution[other_node, other_next_node] = 0

                        # Remove depot edges to current circuit
                        solution[depot_index, current_start] = 0
                        solution[current_end, depot_index] = 0

                        # Add the 2 new edges (join the two circuits)
                        solution[other_node, current_start] = 1
                        solution[current_end, other_next_node] = 1

                        used_circuits += [circuit_index, other_index]

                        used_circuits[depot_index] += [circuit_index]
                        used_circuits[other_depot] += [other_index]

                        self.depot_visits[depot_index] -= 1

                        return True

        return False

    def __reduce_vehicles_by_circuits_joins__(self, solution, depot_circuits):

        changes_are_made = False

        used_circuits = []
        for depot_index in range(self.m):
            used_circuits.append([])

            depot_circuits[depot_index] = sorted(depot_circuits[depot_index], key=lambda t: len(t))
            # random.shuffle(depot_circuits[depot_index])

        depot_list = list(range(self.m))
        random.shuffle(depot_list)

        for depot_index in range(self.m):

            current_circuits = depot_circuits[depot_index]

            for circuit_index in range(len(current_circuits)):

                if circuit_index not in used_circuits[depot_index]:
                    current = current_circuits[circuit_index]
                    current_start = current[0]
                    current_end = current[-1]

                    for other_depot in depot_list:

                        if self.__search_and_join_circuit__(depot_index,
                                                            other_depot,
                                                            depot_circuits,
                                                            used_circuits,
                                                            circuit_index,
                                                            current_start,
                                                            current_end,
                                                            solution):
                            changes_are_made = True
                            break

        return solution, changes_are_made

    def __reduce_vehicles__(self, solution):

        changes_are_made = True

        while changes_are_made:
            depot_circuits = self.__get_circuits_paths__(solution)
            solution, changes_are_made = self.__reduce_vehicles_by_circuits_joins__(solution, depot_circuits)

        return solution

    def __choose_depot__(self):
        # Roulette wheel - choosing the depot based on the available vehicles

        depot_values = [self.depot_capacities[index] - self.depot_visits[index] for index in range(self.m)]
        depots_sum = sum([max([0, depot_val]) for depot_val in depot_values])

        if depots_sum > 0:
            probabilities = [depot_val / depots_sum for depot_val in depot_values]
            cumulative_probs = np.cumsum(probabilities)
            cumulative_probs[-1] = 1.0

            random_number = np.random.rand()
            for index, prob in enumerate(cumulative_probs):
                if random_number <= prob:
                    return index

        else:
            # returns the index of the max depot visits
            return np.argmax(self.depot_visits)

    def construct_solution(self):
        solution = []
        self.depot_visits = self.depot_capacities + 1

        # A solution is feasible only when the depot capacity is not exceeded
        while np.any(self.depot_visits > self.depot_capacities):

            self.depot_visits = np.array([0 for _ in range(self.m)])

            self.local_pheromone_matrix = np.zeros(self.global_pheromone_matrix.shape)
            self.unvisited = list(range(self.cost_matrix.shape[0]))

            # Start from a depot
            current_node = self.__choose_depot__()
            current_depot = current_node
            solution = np.zeros(self.cost_matrix.shape)
            depot_reached = False

            while len(self.unvisited) > 0:

                if depot_reached:
                    depot_reached = False
                    random_number = np.random.rand()
                    if random_number <= self.teleport_factor:
                        # teleport to a depot (it could be the same depot)
                        current_node = self.__choose_depot__()
                        current_depot = current_node

                current_neighbours = self.__get_node_neighbours__(current_node, current_depot)

                q = np.random.rand()
                if q <= self.q_0:
                    next_node = self.__choose_argmax_heuristic__(current_node, current_neighbours)
                else:
                    next_node = self.__choose_aco_heuristic__(current_node, current_neighbours)

                # If the ant returns to a depot, then it finished using one vehicle
                # The next time it starts a new path, it will use another vehicle
                if next_node < self.m:
                    self.depot_visits[next_node] += 1
                    depot_reached = True

                # Consider the node visited if it is not a depot node
                # or if the current node is the last visited node (which is always a depot node)
                if next_node >= self.m:
                    self.unvisited.remove(next_node)
                elif len(self.unvisited) == self.m:
                    for depot in range(self.m):
                        self.unvisited.remove(depot)

                solution[current_node][next_node] = 1
                current_node = next_node

            # if np.any(self.depot_visits > self.depot_capacities):
            solution = self.__reduce_vehicles__(solution)

        self.solution = solution
        self.solution_cost = np.sum(np.multiply(self.cost_matrix, self.solution))
        self.local_pheromone_matrix = self.solution * (1 / self.solution_cost)
        self.global_pheromone_matrix = (1 - self.phi) * self.global_pheromone_matrix + self.phi * self.tau_0

        return self.global_pheromone_matrix


class AntColonySystem3:

    def __init__(self,
                 cost_save_path,
                 solution_save_path,
                 m,
                 n,
                 cost_matrix,
                 depot_capacities,
                 number_of_iterations,
                 number_of_ants,
                 tau_0,
                 alpha,
                 beta,
                 ro,
                 phi,
                 q_0,
                 teleport_factor
                 ):
        self.cost_save_path = cost_save_path
        self.solution_save_path = solution_save_path
        self.cost_matrix = cost_matrix
        self.depot_capacities = depot_capacities
        self.number_of_iterations = number_of_iterations
        self.number_of_ants = number_of_ants
        self.tau_0 = tau_0
        self.alpha = alpha
        self.beta = beta
        self.ro = ro
        self.phi = phi
        self.q_0 = q_0
        self.teleport_factor = teleport_factor

        self.pheromone_matrix = np.full(self.cost_matrix.shape, self.tau_0)

        self.ants = [Ant3(m, n, self.cost_matrix, self.depot_capacities, self.pheromone_matrix,
                          (self.tau_0, self.alpha, self.beta, self.phi, self.q_0, self.teleport_factor))
                     for _ in range(self.number_of_ants)]

        self.best_solution = []
        self.best_solution_cost = -1
        self.best_local_pheromones_matrix = []

    def get_best_cost(self):
        return self.best_solution_cost

    def get_best_solution(self):
        return self.best_solution

    def __log__(self, iteration, current_solution, current_cost):

        with open(self.cost_save_path, "a") as file:
            file.write(f"{iteration}: {current_cost}\n")

        with open(self.solution_save_path, "a") as file:
            file.write(f"{iteration}: {current_solution.tolist()}\n")

    def execute(self):

        for iteration in tqdm(range(self.number_of_iterations)):

            current_best_cost = -1
            current_best_solution = np.array([])

            for ant_index in range(self.number_of_ants):

                # Ant construction steps
                ant = self.ants[ant_index]

                ant.set_global_pheromone_matrix(self.pheromone_matrix)
                self.pheromone_matrix = ant.construct_solution()

                current_cost = ant.get_solution_cost()

                # Update best so far
                if current_cost < self.best_solution_cost or self.best_solution_cost == -1:
                    self.best_solution_cost = current_cost
                    self.best_solution = ant.get_solution()
                    self.best_local_pheromones_matrix = ant.get_local_pheromone_matrix()

                # Update global pheromones
                self.pheromone_matrix = (1 - self.ro) * self.pheromone_matrix + \
                                        self.ro * self.best_local_pheromones_matrix

                if current_cost < current_best_cost or current_best_cost == -1:
                    current_best_solution = ant.get_solution()
                    current_best_cost = current_cost

            print(self.best_solution_cost)

            self.__log__(iteration, current_best_solution, current_best_cost)

        return self.best_solution, self.best_solution_cost
