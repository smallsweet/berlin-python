#!/usr/bin/env python

import json
import logging
import random
import heapq
import time

class Node:
  def __init__(self, id, type, owner=None, units=0):
    self.id=id
    self.type=type
    self.owner=owner
    self.units=units
    self.edges=[] # outgoing edges (id)
  def __repr__(self):
    return 'Node: id:%s, type:%s, owner:%s, units:%s, edges:%s' % \
        (self.id, self.type, self.owner, self.units, self.edges)

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
        self.nodes[n['id']] = Node(n['id'], n['type'])
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

  def dijkstra(self, startnode, evalfunc):
    '''
    returns shortest path between startnode and the closest node for which
    evalfunc returns true. If there are multiple paths of equal length, it 
    will just return one of them.
    path will be an ordered list of nodes that must be visited (not including
    start), or None if no path exists
    '''
    path = []
    visited = set()
    fringe = []
    parent = {startnode.id: None}
    heapq.heappush(fringe, (0, startnode.id))
    while len(fringe) > 0:
      # find best candidate in fringe easy with heap
      (curdist, current) = fringe.pop()
      if evalfunc(self.nodes[current]) is True:
        while parent[current] is not None:
          path.append(current)
          current = parent[current]
        path.reverse()
        return path
      visited.add(current)
      for n in self.nodes[current].edges:
        if n in visited:
          continue
        found_in_fringe = False
        for i in range(len(fringe)):
          # search for the node in the fringe
          # since we know it's unique use a for loop so we can stop as
          # soon as we find it
          (elemdist, element) = fringe[i]
          if element == n:
            found_in_fringe = True
            if elemdist > curdist + 1:
              elemdist = curdist + 1
              fringe[i] = (elemdist, element)
              fringe.sort()
              parent[n] = current
              break
        if not found_in_fringe:
          heapq.heappush(fringe, (curdist + 1, n))
          parent[n] = current
    # if we get here, there's no path
    return None

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
    return move_at_random(self)

class Response:
  def __init__(self):
    self.moves = []

  def add_move(self, origin, destination, units):
    self.moves.append({
      'from': origin,
      'to': destination,
      'number_of_soldiers': units })

  def __repr__(self):
    return json.dumps(self.moves)

def parse_request(request):
  logging.debug('received request: ' + str(request))
  try:
    game = Game(request)
    logging.debug('parsed request: ' + str(game))
  except:
    logging.exception('failed to parse request')
    return None
  return game

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
  logging.basicConfig(format=FORMAT, level=logging.DEBUG)
  test()
 
def test():
  # this mocks server handling
  import json
  import urlparse
  request = {}
  for key, value in \
      urlparse.parse_qs(file('tests/test4.urlencoded','r').read()).items():
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
  l = g.m.dijkstra(n, lambda x: x.id == 22 )
  print l
  t0 = time.time()
  for i in range(10000):
    l = g.m.dijkstra(n, lambda x: x.id == 28 )
  print l
  print "dijkstra 10000 times: %s" % (time.time() - t0)
  for step in l:
    print "%d, %s" % (step, g.m.nodes[step].edges)

if __name__ == '__main__':
  main()


# vim: set sw=2 ts=2 sts=2 et:

