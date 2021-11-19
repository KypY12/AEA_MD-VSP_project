import time

import numpy as np

from genetic_algorithm.crossover import Crossover
from genetic_algorithm.evaluation import Evaluation
from genetic_algorithm.mutation import Mutation
from genetic_algorithm.selection import Selection


class GeneticAlgorithm:

    def __init__(self, cost_matrix_file_path,
                 pop_size,
                 mutation_rate,
                 crossover_rate,
                 crossover_type,
                 mutation_choosing_prob,
                 max_iterations,
                 selection_pressure=1):

        self.mutation = Mutation(mutation_rate, mutation_choosing_prob)
        self.crossover = Crossover(crossover_rate, crossover_type)
        self.selection = Selection()

        self.initial_pop_size = pop_size
        self.selection_pressure = selection_pressure
        self.max_iterations = max_iterations

        self.evals = []
        self.evaluation = Evaluation(cost_matrix_file_path)

        self.m = self.evaluation.m
        self.n = self.evaluation.n
        self.chromosome_size = (self.m + self.n) ** 2
        self.population = np.random.randint(0, 2, (pop_size, self.chromosome_size))

        self.fitness_values = []

    def fitness_execute(self):
        min_eval, max_eval = min(self.evals), max(self.evals)
        eval_diff = max_eval - min_eval
        if eval_diff == 0.0:
            eval_diff = 1.0

        return [(1.01 + (max_eval - current_eval) / eval_diff) ** self.selection_pressure
                for current_eval in self.evals]

    def get_best_eval_chromosome_index(self):
        min_index = 0
        for chromosome_index in range(self.population.shape[0]):
            if self.evals[chromosome_index] < self.evals[min_index]:
                min_index = chromosome_index

        return min_index

    def execute(self):

        for iteration in range(self.max_iterations):
            print(f"Iteration {iteration}")
            start = time.time()

            # Mutation
            print("Mutation")
            self.mutation.execute(self.population)

            # Crossover
            print("Crossover")
            self.crossover.execute(self.population)

            # Evaluation
            print("Evaluation")
            self.evals = self.evaluation.execute(self.population)

            # Fitness
            print("Fitness")
            self.fitness_values = self.fitness_execute()

            # Selection
            print("Selection")
            self.population = self.selection.execute(self.population, self.fitness_values)

            end = time.time()
            print(f"Elapsed time : {end - start} seconds")

        # Compute current evaluations and fitnesses
        self.evals = self.evaluation.execute(self.population)
        self.fitness_values = self.fitness_execute()

        # best_eval_index = self.get_best_eval_chromosome_index()
