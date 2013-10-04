#!/usr/bin/env python

import logging
import random

import berlin

def move_at_random(game):
  '''
  stupid random AI
  '''
  res = berlin.Response()
  for n in game.m.nodes.values():
    if n.owner == game.myself and n.units > 0:
      moves = {}
      neighbours = []
      for i in n.edges:
        neighbours.append(i)
        moves[i] = 0
      for i in range(n.units):
        dest_index = random.randint(0,len(neighbours))
        if dest_index == len(neighbours):
          # stand your ground
          continue
        moves[neighbours[dest_index]] += 1
      for dest, units in moves.items():
        logging.debug("moving %d units from %d to %d" % (units, n.id, dest))
        res.add_move(n.id, dest, units)
  return res

def search_and_destroy(game):
  '''
  go for bases
  '''
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
  
  def prefer_empty_bases(node):
    '''
    causes dijkstra to prefer paths containing empty bases
    '''
    if is_base(node) and node.units is 0:
      return 9
    return 10
  
  empty_nodes = filter(lambda x: x.owner is None, nodes)
  enemy_nodes = filter(lambda x: is_enemy_node(x), nodes)
  empty_bases = filter(lambda x: is_base(x), empty_nodes)
  enemy_bases = filter(lambda x: is_base(x), enemy_nodes)
  if not enemy_bases and not empty_bases:
    return move_at_random(game)

  for n in filter(lambda x: is_my_node(x) and x.units > 0, nodes):
    logging.info("considering node %s" % n)
    queue = []
    path_to_empty = game.m.dijkstra(n, \
        lambda x: x.owner is None and is_base(x),
        prefer_empty_bases)
    logging.info("path to empty: %s" % path_to_empty)
    path_to_enemy = game.m.dijkstra(n, \
        lambda x: is_base(x) and is_enemy_node(x),
        prefer_empty_bases)
    logging.info("path to enemy: %s" % path_to_enemy)
    if path_to_empty:
      queue.append((len(path_to_empty), path_to_empty[0]))
    if path_to_enemy:
      queue.append((len(path_to_enemy), path_to_enemy[0]))
    logging.info("decision queue: %s" % queue)
    queue.sort()
    (distance, destination) = queue[0]
    defenders = 0
    if is_base(n):
      if n.units>6:
        defenders = 2
      elif n.units>2:
        defenders = 1
    res.add_move(n.id, destination, n.units - defenders) 
  logging.info(res)
  return res

def another_bot(game):
  '''
  work in progress
  '''
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
  
  def prefer_empty_bases(node):
    '''
    causes dijkstra to prefer paths containing empty bases
    '''
    if is_base(node) and node.units is 0:
      return 9
    return 10
  
  empty_nodes = filter(lambda x: x.owner is None, nodes)
  enemy_nodes = filter(lambda x: is_enemy_node(x), nodes)
  empty_bases = filter(lambda x: is_base(x), empty_nodes)
  enemy_bases = filter(lambda x: is_base(x), enemy_nodes)
  
  bases = []
  for base in filter(lambda n: is_base(n), nodes):
    (mydistance, mynodes) = game.m.find(base, lambda x: is_my_node(x) and
        x.units > 0)
    (hisdistance, hisnodes) = game.m.find(base, lambda x: is_enemy_node(x) and
        x.units > 0)
    myunits = 0
    hisunits = 0
    if mynodes:
      myunits = reduce(lambda x, y: x.units + y.units, mynodes)
    if hisnodes:
      hisunits = reduce(lambda x, y: x.units + y.units, hisnodes)
    bases.append(mydistance, myunits, hisdistance, hisunits, base.id)
  print bases

# vim: set sw=2 ts=2 sts=2 et:

