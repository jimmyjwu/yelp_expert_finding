import json
import networkx
import itertools


def parse_user_JSON():
	# Convert data from JSON -> Python
	users_file = open('users.json')
	users = []
	for line in itertools.islice(users_file, 100):
		users += [json.loads(line)]

	graph = networkx.Graph()
	node_number = {}	# Mapping of Yelp ID --> simple ID in [0, N)
	current_node_counter = 0
	for user in users:
		if user['user_id'] not in node_number:
			graph.add_node(current_node_counter)
			node_number[user['user_id']] = current_node_counter
			current_node_counter += 1
		for friend_ID in user['friends']:
			if friend_ID not in node_number:
				node_number[friend_ID] = current_node_counter
				current_node_counter += 1
			graph.add_edge(node_number[user['user_id']], node_number[friend_ID])


	# Print edge density
	print float( (graph.size() * 2)) / float( (len(graph) * (len(graph) - 1)) )


	# Write data to JSON file
	JSON = {'nodes': [], 'links': []}
	for user_ID in graph.nodes_iter():
		JSON['nodes'] += [{'name': user_ID}]
	for friend_1_ID, friend_2_ID in graph.edges_iter():
		JSON['links'] += [{'source': friend_1_ID, 'target': friend_2_ID, 'value': 1}]

	with open('graph.json', 'w') as output_file:
		json.dump(JSON, output_file)



if __name__ == "__main__":
	parse_user_JSON()