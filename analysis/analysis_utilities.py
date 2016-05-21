"""
Utilities specifically for machine learning and data analysis.
"""
from utilities import *



def balanced_sample(users, label_name='label'):
	"""
	Given a list of user dictionaries with a Boolean label, returns a maximal sample of the users
	in which both labels are equally common.
	"""
	positive_samples = [user for user in users if user[label_name] == 1]
	negative_samples = [user for user in users if user[label_name] == 0]

	if len(positive_samples) < len(negative_samples):
		return positive_samples + random.sample(negative_samples, len(positive_samples))
	else:
		return random.sample(positive_samples, len(negative_samples)) + negative_samples


def remove_attribute(users, attribute):
	""" Deletes an attribute from all users in a list of user dictionaries. """
	[ user.pop(attribute, None) for user in users ]


def vectorize_users(users, attributes, label_name='label'):
	"""
	Given a list of user dictionaries, returns
		X : a numpy array of arrays, each representing the attribute values of a single user
		y : a numpy array of corresponding correct labels for X

	NOTE: Output vectors respect ordering of input attributes: for every x in X, x[i] is the value
	of attribute attributes[i].
	"""
	user_vectors = []
	labels = []

	for user in users:
		user_vectors += [ [user[attribute] for attribute in attributes if attribute != label_name] ]
		labels += [ user[label_name] ]

	return numpy.array(user_vectors), numpy.array(labels)


def partition_data_vectors(feature_vectors, labels, fraction_for_training=0.7):
	"""
	Given a list of feature vectors (lists) and their corresponding labels, returns:
		- A training set
		- A test set, disjoint from the training set
		- A recall test set (subset of test data labeled positive)

	NOTE: Does not sample randomly. Any randomization must be applied before using this utility.
	"""
	dataset_size = len(feature_vectors)
	training_set_size = int(fraction_for_training * dataset_size)
	test_set_size = dataset_size - training_set_size

	training_set = feature_vectors[0:training_set_size]
	training_set_labels = labels[0:training_set_size]
	test_set = feature_vectors[-test_set_size:]
	test_set_labels = labels[-test_set_size:]
	positive_test_set = [vector for i, vector in enumerate(test_set) if test_set_labels[i] == 1]
	positive_test_set_labels = [1]*len(positive_test_set)

	return training_set, training_set_labels, test_set, test_set_labels, positive_test_set, positive_test_set_labels


def normalize_users(users, excluded_attributes=[]):
	"""
	Given a list of user dictionaries whose attributes are numeric values, returns a list of
	users in which all attributes, EXCEPT those whose names are in excluded_attributes,
	are normalized to [0, 1].

	Normalization is done using min-max.
	"""
	excluded_attributes = set(excluded_attributes)

	# Find extreme values for each attribute
	max_user = {attribute: float('-infinity') for attribute in users[0].keys()}
	min_user = {attribute: float('infinity') for attribute in users[0].keys()}
	for user in users:
		for attribute, value in user.iteritems():
			if attribute not in excluded_attributes:
				max_user[attribute] = max(max_user[attribute], value)
				min_user[attribute] = min(min_user[attribute], value)

	# Normalize users
	for user in users:
		for attribute, value in user.iteritems():
			if attribute not in excluded_attributes:
				user[attribute] = float(value - min_user[attribute]) / (max_user[attribute] - min_user[attribute])

	return users


def show_histogram(values, value_name='Value', bins=100, range_to_display=(0,0), normed=False):
	if range_to_display == (0,0):
		n, bins, patches = pyplot.hist(values, bins=bins, normed=normed, facecolor='g', alpha=0.75)
	else:
		n, bins, patches = pyplot.hist(values, bins=bins, range=range_to_display, normed=normed, facecolor='g', alpha=0.75)
	pyplot.xlabel(value_name)
	pyplot.ylabel('Frequency')
	# pyplot.title('Histogram of ' + value_name + 's')
	pyplot.axis('tight')
	pyplot.grid(True)
	pyplot.show()


def show_histogram_with_broken_y_axis(values, value_name='Value', bins=100, range_to_display=(0,0), normed=False, cutout=(0,0)):
	"""
	Displays a histogram with a break (a section cut out) in the y-dimension.
	"""
	n, bins, patches = pyplot.hist(x=values, bins=bins, range=range_to_display, normed=normed, facecolor='g', alpha=0.75)
	bins = numpy.delete(bins, -1)
	width = bins[2] - bins[1]

	pyplot.xlabel(value_name)
	pyplot.ylabel('Frequency')
	# pyplot.title('Histogram of ' + value_name + 's')
	pyplot.axis('tight')

	# Create two plots with a y-axis break in between
	figure, (axes_1, axes_2) = pyplot.subplots(2, 1, sharex=True)

	# Plot the same data as bar charts on both axes
	axes_1.bar(bins, n, width, color='g', alpha=0.75)
	axes_2.bar(bins, n, width, color='g', alpha=0.75)

	# Turn grid lines on
	axes_1.grid(True)
	axes_2.grid(True)

	axes_1.set_ylim(bottom=cutout[1])	# Limit first axis to upper parts of bars
	axes_2.set_ylim(0, cutout[0])		# Limit second axis to lower parts of bars

	# Fix x-axis boundaries (without this, visible boundary is changed by diagonal lines below)
	axes_1.set_xlim(right=range_to_display[1])
	axes_2.set_xlim(right=range_to_display[1])

	# Hide the spines between axes_1 and axes_2
	axes_1.spines['bottom'].set_visible(False)
	axes_2.spines['top'].set_visible(False)
	axes_1.xaxis.tick_top()
	axes_1.tick_params(labeltop='off') # Omit tick labels at the top
	axes_2.xaxis.tick_bottom()

	# Add short diagonal lines around breaks
	# Note: axis dimensions are always on a [0,1] scale regardless of actual range
	d = .015  # Size of diagonal lines
	kwargs = dict(transform=axes_1.transAxes, color='k', clip_on=False)
	axes_1.plot((-d, +d), (-d, +d), **kwargs) # Top-left diagonal
	axes_1.plot(((1 - d), (1 + d)), (-d, +d), **kwargs) # Top-right diagonal

	kwargs.update(transform=axes_2.transAxes) # Switch to the bottom axes
	axes_2.plot((-d, +d), (1 - d, 1 + d), **kwargs) # Bottom-left diagonal
	axes_2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs) # Bottom-right diagonal

	pyplot.show()


def show_feature_importances(forest, features):
	"""
	Given a trained forest-type classifier (e.g. random forest, boosted decision tree, etc.),
	displays a bar chart of the features' relative importances according to the Gini impurity index.
	"""
	m = len(features)

	sorted_importances_and_features = sorted(zip(forest.feature_importances_, features))
	sorted_importances, sorted_features = zip(*sorted_importances_and_features)

	# Print the feature ranking
	for importance, feature in sorted_importances_and_features:
		print feature, ':\t', format_as_percentage(importance)

	# Plot the feature importances of the forest
	pyplot.figure()
	# pyplot.title('Feature Importances')
	pyplot.barh(range(m), sorted_importances, color='c', align='center')
	pyplot.yticks(range(m), sorted_features, fontsize='xx-large')
	pyplot.ylim([-1, m])
	pyplot.axis('tight')
	pyplot.grid(True)
	pyplot.show()




