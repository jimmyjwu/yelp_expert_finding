# Yelp Expert Finding

The goal of this project is to develop high-accuracy machine learning models for identifying local experts (designated "Elite" users) in the Yelp review network, and to analyze the characteristics of these users.

__Here is a [paper summarizing our methods and findings](https://goo.gl/Kd1gwK)__.


---
## How to Replicate Our Experiments

#### Download Materials
Install all Python packages in requirements.txt:
```bash
pip install -r requirements.txt
```

Download the [Yelp Dataset Challenge](http://www.yelp.com/dataset_challenge/) data. Extract its contents into a new folder `/data/raw_data/`, so that we have:
```
/data/raw_data/yelp_academic_dataset_business.json
/data/raw_data/yelp_academic_dataset_checkin.json
/data/raw_data/yelp_academic_dataset_review.json
/data/raw_data/yelp_academic_dataset_tip.json
/data/raw_data/yelp_academic_dataset_user.json
```


#### Extract Features
We now extract features from the raw dataset. Navigate to the project root, open a Python interactive shell, and execute:
```python
>>> from data.data_processing import *
>>> extract_user_basic_attributes()
>>> extract_user_average_review_lengths()
>>> extract_user_reading_levels()
>>> extract_user_tip_counts()
>>> extract_user_pageranks()
```
This creates new data files under a new folder `/data/processed_data/`. To customize the input/output file names, see `/data/data_processing.py`.


#### Build the Dataset
We now combine all features into a single file. In the same Python shell, execute:
```python
>>> combine_all_user_data()
```

Finally, we randomly partition these users into training and test sets. In the same Python shell, execute:
```python
>>> create_training_and_test_sets(fraction_for_training=0.8)
```
File names can be adjusted via arguments to these functions.


#### Training and Tuning
To train and cross-validate a particular classifier model (on the training set only), simply call the appropriate function in `/analysis/user_elite_analysis.py`.

For example, to train a random forest model, open a Python shell from the project root and execute:
```python
>>> from analysis.user_elite_analysis import *
>>> train_random_forest_elite_status_classifier()
```
This will train a random forest model and present its performance statistics using pre-selected hyperparameters. To adjust the hyperparameters, see `/analysis/user_elite_analysis.py`.

> If multiple experiments are run during the same Python shell session, the dataset will be read only the first time, then cached until Python is exited.


#### Testing
Once you have tuned your favorite classifier model(s) to satisfaction, apply it to the test set.

Suppose we wish to test our random forest model. In the same Python shell, execute:
```python
>>> test_elite_status_classifier(
        ModelClass=RandomForestClassifier,
        attributes=RANDOM_FOREST_USER_ATTRIBUTES,
        model_arguments=RANDOM_FOREST_ARGUMENTS,
        balance_training_set=True, # Optional: whether the model should be trained on equally many Elite and non-Elite users
        balance_test_set=True      # Optional: whether the model should be tested on equally many Elite and non-Elite users
    )
```


#### Visualize Social Network Properties
Open a Python shell from the project root and execute:
```python
>>> from analysis.user_graph_analysis.py import *
>>> analyze_user_graph(
        show_degree_histogram=True
        show_pagerank_histogram=True
    )
```

