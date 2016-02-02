"""
Primary file for analysis of the Yelp dataset.
"""
from sklearn.naive_bayes import GaussianNB

from utilities import *
from data.data_interface import *
from ML_models.regression import *


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
	TEST_ONLY_ONES = False
	TRAIN_ON_ZEROS_TEST_ON_ONES = False

	# Assuming there are fewer positive samples than negative samples
	POSITIVE_SAMPLE_COUNT = 31461

	NAIVE_BAYES_USER_ATTRIBUTES = DEFAULT_USER_ATTRIBUTES

	print 'READING USERS FROM FILE'
	users = read_users(attributes=NAIVE_BAYES_USER_ATTRIBUTES)
	users = remove_labels(users, 'ID')
	users = make_attribute_boolean(users, 'years_elite')

	print 'TAKING STRATIFIED SAMPLE OF DATA'
	# Ensure 50-50 split of 0-labeled and 1-labeled training and test data
	# If we don't do this, data is 94% 0-labeled and performs poorly on 1-labeled users
	elite_users, non_elite_users = stratified_boolean_sample(users, label_name='years_elite')
	users = elite_users + non_elite_users
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

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
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

	# Compute accuracy measures
	print 'Accuracy on test data: ', gnb.score(test_set, test_set_labels)
	print 'Accuracy on training data: ', gnb.score(training_set, training_set_labels)

	print 'Class prior distribution (should be roughly even): ' + str(gnb.class_prior_)





if __name__ == "__main__":
	predict_elite_status_with_bayes()
	# predict_elite_status_with_linear_regression()


