import numpy as np

if __name__ == '__main__':

    # dir_name = "./results"
    # dir_name = "./ant_colony_3_results/done"
    dir_name = "./ant_colony_3_results/sorted"
    alg_names = [
        # "ACS_1",
        # "ACS_2",
        "ACS_3"
    ]
    experiments = [
        "m4n500s0.inp",
        "m4n500s1.inp",
        "m4n500s2.inp",
        "m4n500s3.inp",
        "m4n500s4.inp",
        "m8n500s0.inp",
        "m8n500s1.inp",
        "m8n500s2.inp",
        "m8n500s3.inp",
        "m8n500s4.inp",
    ]

    for index in range(len(experiments)):
        experiments[index] = experiments[index] + "_sorted"

    paths = [(f"{dir_name}/{alg}/{exp}", alg, exp) for alg in alg_names for exp in experiments]
    # paths.remove((f"{dir_name}/ACS_1/m4n500s4.inp", "ACS_1", "m4n500s4.inp"))

    runs = 30

    for file_path, algorithm, experiment in paths:

        runs_bests = []

        for run in range(runs):

            costs = []
            with open(f"{file_path}/cost_run_{run}.txt") as file:
                line = file.readline()
                while line:
                    costs += [int(float(line.strip().split(": ")[1]))]
                    line = file.readline()

            runs_bests += [min(costs)]

        run_values = [np.min(runs_bests),
                      np.max(runs_bests),
                      np.mean(runs_bests),
                      np.median(runs_bests),
                      np.std(runs_bests)]

        values_str = [experiment] + [f"{x:,}".replace(',', ' ').replace('.', ',') for x in run_values]
        str_vals = " & ".join(values_str) + " \\\\"
        print(str_vals)
