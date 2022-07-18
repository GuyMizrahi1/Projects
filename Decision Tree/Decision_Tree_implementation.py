import pandas as pd
import numpy as np
import random
import tqdm
from pprint import pprint
import scipy.stats as stats


def k_cross_attach(separated_dict):
    attached_data = {"k_train": [], "k_test": []}
    for i in range(len(separated_dict["k_data"])):
        attached_data["k_test"].append(separated_dict["k_data"][i])
        temp_dict = {"temp": []}
        for j in range(len(separated_dict["k_data"])):
            if j != i:
                temp_dict["temp"].append(separated_dict["k_data"][j])
        train_df = pd.concat(temp_dict["temp"])
        attached_data["k_train"].append(train_df)
    return attached_data


def k_cross_split(df, k):
    separated_data = {"k_data": []}
    train_df = df
    while k > 1:
        ratio = 1 - 1 / k  # k = 4 -> ratio = 0.75 of train, 0.25 test
        train_df, test_df = train_test_split(train_df, ratio)
        # next iteration k = 3 -> ratio = 2/3, the train equals 0.75 from the first df therefore next train will be-> 0.5 , and the rest -> 0.25 test and so on...
        separated_data["k_data"].append(test_df)
        k -= 1
    separated_data["k_data"].append(train_df)
    return separated_data


# separate the data to train and test data frames
def train_test_split(df, train_size):
    # checks if my train size is actual number or proportion
    if isinstance(train_size, float) or train_size == 1:
        train_size = round(train_size * len(df))
    indices = df.index.tolist()
    train_indices = random.sample(population=indices, k=train_size)
    train_df = df.loc[train_indices]
    test_df = df.drop(train_indices)
    return train_df, test_df


# the input data is df.values
# data purity means if the data has the same value, and our question is if there is more than 650 -> busy day
def check_purity(data):
    label_column = data[2:, 0]  # checks the first column - rented bike count
    unique_classes = np.unique(label_column)
    if len(unique_classes) == 1:
        return True
    return False


# prepare and load data
def prepare_data(ratio, df):
    if df.empty:
        train_df, test_df, df = None, None, None
    else:
        df = arrange_first_columns(df)
        # splits the train and test data by number or ratio
        train_df, test_df = train_test_split(df, ratio)
        train_df = add_labels(train_df)
        # test_df = add_labels(test_df)     made problem when i was checking accuracy
        df = add_labels(df)
    return train_df, test_df, df


def arrange_first_columns(df):
    df = df.rename(columns={"Rented Bike Count": "label"})
    df = df.drop("Date", axis=1)  # drop an irrelevant column for the decision
    data = df.values
    label_column = data[:, 0]
    df = transfer_to_busy(df, label_column)
    return df


# transfer the bike column to a categorical column, eventually it would be understood if pure or not.
def transfer_to_busy(df, label_column):
    for num in label_column:
        if num > 650:
            df = df.replace({"label": num}, "busy")
        else:
            df = df.replace({"label": num}, "not busy")
    return df


def add_labels(df):
    feature_types = determine_type_of_feature(df)
    df = add_to_first_row(df, feature_types)
    attributes = df.columns
    df = add_to_first_row(df, attributes)
    return df


def add_to_first_row(df, row):
    df.loc[-1] = row
    df.index = df.index + 1
    df = df.sort_index()
    return df


# determine type of feature
def determine_type_of_feature(df):
    feature_types = []
    n_unique_values_threshold = 24  # if a feature has a relatively high number of categories - hour for example
    for column in df.columns:
        unique_values = df[column].unique()
        example_value = unique_values[0]
        if (isinstance(example_value, str)) or (len(unique_values) <= n_unique_values_threshold):
            feature_types.append("categorical")
        else:
            feature_types.append("continuous")
    return feature_types


# classify a column by its unique elements and return the element appears most -> I'll use it if the data is pure
# or almost pure but because of my constraints I wouldn't split it again
def classify_data(data):
    label_column = data[2:, 0]
    unique_classes, count_unique_classes = np.unique(label_column,
                                                     return_counts=True)  # what are the elements and how many appearances
    index = count_unique_classes.argmax()  # get the index of the class that appears most often
    classification = unique_classes[index]
    return classification


# gets all the potential splits
def get_potential_splits(data):
    potential_splits = {}  # create a dictionary
    n_row, n_column = data.shape
    for column_index in range(n_column):
        if column_index > 0:  # by that, it wouldn't categorize the first label
            values = data[2:, column_index]
            unique_values = np.unique(values)  # get the unique values from a specific row and arrange them
            type_of_feature = data[1][column_index]
            if type_of_feature == "continuous":
                if len(unique_values) > 1:
                    potential_splits[column_index] = []
                    for index in range(len(unique_values)):
                        if index != 0:  # skipping the first element
                            current_value = unique_values[index]
                            _type = type(current_value)
                            previous_value = unique_values[index - 1]
                            potential_split = round((current_value + previous_value) / 2, 3)
                            potential_splits[column_index].append(potential_split)
            else:
                potential_splits[column_index] = unique_values  # every category use as a split
    return potential_splits


def insert_labels_to_np(data, sec_data):
    rows = data[:2]
    # result_data = np.insert(sec_data, 0, rows)
    result_data = np.vstack((rows, sec_data))
    return result_data


# split data
def split_data(data, split_column, split_value):
    split_column_values = data[2:, split_column]
    type_of_feature = data[1][split_column]
    current_data = data[2:, :]
    if type_of_feature == "continuous":
        data_below = current_data[split_column_values <= split_value]
        data_below = insert_labels_to_np(data, data_below)
        data_above = current_data[split_column_values > split_value]
        data_above = insert_labels_to_np(data, data_above)
    else:
        data_below = current_data[split_column_values == split_value]
        data_below = insert_labels_to_np(data, data_below)
        data_above = current_data[split_column_values != split_value]
        data_above = insert_labels_to_np(data, data_above)
    return data_below, data_above


# entropy of a single column
def calculate_entropy(data):
    label_column = data[2:, 0]
    _, appearances = np.unique(label_column, return_counts=True)
    probabilities = appearances / appearances.sum()
    entropy = sum(probabilities * (-np.log2(probabilities)))
    return entropy


# calculate overall entropy
def calculate_overall_entropy(data_below, data_above):
    # minus the two rows of label and type
    below_length = len(data_below) - 2
    above_length = len(data_above) - 2
    n_data_points = below_length + above_length
    p_below = below_length / n_data_points
    p_above = above_length / n_data_points
    overall_entropy = (p_below * calculate_entropy(data_below)) + (p_above * calculate_entropy(data_above))
    return overall_entropy


# determine the best split by considering entropy
def determine_best_splits(data, potential_splits):
    overall_entropy = 9999
    best_split_column, best_split_value = 0, 0
    for column_index in potential_splits:
        for value in potential_splits[column_index]:
            data_below, data_above = split_data(data, column_index, value)
            current_overall_entropy = calculate_overall_entropy(data_below, data_above)
            if current_overall_entropy <= overall_entropy:
                overall_entropy = current_overall_entropy
                best_split_value = value
                best_split_column = column_index
    return best_split_column, best_split_value


# build the train decision tree, the df will update every iteration, by deleting columns
def decision_tree_algorithm(df, parent_df=None, counter=0):
    # separate the first iteration that df isn't np 2D array
    if counter == 0:
        global COLUMN_HEADERS, FEATURE_TYPES, POTENTIAL_SPLITS
        data = df.values
        COLUMN_HEADERS = df.columns
        FEATURE_TYPES = determine_type_of_feature(df)
        POTENTIAL_SPLITS = get_potential_splits(data)
    else:
        data = df
    # recursive base cases
    num_rows, num_cols = data.shape
    if num_rows <= 2:
        classification = classify_data(parent_df)
        return classification
    elif check_purity(data):
        classification = classify_data(data)
        return classification
    elif num_cols == 1:
        classification = classify_data(data)
        return classification
    # recursive part
    else:
        counter += 1
        types = data[1]
        potential_splits = get_potential_splits(data)
        if len(potential_splits) == 0:
            classification = classify_data(data)
            return classification
        split_column, split_value = determine_best_splits(data, potential_splits)
        # instantiate of a sub-tree
        feature_name = data[0][split_column]
        type_of_feature = data[1][split_column]
        if type_of_feature == "continuous":
            question = "{} <= {}".format(feature_name, split_value)
            data_below, data_above = split_data(data, split_column, split_value)
            data_below = update_data_column(data_below, data, split_column)
            data_above = update_data_column(data_above, data, split_column)
            sub_tree = {question: []}
            yes_answer = decision_tree_algorithm(data_below, data, counter)
            no_answer = decision_tree_algorithm(data_above, data, counter)
            # find answer
            if yes_answer == no_answer:  # for the case I would have a Unnecessary question
                sub_tree = yes_answer
            else:
                sub_tree[question].append(yes_answer)
                sub_tree[question].append(no_answer)
            return sub_tree
        else:  # categorical
            question = "{}".format(feature_name)
            sub_tree = {question: []}
            help_counter = -1
            for name in COLUMN_HEADERS:
                help_counter += 1
                if name == feature_name:
                    break
            all_branches = POTENTIAL_SPLITS[help_counter]
            all_categorical_data = {}
            for value in all_branches:
                categorical_data, _ = split_data(data, split_column, value)
                all_categorical_data[str(value)] = update_data_column(categorical_data, data, split_column)
            for j in range(len(all_categorical_data.keys())):
                answer = decision_tree_algorithm(all_categorical_data[str(all_branches[j])], data, counter)
                sub_question = "{} = {}".format(feature_name, all_branches[j])
                categorical_tree = {sub_question: answer}
                sub_tree[question].append(categorical_tree)
            return sub_tree


def update_data_column(partial_data, data, split_column):
    if partial_data.size == 0:
        partial_data.append(classify_data(data))
    else:
        partial_data = np.delete(partial_data, np.s_[split_column],
                                 axis=1)  # drop the used column from the data to the next decision
    return partial_data


# classification of questions after any label has split value
def classify_record(record, tree, df):
    question = list(tree.keys())[0]  # question: temperature (c) >= 15 or seasons
    feature_name, comparison_operator, value = split_question_to_label(question)  # (temperature (c), >=, 15) or seasons
    # ask question
    if comparison_operator is None:
        # get all categories
        question_place = 0
        for i in range(len(tree[question])):
            categorical_question = list(tree[question][i])
            _, _, current_value = split_question_to_label(categorical_question[0])
            if str(current_value) == str(record[feature_name]):
                question_place = i
                break
        answer = tree[question][question_place]
    # divide to continuous situation
    elif comparison_operator == "<=":
        if float(record[feature_name]) <= float(value):
            # takes the last of the tree that says yes
            answer = tree[question][0]
        else:
            # takes the last of the tree that says no
            answer = tree[question][1]
    else:
        answer = tree[question]
    # base case -> there is no dictionary means it reached a leaf, that is the label
    if not isinstance(answer, dict):
        return answer
    # recursive part
    else:
        residual_tree = answer
        return classify_record(record, residual_tree, df)


def split_question_to_label(question):
    x = question.split(" ")
    if len(x) == 1:
        feature_name = question
        comparison_operator = None
        value = None
    else:
        feature_name = ""
        if x[len(x) - 2] == 'No':
            value = x[len(x) - 2] + " " + x[len(x) - 1]
            comparison_operator = x[len(x) - 3]
            operator_location = len(x) - 3
        else:
            value = x[len(x) - 1]
            comparison_operator = x[len(x) - 2]
            operator_location = len(x) - 2
        index = 0
        for i in x:
            if index < operator_location:
                feature_name += str(i)
                index += 1
                if index < operator_location:
                    feature_name += " "
    return feature_name, comparison_operator, value


# def pruning(tree):
#     # conclusion = chi_square_calc(tree)
#     return tree

# accuracy of examine the test data frame
def calculate_accuracy(df, tree):
    # create a column that classified to 'busy' , 'not busy'
    df["classification"] = df.apply(classify_record, axis=1, args=(tree, df,))
    # create a column of booleans, true values interpreted as 1, and false as zero -> therefore it is possible to calculate mean
    df["classification_correct"] = df.classification == df.label
    accuracy = df.classification_correct.mean()
    return accuracy


# default value for df as None, means
def build_tree(ratio, df=None, test_df=None):
    # creation of default df as none help to call it fromm k cross validation with another partial data
    if df is None:
        df = pd.read_csv("SeoulBikeData.csv", encoding='unicode_escape')
        # actual check if there was no data on file
        if df is None:
            print("No data has inserted")
        else:
            build_print_tree(ratio, df)
    else:
        tree, error = build_tree_k_cross(ratio, df, test_df)
        return tree, error


def build_print_tree(ratio, df):
    train_df, test_df, df = prepare_data(ratio, df)
    tree = decision_tree_algorithm(train_df, 0)
    # pruned_tree = pruning(tree)
    if ratio != 1:
        accuracy = calculate_accuracy(test_df, tree)
    else:
        train_df = train_df.iloc[2:, :]
        accuracy = calculate_accuracy(train_df, tree)
    pprint(tree, width=5)
    print("The error is: " + str(1 - accuracy))


def build_tree_k_cross(ratio, train_df, test_df):
    train_df, _, df = prepare_data(ratio, train_df)
    tree = decision_tree_algorithm(train_df, 0)
    # pruned_tree = pruning(tree)
    test_df = arrange_first_columns(test_df)
    accuracy = calculate_accuracy(test_df, tree)
    return tree, 1 - accuracy


def tree_error(k, check_one_record=False):
    df = pd.read_csv("SeoulBikeData.csv", encoding='unicode_escape')
    separated_dict = k_cross_split(df, k)
    arranged_dict = k_cross_attach(separated_dict)
    tree_dict = {"tree": [], "error": []}
    index = 0
    sum_errors = 0
    lowest_error = 1
    for i in range(k):
        tree, error = build_tree(1, arranged_dict["k_train"][i], arranged_dict["k_test"][i])
        sum_errors += error
        tree_dict["tree"].append(tree)
        tree_dict["error"].append(error)
        if error < lowest_error:
            index = i
            lowest_error = error
    mean_error = sum_errors / k
    if not check_one_record:
        print("The lowest error reported by k-fold cross validation: " + str(lowest_error))
        print("The mean error reported by k-fold cross validation: " + str(mean_error))
    else:
        best_tree = tree_dict["tree"][index]
        return best_tree, df.columns


def arrange_row(row_values, label_row):
    # add features name, label column
    row_values = row_values.insert(1, "busy")
    record = pd.Series(row_values)
    record = record.rename(lambda i: label_row[i])
    record = record.rename({"Rented Bike Count": "label"})
    record.pop("Date")
    return record


def is_busy(row_input):
    row_values = row_input.columns  # index object
    if row_values is not None:
        best_tree, label_row = tree_error(2, True)
        record = arrange_row(row_values, label_row)
        answer = classify_record(record, best_tree, None)
        if answer == "busy":
            return "busy"
        else:
            return "not busy"
    else:
        print("invalid input")


if __name__ == "__main__":
    build_tree(0.8)
    tree_error(3)
    # prediction for a busy day or not by all the other parameters
    row_input = pd.read_csv("one_line.csv", encoding='unicode_escape')
    output = is_busy(row_input)
    print("The prediction is: " + str(output))
