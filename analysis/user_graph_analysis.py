"""
Tools for analyzing the Yelp social network.
"""
from utilities import *
from data.data_interface import *

from analysis_utilities import *


def analyze_user_graph(
	user_graph_file_name=DEFAULT_RAW_USERS_FILE_NAME,
	user_pageranks_file_name=DEFAULT_PAGERANKS_FILE_NAME,
	show_degree_histogram=True,
	show_pagerank_histogram=False,
):
	"""
	Computes and visualizes statistics on the Yelp user graph.
	"""
	print 'READING IN YELP USER GRAPH'
	graph = read_user_graph(input_file_name=user_graph_file_name)

	print 'COMPUTING GRAPH PROPERTIES'
	edge_density = networkx.density(graph)
	node_degrees = [graph.degree(node) for node in graph.nodes_iter()]
	maximum_degree = max(node_degrees)

	print 'READING IN PAGERANKS'
	pagerank_for_node = read_user_pageranks(input_file_name=user_pageranks_file_name)

	print '\n============================================================================'
	print 'YELP USER GRAPH STATISTICS'
	print 'Edge density: ' + str(edge_density)

	print '\n============================================================================'
	print 'COMPUTING HISTOGRAMS'

	if show_degree_histogram:
		bin_width = 1
		maximum_degree_shown = 50
		show_histogram(values=node_degrees, value_name='Node Degree', bins=range(-1, maximum_degree_shown, bin_width), range_to_display=(-1, maximum_degree_shown + 1))

	if show_pagerank_histogram:
		show_histogram(values=pagerank_for_node.values(), value_name='PageRank', bins=500, range_to_display=(0, 0.001))


if __name__ == "__main__":
	analyze_user_graph()