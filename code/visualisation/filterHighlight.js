// Custom code to replace missing highlightFilter function for web display of graph
Object.filter = (obj, predicate) =>
  Object.keys(obj)
    .filter((key) => predicate(obj[key]))
    .reduce((res, key) => ((res[key] = obj[key]), res), {});

function highlightFilter(filter, reset = false) {
  if (reset) {
    nodes = new vis.DataSet(Object.values(allNodes));
    edges = new vis.DataSet(Object.values(allEdges));
  }

  if (filter.item == "node") {
    filteredNodes = Object.filter(allNodes, (obj) => {
      if (obj[filter.property] in filter.value) {
        return true;
      }
      return false;
    });
    nodes = new vis.DataSet(Object.values(filteredNodes));
  } else if (filter.item == "edge") {
    filteredEdges = Object.filter(allEdges, (obj) => {
      if (obj[filter.property] in filter.value) {
        return true;
      }
      return false;
    });
    edges = new vis.DataSet(Object.values(filteredEdges));
  }

  var container = document.getElementById("mynetwork");
  data = { nodes: nodes, edges: edges };

  network = new vis.Network(container, data, parsed_options);
}

function filterHighlight(input) {
  if (input.nodes.length == 0) {
    highlightFilter({}, (reset = true));
  }
}
