"""
Utilities for the following:

          +-----------+
          | raw_data/ | -----> +----- THIS FILE ------+
          +-----------+        | read from file(s)    |        +--------------+
                               | build Python objects | -----> | applications |
    +-----------------+        |                      |        +--------------+
    | processed_data/ | -----> +----------------------+
    +-----------------+

IMPORTANT: All data retrieval should be done through this file.
"""
from utilities import *
from data_utilities import *


def read_user_graph(file_name='raw_data/yelp_academic_dataset_user.json'):
	"""
	Given a Yelp dataset user file (with users in JSON format), returns a graph of the users and
	their friendships.
	"""
	users_file = open(file_name)
	users = [json.loads(line) for line in users_file.readlines()]

	graph = networkx.Graph()
	for user in users:
		user_ID = user['user_id']
		graph.add_node(user_ID)
		for friend_ID in user['friends']:
			graph.add_edge(user_ID, friend_ID)

	return graph