//  Custom code to replace missing highlightFilter function for web display of graph

// Generic object filtering function
Object.filter = (obj, predicate) =>
  Object.keys(obj)
    .filter((key) => predicate(obj[key]))
    .reduce((res, key) => ((res[key] = obj[key]), res), {});

// Filter data according to user input
function highlightFilter(filter, reset = false) {
  if (reset) {
    nodes = new vis.DataSet(Object.values(allNodes));
    edges = new vis.DataSet(Object.values(allEdges));
  }

  if (filter.item == "node") {
    // Filter nodes
    filteredNodes = Object.filter(allNodes, (obj) => {
      if (filter.value.includes(obj[filter.property].toString())) {
        return true;
      }
      return false;
    });
    // Filtered set of nodes
    nodes = new vis.DataSet(Object.values(filteredNodes));
  } else if (filter.item == "edge") {
    // Filter edges
    filteredEdges = Object.filter(allEdges, (obj) => {
      if (obj[filter.property] in filter.value) {
        return true;
      }
      return false;
    });
    // Filtered set of edges
    edges = new vis.DataSet(Object.values(filteredEdges));
  }

  // Reinitialize network with filtered data
  var container = document.getElementById("mynetwork");
  data = { nodes: nodes, edges: edges };
  network = new vis.Network(container, data, parsed_options);
}

function filterHighlight(input) {
  // Reset filter
  if (input.nodes.length == 0) {
    highlightFilter({}, (reset = true));
  }
}
