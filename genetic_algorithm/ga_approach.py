from genetic_algorithm.ga import GeneticAlgorithm

if __name__ == '__main__':
    file_path = "../data/m4n500/m4n500s0.inp"

    # TO DO:
    #   initialize the genetic algorithm population with gurobi solutions
    ga = GeneticAlgorithm(file_path,
                          pop_size=100,
                          mutation_rate=0.01,
                          crossover_rate=0.3,
                          crossover_type="double_cut",
                          mutation_choosing_prob=1.0,
                          max_iterations=1000,
                          selection_pressure=5.0)

    ga.execute()
