# TODO: #9 make visualisation of graph with connections
# TODO: #10 make bar charts of students per room (and its max capacity), courses per rooms, etc for quick error checking
# TODO: #12 make representation of one student's schedule

from ..classes.schedule import Schedule
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


# Defining a Class
class GraphVisualization:
    def __init__(
        self,
        schedule: Schedule,
    ):
        self.schedule = schedule
        # edges is a list which stores the set of edges that constitutes a graph
        self.edges = schedule.edges

    # addEdge function inputs the vertices of an
    # edge and appends it to the visual list
    # def addEdge(self, a, b):
    #     temp = [a, b]
    #     self.edges.append(temp)

    def visualize(self, replace_id: bool = False, show_bipartite: bool = False):
        """In visualize function G is an object of class Graph given by networkx G.add_edges_from(visual).
        Creates a graph with a given list."""
        # Print nodes in rows to terminal
        for id in self.schedule.nodes.keys():
            print(f"{id}: {self.schedule.nodes[id]}")
        _edges_vis = []
        if replace_id:
            for edge in self.edges:
                names = [self.schedule.nodes[id].__str__ for id in edge]
                _edges_vis.append(names)
        else:
            _edges_vis = self.edges

        G = nx.Graph()
        if show_bipartite:
            nodes_students = list(self.schedule.students.keys())
            nodes_courses = list(self.schedule.students.keys())
            G.add_nodes_from(nodes_students, bipartite=0)
            G.add_nodes_from(nodes_courses, bipartite=1)
            # nx.draw_networkx(G) - plots the graph

            nx.draw_networkx(
                G,
                pos=nx.drawing.layout.bipartite_layout(G, nodes_courses),
                width=2,
            )
        else:
            G.add_nodes_from(self.schedule.nodes)
            G.add_edges_from(_edges_vis)
            nx.draw_networkx(G)

        # # TEST
        # _edges_vis.append((nodes_courses[0], nodes_rooms[0]))

        # plt.show() - displays the graph
        plt.show()

        net = Network(notebook=False)
        net.from_nx(G)
        net.show("output/example.html")
