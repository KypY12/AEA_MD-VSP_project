class ProblemGraph:

    def __init__(self, cost_matrix, m=None, n=None, depot_capacities=None):
        self.cost_matrix = cost_matrix
        self.m = m
        self.n = n
        self.depot_capacities = depot_capacities

    def get_in_neighbours(self, node):
        return [row_index for row_index in range(self.cost_matrix.shape[0]) if self.cost_matrix[row_index, node] != -1]

    def get_out_neighbours(self, node):
        return [col_index for col_index in range(self.cost_matrix.shape[1]) if self.cost_matrix[node, col_index] != -1]

    def get_neighbours(self, node, orientation="all"):
        if orientation == "in":
            return self.get_in_neighbours(node)
        elif orientation == "out":
            return self.get_out_neighbours(node)

        return self.get_in_neighbours(node) + self.get_out_neighbours(node)

    def get_in_neighbours_cost(self, node):
        return [(row_index, self.cost_matrix[row_index, node]) for row_index in range(self.cost_matrix.shape[0]) if
                self.cost_matrix[row_index, node] != -1]

    def get_out_neighbours_cost(self, node):
        return [(col_index, self.cost_matrix[node, col_index]) for col_index in range(self.cost_matrix.shape[1]) if
                self.cost_matrix[node, col_index] != -1]

    def get_neighbours_cost(self, node, orientation="all"):
        if orientation == "in":
            return self.get_in_neighbours_cost(node)
        elif orientation == "out":
            return self.get_out_neighbours_cost(node)

        return self.get_in_neighbours_cost(node) + self.get_out_neighbours_cost(node)

    def get_cost_of(self, node_1, node_2):
        return self.cost_matrix[node_1, node_2]

    def get_cost_matrix(self):
        return self.cost_matrix

    def get_n(self):
        return self.n

    def get_m(self):
        return self.m

    def get_matrix_size(self):
        return self.cost_matrix.shape[0]

    def get_depot_capacities(self):
        return self.depot_capacities