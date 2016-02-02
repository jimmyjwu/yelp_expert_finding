"""
Primary file for analysis of the Yelp dataset.
"""
from sklearn.naive_bayes import GaussianNB

from utilities import *
from data.data_interface import *
from ML_models.regression import *

from analysis_utilities import *


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


def predict_elite_status_with_naive_bayes():
	"""Trains and tests a Naive Bayes model for predicting users' Elite status."""
	# Hyperparameters
	FRACTION_FOR_TRAINING = 0.7
	NAIVE_BAYES_USER_ATTRIBUTES = DEFAULT_USER_ATTRIBUTES

	print 'READING USERS FROM FILE'
	users = read_users(attributes=NAIVE_BAYES_USER_ATTRIBUTES)
	users = remove_labels(users, 'ID')
	users = make_attribute_boolean(users, 'years_elite')

	# Ensure 50-50 split of positive and negative data, preventing a natural bias towards the 94% negative labels
	print 'TAKING STRATIFIED SAMPLE OF DATA'
	users = stratified_boolean_sample(users, label_name='years_elite')
	random.shuffle(users)
	user_vectors, labels = vectorize_users(users, label_name='years_elite')

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	training_set, training_set_labels, test_set, test_set_labels, positive_test_set, positive_test_set_labels = partition_data_vectors(user_vectors, labels, FRACTION_FOR_TRAINING)

	# Train Naive Bayes model
	naive_bayes_model = GaussianNB()
	naive_bayes_model.fit(training_set, training_set_labels)

	# Compute accuracy measures
	print 'Accuracy on test data: ', format_as_percentage( naive_bayes_model.score(test_set, test_set_labels) )
	print 'Accuracy on training data: ', format_as_percentage( naive_bayes_model.score(training_set, training_set_labels) )
	print 'Recall of positive samples: ', format_as_percentage( naive_bayes_model.score(positive_test_set, positive_test_set_labels) )
	print 'Class prior distribution (should be roughly even): ', naive_bayes_model.class_prior_




if __name__ == "__main__":
	predict_elite_status_with_naive_bayes()
	# predict_elite_status_with_linear_regression()


