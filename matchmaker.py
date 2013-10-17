#!/usr/bin/env python

import berlin
import ai

import ipdb
import json


#ipdb.set_trace()
jh = open('tests_json/smallmap.json')
game = berlin.parse_request(json.loads(jh.read()))
print game
match = berlin.Match(game)

ai0 = ai.another_bot
ai1 = berlin.move_at_random
ai1=ai.another_bot
while True:
	print '*'*50
	print "initial"
	for nid,node in match.game.m.nodes.items():
		print node.id,(node.owner and 'B' or 'A')*node.units
	response0 = ai0(match.send_game(0))
	response1 = ai1(match.send_game(1))
	print '\n',
	for ii,res in enumerate([response0,response1]):
		for move in res.moves:
			if not move['number_of_soldiers']:continue
			print move['from'],'===>',((ii and 'B' or 'A')*move['number_of_soldiers']),'==>',move['to']
	print '\n',
	match.add_response(0,response0)
	match.add_response(1,response1)

	(score, units) = match.score()
	result = match.resolve_turn()
	print match.game.turn
	print "final"
	for nid,node in match.game.m.nodes.items():
		print node.id,(node.owner and 'B' or 'A')*node.units
	print "score:", score
	print "units:", units
	if result is False or score[0] == 0 or score[1]==0:
		break



