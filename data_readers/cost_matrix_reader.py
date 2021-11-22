import numpy as np


class CostMatrixReader:

    def __init__(self, file_path, _format="standard"):
        self.file_path = file_path
        self._format = _format

    def read(self):

        if self._format == "standard":

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

            with open(self.file_path, "r") as file:
                cost_matrix_list = []

                line = file.readline()
                m, n, depot_capacities = process_first_line(line)

                line = file.readline()
                while line:
                    cost_matrix_list = process_matrix_line(cost_matrix_list, line)
                    line = file.readline()

            return m, n, depot_capacities, np.array(cost_matrix_list)
