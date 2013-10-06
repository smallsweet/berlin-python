#!/usr/bin/env python

import logging
import heapq
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
    print "move around at random"
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

class Target:
  def __init__(self, prio, dest, orig=None, units_min=None, units_max=None):
    if orig is None:
      orig = []
    if units_min is None:
      units_min = 1
    self.prio = prio
    self.dest = dest
    self.orig = orig
    self.units_min = units_min
    self.units_max = units_max
  def __repr__(self):
    return "prio: %s, dest: %s, orig: %s, min: %s, max: %s" \
        % (self.prio, self.dest, self.orig, self.units_min, self.units_max)

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
  enemy_units_nodes = filter(lambda x: x.units > 0, enemy_nodes)
  if not enemy_units_nodes:
    print "move around at random"
    return move_at_random(game)
  
  # muster available forces
  free_units = 0
  free_nodes = {}
  for node in nodes:
    if is_my_node(node) and node.units > 0:
      free_units += node.units
      free_nodes[node.id] = node.units

  # create objectives
  objectives = []
  targets = [] # targets
  for base in filter(lambda x: is_base(x), nodes):
    #print "base: ", base
    (mydistance, mynodes) = game.m.find(base, lambda x: is_my_node(x) and
        x.units > 0)
    print "found my guys", mydistance, mynodes
    (hisdistance, hisnodes) = game.m.find(base, lambda x: is_enemy_node(x) and
        x.units > 0)
    print "found his guys", hisdistance, hisnodes
    hismaxunits=0
    for n in game.m.radius(base, mydistance):
      # bool counts as int in python
      hismaxunits += is_enemy_node(n) * n.units
    mymaxunits=0
    for n in game.m.radius(base, hisdistance):
      # bool counts as int in python
      mymaxunits += is_my_node(n) * n.units
    myunits = 0
    hisunits = 0
    for n in mynodes:
      myunits += n.units
    for n in hisnodes:
      hisunits += n.units
    objectives.append((base.id, hisdistance - mydistance,
      mydistance, hisdistance, myunits, hisunits,
      mymaxunits, hismaxunits, mynodes))
  
  def sort_by_eta_distance(a, b):
    '''
    sort by eta and then by distance
    '''
    if a[2] == b[2]:
      return abs(a[1]) < abs(b[1])
    return a[2] < b[2]

  # prioritize objectives
  objectives.sort(cmp=sort_by_eta_distance)
  print objectives

  for o in objectives:
    (base_id, distdelta, mydist, hisdist, myunits, hisunits,
        mymaxunits, hismaxunits, mynodes) = o
    print base_id, distdelta, mydist, hisdist, myunits, hisunits, \
        mymaxunits, hismaxunits, map(lambda x: x.id, mynodes)
    if game.m.nodes[base_id].owner is None:
      # empty bases
      if distdelta > 0:
        # only send one guy if we can get there first
        t = Target(abs(distdelta), base_id, mynodes, None, 1)
        print t
        heapq.heappush(targets,(t.prio,t))
      elif distdelta == 0:
        t = Target(abs(distdelta), base_id, mynodes)
        print t
        heapq.heappush(targets,(t.prio,t))
      continue
    elif is_my_node(game.m.nodes[base_id]):
      # defend my bases if he can take the base if we do nothing
      needed = hisunits + 1
      t = Target((hisdist - 1) * 2, base_id, None, needed, needed)
      print "defend base at", base_id, "hisdist:", hisdist
      print t
      heapq.heappush(targets,(t.prio, t))
      continue
    elif is_enemy_node(game.m.nodes[base_id]):
      # conquer
      t = Target(mydist + abs(hisunits - myunits), base_id)
      print t
      heapq.heappush(targets, (t.prio, t))
  
  targets.sort()
  print "targets", targets
  orders = {}
  # create orders
  print "creating orders"
  while free_units > 0 and len(targets) > 0:
    (prio, t) = heapq.heappop(targets)
    print "free_units", free_units
    print t
    dest = t.dest
    units_min = t.units_min
    units = 0
    sources = t.orig
    if not sources:
      (dist, sources) = game.m.find(game.m.nodes[dest], lambda x: x.id in free_nodes)
    # filter again because might have been predeclared
    print sources
    sources = filter(lambda x: x.id in free_nodes, sources)
    if not sources:
      # noone left to send, pity
      continue
    orig = sources[0].id
    while units < units_min:
      units += 1
      free_units -= 1
      free_nodes[orig] -= 1
      if free_nodes[orig] <= 0:
        del free_nodes[orig]
        break
    path = [dest]
    if orig != dest:
      path = game.m.dijkstra(game.m.nodes[orig], lambda x: x.id == dest, prefer_empty_bases)
      print path
      if not path:
        print "ERROR no path found from %d to %d" % (orig, dest)
        continue
    dest = path[0]
    if orig not in orders:
      orders[orig] = {}
    if dest not in orders[orig]:
      orders[orig][dest] = 0
    print "sending %d guys from %d to %d" % (units, orig, dest)
    orders[orig][dest] += units
    if t.units_min is not None:
      if units < t.units_min:
        t.prio += 1
        t.units_min -= units 
        print "requested %d units, order not fulfilled, reenque" % (t.units_min)
        print t
        heapq.heappush(targets,(t.prio,t))
        print targets
        continue
    if t.units_max is not None:
      if units >= t.units_max:
        print "order fulfilled"
        continue
      t.units_max -= units
    t.prio += 1
    print "sent 1 guy from %d to %d, open order, reenque" % (orig, dest)
    print t
    heapq.heappush(targets,(t.prio,t))
    print targets

  print orders
  # dispatch orders
  for orig in orders:
    for dest in orders[orig]:
      if dest == orig:
        continue
      res.add_move(orig, dest, orders[orig][dest])
  return res

# vim: set sw=2 ts=2 sts=2 et:

