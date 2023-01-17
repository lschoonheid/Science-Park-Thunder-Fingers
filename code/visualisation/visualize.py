# TODO: #10 make bar charts of students per room (and its max capacity), courses per rooms, etc for quick error checking
# TODO: #12 make representation of one student's schedule

from ..classes.schedule import Schedule
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network as PyvisNetwork


class GraphVisualization:
    """Visualize schedule as a graph."""

    def __init__(
        self,
        schedule: Schedule,
    ):
        self.schedule = schedule
        # edges is a list which stores the set of edges that constitutes a graph
        self.edges = schedule.edges

    def print_nodes(self):
        """Print nodes with id's in rows to terminal"""
        print("\n")
        print("Nodes by id:")
        for id in self.schedule.nodes.keys():
            print(f"{id}: {self.schedule.nodes[id]}")
        print("\n")

    def visualize(self, print_nodes: bool = False, plot: bool = False):
        """In visualize function G is an object of class Graph given by networkx G.add_edges_from(visual).
        Creates a graph with a given list."""
        if print_nodes:
            self.print_nodes()

        _edges_vis = self.edges

        G = nx.Graph()

        # Add all nodes with relevant metadata to networkx graph
        for student in self.schedule.students.values():
            G.add_node(student.id, title=student.name, label=student.node_type, color="blue")
        for course in self.schedule.courses.values():
            G.add_node(course.id, title=course.name, label=course.node_type, color="red", value=len(course.students))
        for activity in self.schedule.activities.values():
            G.add_node(
                activity.id,
                title=str(activity),
                label=activity.node_type,
                color="orange",
                value=len(activity.students),
                bipartite=1,
            )
        for room in self.schedule.rooms.values():
            G.add_node(room.id, title=room.name, label=room.node_type, color="purple")
        for timeslot in self.schedule.timeslots.values():
            G.add_node(
                timeslot.id,
                title=str(timeslot),
                label=timeslot.node_type,
                color="green",
                value=len(timeslot.activities),
                bipartite=0,
            )

        # Add all adges to networkx graph
        G.add_edges_from(_edges_vis)

        # Output interactive visualization to html file with pyvis
        net = PyvisNetwork()
        net.from_nx(G)
        net.show("output/graph.html")
        print("View output/graph.html in your browser")

        if plot:
            # Plot matplotlib graph in shell configuration
            nx.draw_networkx(
                G,
                pos=nx.drawing.layout.shell_layout(
                    G,
                    [
                        self.schedule.students,
                        self.schedule.courses,
                        self.schedule.activities,
                        self.schedule.rooms,
                        self.schedule.timeslots,
                    ],
                    scale=5,
                ),
            )
            plt.show()
