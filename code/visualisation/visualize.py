# TODO: #9 make visualisation of graph with connections
# TODO: #10 make bar charts of students per room (and its max capacity), courses per rooms, etc for quick error checking
# TODO: #12 make representation of one student's schedule

from ..classes.schedule import Schedule
import networkx as nx
import matplotlib.pyplot as plt


# Defining a Class
class GraphVisualization:
    def __init__(
        self,
        schedule: Schedule,
    ):
        self.schedule = schedule
        # visual is a list which stores all
        # the set of edges that constitutes a
        # graph
        self.edges = schedule.edges

    # addEdge function inputs the vertices of an
    # edge and appends it to the visual list
    # def addEdge(self, a, b):
    #     temp = [a, b]
    #     self.edges.append(temp)

    # In visualize function G is an object of
    # class Graph given by networkx G.add_edges_from(visual)
    # creates a graph with a given list
    # nx.draw_networkx(G) - plots the graph
    # plt.show() - displays the graph
    def visualize(self, replace_id: bool = False):
        _edges_vis = []
        if replace_id:
            for edge in self.edges:
                names = [self.schedule.nodes[id].name for id in edge]
                _edges_vis.append(names)
        else:
            _edges_vis = self.edges

        G = nx.Graph()
        nodes_students = list(self.schedule.students.keys())
        nodes_courses = list(self.schedule.students.keys())
        nodes_rooms = list(self.schedule.rooms.keys())
        G.add_nodes_from(nodes_students, bipartite=0)
        G.add_nodes_from(nodes_courses, bipartite=1)
        G.add_nodes_from(nodes_rooms, bipartite=2)

        # # TEST
        # _edges_vis.append((nodes_courses[0], nodes_rooms[0]))

        G.add_edges_from(_edges_vis)
        # nx.draw_networkx(G)
        nx.draw_networkx(
            G,
            pos=nx.drawing.layout.bipartite_layout(G, nodes_courses),
            width=2,
        )

        plt.show()
