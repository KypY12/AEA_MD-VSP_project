import json
import os

import numpy as np
from tqdm import tqdm

from data_readers.cost_matrix_reader import CostMatrixReader

from ant_colony_2.ant_colony_system import AntColonySystem2

from genetic_algorithm.evaluation import Evaluation

if __name__ == '__main__':

    runs = 30

    instances_sizes = [
        # "m4n500",
        # "m4n1000",
        # "m4n1500",
        "m8n500",
        "m8n1000",
        "m8n1500"
    ]
    instance_names = [f"s{i}.inp" for i in range(5)]

    file_paths = [(f"data/{inst_size}/{inst_size}{inst_name}", inst_size + inst_name) for inst_size in instances_sizes
                  for inst_name in
                  instance_names]

    print(file_paths)

    for file_path, experiment_name in file_paths:

        m, n, depot_capacities, cost_matrix = CostMatrixReader(file_path).read()

        dir_name = f"./ant_colony_2_results/{experiment_name}"
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        for run_index in tqdm(range(runs)):
            params = {
                "cost_save_path": f"{dir_name}/cost_run_{run_index}.txt",
                "solution_save_path": f"{dir_name}/solution_run_{run_index}.txt",
                "number_of_iterations": 50,
                "number_of_ants": 10,
                "tau_0": 1.0,
                "alpha": 1.0,
                "beta": 2.0,
                "ro": 0.1,
                "phi": 0.1,
                "q_0": 0.5,
                "teleport_factor": 0.5
            }

            with open(f"{dir_name}/_parameters.json", "a") as file:
                file.write(json.dumps(params, default=lambda t: str(t), sort_keys=False, indent=4))

            acs2 = AntColonySystem2(m=m, n=n, cost_matrix=cost_matrix, depot_capacities=depot_capacities, **params)

            solution, cost = acs2.execute()

# file_path = "data/m4n500/m4n500s0.inp"
# file_path = "data/m4n500/m4n500s1.inp"
# file_path = "data/m4n500/m4n500s2.inp"
# file_path = "data/m4n500/m4n500s3.inp"
# file_path = "data/m4n500/m4n500s4.inp"  # V

# file_path = "data/m4n1000/m4n1000s0.inp"
# file_path = "data/m4n1000/m4n1000s1.inp"
# file_path = "data/m4n1000/m4n1000s2.inp"
# file_path = "data/m4n1000/m4n1000s3.inp"
# file_path = "data/m4n1000/m4n1000s4.inp"

# file_path = "data/m4n1500/m4n1500s0.inp"  # V
# file_path = "data/m4n1500/m4n1500s1.inp"
# file_path = "data/m4n1500/m4n1500s2.inp"
# file_path = "data/m4n1500/m4n1500s3.inp"
# file_path = "data/m4n1500/m4n1500s4.inp"  # V

# file_path = "data/m8n500/m8n500s0.inp"
# file_path = "data/m8n500/m8n500s1.inp"
# file_path = "data/m8n500/m8n500s2.inp"
# file_path = "data/m8n500/m8n500s3.inp"
# file_path = "data/m8n500/m8n500s4.inp"

# file_path = "data/m8n1000/m8n1000s0.inp"
# file_path = "data/m8n1000/m8n1000s1.inp"
# file_path = "data/m8n1000/m8n1000s2.inp"
# file_path = "data/m8n1000/m8n1000s3.inp"
# file_path = "data/m8n1000/m8n1000s4.inp"

# file_path = "data/m8n1500/m8n1500s0.inp"
# file_path = "data/m8n1500/m8n1500s1.inp"
# file_path = "data/m8n1500/m8n1500s2.inp"
# file_path = "data/m8n1500/m8n1500s3.inp"
# file_path = "data/m8n1500/m8n1500s4.inp"


# # file_path = "data/m4n500/m4n500s0.inp"
# file_path = "data/m4n1500/m4n1500s0.inp"
#
# m, n, depot_capacities, cost_matrix = CostMatrixReader(file_path).read()
#
# dir_name = f"./ant_colony_2_results/maine"
# if not os.path.exists(dir_name):
#     os.makedirs(dir_name)
# run_index = 0
# params = {
#     "cost_save_path": f"{dir_name}/cost_run_{run_index}.txt",
#     "solution_save_path": f"{dir_name}/solution_run_{run_index}.txt",
#     "number_of_iterations": 1,
#     "number_of_ants": 1,
#     "tau_0": 1.0,
#     "alpha": 1.0,
#     "beta": 2.0,
#     "ro": 0.1,
#     "phi": 0.1,
#     "q_0": 0.5,
#     "teleport_factor": 0.5
# }
#
# acs = AntColonySystem2(m=m,
#                        n=n,
#                        cost_matrix=cost_matrix,
#                        depot_capacities=depot_capacities,
#                        **params)
#
# solution, cost = acs.execute()
#
# print(solution)
# print(cost)
# print(np.sum(np.multiply(solution, cost_matrix)))
#
# eval = Evaluation(file_path)
#
# print("Unfeasible arcs = ", eval.get_unfeasible_arcs_violations(solution.flatten()))
# print("Single entering violations = ", eval.get_single_entering_violations(solution.flatten()))
# print("Single leaving violations = ", eval.get_single_leaving_violations(solution.flatten()))
# print("Depot entering==leaving violations = ", eval.get_depot_violations(solution.flatten()))
# print("Depot path violations = ", eval.get_depot_paths_violations(solution.flatten()))
# print("Depot capacity violations = ", eval.get_depot_capacity_violations(solution.flatten()))
