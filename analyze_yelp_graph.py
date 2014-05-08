"""
Primary file for analysis of the Yelp dataset.
"""

from utilities import *
import regression


def analyze_yelp_graph():
	# Hyperparameters
	MINIMUM_FRIEND_COUNT = 1

	# Generate graph
	graph = read_graph_from_yelp_JSON_file()

	# Remove users with low friend count
	remove_low_degree_nodes(graph, MINIMUM_FRIEND_COUNT)

	# Calculate various graph metrics
	edge_density = networkx.density(graph)
	degree_histogram = networkx.degree_histogram(graph)

	# Calculate and show PageRank metrics
	pagerank_for_node = networkx.pagerank(graph)
	pageranks = sorted(pagerank_for_node.values())
	unique_pageranks = sorted(unique(pageranks))		# 26,145 unique PageRanks out of 70,817 total
	pagerank_frequencies = sorted(frequencies(pageranks).items(), key=lambda x: x[1])

	print 'The 5 smallest PageRanks are: ' + str(smallest_unique_values(pageranks, 5)) + '\n'
	print 'The 5 most frequent PageRanks are:'
	for pagerank, frequency in most_frequent_values_and_frequencies(pageranks, 5):
		print str(pagerank) + ', ' + str(frequency)


	# Plot histogram of PageRanks
	show_histogram(values=pageranks, value_name='PageRank', bins=500, range_to_display=(0,0.001))



def predict_elite_status():
	# Prepare user data
	users = read_users_from_yelp_JSON_file()
	users = remove_labels(users, label_name='ID')
	users = normalize_users(users, excluded_attributes=['years_elite'])
	users = designate_attribute_as_label(users, 'years_elite')

	# Split data into training and test
	user_count = len(users)
	training_set_size = int(0.75 * user_count)
	test_set_size = user_count - training_set_size
	training_set = users[0:training_set_size]
	test_set = users[-test_set_size:]

	# Fit to hyperplane
	model = regression.get_model(training_set)

	# Show us how important each attribute is
	print 'Attribute weights:'
	for attribute, weight in regression.get_weights(training_set).items():
		print attribute + ': ' + str(weight)

	# Test the model by calculating its coefficient of determination (R^2) on test data
	test_samples, test_labels, _ = regression.prep_data(test_set)
	test_score = model.score(test_samples, test_labels)
	print 'Test score: ' + str(test_score)



def predict_pagerank():
	# Hyperparameters
	MINIMUM_FRIEND_COUNT = 1

	# Generate graph and users
	graph = read_graph_from_yelp_JSON_file()
	remove_low_degree_nodes(graph, MINIMUM_FRIEND_COUNT)
	users = read_users_from_yelp_JSON_file()

	# Add PageRank to user dictionaries
	pagerank_for_node = networkx.pagerank(graph)
	user_pageranks = [{'ID': node_ID, 'pagerank': pagerank} for node_ID, pagerank in pagerank_for_node.iteritems()]
	users = join_dictionaries(user_pageranks, users, 'ID')

	# Prepare users for regression
	users = remove_labels(users, label_name='ID')
	users = remove_labels(users, label_name='friend_count')
	users = normalize_users(users, excluded_attributes=['ID', 'years_elite'])
	users = designate_attribute_as_label(users, attribute='pagerank')

	# Fit to hyperplane
	training_set = users
	model = regression.get_model(training_set)

	# Show us how important each attribute is
	print 'Attribute weights:'
	for attribute, weight in regression.get_weights(training_set).items():
		print attribute + ': ' + str(weight * 100)




if __name__ == "__main__":
	predict_pagerank()







