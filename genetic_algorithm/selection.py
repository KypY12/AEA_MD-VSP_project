import numpy as np


class Selection:

    def execute(self, population, fitness_values):
        intervals = np.cumsum(fitness_values) / np.sum(fitness_values)

        pop_size = population.shape[0]
        selected = np.random.rand(pop_size)
        selected_indecies = []

        for value in selected:
            for index, interval in enumerate(intervals):
                if value < interval:
                    selected_indecies += [index]
                    break

        return population[selected_indecies]
