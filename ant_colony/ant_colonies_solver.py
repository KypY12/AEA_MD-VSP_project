import os

import numpy as np
from tqdm import tqdm

from ant_colony.partitioning.partitioner import Partitioner
from ant_colony.ant_colony_system import AntColonySystem


class AntColoniesSolver:

    def __init__(self,
                 cost_save_path,
                 solution_save_path,
                 partitioner: Partitioner,
                 number_of_iterations,
                 number_of_ants,
                 tau_0,
                 alpha,
                 beta,
                 ro,
                 phi,
                 q_0):

        self.cost_save_path = cost_save_path
        self.solution_save_path = solution_save_path
        self.partitioner = partitioner
        self.graph = partitioner.get_graph()

        self.cost_matrix = self.graph.get_cost_matrix()
        self.depot_capacities = self.graph.get_depot_capacities()
        self.m = self.graph.get_m()
        self.n = self.graph.get_n()

        self.number_of_iterations = number_of_iterations
        self.number_of_ants = number_of_ants
        self.tau_0 = tau_0
        self.alpha = alpha
        self.beta = beta
        self.ro = ro
        self.phi = phi
        self.q_0 = q_0

        self.colonies = []
        self.__init_colonies__()

    def __init_colonies__(self):
        for part in self.partitioner.get_partitions():
            depot_node = part.get_depot()
            nodes = part.get_nodes()
            all_nodes = [depot_node] + nodes

            # Keep only the lines and columns that we need from the cost matrix
            cost_sub_matrix = self.cost_matrix[all_nodes][:, all_nodes]

            alg_params = (self.number_of_ants, self.tau_0, self.alpha, self.beta, self.ro, self.phi, self.q_0)
            acs = AntColonySystem(cost_sub_matrix, self.depot_capacities[depot_node], alg_params)

            entry = dict()
            entry["depot"] = depot_node
            entry["all_nodes"] = all_nodes
            entry["colony"] = acs

            self.colonies.append(entry)

    def __add_partial_solution__(self, current_solution, initial_nodes, partial_solution):
        for row_index in range(partial_solution.shape[0]):
            for col_index in range(partial_solution.shape[1]):
                current_solution[initial_nodes[row_index], initial_nodes[col_index]] = \
                    partial_solution[row_index, col_index]

    def __log__(self, iteration, current_solution, current_cost):

        with open(self.cost_save_path, "a") as file:
            file.write(f"{iteration}: {current_cost}\n")

        with open(self.solution_save_path, "a") as file:
            file.write(f"{iteration}: {current_solution.tolist()}\n")

    def solve(self):

        best_solution = []
        best_cost = -1

        for iteration in range(self.number_of_iterations):

            current_solution = np.zeros(self.cost_matrix.shape)
            current_cost = 0

            for colony in self.colonies:
                acs = colony["colony"]

                # Execute colony iteration
                acs.execute_iteration()

                # Get best solution so far
                best_colony_solution = acs.get_best_solution()
                best_colony_cost = acs.get_best_cost()

                # Update current solution and cost
                current_cost += best_colony_cost
                self.__add_partial_solution__(current_solution,
                                              initial_nodes=colony["all_nodes"],
                                              partial_solution=best_colony_solution)

            if current_cost < best_cost or best_cost == -1:
                best_cost = current_cost
                best_solution = current_solution

            # print(best_cost)

            self.__log__(iteration, current_solution, current_cost)

        return best_solution, best_cost
