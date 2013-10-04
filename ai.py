#!/usr/bin/env python

import berlin
import logging


def search_and_destroy(game):
	res = berlin.Response()
	me = game.myself
	nodes = game.m.nodes.values()
	logging.info("I am %s" % me)
	for n in nodes:
		logging.info(n)

	# helper functions
	def is_base(node):
		return node.units_per_turn > 0
	
	def is_my_node(node):
		return node.owner is me 
	
	def is_enemy_node(node):
		return node.owner is not None and node.owner is not me 
	
	empty_nodes = filter(lambda x: x.owner is None, nodes)
	enemy_nodes = filter(lambda x: is_enemy_node(x), nodes)
	empty_bases = filter(lambda x: is_base(x), empty_nodes)
	enemy_bases = filter(lambda x: is_base(x), enemy_nodes)
	if not enemy_bases and not empty_bases:
			return berlin.move_at_random(game)

	for n in filter(lambda x: is_my_node(x) and x.units > 0, nodes):
		logging.info("considering node %s" % n)
		queue = []
		path_to_empty = game.m.dijkstra(n, \
				lambda x: x.owner is None and is_base(x))
		logging.info("path to empty: %s" % path_to_empty)
		path_to_enemy = game.m.dijkstra(n, \
				lambda x: is_base(x) and is_enemy_node(x))
		logging.info("path to enemy: %s" % path_to_enemy)
		if path_to_empty:
			queue.append((len(path_to_empty), path_to_empty[0]))
		if path_to_enemy:
			queue.append((len(path_to_enemy), path_to_enemy[0]))
		logging.info("decision queue: %s" % queue)
		queue.sort()
		move = queue[0]
		defenders = 0
		if is_base(n):
			if n.units>6:
				defenders = 2
			elif n.units>2:
				defenders = 1
		res.add_move(n.id, move[1], n.units - defenders) 
	logging.info(res)
	return res

