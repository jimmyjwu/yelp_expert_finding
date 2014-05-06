"""
Primary file for analysis of the Yelp dataset.
"""

from utilities import *


def analyze_yelp_graph():
	graph = read_graph_from_yelp_JSON_file()
	edge_density = networkx.density(graph)
	# degree_histogram = networkx.degree_histogram(graph)
	pagerank_for_node = networkx.pagerank(graph)
	pageranks = sorted(pagerank_for_node.values())
	unique_pageranks = sorted(unique(pageranks))		# 26,145 unique PageRanks out of 70,817 total
	pagerank_frequencies = sorted(frequencies(pageranks).items(), key=lambda x: x[1])


	print 'The 5 smallest PageRanks are: ' + str(smallest_unique_values(pageranks, 5)) + '\n'
	print 'The 5 most frequent PageRanks are: ' + str(most_frequent_values_and_frequencies(pageranks, 5)) + '\n'


	# Plot histogram of PageRanks
	show_pagerank_histogram(pageranks)


	# TODO: Eliminate users without friends, so as to reduce the number of small PageRanks that dominate the histogram






if __name__ == "__main__":
	analyze_yelp_graph()