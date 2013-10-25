import random, json, math

nodes=[]
links=[]
MAX=30
PATHS=0
def r():
	return random.random()

for n in range(1,MAX):
	kind=r()<0.2 and 'city' or 'node'
	nodes.append({'name':str(n),'id':n,'type':kind})
	if 0 and random.random()>0.7 and n>2:
		links.append({'from':n,'to':n-1})
	if 0 and random.random()<0.8 and n<MAX-1:
		links.append({'from':n,'to':n+1})
	if 0 and random.random()<0.3 and n>3:
		links.append({'from':n,'to':n-2})
	for nn in range(1,n):
		if r()>0.8+30*(nn/n):
			links.append({'from':n,'to':nn})

for n in range(PATHS):
	a=random.choice(nodes)
	b=random.choice(nodes)
	if a==b:continue
	links.append({'from':a['id'],'to':b['id']})

res=json.dumps({'map':{'paths':links,'nodes':nodes},'state':[],})
outfn='random.js'
out=open(outfn,'w').write('var game=%s'%res)
