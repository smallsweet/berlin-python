#!/usr/bin/env python

import berlin
import ai

import ipdb
import json


jh = open('tests_json/smallmap.json').read()
jh=open('viewer/random.js').read()[9:]
dat=json.loads(jh)
if 'action' not in dat:
	dat['action']='turn'
if 'infos' not in dat:
	dat['infos']={
			'game_id':'fart',
			'maximum_number_of_turns':50,
			'current_turn':0,
			'time_limit_per_turn':5000,
			'directed':False,
			'number_of_players':2,
			'player_id':0
			}
if 'types' not in dat['map']:
	dat['map']['types']=[
			{"points": 0, "soldiers_per_turn": 0, "name": "node"},
			{"points": 1, "soldiers_per_turn": 1, "name": "city"}
			]
game = berlin.parse_request(dat)

match = berlin.Match(game)
game.to_berlin()
ai0 = ai.another_bot
ai1 = berlin.move_at_random
ai1=ai.another_bot

fn='viewer/gamedump.js'
out=open(fn,'w')
out.write('var game=[')
written=False
import logging
while True:
	print '*'*50
	print "initial"
	if written:out.write(',')
	out.write(json.dumps(match.game.to_berlin()))
	written=True
	for nid,node in match.game.m.nodes.items():
		print node.id,(node.owner and 'B' or 'A')*node.units
	try:
		response0 = ai0(match.send_game(0))
		print response0
	except:
		logging.exception('ai failed to make a response')
		response0=[]
	try:
		response1 = ai1(match.send_game(1))
	except:
		logging.exception('ai failed to make a response')
		response1=[]
	print '\n',
	for ii,res in enumerate([response0,response1]):
		if res:
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
out.write(']')

