function berlingame2d3format(turn){
  //berlin better not lie about node ids or have any missing
  //let's hope it's consistent about 1 indexing them too
  
  var nodes = []
  var links=[]
  
  for (var i = 0; i < turn.map.nodes.length; i++) {
    var bnode = turn.map.nodes[i]
    nodes.push({ "name": bnode.id-1, "type": bnode.type })
  }

  for (var i = 0; i < turn.states.length; i++ ) {
    state = turn.states[i]
    nodes[state.node_id-1].units = state.number_of_soldiers
    nodes[state.node_id-1].player_id = state.player_id
  }

  for (var key in turn.map.paths) {
    path = turn.map.paths[key]
    links.push({'source':(path.from-1), 'target':(path.to-1), 'value':1})
  } 

  var res={'nodes':nodes,'links':links}
  return res
}

//var svg = d3.select("#board").append("svg")
//var circle = svg.selectAll("circle");

$(document).ready(function(){
  d3_state = make_map(game);
	//run_turns(d3_state)
	setup_buttons()
})

function setup_buttons(){
	$("#next").click(function(){
		current_turn+=1;
		run_turn(d3_state);
	});
	$("#prev").click(function(){
		current_turn-=1;
		run_turn(d3_state);
	});
}

current_turn=0;

var color={
	null:'#eee',
	0:'lightblue',
	1:'lightgreen',
	2:'lightred',
 	3:'gold'
}

function run_turns(d3_state){
	$.each(game, function(index,turn){
		console.log('running',turn)
		run_turn(d3_state, turn);
     
	});
}

function notify(message,success){
	$(".notifications").prepend(message)
}

function run_turn(d3_state){
	var force = d3_state.force
	var node = d3_state.node
	var labels = d3_state.labels
	var turn=game[current_turn]
	notify('running'+current_turn)
	var d3turn=berlingame2d3format(turn)
	$.each(d3turn.nodes, function(nodeindex, node){
		var exinode=force.nodes()[node.name]
		exinode.units=node.units
		exinode.player_id=node.player_id
	});
	node.transition().style("fill", function(d) {
		 	return color[d.player_id]
	})
		
	labels.transition().text(function(d) {
		return d.player_id == null ? '' : d.units.toString() 
	})
	force.resume()
}

function make_map(game){
	var firstturn = game[0]

  var width = 1100;
  var height = 800;
  var d3turn=berlingame2d3format(firstturn);

  var svg = d3.select("#board").append("svg")
    .attr("width", width)
    .attr("height", height);

  var force = d3.layout.force()
    .charge(-420)
    .linkDistance(60)
    .linkStrength(1.0)
    .friction(0.95) // higher values = better untangling
    .gravity(0.05)
    .size([width, height]);

  var link = svg.selectAll(".link")
      .data(d3turn.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  force.nodes(d3turn.nodes)
    .links(d3turn.links)
    .start();

  var gnodes = svg.selectAll('g.gnode')
    .data(d3turn.nodes)
   .enter()
    .append('g')
    .classed('gnode', true);
  
  var node = gnodes.append("circle")
		//FIXME.  previously assigned class with just d.type but sth is wrong upstream.
    .attr("class", function(d) {return "node-"+d.type.name })
    .attr("r", function(d) { return d.type.name == "city" ? 30 : 20 })
    .style("fill", function(d) {return color[d.player_id]; })
    .call(force.drag);

  node.append("title")
    .text(function(d) {
      return 'nodeid: ' + d.name + ', type: ' + d.type;
    });
      
  var labels = gnodes.append("text")
    .text(function(d) {
      return d.player_id == null ? '' : d.units.toString() 
    })
    .style("fill", "#555")
    .style("font-family", "Arial")
    .style("font-size", 12);

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
    gnodes.attr("transform", function(d) { 
      return 'translate(' + [d.x, d.y] + ')'; 
    })    

		
  });
	return {'force': force, 'node': node, 'labels': labels}
};
