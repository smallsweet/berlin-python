var svg = d3.select("#board").append("svg")
var circle = svg.selectAll("circle");

$(document).ready(function(){
  draw_game(game);
})

function berlingame2d3format(berlin){
  //berlin better not lie about node ids or have any missing
  //let's hope it's consistent about 1 indexing them too
  
  var nodes = {}
  var links=[]
  
  for (var key in berlin.map.nodes) {
    var bnode = berlin.map.nodes[key]
    nodes[bnode.id-1]={
      "name": bnode.id-1, "type": bnode.type }
  }

  for (var index in berlin.state ) {
    state = berlin.state[index]
    nodes[state.node_id-1].units = state.number_of_soldiers
    nodes[state.node_id-1].owner = state.player_id
  }

  for (var key in berlin.map.paths) {
    path = berlin.map.paths[key]
    links.push({'source':(path.from-1), 'target':(path.to-1), 'value':1})
  } 

  var nodelist=[]
  for (var key in nodes) {
    nodelist.push(nodes[key])
  }
  
  var res={'nodes':nodelist,'links':links}
  return res
}

function draw_game(berlin){
  
  var width = 1100;
  var height = 800;
  d3game=berlingame2d3format(game, width, height);
  var color = d3.scale.category20();

  var svg = d3.select("#board").append("svg")
    .attr("width", width)
    .attr("height", height);

  var force = d3.layout.force()
    .charge(-800)
    .linkDistance(60)
    .linkStrength(1.0)
    .friction(0.95) // higher values = better untangling
    .gravity(0.05)
    .size([width, height]);

  var link = svg.selectAll(".link")
      .data(d3game.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  var node = svg.selectAll(".node")
      .data(d3game.nodes)
    .enter().append("circle")
      .attr("class", function(d) { return "node-"+d.type })
      .attr("r", function(d) { return d.type == "city" ? 30 : 20 })
      .style("fill", function(d) { return color(d.owner); })
      .call(force.drag);
  
  force.nodes(d3game.nodes)
    .links(d3game.links)
    .start();

  node.append("title")
    .text(function(d) { return d.name; });

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
    node.attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });
  });
  return force
};
