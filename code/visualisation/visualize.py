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

        # Initialize Networkx graph
        G = nx.Graph()

        # Define iterables for hierarchal structure
        shown_nodes = [
            self.schedule.activities.values(),
            self.schedule.timeslots.values(),
            self.schedule.students.values(),
        ]
        hidden_nodes = [
            self.schedule.courses.values(),
            self.schedule.rooms.values(),
        ]
        colors = ["blue", "red", "orange", "green", "purple"]
        assert len(colors) >= len(shown_nodes), "Not enough colors available for levels."

        # Add all nodes with relevant metadata to networkx graph
        for (category, color, level) in zip(shown_nodes, colors, range(len(shown_nodes))):
            for node in category:
                title = f"""ID: {node.id}
                Type: {type(node).__name__}
                label: {str(node)}
                """
                for neighbor_tag in ["activities", "students", "timeslots"]:
                    if hasattr(node, neighbor_tag):
                        title += f"{neighbor_tag}: [\n"
                        for neighbor in getattr(node, neighbor_tag).values():
                            title += f"    {neighbor.id}: {neighbor} \n"
                        title += "]\n"
                G.add_node(node.id, title=title, label=str(node), color=color, level=level)

        # Add hidden nodes
        for category in hidden_nodes:
            for node in category:
                G.add_node(node.id, level=len(shown_nodes), hidden=True)

        # Add all edges to networkx graph
        G.add_edges_from(self.edges)

        # Output interactive visualization to html file with pyvis
        net = PyvisNetwork(layout=True, height="900px")
        net.from_nx(G)
        net.options.physics.enabled = True
        net.repulsion()
        net.options.edges.smooth.enabled = False
        net.options.layout.set_separation(500)
        net.options.layout.hierarchical.sortMethod = "directed"
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
