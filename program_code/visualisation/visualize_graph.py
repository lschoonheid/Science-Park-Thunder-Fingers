import networkx as nx
from pyvis.network import Network as PyvisNetwork
from .fix_webpage import fix_webpage
from ..classes import Schedule
from ..helpers import prepare_path


def print_nodes(schedule: Schedule):
    """Print nodes with id's in rows to terminal"""
    print("\n")
    print("Nodes by id:")
    for id in schedule.nodes.keys():
        print(f"{id}: {schedule.nodes[id]}")
    print("\n")


def visualize_graph(
    schedule: Schedule, do_print_nodes: bool = False, output_folder: str = "output", plot: bool = False
):
    """Visualize schedule as a graph."""
    # edges is a list which stores the set of edges that constitutes a graph
    edges = schedule.edges

    if do_print_nodes:
        print_nodes(schedule)

    # Initialize Networkx graph
    G = nx.Graph()

    # Define iterables for hierarchal structure
    shown_nodes = [
        schedule.activities.values(),
        schedule.timeslots.values(),
        schedule.students.values(),
    ]
    hidden_nodes = [
        schedule.courses.values(),
        schedule.rooms.values(),
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
    G.add_edges_from(edges)

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

    print(f"View a sample of graph results in your browser: {output_folder}/sample.html")
