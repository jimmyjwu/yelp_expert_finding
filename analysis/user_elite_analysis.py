"""
Primary file for analysis of the Yelp dataset.
"""
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals.six import StringIO
import pydot

from utilities import *
from data.data_interface import *

from analysis_utilities import *


# Cache expensive file reads and computations
CACHE = {
	'users': None,
}



def train_elite_status_classifier(ModelClass, attributes, fraction_for_training, model_arguments={}):
	"""
	Given a constructor for a classifier object and a list of user attributes to use, trains,
	tests, and returns a classifier for Elite status.
	"""
	print ''
	if CACHE['users']:
		print 'USERS LOADED FROM MEMORY'
		users = CACHE['users']
	else:
		print 'READING USERS FROM FILE'
		users = read_users()
		remove_attribute(users, 'ID')
		make_attribute_boolean(users, 'years_elite')
		designate_attribute_as_label(users, 'years_elite')
		CACHE['users'] = users

	# Ensure 50-50 split of positive and negative data, preventing a natural bias towards the 94% negative labels
	print 'TAKING STRATIFIED SAMPLE OF DATA'
	sampled_users = stratified_boolean_sample(users)
	random.shuffle(sampled_users)
	user_vectors, labels = vectorize_users(sampled_users, attributes)

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	training_set, training_set_labels, test_set, test_set_labels, positive_test_set, positive_test_set_labels = partition_data_vectors(user_vectors, labels, fraction_for_training)

	print 'TRAINING ' + ModelClass.__name__ + ' CLASSIFIER'
	model = ModelClass(**model_arguments)
	model.fit(training_set, training_set_labels)

	# Compute accuracy measures
	print ''
	print 'Accuracy on test data: ', format_as_percentage( model.score(test_set, test_set_labels) )
	print 'Accuracy on training data: ', format_as_percentage( model.score(training_set, training_set_labels) )
	print 'Recall of positive samples: ', format_as_percentage( model.score(positive_test_set, positive_test_set_labels) )
	print ''

	return model



FRACTION_FOR_TRAINING = 0.7
NAIVE_BAYES_USER_ATTRIBUTES = [
	'review_count',
	'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	'pagerank',
]
def train_naive_bayes_elite_status_classifier():
	"""Trains and tests a naive Bayes model for predicting users' Elite status."""
	model = train_elite_status_classifier(GaussianNB, NAIVE_BAYES_USER_ATTRIBUTES, FRACTION_FOR_TRAINING)



LOGISTIC_REGRESSION_FRACTION_FOR_TRAINING = 0.7
LOGISTIC_REGRESSION_USER_ATTRIBUTES = [
	'review_count',
	#'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	#'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	#'pagerank',
]
def train_logistic_regression_elite_status_classifier():
	"""Trains and tests a logistic regression model for predicting users' Elite status."""
	model = train_elite_status_classifier(LogisticRegression, LOGISTIC_REGRESSION_USER_ATTRIBUTES, LOGISTIC_REGRESSION_FRACTION_FOR_TRAINING)



DECISION_TREE_FRACTION_FOR_TRAINING = 0.8
DECISION_TREE_USER_ATTRIBUTES = [
	'review_count',
	#'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	#'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	#'pagerank',
]
def train_decision_tree_elite_status_classifier():
	"""Trains and tests a decision tree model for predicting users' Elite status."""
	model = train_elite_status_classifier(DecisionTreeClassifier, DECISION_TREE_USER_ATTRIBUTES, DECISION_TREE_FRACTION_FOR_TRAINING)

	# Output tree representation showing decision rules
	dot_data = StringIO()
	tree.export_graphviz(model, out_file=dot_data, class_names=True, filled=True)
	graph = pydot.graph_from_dot_data(dot_data.getvalue())
	graph.write_pdf('analysis/analysis_results/decision_tree.pdf')



# Current best: FRACTION_FOR_TRAINING=0.8, n_estimators=100
# Accuracy on test data: ~96%
# Accuracy on training data: 100%
# Recall on positive samples: ~97.5%
RANDOM_FOREST_FRACTION_FOR_TRAINING = 0.8
RANDOM_FOREST_USER_ATTRIBUTES = [
	'review_count',
	'average_stars',
	'funny_vote_count',
	'useful_vote_count',
	'cool_vote_count',
	'friend_count',
	'months_member',
	'compliment_count',
	'fan_count',
	'average_review_length',
	'average_reading_level',
	'tip_count',
	'pagerank',
]
RANDOM_FOREST_ARGUMENTS = {
	'n_estimators': 100
}
def train_random_forest_elite_status_classifier():
	"""Trains and tests a random forest model for predicting users' Elite status."""
	model = train_elite_status_classifier(RandomForestClassifier, RANDOM_FOREST_USER_ATTRIBUTES, RANDOM_FOREST_FRACTION_FOR_TRAINING, model_arguments=RANDOM_FOREST_ARGUMENTS)

	# Print features and importances side-by-side
	for importance, attribute in sorted(zip(model.feature_importances_, RANDOM_FOREST_USER_ATTRIBUTES)):
		print attribute, '\t', format_as_percentage(importance)



if __name__ == "__main__":
	train_decision_tree_elite_status_classifier()


