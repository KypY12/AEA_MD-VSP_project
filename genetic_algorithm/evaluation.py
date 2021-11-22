from genetic_algorithm.eval_helpers import read_cost_matrix, get_unfeasible_matrix, get_unfeasible_paths
import tqdm


class Evaluation:

    def __init__(self, cost_matrix_file_path):

        self.m, self.n, self.depots_capacities, self.cost_matrix = read_cost_matrix(cost_matrix_file_path)
        self.cost_matrix_flat = self.cost_matrix.flatten()

        self.violations_range = self.m + self.n
        self.violations_functions = [self.get_unfeasible_arcs_violations,
                                     self.get_single_entering_violations,
                                     self.get_single_leaving_violations,
                                     self.get_depot_violations,
                                     self.get_depot_capacity_violations,
                                     self.get_depot_paths_violations]
        self.unfeasible_matrix = get_unfeasible_matrix(self.cost_matrix)

    def get_unfeasible_arcs_violations(self, chromosome):
        # Unfeasible arcs should not be chosen
        # Counts and returns the number of unfeasible arcs chosen
        return self.unfeasible_matrix.dot(chromosome)

    def get_single_entering_violations(self, chromosome):
        # 'sum' == 1.0 (constraint)
        # Counts and returns the number of violations
        violations = 0
        for j in range(self.m, self.m + self.n):
            violations += int(sum(chromosome[(self.m + self.n) * i + j] for i in range(0, self.m + self.n)) != 1.0)

        return violations

    def get_single_leaving_violations(self, chromosome):
        # 'sum' == 1.0 (constraint)
        # Counts and returns the number of violations

        violations = 0
        for i in range(self.m, self.m + self.n):
            violations += int(sum(chromosome[(self.m + self.n) * i + j] for j in range(0, self.m + self.n)) != 1.0)

        return violations

    def get_depot_violations(self, chromosome):
        # depot entering == depot leaving
        # Counts and returns the number of violations
        violations = 0
        for depot_index in range(0, self.m):
            violations += int(sum(chromosome[(self.m + self.n) * depot_index + j] for j in range(0, self.m + self.n)) !=
                              sum(chromosome[(self.m + self.n) * i + depot_index] for i in range(0, self.m + self.n)))

        return violations

    def get_depot_capacity_violations(self, chromosome):
        # Depots capacities should be met ( sum <= depot_capacity)
        # Counts and returns the number of violations
        violations = 0
        for i in range(0, self.m):
            violations += int(sum(chromosome[(self.m + self.n) * i + j]
                                  for j in range(0, self.m + self.n)) > self.depots_capacities[i])

        return violations

    def get_depot_paths_violations(self, chromosome):
        # Any path starting from a depot should end at the same depot
        # Counts and returns the number of violations (the number of unfeasible paths)
        return len(get_unfeasible_paths(self.m, self.n, chromosome))

    def get_first_constraints_violations(self, chromosome):
        violations = 0
        violations += self.get_unfeasible_arcs_violations(chromosome)
        violations += self.get_single_entering_violations(chromosome)
        violations += self.get_single_leaving_violations(chromosome)
        violations += self.get_depot_violations(chromosome)
        violations += self.get_depot_capacity_violations(chromosome)

        return violations

    # def get_all_constraints_violations(self, chromosome):
    #     violations = 0
    #     violations += self.get_unfeasible_arcs_violations(chromosome)
    #     violations += self.get_single_entering_violations(chromosome)
    #     violations += self.get_single_leaving_violations(chromosome)
    #     violations += self.get_depot_violations(chromosome)
    #     violations += self.get_depot_capacity_violations(chromosome)
    #     violations += self.get_depot_paths_violations(chromosome)
    #
    #     return violations

    def chromosome_eval(self, chromosome):
        # current_index = 0
        # violations = self.violations_functions[current_index](chromosome)
        #
        # for index, violation_function in enumerate(self.violations_functions):
        #     violations = self.violations_functions[current_index](chromosome)
        #     if violations > 0:
        #         return (self.violations_range * (len(self.violations_functions) - index - 1)) + \
        #                (violations / self.violations_range)
        #
        # return 0

        first_violations = self.get_first_constraints_violations(chromosome)
        if first_violations == 0:
            path_violations = self.get_depot_paths_violations(chromosome)
            return path_violations / self.violations_range
        else:
            return self.violations_range + first_violations

        # return self.get_constraints_violations(chromosome)

    def execute(self, population):
        evals = []
        for chrom in population:
            evals += [self.chromosome_eval(chrom)]

        return evals
        # return [self.chromosome_eval(chromosome) for chromosome in population]
