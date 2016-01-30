"""
Primary file for analysis of the Yelp dataset.
"""

from utilities import *
import regression
from sklearn.naive_bayes import GaussianNB, BernoulliNB


def analyze_yelp_graph():
	# Hyperparameters
	MINIMUM_FRIEND_COUNT = 0
	SHOW_PAGERANK_METRICS = False

	# Generate graph
	graph = read_graph_from_yelp_JSON_file()

	# Remove users with low friend count
	remove_low_degree_nodes(graph, MINIMUM_FRIEND_COUNT)

	# Calculate various graph metrics
	edge_density = networkx.density(graph)
	degree_histogram = networkx.degree_histogram(graph)
	degrees = [graph.degree(node) for node in graph.nodes()]
	print 'Edge density: ' + str(edge_density)

	# Calculate and show PageRank metrics
	if SHOW_PAGERANK_METRICS:
		pagerank_for_node = networkx.pagerank(graph)
		pageranks = sorted(pagerank_for_node.values())
		unique_pageranks = sorted(unique_values(pageranks))		# 26,145 unique PageRanks out of 70,817 total
		pagerank_frequencies = sorted(frequencies(pageranks).items(), key=lambda x: x[1])

		print 'The 5 smallest PageRanks are: ' + str(smallest_unique_values(pageranks, 5)) + '\n'
		print 'The 5 most frequent PageRanks are:'
		for pagerank, frequency in most_frequent_values_and_frequencies(pageranks, 5):
			print str(pagerank) + ', ' + str(frequency)

		show_histogram(values=pageranks, value_name='PageRank', bins=500, range_to_display=(0,0.001))

	# Plot histogram of node degrees
	show_histogram(values=degrees, value_name='Node Degree', bins=500, range_to_display=(-1,30))


def predict_elite_status_with_linear_regression():
	# Generate graph and user dictionaries
	graph = read_graph_from_yelp_JSON_file()
	users = read_users_from_yelp_JSON_file(model_type='linear_regression')

	# Add PageRank to user dictionaries
	pagerank_for_node = networkx.pagerank(graph)
	user_pageranks = [{'ID': node_ID, 'pagerank': pagerank} for node_ID, pagerank in pagerank_for_node.iteritems()]
	users = join_dictionaries(user_pageranks, users, 'ID')

	# Prepare users for learning
	users = remove_labels(users, 'ID')
	users = normalize_users(users, excluded_attributes=['years_elite'])
	users = designate_attribute_as_label(users, 'years_elite')
	random.shuffle(users)

	# Split data into training and test
	user_count = len(users)
	training_set_size = int(0.75 * user_count)
	test_set_size = user_count - training_set_size
	training_set = users[0:training_set_size]
	test_set = users[-test_set_size:]

	# Fit to hyperplane
	model, weights = regression.get_model_and_weights(training_set)

	# Show us how important each attribute is
	print 'Attribute weights:'
	for attribute, weight in weights.items():
		print attribute + ': ' + str(weight)

	# Test the model by calculating its coefficient of determination (R^2) on test data
	test_samples, test_labels, _ = regression.prep_data(test_set)
	test_score = model.score(test_samples, test_labels)
	print 'Test score: ' + str(test_score)


def predict_elite_status_with_bayes():
	# Hyperparameters
	TEST_ONLY_ONES = True
	TRAIN_ON_ZEROS_TEST_ON_ONES = False

	# Generate graph and user dictionaries
	graph = read_graph_from_yelp_JSON_file()
	print 'Finished reading graph'

	users = read_users_from_yelp_JSON_file(model_type='naive_bayes')
	print 'Finished reading users'

	# Add PageRank to user dictionaries
	pagerank_for_node = networkx.pagerank(graph)
	user_pageranks = [{'ID': node_ID, 'pagerank': pagerank} for node_ID, pagerank in pagerank_for_node.iteritems()]
	users = join_dictionaries(user_pageranks, users, 'ID')
	print 'Finished adding PageRanks to users'
	
	# Add reading level to user dictionaries
	reading_level_for_user = read_user_reading_levels_from_yelp_JSON_file()
	reading_levels = [{'ID': ID, 'reading_level': reading_level} for ID, reading_level in reading_level_for_user.items()]
	users = join_dictionaries(reading_levels, users, 'ID')
	print 'Finished adding reading level to users'

	# Prepare users for learning
	users = remove_labels(users, 'ID')
	random.shuffle(users)

	# Ensure 50-50 split of 0-labeled and 1-labeled training and test data
	# If we don't do this, data is 93% 0-labeled and performs poorly on 1-labeled users
	users_0 = 0
	users_1 = 0
	temporary_users = []
	for user in users:
		if user['years_elite'] == 0:
			if users_0 < 5000:
				temporary_users += [user]
				users_0 += 1
		else:
			if users_1 < 5000:
				temporary_users += [user]
				users_1 += 1
	users = temporary_users

	random.shuffle(users)

	labels = []
	user_vectors = []
	sorted_keys = sorted(users[0].keys())
	for user in users:
		# Transform each user into a vector
		user_vector = []
		for key in sorted_keys:
			if key != 'years_elite':
				user_vector.append(user[key])
		user_vectors.append(user_vector)

		# Generate a label for every user
		labels.append(1 if user['years_elite'] > 0 else 0)

	# Split data into training and test
	user_count = len(user_vectors)
	training_set_size = int(0.7 * user_count)
	test_set_size = user_count - training_set_size
	training_set = user_vectors[0:training_set_size]
	training_set_labels = labels[0:training_set_size]
	test_set = user_vectors[-test_set_size:]
	test_set_labels = labels[-test_set_size:]

	# Train on only 0's, test on only 1's. Result is zero accuracy score.
	if TRAIN_ON_ZEROS_TEST_ON_ONES:
		print "Training only on 0's, testing only on 1's."
		training = []
		training_labels = []
		test = []
		test_labels = []
		for i in range(user_count):
			if labels[i] == 0:
				training += [user_vectors[i]]
				training_labels += [labels[i]]
			else:
				test += [user_vectors[i]]
				test_labels += [labels[i]]
		training_set = training
		training_set_labels = training_labels
		test_set = test
		test_set_labels = test_labels
	
	# Test for recall on 1's
	if TEST_ONLY_ONES:
		print "Testing only on 1's (recall)."
		test = []
		test_labels = []
		for i in range(test_set_size):
			if test_set_labels[i] == 1:
				test += [test_set[i]]
				test_labels += [test_set_labels[i]]
		test_set = test
		test_set_labels = test_labels
		print len(test_set)
		print user_count

	# Train Naive Bayes model
	gnb = GaussianNB()
	gnb.fit(training_set, training_set_labels)

	# Calculate mean accuracy on test data
	print "Classification score: ", gnb.score(test_set, test_set_labels)

	print 'Class prior distribution (should be roughly even): ' + str(gnb.class_prior_)


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
	model, weights = regression.get_model_and_weights(training_set)

	# Show us how important each attribute is
	print 'Attribute weights:'
	for attribute, weight in weights.items():
		print attribute + ': ' + str(weight * 100)




if __name__ == "__main__":
	# predict_elite_status_with_bayes()
	# predict_elite_status_with_linear_regression()
	# predict_pagerank()
	analyze_yelp_graph()


