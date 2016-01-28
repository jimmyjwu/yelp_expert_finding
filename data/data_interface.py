"""
Utilities for the following:

          +-----------+        +----- THIS FILE ------+
          | raw_data/ | -----> | read from file(s)    |
          +-----------+        | build Python objects |        +--------------+
                               |                      | <----> | applications |
    +-----------------+        | export analysis to   |        +--------------+
    | processed_data/ | <----> | images, D3, etc.     |
    +-----------------+        +----------------------+

IMPORTANT: All data retrieval should be done through this file.
"""
from utilities import *
from data_utilities import *


def read_user_graph(input_file_name=DEFAULT_RAW_USERS_FILE_NAME):
	"""
	Given a Yelp dataset user file (with users in JSON format), returns a graph of the users and
	their friendships.
	"""
	graph = networkx.Graph()

	with open(_raw_data_absolute_path(input_file_name)) as users_file:

		for user_line in users_file:
			user = json.loads(user_line)
			graph.add_node(user['user_id'])
			for friend_ID in user['friends']:
				graph.add_edge(user['user_id'], friend_ID)

	return graph


def read_user_average_review_lengths(input_file_name=DEFAULT_REVIEW_LENGTHS_FILE_NAME):
	"""
	Given a processed review lengths file, returns a dictionary:
		{ user_1_ID: user_1_average_review_length, ..., user_N_ID: user_N_average_review_length }
	"""
	average_review_length_for_user = {}

	with open(_processed_data_absolute_path(input_file_name)) as review_lengths_file:

		for user_line in review_lengths_file:
			user_ID, average_review_length = user_line.split()
			average_review_length_for_user[user_ID] = average_review_length

	return average_review_length_for_user


def read_user_average_reading_levels(input_file_name=DEFAULT_READING_LEVELS_FILE_NAME):
	"""
	Given a processed reading levels file, returns a dictionary:
		{ user_1_ID: user_1_average_reading_level, ..., user_N_ID: user_N_average_reading_level }
	"""
	# Exploit the fact that the 'review length' and 'reading level' files are formatted the same
	return _read_user_average_review_lengths(input_file_name)


def write_D3_graph(graph, output_file_name=DEFAULT_D3_GRAPH_FILE_NAME):
	"""Writes a given graph to a JSON file suitable for displaying a D3 force-directed graph."""
	D3_dictionary = {'nodes': [], 'links': []}

	[ D3_dictionary['nodes'].append( {'name': user_ID} ) for user_ID in graph.nodes_iter() ]
	[ D3_dictionary['links'].append( {'source': friend_1_ID, 'target': friend_2_ID, 'value': 1} ) for friend_1_ID, friend_2_ID in graph.edges_iter() ]

	with open(_raw_data_absolute_path(output_file_name), 'w') as D3_graph_file:
		json.dump(D3_dictionary, D3_graph_file)

