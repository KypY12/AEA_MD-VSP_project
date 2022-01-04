import json

from ant_colony.problem_graph import ProblemGraph
from ant_colony.partitioning.graph_partition import GraphPartition


class Partitioner:

    def __init__(self, graph: ProblemGraph):
        self.graph = graph
        self.partitions = []

    def toJSON(self):
        return json.dumps(self, default=lambda t: t.__dict__, sort_keys=True, indent=4)

    def get_graph(self):
        return self.graph

    def get_partitions(self):
        return self.partitions

    def __setup_partitions__(self, partitions):
        for depot_index, part in enumerate(partitions):
            part_obj = GraphPartition(depot_index)
            part_obj.add_nodes(part)
            self.partitions.append(part_obj)

    # def execute(self):
    #     # Partition based on trip closest depot
    #     partitions = [[] for _ in range(self.graph.get_m())]
    #     for trip_node in range(self.graph.get_m(), self.graph.get_matrix_size()):
    #         partitions[self.__find_closest_depot_by_cost__(trip_node)] += [trip_node]
    #
    #     self.__setup_partitions__(partitions)

    # def execute(self):
    #     # Partition based on node index
    #     m = self.graph.get_m()
    #     n = self.graph.get_n()
    #     partition_size = int(n / m)
    #
    #     partitions = []
    #     for index in range(m, n, partition_size):
    #         partitions.append(list(range(index, index + partition_size)))
    #
    #     self.__setup_partitions__(partitions)

    def execute(self):
        # Partition based on balanced node weights
        def get_node_weight(node):
            cost_matrix = self.graph.get_cost_matrix()

            in_weight = 0
            for row_index in range(cost_matrix.shape[0]):
                if cost_matrix[row_index, node] != -1:
                    in_weight += 1

            out_weight = 0
            for col_index in range(cost_matrix.shape[1]):
                if cost_matrix[node, col_index] != -1:
                    out_weight += 1

            return in_weight + out_weight

        m = self.graph.get_m()
        n = self.graph.get_n()

        nodes = list(range(m, n + m))
        sorted_nodes = sorted(nodes, key=get_node_weight, reverse=True)

        partitions = [[] for _ in range(m)]
        for index in range(m, n + m):
            partitions[index % m].append(sorted_nodes[index - m])

        self.__setup_partitions__(partitions)

    def __find_closest_depot_by_cost__(self, node):
        # Searches the closest depot by cost
        # Obs.: the search is done using both arc orientations
        depot_neighbours = list(filter(lambda t: t[0] < self.graph.get_m(), self.graph.get_neighbours_cost(node)))
        min_depot = min(depot_neighbours, key=lambda t: t[1])
        return min_depot[0]
