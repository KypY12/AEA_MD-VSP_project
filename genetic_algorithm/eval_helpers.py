import numpy as np


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
