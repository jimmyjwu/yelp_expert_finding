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
	return _read_single_user_attribute(input_file_name)


def read_user_average_reading_levels(input_file_name=DEFAULT_READING_LEVELS_FILE_NAME):
	"""
	Given a processed reading levels file, returns a dictionary:
		{ user_1_ID: user_1_average_reading_level, ..., user_N_ID: user_N_average_reading_level }
	"""
	return _read_single_user_attribute(input_file_name)


def read_user_pageranks(input_file_name=DEFAULT_PAGERANKS_FILE_NAME):
	"""
	Given a processed reading levels file, returns a dictionary:
		{ user_1_ID: user_1_PageRank, ..., user_N_ID: user_N_PageRank }
	"""
	return _read_single_user_attribute(input_file_name)


def read_user_basic_attributes(input_file_name=DEFAULT_BASIC_ATTRIBUTES_FILE_NAME):
	"""
	Given a processed basic attributes file, returns a list of user dictionaries containing all
	attributes found in the file.
	"""
	users = []

	with open(_raw_data_absolute_path(input_file_name)) as user_basic_attributes_file:

		# Row 1: attribute names
		all_attributes = user_basic_attributes_file.readline().split()

		# Rows 2,...,N: users' attribute values written in the same order
		for user_line in user_basic_attributes_file:
			user_attribute_values = user_line.split()
			users += [ { attribute_name: user_attribute_values[i] for i, attribute_name in enumerate(all_attributes) } ]

	return users


def read_users(input_file_name=DEFAULT_COMBINED_USERS_FILE_NAME, attributes=DEFAULT_USER_ATTRIBUTES):
	"""
	Given a combined Yelp dataset user file and a list of attributes, returns a list of user
	dictionaries containing only the desired attributes.
	"""
	attributes_set = set(attributes)
	users = []

	with open(_raw_data_absolute_path(input_file_name)) as combined_users_file:

		# Row 1: attribute names
		all_attributes = combined_users_file.readline().split()

		# Rows 2,...,N: users' attribute values written in the same order
		for user_line in combined_users_file:
			user_attribute_values = user_line.split()
			users += [ { attribute_name: user_attribute_values[i] for i, attribute_name in enumerate(all_attributes) if attribute_name in attributes_set } ]

	return users


def write_D3_graph(graph, output_file_name=DEFAULT_D3_GRAPH_FILE_NAME):
	"""Writes a given graph to a JSON file suitable for displaying a D3 force-directed graph."""
	D3_dictionary = {'nodes': [], 'links': []}

	[ D3_dictionary['nodes'].append( {'name': user_ID} ) for user_ID in graph.nodes_iter() ]
	[ D3_dictionary['links'].append( {'source': friend_1_ID, 'target': friend_2_ID, 'value': 1} ) for friend_1_ID, friend_2_ID in graph.edges_iter() ]

	with open(_raw_data_absolute_path(output_file_name), 'w') as D3_graph_file:
		json.dump(D3_dictionary, D3_graph_file)

