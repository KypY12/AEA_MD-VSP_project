import numpy as np


class Ant:
    def __init__(self,
                 cost_matrix,
                 depot_capacity,
                 pheromone_matrix,
                 ant_params: tuple):

        self.cost_matrix = cost_matrix
        self.inverse_div_cost_matrix = 1 / (self.cost_matrix + 1e-10)  # avoid zero cost division
        self.depot_capacity = depot_capacity

        self.global_pheromone_matrix = pheromone_matrix
        self.local_pheromone_matrix = np.zeros(pheromone_matrix.shape)

        self.tau_0, self.alpha, self.beta, self.phi, self.q_0 = ant_params

        self.unvisited = list(range(cost_matrix.shape[0]))

        # the ant always starts from the depot
        # but a new vehicle is used (counted) every time the ant is returning to the depot
        self.depot_visits = 0

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

    def __get_node_neighbours__(self, node):
        neighbours = []
        for unvisited_node in self.unvisited:
            if self.cost_matrix[node, unvisited_node] != -1:
                neighbours.append(unvisited_node)

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

    def __repair_unfeasible__(self, solution):

        # Find all trips that enter the depot directly (in_trips)
        in_nodes = []
        for row_index in range(1, solution.shape[0]):
            if solution[row_index, 0] == 1:
                in_nodes.append(row_index)

        # Find all the trips that leave the depot directly (out_trips)
        out_nodes = []
        for col_index in range(1, solution.shape[1]):
            if solution[0, col_index] == 1:
                out_nodes.append(col_index)

        output_used = []
        # For each in_trip and out_trip
        for in_index, in_node in enumerate(in_nodes):
            for out_index, out_node in enumerate(out_nodes):
                # if there is a feasible arc between the in_trip and the out_trip
                if self.cost_matrix[in_node, out_node] != -1 and out_node not in output_used:
                    # Remove old arcs to/from depot
                    solution[in_node, 0] = 0
                    solution[0, out_node] = 0

                    # Add new arc between the
                    solution[in_node, out_node] = 1

                    output_used += [out_node]

                    # Remove one vehicle
                    self.depot_visits -= 1
                    # Go to the next in_trip
                    break

            # if self.depot_visits <= self.depot_capacity:
            #     break

        return solution

    def construct_solution(self):

        solution = []
        self.depot_visits = self.depot_capacity + 1

        # A solution is feasible only when the depot capacity is not exceeded
        while self.depot_visits > self.depot_capacity:

            self.depot_visits = 0
            self.local_pheromone_matrix = np.zeros(self.global_pheromone_matrix.shape)
            self.unvisited = list(range(self.cost_matrix.shape[0]))

            # Start from the depot
            current_node = 0
            solution = np.zeros(self.cost_matrix.shape)

            while len(self.unvisited) > 0:
                current_neighbours = self.__get_node_neighbours__(current_node)

                q = np.random.rand()
                if q <= self.q_0:
                    next_node = self.__choose_argmax_heuristic__(current_node, current_neighbours)
                else:
                    next_node = self.__choose_aco_heuristic__(current_node, current_neighbours)

                # If the ant returns to the depot, then it finished using one vehicle
                # The next time it starts a new path, it will use another vehicle
                if next_node == 0:
                    self.depot_visits += 1

                # Consider the node visited if it is not the depot node
                # or if the current node is the last visited node (which is always the depot node)
                if next_node != 0 or len(self.unvisited) == 1:
                    self.unvisited.remove(next_node)

                # solution.append(next_node)
                solution[current_node][next_node] = 1
                current_node = next_node

            # if self.depot_visits > self.depot_capacity:
            solution = self.__repair_unfeasible__(solution)

        self.solution = solution
        self.solution_cost = np.sum(np.multiply(self.cost_matrix, self.solution))
        self.local_pheromone_matrix = self.solution * (1 / self.solution_cost)
        self.global_pheromone_matrix = (1 - self.phi) * self.global_pheromone_matrix + self.phi * self.tau_0

        return self.global_pheromone_matrix


class AntColonySystem:

    def __init__(self,
                 cost_matrix,
                 depot_capacity,
                 alg_params: tuple):
        self.cost_matrix = cost_matrix
        self.depot_capacity = depot_capacity
        self.number_of_ants, self.tau_0, self.alpha, self.beta, self.ro, self.phi, self.q_0 \
            = alg_params

        self.pheromone_matrix = np.full(self.cost_matrix.shape, self.tau_0)

        self.ants = [Ant(self.cost_matrix, depot_capacity, self.pheromone_matrix,
                         (self.tau_0, self.alpha, self.beta, self.phi, self.q_0))
                     for _ in range(self.number_of_ants)]

        self.best_solution = []
        self.best_solution_cost = -1
        self.best_local_pheromones_matrix = []

    def get_best_cost(self):
        return self.best_solution_cost

    def get_best_solution(self):
        return self.best_solution

    def execute_iteration(self):
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
            self.pheromone_matrix = (1 - self.ro) * self.pheromone_matrix + self.ro * self.best_local_pheromones_matrix
