import numpy as np


from evaluation.evaluation import Evaluation


def generate_random_bit_string(shape):
    return np.random.randint(0, 2, shape)


if __name__ == '__main__':
    file_path = "../data/m4n500/m4n500s0.inp"
    evaluation = Evaluation(file_path)
    cost_matrix_flat = evaluation.cost_matrix_flat

    max_iterations = 2

    for iteration in range(max_iterations):
        last_violations = 1
        while last_violations > 0:
            candidate_solution = generate_random_bit_string(cost_matrix_flat.shape[0])
            first_violations = evaluation.get_first_constraints_violations(candidate_solution)
            print("First")
            while first_violations > 0:
                candidate_solution = generate_random_bit_string(cost_matrix_flat.shape[0])
                first_violations = evaluation.get_first_constraints_violations(candidate_solution)
            print("Second")
            last_violations = evaluation.get_last_constraint_violations(candidate_solution)

        print(f"Iteration {iteration} finished!")

