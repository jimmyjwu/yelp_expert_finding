"""
Utilities specifically for machine learning and data analysis.
"""
from utilities import *


def make_attribute_boolean(users, attribute):
	"""
	Given a list of user dictionaries and an attribute name, returns a new list
	of users whose designated attribute is transformed as follows:
		value <= 0	-->		new value = 0
		value > 0	-->		new value = 1
	and all other attributes are copied without change.
	"""
	transformed_users = []
	for user in users:
		user_copy = {key: value for key, value in user.iteritems() if key != attribute}
		user_copy[attribute] = 1 if user[attribute] > 0 else 0
		transformed_users += [user_copy]
	return transformed_users


def designate_attribute_as_label(users, attribute):
	"""
	Given a list of user dictionaries and an attribute name, returns a new list
	of users whose designated attribute is named 'label', and all other attributes
	are copied without change.
	"""
	labeled_users = []
	for user in users:
		user_copy = {key: value for key, value in user.iteritems() if key != attribute}
		user_copy['label'] = user[attribute]
		labeled_users += [user_copy]
	return labeled_users


def stratified_boolean_sample(users, label_name='label'):
	"""
	Given a list of user dictionaries and the name of a Boolean-valued label, samples and returns
	two maximal, equal-size lists of positive and negative samples.
	"""
	positive_samples = [user for user in users if user[label_name] == 1]
	negative_samples = [user for user in users if user[label_name] == 0]

	return (positive_samples, random.sample(negative_samples, len(positive_samples))) if len(positive_samples) < len(negative_samples) else (random.sample(positive_samples, len(negative_samples)), negative_samples)


def remove_labels(users, label_name='label'):
	"""
	Given a list of user dictionaries, returns a new list of users without
	the label attribute, but with all other attributes copied.
	"""
	unlabeled_users = []
	for user in users:
		unlabeled_users += [{key: value for key, value in user.items() if key != label_name}]
	return unlabeled_users


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
	pyplot.title('Histogram of ' + value_name + 's')
	pyplot.axis('tight')
	pyplot.grid(True)
	pyplot.show()



