#CSCI 3202 Assignment 3
#Implementing A* Search
#Implementing Dijkstra's Algorithm
#Comparing the two
#
#Name: Matt Oakley
#Date: 9/12/16

# IMPORTS #
import time

class A_Node:
	def __init__(self):
		self.name = ""
		self.heuristic = 0
		self.distance = {}
		self.distance_so_far = 0
		self.f_of_n = 0
		self.parent = None
		self.neighbors = []

class D_Node:
	def __init__(self):
		self.name = ""
		self.distance = {}
		self.distance_so_far = 0
		self.f_of_n = 0
		self.parent = None
		self.neighbors = []

class Graph:
	def __init__(self):
		self.verticies = {}
			
	def addVertex(self, value):
		if value in self.verticies:
			print "Vertex already exists"
		else:
			self.verticies[value] = []

	def addEdge(self, val1, val2, distance):
		if val1 not in self.verticies and val2 not in self.veriticies:
			print "One or more vertices not found."
		else:
			self.verticies[val1].append(val2 + ", " + distance)
			self.verticies[val2].append(val1 + ", " + distance)

	def findVertex(self, val):
		if val in self.verticies:
			print self.verticies[val][0]
		else:
			print "Vertex not found."

def read_file():
	#Create lists containing the edges and heuristics provided in the text file
	edges = []
	heuristics = []

	file = open("Assignment_3.txt", "r").read()
	contents = file.splitlines()
	for item in contents:
		if item == "":
			continue
		if item[0] == "[":
			edges.append(item)
		elif item[1] == "=":
			heuristics.append(item)

	return edges, heuristics

def create_graph(edges, heuristics):
	#Create a new Graph objects
	graph = Graph()

	#Add all of the available verticies to the graph
	for item in heuristics:
		graph.addVertex(item[0])

	#Add all of the available edges to the graph
	for item in edges:
		v1 = item[1]
		v2 = item[3]
		last_comma_index = 5
		str_length = len(item) - 1
		distance = item[last_comma_index:str_length]
		graph.addEdge(v1, v2, distance)

	return graph

def create_nodes(graph, edges, heuristics):
	#Instantiate the list of nodes that we'll return
	A_nodes = []
	D_nodes = []

	#Iterate through verticies and set node's name
	for key in graph.verticies:
		A_node = A_Node()
		D_node = D_Node()
		A_node.name = key
		D_node.name = key

		#Set node's heuristic value
		for line in heuristics:
			if line[0] == key:
				A_node.heuristic = int(line[2:])

		#Set node's neighbors
		A_neighbors = []
		D_neighbors = []
		for line in edges:
			if line[1] == key:
				A_neighbors.append(line[3])
				D_neighbors.append(line[3])
			A_node.neighbors = A_neighbors
			D_node.neighbors = D_neighbors
		
		#Add nodes to the list
		A_nodes.append(A_node)
		D_nodes.append(D_node)

	#Convert neighbors to be nodes themselves
	for node in A_nodes:
		for neighbor in node.neighbors:
			for neighbor_node in A_nodes:
				if neighbor_node.name == neighbor:
					node.neighbors.append(neighbor_node)
	for node in D_nodes:
		for neighbor in node.neighbors:
			for neighbor_node in D_nodes:
				if neighbor_node.name == neighbor:
					node.neighbors.append(neighbor_node)


	#Get rid of neighbors that aren't of type Node()
	for node in A_nodes:
		half = len(node.neighbors)/2
		node.neighbors = node.neighbors[half:]
	for node in D_nodes:
		half = len(node.neighbors)/2
		node.neighbors = node.neighbors[half:]

	#Set node's distance from parent node
	for node in A_nodes:
		for neighbor in node.neighbors:
			for line in edges:
				if line[3] == neighbor.name and line[1] == node.name:
					last_comma_index = 5
					str_length = len(line) - 1
					node.distance[neighbor.name] = line[last_comma_index:str_length]
	for node in D_nodes:
		for neighbor in node.neighbors:
			for line in edges:
				if line[3] == neighbor.name and line[1] == node.name:
					last_comma_index = 5
					str_length = len(line) - 1
					node.distance[neighbor.name] = line[last_comma_index:str_length]
	
	return A_nodes, D_nodes

def a_star_search(graph, nodes, start, end):
	print ":::A* SEARCH:::"

	open_verticies = []
	closed_verticies = []
	open_verticies.append(start)
	time_start = time.time()
	nodes_visited = 0

	while len(open_verticies) != 0:

		#Find smallest heuristic value in open nodes
		equals = []
		MAX_INT = 999999
		MAX_CHAR = 999999
		for node in open_verticies:
			if node.f_of_n < MAX_INT:
				smallest_node = node
				MAX_INT = node.f_of_n

		#If there are ties for smallest f(n), choose lowest alphabetical option
		for node in open_verticies:
			if node.f_of_n == smallest_node.f_of_n:
				equals.append(node)
		if len(equals) > 1:
			for node in equals:
				if ord(node.name) < MAX_CHAR:
					smallest_node = node
					MAX_CHAR = ord(node.name)

		#Remove the smallest node from the open list
		open_verticies.remove(smallest_node)

		#As long as we're not at the end...
		if smallest_node != end:

			#Add the smallest node to the closed list
			closed_verticies.append(smallest_node)

			#Visit each of the smallest node's neighbors
			for neighbor in smallest_node.neighbors:

				#Calculate f(n) value
				f_of_n = neighbor.heuristic + int(smallest_node.distance[neighbor.name]) + smallest_node.distance_so_far

				#If a neighbor is already in the open list, reassign its value if it's smaller
				if neighbor in open_verticies:
					old_f_of_n = neighbor.f_of_n
					if f_of_n < old_f_of_n:
						neighbor.parent = smallest_node
						neighbor.f_of_n = f_of_n

				#Otherwise, if our node does not already exist in the open list...
				else:

					#Set its parent node accordingly
					neighbor.parent = smallest_node
					neighbor.f_of_n = f_of_n

					#Get the neighbor's distance so far
					neighbor.distance_so_far = int(smallest_node.distance[neighbor.name]) + neighbor.parent.distance_so_far
					open_verticies.append(neighbor)

			print "Visiting Node:", smallest_node.name + "..."
			nodes_visited += 1

		#Otherwise, we know we've reached our destination
		else:
			time_end = time.time()

			#Trail the parent of F to construct our path
			path = []
			final_node = smallest_node
			path.append(final_node.name)
			while final_node.parent != None:
				path.append(final_node.parent.name)
				final_node.parent = final_node.parent.parent

			#Print shortest path and cost
			for i in range(0, len(path)):
				if i == len(path) - 1:
					print path[0]
				else:
					print path[len(path) - 1 - i] + " ->",
			print "Total Nodes Visited:", nodes_visited
			print "Total Distance:", smallest_node.distance_so_far
			print "Time Elapsed:", (time_end - time_start), "seconds"
			print "--------------------------------"

			break

def dijkstra_search(graph, nodes, start, end):
	print ":::DIJKSTRA'S ALGORITHM:::"

	open_verticies = []
	closed_verticies = []
	open_verticies.append(start)
	time_start = time.time()
	nodes_visited = 0

	while len(open_verticies) != 0:

		#Find smallest heuristic value in open nodes
		equals = []
		MAX_INT = 999999
		MAX_CHAR = 999999
		for node in open_verticies:
			if node.f_of_n < MAX_INT:
				smallest_node = node
				MAX_INT = node.f_of_n

		#If there are ties for smallest f(n), choose lowest alphabetical option
		for node in open_verticies:
			if node.f_of_n == smallest_node.f_of_n:
				equals.append(node)
		if len(equals) > 1:
			for node in equals:
				if ord(node.name) < MAX_CHAR:
					smallest_node = node
					MAX_CHAR = ord(node.name)

		#Remove the smallest node from the open list
		open_verticies.remove(smallest_node)

		#As long as we're not at the end...
		if smallest_node != end:

			#Add the smallest node to the closed list
			closed_verticies.append(smallest_node)

			#Visit each of the smallest node's neighbors
			for neighbor in smallest_node.neighbors:

				#Calculate f(n) value
				f_of_n = int(smallest_node.distance[neighbor.name]) + smallest_node.distance_so_far

				#If a neighbor is already in the open list, reassign its value if it's smaller
				if neighbor in open_verticies:
					old_f_of_n = neighbor.f_of_n
					if f_of_n < old_f_of_n:
						neighbor.parent = smallest_node
						neighbor.f_of_n = f_of_n

				#Otherwise, if our node does not already exist in the open list...
				else:

					#Set its parent node accordingly
					neighbor.parent = smallest_node
					neighbor.f_of_n = f_of_n

					#Get the neighbor's distance so far
					neighbor.distance_so_far = int(smallest_node.distance[neighbor.name]) + neighbor.parent.distance_so_far
					open_verticies.append(neighbor)

			print "Visiting Node:", smallest_node.name + "..."
			nodes_visited += 1

		#Otherwise, we know we've reached our destination
		else:
			time_end = time.time()

			#Trail the parent of F to construct our path
			path = []
			final_node = smallest_node
			path.append(final_node.name)
			while final_node.parent != None:
				path.append(final_node.parent.name)
				final_node.parent = final_node.parent.parent

			#Print shortest path and cost
			for i in range(0, len(path)):
				if i == len(path) - 1:
					print path[0]
				else:
					print path[len(path) - 1 - i] + " ->",
			print "Total Nodes Visited:", nodes_visited
			print "Total Distance:", smallest_node.distance_so_far
			print "Time Elapsed:", (time_end - time_start), "seconds"
			print "--------------------------------"

			break



edges, heuristics = read_file()
graph = create_graph(edges, heuristics)
A_nodes, D_nodes = create_nodes(graph, edges, heuristics)
for node in A_nodes:
	if node.name == "S":
		A_start = node
	elif node.name == "F":
		A_end = node
for node in D_nodes:
	if node.name == "S":
		D_start = node
	elif node.name == "F":
		D_end = node
a_star_search(graph, A_nodes, A_start, A_end)
dijkstra_search(graph, D_nodes, D_start, D_end)
