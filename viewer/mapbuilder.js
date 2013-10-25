var svg = d3.select("#board").append("svg")
var circle = svg.selectAll("circle");

$(document).ready(function(){
draw_game(game);

})

function berlingame2d3format(berlin){
	var nodes=[]
  var links=[]
	//berlin better not lie about node ids or have any missing.
	
  $.each(berlin.map.nodes, function(index,guy){
		nodes[guy.id-1]={"name":guy.id-1,"group":1, "type": guy.type}
   })
  $.each(berlin.state, function(index,guy){
		nodes[guy.node_id-1].units = guy.number_of_soldiers
		nodes[guy.node_id-1].owner = guy.player_id
   })

   if (nodes.length!=berlin.map.nodes.length){
		debugger;
	  rwiefjfew;
	 }
   $.each(berlin.map.paths, function(index,guy){
		links.push({'source':(guy.from-1),'target':(guy.to-1), 'value':1})
	 })	 
	var res={'nodes':nodes,'links':links}
	return res
}

function draw_game(berlin){
	d3game=berlingame2d3format(game);
	var width = 1100,
    height = 800;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-100)
    .linkDistance(30)
    .size([width, height]);

var svg = d3.select("#board").append("svg")
    .attr("width", width)
    .attr("height", height);

  force
      .nodes(d3game.nodes)
      .links(d3game.links)
      .start();

  var link = svg.selectAll(".link")
      .data(d3game.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  var node = svg.selectAll(".node")
      .data(d3game.nodes)
    .enter().append("circle")
      .attr("class", function(d) { return "node-"+d.type })
      .attr("r", function(d) { return d.type == "city" ? 8 : 2 })
      .style("fill", function(d) { return color(d.owner); })

			.call(force.drag);

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
