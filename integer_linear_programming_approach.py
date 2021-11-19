import time

import gurobipy as gp
from gurobipy import GRB
import numpy as np

env = gp.Env(empty=True)
env.setParam("LogToConsole", 0)
env.start()


def process_first_line(line_str):
    tokens = line_str.split()

    m = int(tokens[0])
    n = int(tokens[1])

    depot_capaities = []
    for index in range(2, len(tokens)):
        depot_capaities += [int(tokens[index])]

    return m, n, depot_capaities


def process_matrix_line(matrix, line_str):
    matrix_line = list(map(lambda t: int(t), line_str.split()))
    return matrix + [matrix_line]


def read_cost_matrix(file_path):
    with open(file_path, "r") as file:
        cost_matrix_list = []

        line = file.readline()
        m, n, depot_capacities = process_first_line(line)

        line = file.readline()
        while line:
            cost_matrix_list = process_matrix_line(cost_matrix_list, line)
            line = file.readline()

    return m, n, depot_capacities, np.array(cost_matrix_list)


def get_unfeasible_matrix(cost_matrix):
    cost_matrix_flat = cost_matrix.flatten()

    unfeasible_matrix_list = []
    for index in range(cost_matrix_flat.shape[0]):
        if cost_matrix_flat[index] == -1:
            unfeasible_matrix_list += [1.0]
        else:
            unfeasible_matrix_list += [0.0]

    unfeasible_matrix = np.array(unfeasible_matrix_list)
    return unfeasible_matrix


def solve(m, n, depots_capacities, cost_matrix, unfeasible_matrix, unfeasible_paths):
    # Create the model
    model = gp.Model("MD-VSP single commodity", env=env)

    # Create the variables (corresponding to the arcs in the problem)
    x = model.addMVar(shape=(m + n) * (m + n), vtype=GRB.BINARY, name="x")

    # Set the objective function ( sum(sum(c_ij * x_ij)) )
    model.setObjective(cost_matrix.flatten() @ x, GRB.MINIMIZE)

    # All unfeasible arcs should be zero
    # (this is necessary because the cost matrix contains -1's for the unfeasible arcs
    # which would not constrain the use of unfeasible solutions in gurobi)
    model.addConstr(unfeasible_matrix @ x == 0.0, name="unfeasible")

    # Trips single-entering constraints ( constraint (2) for trips )
    for j in range(m, m + n):
        model.addConstr(sum(x[(m + n) * i + j] for i in range(0, m + n)) == 1.0,
                        name="trip_in_" + str(j))

    # Trips single-leaving constraints ( constraint (3) for trips )
    for i in range(m, m + n):
        model.addConstr(sum(x[(m + n) * i + j] for j in range(0, m + n)) == 1.0,
                        name="trip_out_" + str(i))

    # Leaving depot == Entering depot constraints
    for depot_index in range(0, m):
        model.addConstr(sum(x[(m + n) * depot_index + j] for j in range(0, m + n)) ==
                        sum(x[(m + n) * i + depot_index] for i in range(0, m + n)),
                        name="depot_" + str(depot_index))

    # Depots capacity constraints
    for i in range(0, m):
        model.addConstr(sum(x[(m + n) * i + j] for j in range(0, m + n)) <= depots_capacities[i],
                        name="depot_capacity_" + str(i))

    # Add the path constraints
    if len(unfeasible_paths) > 0:
        for path in unfeasible_paths:
            model.addConstr(sum(x[(m + n) * path[i] + path[i + 1]] for i in range(len(path) - 1)) <= (len(path) - 1))

    # Optimize model
    model.optimize()

    return model, x


def follow_path_from_start(m, solution_matrix, starting_depot, first_trip):
    current_path = [starting_depot, first_trip]

    while current_path[-1] != starting_depot:

        for next_index in range(solution_matrix.shape[0]):
            if solution_matrix[current_path[-1], next_index] == 1.0:
                current_path += [next_index]
                break

        # if it gets to another depot => stop
        if current_path[-1] < m:
            break

    if current_path[-1] != starting_depot:
        return current_path
    else:
        return []


def get_unfeasible_paths_for_depot(m, n, solution_array, starting_depot):
    solution_matrix = solution_array.reshape(m + n, m + n)

    paths = []
    for start_trip in range(m + n):
        if solution_matrix[starting_depot, start_trip] == 1.0:
            paths += [follow_path_from_start(m, solution_matrix, starting_depot, first_trip=start_trip)]

    unfeasible_paths = []
    for path in paths:
        if len(path) > 0:
            unfeasible_paths += [path]

    return unfeasible_paths


def get_unfeasible_paths(m, n, solution_array):
    unfeasible_paths = []
    for depot in range(m):
        unfeasible_paths += get_unfeasible_paths_for_depot(m, n, solution_array, starting_depot=depot)

    return unfeasible_paths


def read_obj_file_paths(file_path):
    with open(file_path, "r") as file:
        first = file.readline()
        second = file.readline()
        third = file.readline()

        unfeasible_paths = [[int(elem) for elem in arr.split(", ")] for arr in third[2:-2].split("], [")]

        iteration = int(second.split()[1]) + 1

    return unfeasible_paths, iteration


if __name__ == '__main__':
    file_path = "./data/m4n500s0.inp"
    m, n, depots_capacities, cost_matrix = read_cost_matrix(file_path)
    unfeasible_matrix = get_unfeasible_matrix(cost_matrix)

    print(cost_matrix)
    print(m, " ", n, " ", depots_capacities)

    # unfeasible_paths = []
    # iteration_count = 0
    unfeasible_paths, iteration_count = read_obj_file_paths("objective_0.out")

    try:

        unfeasible_paths_count = len(unfeasible_paths) - 1

        while unfeasible_paths_count < len(unfeasible_paths):
            start = time.time()

            unfeasible_paths_count = len(unfeasible_paths)

            model, x = solve(m, n, depots_capacities, cost_matrix, unfeasible_matrix, unfeasible_paths)
            unfeasible_paths += get_unfeasible_paths(m, n, x.X)

            end = time.time()
            print(" ELAPES TIME : ", (end - start))

            print("Current Obj (iteration ", iteration_count, ") : ", model.objVal)

            np.save("results.npy", x.X)
            with open("objective_1.out", "w") as file:
                file.write(str(model.objVal) + "\n")
                file.write("Iteration: " + str(iteration_count) + "\n")
                file.write(str(unfeasible_paths))

            iteration_count += 1

        print("Final solution:\n", x.X)
        print("Final Obj (iteration ", iteration_count, ") : ", model.objVal)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))
    except AttributeError:
        print('Encountered an attribute error')
