# TODO: #10 make bar charts of students per room (and its max capacity), courses per rooms, etc for quick error checking
# TODO: #12 make representation of one student's schedule

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network as PyvisNetwork
from .fix_webpage import fix_webpage
from ..classes.result import Result
from ..classes.data import prepare_path


def plot_statistics(results: list[Result]):
    evening_timeslots = [result.score_vector[0] for result in results]
    student_overbookings = [result.score_vector[1] for result in results]
    gaps_1, gaps_2, gaps_3 = [[result.score_vector[i] for result in results] for i in range(2, 5)]
    total_scores = [result.score for result in results]

    fig, ax = plt.subplots(2, 3, figsize=(9, 4.5), tight_layout=True, sharex=True, sharey=False)

    axtot = ax[0, 0]  # type: ignore
    axtot.hist(total_scores, 100)
    axtot.set_title(f"Total score \n mean: ${np.mean(total_scores):.2f} ± {np.std(total_scores):.2f}$")

    axevn = ax[0, 1]  # type: ignore
    axevn.hist(evening_timeslots, 100)
    axevn.set_title(f"Evening timeslots \n mean: ${np.mean(evening_timeslots):.2f} ± {np.std(evening_timeslots):.2f}$")

    axconf = ax[0, 2]  # type: ignore
    axconf.hist(student_overbookings, 100)
    axconf.set_title(
        f"Course conflicts \n mean: ${np.mean(student_overbookings):.2f} ± {np.std(student_overbookings):.2f}$"
    )

    axg1 = ax[1, 0]  # type: ignore
    axg1.hist(gaps_1, 100)
    axg1.set_title(f"1 gap \n mean: ${np.mean(gaps_1):.2f} ± {np.std(gaps_1):.2f}$")

    axg1 = ax[1, 1]  # type: ignore
    axg1.hist(gaps_2, 100)
    axg1.set_title(f"2 gaps \n mean: ${np.mean(gaps_2):.2f} ± {np.std(gaps_2):.2f}$")

    axg1 = ax[1, 2]  # type: ignore
    axg1.hist(gaps_3, 100)
    axg1.set_title(f">2 gaps \n mean: ${np.mean(gaps_3):.2f} ± {np.std(gaps_3):.2f}$")

    plt.savefig("output/image.png")
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
        prepare_path(output_folder)
        net.show(f"{output_folder}/graph.html")

        if do_filter_menu:
            # Filter menu function is broken, this function repairs it.
            fix_webpage(output_folder, net)

        print(f"\nView a sample of graph results in your browser: {output_folder}/sample.html")
