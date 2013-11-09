import random, json, math

nodes=[]
links=[]
MAX=12
PATHS=3
def r():
	return random.random()

states=[]
for n in range(1,MAX):
	kind=r()<0.3 and 'city' or 'node'
	nodes.append({'id':n,'type':kind})
	if n>2 and random.random()>0.7:
		links.append({'from':n,'to':n-1})
	if n>3 and random.random()<0.3:
		links.append({'from':n,'to':n-2})
	if n>1:
		links.append({'from':n,'to':n-1})
	if n>1:
		links.append({'from':n,'to':5})
	states.append({'player_id':None,'number_of_soldiers':0,'node_id':n})
aa=random.choice(states)
aa['player_id']=0
aa['number_of_soldiers']=5
nodes[aa['node_id']-1]['type'] = 'city'

aa=random.choice(states)
aa['player_id']=1
aa['number_of_soldiers']=5
nodes[aa['node_id']-1]['type'] = 'city'

for n in range(PATHS):
	a=random.choice(nodes)
	b=random.choice(nodes)
	if a==b:continue
	links.append({'from':a['id'],'to':b['id']})

res=json.dumps({'map':{'paths':links,'nodes':nodes},'states':states,})
outfn='viewer/random.js'
out=open(outfn,'w').write('var game=%s'%res)
