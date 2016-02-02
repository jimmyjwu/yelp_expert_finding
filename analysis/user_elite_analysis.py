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


def predict_elite_status_with_bayes():
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

	user_vectors, labels = vectorize_users(users, label_name='years_elite')

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	user_count = len(user_vectors)
	training_set_size = int(0.7 * user_count)
	test_set_size = user_count - training_set_size
	training_set = user_vectors[0:training_set_size]
	training_set_labels = labels[0:training_set_size]
	test_set = user_vectors[-test_set_size:]
	test_set_labels = labels[-test_set_size:]

	# Train Naive Bayes model
	gnb = GaussianNB()
	gnb.fit(training_set, training_set_labels)

	# Compute accuracy measures
	print 'Accuracy on test data: ', format_as_percentage( gnb.score(test_set, test_set_labels) )
	print 'Accuracy on training data: ', format_as_percentage( gnb.score(training_set, training_set_labels) )

	positive_test_samples = [sample for i, sample in enumerate(test_set) if test_set_labels[i] == 1]
	positive_test_samples_labels = [1]*len(positive_test_samples)
	print 'Recall of positive samples: ', format_as_percentage( gnb.score(positive_test_samples, positive_test_samples_labels) )

	print 'Class prior distribution (should be roughly even): ', gnb.class_prior_





if __name__ == "__main__":
	predict_elite_status_with_bayes()
	# predict_elite_status_with_linear_regression()


