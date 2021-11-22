class GraphPartition:

    def __init__(self, depot_node):
        self.depot_node = depot_node
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_nodes(self, nodes):
        self.nodes += nodes

    def remove_node(self, node):
        self.nodes.remove(node)

    def remove_nodes(self, nodes):
        for node in nodes:
            self.nodes.remove(node)

    def get_nodes(self):
        return self.nodes

    def get_depot(self):
        return self.depot_node

    def __str__(self):
        return f"{self.depot_node} => {len(self.nodes)} nodes = {self.nodes}"
