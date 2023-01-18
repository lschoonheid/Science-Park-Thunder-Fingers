"""The default html generator of pyvis does not offer full functionality of filter menu.
This program fixes broken links and missing functions.
"""

from pyvis.network import Network as PyvisNetwork
import json
from copy import copy
from bs4 import BeautifulSoup


def fix_webpage(output_folder: str, net: PyvisNetwork):
    # Convert network options to dictionary
    parsed_options = {}
    parsed_options["configure"] = net.options.configure.__dict__
    edges_dict = copy(net.options.edges.__dict__)
    edges_dict["smooth"] = net.options.edges.smooth.__dict__
    edges_dict["color"] = net.options.edges.color.__dict__
    parsed_options["edges"] = edges_dict
    parsed_options["interaction"] = net.options.interaction.__dict__
    layout_dict = copy(net.options.layout.__dict__)
    layout_dict["hierarchical"] = net.options.layout.hierarchical.__dict__
    parsed_options["layout"] = layout_dict

    # Generate javascript string to fix missing functions
    with open("code/visualisation/filterHighlight.js", "r") as file:
        # Insert options json
        script_var = "var parsed_options = " + json.dumps(parsed_options) + "\n"

        script = file.read()
        script = script_var + script

    with open(f"{output_folder}/graph.html", "r") as file:
        # Read incorrectly generated html file
        content = file.read()
        soup = BeautifulSoup(content, "lxml")

        # Broken links
        links = """<link href="https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.css" rel="stylesheet">
                        <script src="https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/js/tom-select.complete.min.js"></script>
                    
                        <script src="filterHighlight.js"></script>
                        """
        linksSoup = BeautifulSoup(links, "html.parser")

        head = soup.find("head")
        head.insert(-1, linksSoup)  # type: ignore

        visScript = soup.find_all("script")[-1]
        visScript.insert(0, script)

    with open(f"{output_folder}/graph.html", "w") as file:
        file.write(str(soup))
