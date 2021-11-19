import numpy as np


class Mutation:

    def __init__(self, mutation_prob, mutation_choosing_prob):
        self.mutation_prob = mutation_prob
        self.mutation_choosing_prob = mutation_choosing_prob

    def execute(self, population):
        pop_size, chromosome_size = population.shape

        # Select chromosomes for mutation (save their indecies)
        indecies = np.nonzero(np.random.rand(pop_size) < self.mutation_choosing_prob)[0]

        for index in indecies:
            # Create a mask with selected genes for mutation
            mutation_mask = np.array(np.random.rand(chromosome_size) < self.mutation_prob, dtype=np.byte)

            # Apply mutation
            population[index] = (population[index] + mutation_mask) % 2
