import random

for i in range(50):
	g.addNode()

for u in g.nodes:
	for v in g.nodes:
		if random.random() < 0.1:
			g.addEdge(u,v)

run_layout(ForceAtlas, iters=100)