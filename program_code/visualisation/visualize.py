# TODO: #10 make bar charts of students per room (and its max capacity), courses per rooms, etc for quick error checking
# TODO: #12 make representation of one student's schedule

import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network as PyvisNetwork
from .fix_webpage import fix_webpage
from ..classes.result import Result


def plot_statistics(results: list[Result]):
    evening_timeslots = [result.score_vector[1] for result in results]
    student_overbookings = [result.score_vector[2] for result in results]
    gaps = [result.score_vector[3] for result in results]
    total_scores = [result.score for result in results]
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(9, 4.5), tight_layout=True)
    ax1.hist(
        total_scores,
        100,
    )
    ax1.set_title("Total score")

    ax2.hist(evening_timeslots, 100)
    ax2.set_title("Evening timeslots")

    ax3.hist(student_overbookings, 100)
    ax3.set_title("Couse conflicts")

    ax4.hist(gaps, 100)
    ax4.set_title("Gaps")

    plt.show()


class GraphVisualization:
    """Visualize schedule as a graph."""

    def __init__(self, schedule):
        self.schedule = schedule
        # edges is a list which stores the set of edges that constitutes a graph
        self.edges = self.schedule.edges

    def print_nodes(self):
        """Print nodes with id's in rows to terminal"""
        print("\n")
        print("Nodes by id:")
        for id in self.schedule.nodes.keys():
            print(f"{id}: {self.schedule.nodes[id]}")
        print("\n")

    def visualize(self, print_nodes: bool = False, output_folder: str = "output", plot: bool = False):
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
                Level: {level}
                Label: {str(node)}
                """
                for neighbor_tag in ["activities", "students", "timeslots"]:
                    if hasattr(node, neighbor_tag):
                        title += f"{neighbor_tag}: [\n"
                        for neighbor in getattr(node, neighbor_tag).values():
                            title += f"    {neighbor.id}: {neighbor} \n"
                        title += "]\n"
                title += f"""
                
                Attributes: {node.__dict__}
                """
                G.add_node(node.id, title=title, label=str(node), color=color, level=level)

        # Add hidden nodes
        for category in hidden_nodes:
            for node in category:
                G.add_node(node.id, level=len(shown_nodes), hidden=True)

        # Add all edges to networkx graph
        G.add_edges_from(self.edges)

        # Output interactive visualization to html file with pyvis
        do_filter_menu = True
        net = PyvisNetwork(layout=True, height="900px", filter_menu=do_filter_menu)
        net.from_nx(G)
        net.options.physics.enabled = True
        net.repulsion()
        net.options.edges.smooth.enabled = False
        net.options.layout.set_separation(500)
        net.options.layout.hierarchical.sortMethod = "directed"
        net.show(f"{output_folder}/graph.html")

        if do_filter_menu:
            # Filter menu function is broken, this function repairs it.
            fix_webpage(output_folder, net)

        print(f"\nView a sample of graph results in your browser: {output_folder}/sample.html")
