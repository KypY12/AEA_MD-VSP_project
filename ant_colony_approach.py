import numpy as np

from data_readers.cost_matrix_reader import CostMatrixReader

from ant_colony.problem_graph import ProblemGraph
from ant_colony.partitioning.partitioner import Partitioner

from ant_colony.ant_colonies_solver import AntColoniesSolver

from genetic_algorithm.evaluation import Evaluation

if __name__ == '__main__':

    file_path = "data/4m500n/m4n500s0.inp"
    # file_path = "data/4m500n/m4n500s1.inp"
    # file_path = "data/4m500n/m4n500s2.inp"
    # file_path = "data/4m500n/m4n500s3.inp"
    # file_path = "data/4m500n/m4n500s4.inp"  # V

    # file_path = "data/4m1000n/m4n1000s0.inp"
    # file_path = "data/4m1000n/m4n1000s1.inp"
    # file_path = "data/4m1000n/m4n1000s2.inp"
    # file_path = "data/4m1000n/m4n1000s3.inp"
    # file_path = "data/4m1000n/m4n1000s4.inp"

    # file_path = "data/4m1500n/m4n1500s0.inp"  # V
    # file_path = "data/4m1500n/m4n1500s1.inp"
    # file_path = "data/4m1500n/m4n1500s2.inp"
    # file_path = "data/4m1500n/m4n1500s3.inp"
    # file_path = "data/4m1500n/m4n1500s4.inp"  # V

    # file_path = "data/8m500n/m8n500s0.inp"
    # file_path = "data/8m500n/m8n500s1.inp"
    # file_path = "data/8m500n/m8n500s2.inp"
    # file_path = "data/8m500n/m8n500s3.inp"
    # file_path = "data/8m500n/m8n500s4.inp"

    # file_path = "data/8m1000n/m8n1000s0.inp"
    # file_path = "data/8m1000n/m8n1000s1.inp"
    # file_path = "data/8m1000n/m8n1000s2.inp"
    # file_path = "data/8m1000n/m8n1000s3.inp"
    # file_path = "data/8m1000n/m8n1000s4.inp"

    # file_path = "data/8m1500n/m8n1500s0.inp"
    # file_path = "data/8m1500n/m8n1500s1.inp"
    # file_path = "data/8m1500n/m8n1500s2.inp"
    # file_path = "data/8m1500n/m8n1500s3.inp"
    # file_path = "data/8m1500n/m8n1500s4.inp"

    m, n, depot_capacities, cost_matrix = CostMatrixReader(file_path).read()

    problem_graph = ProblemGraph(cost_matrix, m, n, depot_capacities)
    partitioner = Partitioner(problem_graph)
    partitioner.execute()

    for part in partitioner.get_partitions():
        print(part)

    ant_solver = AntColoniesSolver(partitioner,
                                   number_of_iterations=50,
                                   number_of_ants=50,
                                   tau_0=1.0,
                                   alpha=1.0,
                                   beta=2.0,
                                   ro=0.3,
                                   phi=0.3,
                                   q_0=0.5)

    solution, cost = ant_solver.solve()

    print(solution)
    print(cost)
    print(np.sum(np.multiply(cost_matrix, solution)))
    eval = Evaluation(file_path)

    print("Unfeasible arcs = ", eval.get_unfeasible_arcs_violations(solution.flatten()))
    print("Single entering violations = ", eval.get_single_entering_violations(solution.flatten()))
    print("Single leaving violations = ", eval.get_single_leaving_violations(solution.flatten()))
    print("Depot entering==leaving violations = ", eval.get_depot_violations(solution.flatten()))
    print("Depot path violations = ", eval.get_depot_paths_violations(solution.flatten()))
    print("Depot capacity violations = ", eval.get_depot_capacity_violations(solution.flatten()))

    # print("recalculated: ", np.sum(np.multiply(solution, cost_matrix)))
