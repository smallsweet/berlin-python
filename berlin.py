#!/usr/bin/env python

import json
import logging
import random
import heapq
import time

import ai

version = "0.1"

class Node:
  def __init__(self, id, points, units_per_turn, owner=None, units=0):
    self.id=id
    self.points=points
    self.units_per_turn=units_per_turn
    self.owner=owner
    self.units=units
    self.edges=[] # outgoing edges (id)
  def __repr__(self):
    return 'Node: id:%s, points:%s, units_per_turn:%s owner:%s, units:%s, edges:%s' % \
        (self.id, self.points, self.units_per_turn,
            self.owner, self.units, self.edges)

class Map:
  def __init__(self, mapdict, directed = False):
    try:
      self.directed = directed
      self.types = {}
      for t in mapdict['types']:
        self.types[t['name']] = {}
        self.types[t['name']]['points'] = t['points']
        self.types[t['name']]['units_per_turn'] = t['soldiers_per_turn']

      self.nodes = {} # should probably be a list, but largest map has
                      # less than 30 nodes, so whatever
      for n in mapdict['nodes']:
        self.nodes[n['id']] = Node(n['id'],
            self.types[n['type']]['points'],
            self.types[n['type']]['units_per_turn'])

      for p in mapdict['paths']:
        self.nodes[p['from']].edges.append(p['to'])
        if not self.directed:
          self.nodes[p['to']].edges.append(p['from'])
    except:
      logging.exception('failed to parse map')
      raise

  def __repr__(self):
    return 'Map: directed:%s, types:%s, nodes:%s' % \
        (self.directed, self.types, self.nodes)

  def update(self,statelist):
    for s in statelist:
      self.nodes[s['node_id']].owner = s['player_id']
      self.nodes[s['node_id']].units = s['number_of_soldiers']

  def floodFill(self, startnode, evalfunc):
    '''
    Starts from given node and grows through nodes for which evalfunc(node)
    evaluates as true.
    Returns a list of connected nodes (ids) that match the condition.
    '''
    result = []
    if evalfunc(startnode) is False:
      return result
    result.append(startnode.id)
    visited = set([startnode.id])
    fringe = set(startnode.edges)
    while len(fringe) > 0:
      curr = fringe.pop()
      if curr in visited:
        continue
      visited.add(curr)
      if evalfunc(self.nodes[curr]) is False:
        continue
      result.append(curr)
      for neighbour in self.nodes[curr].edges:
        if neighbour in visited:
          continue
        fringe.add(neighbour)
    return result

  def dijkstra(self, startnode, evalfunc, costfunc=None):
    '''
    returns shortest path between startnode and the closest node for which
    evalfunc returns true. If there are multiple paths of equal length, it 
    will just return one of them.
    path will be an ordered list of nodes that must be visited (not including
    startnode), or None if no path exists
    optional costfunc should return the cost for visiting a given node, it can
    be useful to cause the pathfinding to prefer/avoid certain routes.
    '''
    if costfunc is None:
      # default cost is 1
      costfunc = lambda x: 1
    path = []
    visited = set()
    fringe = []
    parent = {startnode.id: None}
    heapq.heappush(fringe, (0, startnode.id))
    while len(fringe) > 0:
      # find best candidate in fringe
      #print "fringe: ", fringe
      (curdist, current) = heapq.heappop(fringe)
      #print "popped ", current
      if evalfunc(self.nodes[current]) is True:
        #print "found target"
        while parent[current] is not None:
          path.append(current)
          current = parent[current]
        path.reverse()
        return path
      visited.add(current)
      for n in self.nodes[current].edges:
        #print "neighbour: ", n
        if n in visited:
          #print "already been there"
          continue
        # make the pathfinder favour paths that contain empty bases
        cost = costfunc(self.nodes[n])
        found_in_fringe = False
        # search for the node in the fringe
        # since we know it's unique use a for loop so we can stop as soon
        # as we find it
        #print "looking in fringe"
        for i in range(len(fringe)):
          (elemdist, element) = fringe[i]
          if element == n:
            found_in_fringe = True
            #print "found in fringe"
            if elemdist > curdist + cost:
              elemdist = curdist + cost
              fringe[i] = (elemdist, element)
              fringe.sort()
              parent[n] = current
              break
        if not found_in_fringe:
          #print "adding to fringe", n
          heapq.heappush(fringe, (curdist + cost, n))
          parent[n] = current
    # if we get here, there's no path
    return None

  def find(self, startnode, evalfunc):
    '''
    A breadth first search that will find the closest node that satisfies
    the condition. Will find multiple nodes if they are at the same
    distance.
    Returns a tuple containing the distance and the list of nodes.
    If no matching node is found will return (None, [])
    '''
    maxdist = None
    visited = set()
    found = []
    fringe = []
    heapq.heappush(fringe, (0, startnode.id))
    while len(fringe) > 0:
      (curdist, current) = heapq.heappop(fringe)
      visited.add(current)
      #if curdist > 0 and evalfunc(self.nodes[current]):
      if evalfunc(self.nodes[current]):
        # found node
        if maxdist is None:
          maxdist = curdist
        if curdist > maxdist:
          continue
        # FIXME ? return ids or nodes ?
        # found.append(current)
        found.append(self.nodes[current])
      if maxdist is not None and (curdist + 1) > maxdist:
        # gone too far, skip it
        continue
      for n in self.nodes[current].edges:
        if n in visited:
          continue
        found_in_fringe = False
        for (elemdist, element) in fringe:
          if element == n:
            found_in_fringe = True
            break
        if not found_in_fringe:
          heapq.heappush(fringe, (curdist + 1, n))
    return (maxdist, found)
  
  def radius(self, startnode, maxdist, dofunc=None):
    '''
    Grow from startnode until maxdistance.
    Returns list of visited nodes.
    Optionally apply dofunc to each node encountered
    '''
    visited = set()
    fringe = []
    heapq.heappush(fringe, (0, startnode.id))
    while len(fringe) > 0:
      (curdist, current) = heapq.heappop(fringe)
      visited.add(current)
      #if curdist > 0 and evalfunc(self.nodes[current]):
      if dofunc is not None:
        dofunc(self.nodes[current])
      if (curdist + 1) > maxdist:
        # gone too far, do not enter edges
        continue
      for n in self.nodes[current].edges:
        if n in visited:
          continue
        found_in_fringe = False
        for (elemdist, element) in fringe:
          if element == n:
            found_in_fringe = True
            break
        if not found_in_fringe:
          heapq.heappush(fringe, (curdist + 1, n))
    v = []
    for n in visited:
      v.append(self.nodes[n])
    return v

class Game:
  def __init__(self, parsed_request):
    try:
      self.action = parsed_request['action']
      self.game_id = parsed_request['infos']['game_id']
      # assuming this is inclusive
      self.maxturns = parsed_request['infos']['maximum_number_of_turns']
      self.turn = parsed_request['infos']['current_turn']
      self.players = parsed_request['infos']['number_of_players']
      self.myself = parsed_request['infos']['player_id']
      self.timeout = parsed_request['infos']['time_limit_per_turn']
      self.directed = parsed_request['infos']['directed']
      self.m = Map(parsed_request['map'], self.directed)
      self.m.update(parsed_request['state'])
    except:
      logging.exception('failed to parse game')
      raise
  
  def __repr__(self):
    return 'Game: %s, %s, %s, %s, %s, %s, %s, %s' \
        % (self.action, self.game_id, self.maxturns, self.turn, self.players,
            self.myself, self.timeout, self.m)

  def generate_turn(self):
    '''
    do something here
    '''
    return ai.move_at_random(self)

class Response:
  def __init__(self):
    self.moves = []

  def add_move(self, origin, destination, units):
    self.moves.append({
      'from': origin,
      'to': destination,
      'number_of_soldiers': units })

  def __repr__(self):
    return 'Response: %s' % json.dumps(self.moves)

def parse_request(request):
  logging.debug('received request: ' + str(request))
  try:
    game = Game(request)
    logging.debug('parsed request: ' + str(game))
  except:
    logging.exception('failed to parse request')
    return None
  return game

class Match:
  def __init__(self, game):
    self.game = game
    self.players = game.players
    self.responses = [None] * self.players
    self.nodes = {}
    self.sync()

  def sync(self):
    self.nodes = {}
    for n in self.game.m.nodes.values():
      self.nodes[n.id] = [0] * self.players
      if n.owner is None:
        continue
      self.nodes[n.id][n.owner] = n.units
    
  def add_response(self, player_id, response):
    self.responses[player_id] = response

  def resolve_movement(self):
    self.sync() # necessary ?
    for player_id in range(self.players):
      resp = self.responses[player_id]
      if resp is None:
        logging.info("skipping missing move for player: %s" % player_id)
        continue
      for move in resp.moves:
        orig = self.game.m.nodes[move['from']]
        dest = self.game.m.nodes[move['to']]
        units = move['number_of_soldiers']
        if orig.owner is not player_id or orig.units < units:
          logging.info("ignoring invalid move from player: %s" % player_id)
          continue
        self.game.m.nodes[orig.id].units -= units
        self.nodes[orig.id][player_id] -= units
        self.nodes[dest.id][player_id] += units

  def resolve_combat(self):
    for (nodeid, nodeunits) in self.nodes.items():
      topplayer = (None, 0)
      secondplayer = (None, 0)
      for i in range(len(nodeunits)):
        units = nodeunits[i]
        if units > topplayer[1]:
          secondplayer = topplayer
          topplayer = (i, units)
          continue # next player
        if units > secondplayer[1]:
          secondplayer = (i,units)
      units_left = topplayer[1] - secondplayer[1]
      if units_left == 0:
        continue # next node
      node = self.game.m.nodes[nodeid]
      node.units = units_left
      if topplayer[0] != node.owner:
        node.owner = topplayer[0]

  def resolve_spawn(self):
    for node in self.game.m.nodes.values():
      if node.owner is None:
        continue
      node.units += node.units_per_turn
      node.units = max(node.units,0) # units cannot be negative

  def show(self):
    for nid,node in self.game.m.nodes.items():
  		print node.id,(node.owner and 'B' or 'A')*node.units


  def resolve_turn(self):
    self.resolve_movement()
    self.resolve_combat()
    self.resolve_spawn()
    self.game.turn += 1
    if self.game.turn < self.game.maxturns:
      return True
    self.game.turn = self.game.maxturns
    self.game.action = 'game_over'
    return False

  def score(self):
    scores = [0] * self.players
    units = [0] * self.players
    for node in self.game.m.nodes.values():
      if node.owner is not None:
        scores[node.owner] += node.points
        units[node.owner] += node.units
    # FIXME this is horrrrrible
    return (scores,units)

  def send_game(self,playerid):
    self.game.myself = playerid
    return self.game

def move_at_random(game):
  '''
  stupid random AI
  '''
  res = Response()
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

def main():
  FORMAT = '%(asctime)s %(levelname)s %(message)s'
  logging.basicConfig(format=FORMAT, level=logging.INFO)
  test()
 
def test():
  # this mocks server handling
  import json
  import urlparse
  request = {}
  for key, value in urlparse.parse_qs(\
      file('tests/test4.urlencoded','r').read()).items():
        # this a silly hack
        if key == 'action':
          request['action'] = value[0]
          continue
        request[key] = json.loads(value[0])
  g = parse_request(request)
  print g.generate_turn()
  n = g.m.nodes[5]
  l = g.m.floodFill(n, lambda x: x.owner is None )
  print sorted(l)
  l = g.m.dijkstra(n, lambda x: x.id == 17 )
  print l
  l = g.m.dijkstra(g.m.nodes[28], lambda x: x.id == 5)
  print l

  t0 = time.time()
  for i in range(10000):
    l = g.m.dijkstra(n, lambda x: x.id == 28 )
  print "should find a path 5 nodes long", l
  print "dijkstra 10000 times: %s" % (time.time() - t0)
  for step in l:
    print "%d, %s" % (step, g.m.nodes[step].edges)

  # same, but avoid node 25
  def avoid_node_25(node):
    if node.id is 25:
      return 11
    return 10
  l = g.m.dijkstra(n, lambda x: x.id == 28, avoid_node_25)
  print "should avoid 25", l

  def is_base(node):
    return node.units_per_turn > 0

  print "search"
  s = g.m.find(n, is_base)
  print "should find 4 and 6 at distance 2", s

  s = g.m.find(g.m.nodes[1], lambda x: x.owner == 1)
  print "should find 4 at distance 5", s

if __name__ == '__main__':
  main()

# vim: set sw=2 ts=2 sts=2 et:

