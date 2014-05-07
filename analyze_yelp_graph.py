"""
Primary file for analysis of the Yelp dataset.
"""

from utilities import *
import regression


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



def predict_elite_status():
	# Prepare user data
	users = read_users_from_yelp_JSON_file()
	normalized_users = normalize_users(users, excluded_attributes=['years_elite'])
	labeled_users = designate_attribute_as_label(normalized_users, 'years_elite')

	# Fit to hyperplane
	model = regression.get_model(labeled_users)

	# Test on some users
	sample_users = labeled_users[0:100]
	for user in sample_users:
		print user['label']
		print regression.predict(remove_labels([user]).pop(), model)
		print ''

	# Show us how important each attribute is
	print 'Attribute weights:'
	for attribute, weight in regression.get_weights(labeled_users).items():
		print attribute + ': ' + str(weight)





if __name__ == "__main__":
	predict_elite_status()