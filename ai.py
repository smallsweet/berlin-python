#!/usr/bin/env python

import logging
import heapq
import random
import time

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
  t0 = time.time()
  res = berlin.Response()
  me = game.myself
  nodes = game.m.nodes.values()
  logging.info("turn %d started, %d turns left" % \
      (game.turn, game.maxturns - game.turn))
  logging.info("my id is %s" % me)
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
    logging.info("move around at random")
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
  logging.info("search_and_destroy done in %f" % (time.time() - t0))
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
  t0 = time.time()
  res = berlin.Response()
  me = game.myself
  nodes = game.m.nodes.values()
  logging.info("turn %d started, %d turns left" % \
      (game.turn, game.maxturns - game.turn))
  logging.info("my id is %s" % me)
  for n in nodes:
    logging.info(n)

  # helper functions
  def is_base(node):
    return node.units_per_turn > 0
  
  def is_my_node(node):
    return node.owner == me 
  
  def is_my_base(node):
    return node.owner == me and node.units_per_turn > 0
  
  def is_enemy_node(node):
    return node.owner is not None and node.owner != me 
  
  def is_enemy_base(node):
    return is_enemy_node(node) and node.units_per_turn > 0
  
  def prefer_empty_bases(node):
    '''
    causes dijkstra to prefer paths containing empty bases
    '''
    if is_base(node) and node.units is 0:
      return 9
    return 10
  
  #empty_nodes = filter(lambda x: x.owner is None, nodes)
  enemy_nodes = filter(lambda x: is_enemy_node(x), nodes)
  #empty_bases = filter(lambda x: is_base(x), empty_nodes)
  #enemy_bases = filter(lambda x: is_base(x), enemy_nodes)

  # if there are no enemy units left following calculations fail
  if len(filter(lambda x: x.units > 0, enemy_nodes)) == 0:
    logging.info("move around at random")
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
  for base in filter(lambda x: is_base(x), nodes):
    #logging.info("base: ", base)
    (mydistance, mynodes) = game.m.find(base, lambda x: is_my_node(x) and
        x.units > 0)
    logging.debug("base %d: found my guys, distance: %s, nodes: %s" \
        % (base.id, mydistance, mynodes))
    (hisdistance, hisnodes) = game.m.find(base, lambda x: is_enemy_node(x) and
        x.units > 0)
    logging.debug("base %d: found his guys, distance: %s, nodes %s"\
        % (base.id, hisdistance, hisnodes))
    players = {}
    hismaxunits=0
    for n in game.m.radius(base, mydistance):
      if is_enemy_node(n):
        p = n.owner
        if p not in players:
          players[p] = 0
        players[p] += n.units
    if players:
      hismaxunits = max(players.values())
    mymaxunits=0
    for n in game.m.radius(base, hisdistance):
      # bool counts as int in python
      mymaxunits += is_my_node(n) * n.units
    myunits = 0
    for n in mynodes:
      myunits += n.units
    hisunits = 0
    players = {}
    for n in hisnodes:
      if is_enemy_node(n):
        p = n.owner
        if p not in players:
          players[p] = 0
        players[p] += n.units
    if players:
      hisunits = max(players.values())
    objectives.append((base.id, hisdistance - mydistance,
      mydistance, hisdistance, myunits, hisunits,
      mymaxunits, hismaxunits, mynodes, base))
  
  targets = []
  logging.info("prioritizing targets")
  logging.debug(("base_id", "distdelta", "mydist", "hisdist",
    "myunits", "hisunits", "mymaxunits", "hismaxunits", "mynodes", "objective"))
  for o in objectives:
    (base_id, distdelta, mydist, hisdist, myunits, hisunits,
        mymaxunits, hismaxunits, mynodes, base) = o
    logging.debug((base_id, distdelta, mydist, hisdist, myunits, hisunits, \
        mymaxunits, hismaxunits, map(lambda x: x.id, mynodes), base))
    if base.owner is None:
      # empty bases
      if distdelta == 0:
        #t = Target(mydist, base_id, mynodes)
        # FIXME: increase priority ?
        t = Target(-1, base_id, mynodes, 1, hisunits + 1)
        logging.debug(t)
        heapq.heappush(targets,(t.prio,t))
      elif distdelta > 0:
        # only send one guy if we can get there first
        t = Target(distdelta -1, base_id, mynodes, None, 1)
        logging.debug(t)
        heapq.heappush(targets,(t.prio,t))
      continue
    elif is_my_node(base):
      # defend our bases unless he can take them whatever we do
      if hisdist == 1 and hisunits <= mymaxunits:
        logging.debug("defend base at %s, hisdist: %s" %(base_id, hisdist))
        needed = hisunits
        t = Target(0 , base_id, None, needed, needed)
        logging.debug(t)
        heapq.heappush(targets,(t.prio, t))
        continue
    elif is_enemy_node(base):
      if myunits > hismaxunits:
        # if local advantage
        adjnodes = game.m.radius(base, 1)
        mybases = filter(lambda n: is_my_node(n), adjnodes)
        hisbases = filter(lambda n: n.owner == base.owner, adjnodes)
        if len(mybases) > len(hisbases) or\
            len(mybases) == len(hisbases) and\
            len(mybases) > 0 and myunits/len(mybases) > hismaxunits:
          # find best base to exchange
          reinforcements = []
          for mybase in mybases:
              fbases = filter(lambda x: is_my_node(x), game.m.radius(mybase, 1))
              units = sum(map(lambda x: x.units, fbases))
              reinforcements.append((len(fbases), units, mybase))
          reinforcements.sort()
          logging.debug(reinforcements)
          selected = None
          while len(reinforcements) > 0: 
            selected = reinforcements.pop()[2]
            if selected.units >= base.units + 1:
              break
          if selected is not None:
            logging.debug("exchange base at %s for my base at %s" % \
                (base_id, selected))
            units_to_send = min(selected.units, base.units + 1)
            t = Target(-1, base_id, [selected], units_to_send, units_to_send)
            heapq.heappush(targets, (t.prio, t))
            continue
      # conquer
      prio = mydist +1
      t = Target(prio, base_id, None, hisunits +1, hismaxunits +1)
      logging.debug(t)
      heapq.heappush(targets, (t.prio, t))
  
  targets.sort()
  logging.debug("targets %s" % targets)
  orders = {}
  # create orders
  logging.info("creating orders")
  while free_units > 0 and len(targets) > 0:
    (prio, t) = heapq.heappop(targets)
    logging.debug("free_units %s" % free_units)
    logging.info("target: %s" % t)
    dest = t.dest
    units_min = t.units_min
    if units_min is None:
      units_min = 1
    units = 0
    sources = filter(lambda x: x.id in free_nodes, t.orig)
    if not sources:
      (dist, sources) = game.m.find(game.m.nodes[dest],
          lambda x: x.id in free_nodes)
    logging.debug("available sources: %s" % sources)
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
    path = [orig]
    if orig != dest:
      path = game.m.dijkstra(game.m.nodes[orig],
          lambda x: x.id == dest, prefer_empty_bases)
      logging.debug(path)
      if not path:
        logging.error("ERROR no path found from %d to %d" % (orig, dest))
        continue
    dest = path[0]
    if orig not in orders:
      orders[orig] = {}
    if dest not in orders[orig]:
      orders[orig][dest] = 0
    logging.info("sending %d guys from %d to %d" % (units, orig, dest))
    orders[orig][dest] += units
    # reenqueue
    if t.units_min is not None:
      if units < t.units_min:
        # do not decrease priority for min orders
        #t.prio += 1
        t.units_min -= units 
        if t.units_max is not None:
          t.units_max -= units 
        logging.info("requested %d more units, order not fulfilled, reenqued"\
            % (t.units_min))
        logging.debug(t)
        heapq.heappush(targets,(t.prio,t))
        continue
      # remove min property
      t.units_min = None
      logging.info("min order fulfilled, removing min property")
      logging.info(t)
    if t.units_max is not None:
      if units >= t.units_max:
        logging.info("order fulfilled")
        continue
      t.units_max -= units
    t.prio += 1
    logging.debug(t)
    heapq.heappush(targets,(t.prio,t))
    logging.info("open order, reenqued with lower priority")
    logging.info("targets remaining:")
    logging.debug(targets)

  logging.info("unfulfilled targets: %s" % len(targets))
  logging.info("free_units: %s" % free_units)
  logging.debug("free_nodes: %s" % free_nodes)
  # if we still have free stuff, move it towards closest enemy (base if any)
  for (orig,units) in free_nodes.items():
    path = game.m.dijkstra(game.m.nodes[orig],
        lambda x: is_enemy_node(x) and is_base(x), prefer_empty_bases)
    if not path:
      path = game.m.dijkstra(game.m.nodes[orig],
          lambda x: is_enemy_node(x), prefer_empty_bases)
    if path:
      dest = path[0]
      logging.info("sending %d free guys from %d to %d" % (units, orig, dest) )
      if orig not in orders:
        orders[orig] = {}
      if dest not in orders[orig]:
        orders[orig][dest] = 0
      orders[orig][dest] += units

  logging.debug("orders:")
  # dispatch orders
  for orig in orders:
    for dest in orders[orig]:
      if dest == orig:
        logging.debug("defending %d with %d units" % (orig, orders[orig][dest]))
        continue
      logging.debug("%d -> %d %d units" % (orig, dest, orders[orig][dest]))
      res.add_move(orig, dest, orders[orig][dest])
  logging.debug("response:")
  logging.debug(res)
  logging.info("turn %d end" % game.turn)
  logging.info("bot done in %f" % (time.time() - t0))
  return res

# vim: set sw=2 ts=2 sts=2 et:

