import numpy as np
import pandas as pd
import csv
import os
import io
import sys
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn import preprocessing
from modAL.models import ActiveLearner
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from modAL.uncertainty import uncertainty_sampling
from sklearn.ensemble import RandomForestClassifier

from modAL.uncertainty import margin_sampling
from modAL.uncertainty import entropy_sampling
from modAL.uncertainty import uncertainty_sampling


def random_sampling(classifier, X_pool):
    number_of_samples = len(X_pool)
    query_samples = np.random.choice(range(number_of_samples))
    return query_samples, X_pool[query_samples]


# Read Data
def data_read(file_name):
    path_dir = os.getcwd()
    file = path_dir + file_name
    mydata = pd.read_csv(file)
    newData = pd.get_dummies(mydata)
    feature_names = [
        "speed",
        "brake_brake1",
        "car_model_etk800",
        "brake_brake2",
        "brake_brake3",
        "car_model_etkc",
        "car_model_hopper",
        "car_model_van",
        "transmission_transmission1",
        "transmission_transmission2",
        "transmission_transmission3",
        "tire_tire1",
        "tire_tire2",
        "tire_tire3",
    ]

    feature_names = [
        "speed",
        "brake_brake1",
        "car_model_etk800",
        "brake_brake2",
        "brake_brake3",
        "car_model_etkc",
        "car_model_hopper",
        "car_model_van",
        "transmission_transmission1",
        "transmission_transmission2",
        "transmission_transmission3",
        "tire_tire1",
        "tire_tire2",
        "tire_tire3",
    ]
    X_raw = newData[feature_names]
    y_raw = newData["result"]
    return X_raw, y_raw


def pool_based_sampling(X_raw, y_raw, budget, approach):
    # Function adapted as required by framework from https://modal-python.readthedocs.io/en/latest/content/examples/pool-based_sampling.html
    X_value = np.asarray(X_raw)
    y_value = np.asarray(y_raw)
    Random_State_val = 123
    np.random.seed(Random_State_val)

    labeled_n_samples = X_value.shape[0]
    training_index = np.random.randint(low=0, high=labeled_n_samples + 1, size=5)
    print(training_index)

    X_train = X_value[training_index]
    y_train = y_value[training_index]

    # Remove non training samples from the pool
    X_pool = np.delete(X_value, training_index, axis=0)
    y_pool = np.delete(y_value, training_index, axis=0)

    # Here the approach choosen is run by active learning to label the test cases.

    if approach == "GPC_uncertain":
        gpc = GaussianProcessClassifier()

        learner = ActiveLearner(
            estimator=gpc,
            query_strategy=uncertainty_sampling,
            X_training=X_train,
            y_training=y_train,
        )

    elif approach == "GPC_random":
        gpc = GaussianProcessClassifier()

        learner = ActiveLearner(
            estimator=gpc,
            query_strategy=random_sampling,
            X_training=X_train,
            y_training=y_train,
        )

    elif approach == "RFC_uncertain":

        rf = RandomForestClassifier()

        learner = ActiveLearner(
            estimator=rf,
            query_strategy=uncertainty_sampling,
            X_training=X_train,
            y_training=y_train,
        )

    elif approach == "RFC_random":

        rf = RandomForestClassifier()

        learner = ActiveLearner(
            estimator=rf,
            query_strategy=random_sampling,
            X_training=X_train,
            y_training=y_train,
        )

    # Prediction is done with the intial label provided.
    predictions = learner.predict(X_pool)

    # Accuracy is returned for the prediction
    initial_score = learner.score(X_value, y_value)

    # Here the model is updated to increase the accuracy by budget defined by the user
    num_of_queries = budget
    performance_history = [initial_score]
    X = None
    y = None
    result_pool = []
    uncertain_samples = []

    # Model queries for the unlabeled test cases. Query selection is based on the informative points returned by the selection strategy.
    for index in range(num_of_queries):
        query_index, query_instance = learner.query(X_pool)
        uncertain_samples.append(query_index)

        # Here the ActiveLearner model learns from the test cases it has requested.
        X, y = X_pool[query_index].reshape(1, -1), y_pool[query_index].reshape(
            1,
        )  # y=np.asarray(BeamNG_scenario).reshape(1, ), this need to be called for getting labels from BeamNG in run time. BeamNG_scenario needs to be inside function.
        learner.teach(X=X, y=y)
        # print(query_index)
        result_pool.append(y)

        # Removes the queried test cases from the unlabeled pool.
        X_pool, y_pool = np.delete(X_pool, query_index, axis=0), np.delete(
            y_pool, query_index
        )

        # Checks the model accuracy
        model_accuracy_final = learner.score(X_raw, y_raw)
        print(
            "Accuracy after query {n}: {acc:0.4f}".format(
                n=index + 1, acc=model_accuracy_final
            )
        )
        # Save our model's accuracy
        performance_history.append(model_accuracy_final)

    initial_score = learner.score(X_value, y_value)
    print(initial_score)

    predictions = learner.predict(X_pool)
    output_df = pd.DataFrame(predictions, columns=["result"])
    out_df = pd.DataFrame(
        X_pool,
        columns=[
            "speed",
            "brake_brake1",
            "car_model_etk800",
            "brake_brake2",
            "brake_brake3",
            "car_model_etkc",
            "car_model_hopper",
            "car_model_van",
            "transmission_transmission1",
            "transmission_transmission2",
            "transmission_transmission3",
            "tire_tire1",
            "tire_tire2",
            "tire_tire3",
        ],
    )

    # label received is concatenated with their respective test cases
    result = pd.concat([out_df, output_df], axis=1)
    print(result)

    # As the features were categorical, the features had to be encoded by one hot encoding.
    # The line of coded below, convert the features back to categorical with labels obtained for respective test cases.

    result.loc[result["brake_brake1"] == 1, "brake"] = "brake1"
    result.loc[result["brake_brake2"] == 1, "brake"] = "brake2"
    result.loc[result["brake_brake3"] == 1, "brake"] = "brake3"
    result.loc[result["car_model_etk800"] == 1, "car_model"] = "etk800"
    result.loc[result["car_model_etkc"] == 1, "car_model"] = "etkc"
    result.loc[result["car_model_hopper"] == 1, "car_model"] = "hopper"
    result.loc[result["car_model_van"] == 1, "car_model"] = "van"
    result.loc[
        result["transmission_transmission1"] == 1, "transmission"
    ] = "transmission1"
    result.loc[
        result["transmission_transmission2"] == 1, "transmission"
    ] = "transmission2"
    result.loc[
        result["transmission_transmission3"] == 1, "transmission"
    ] = "transmission3"
    result.loc[result["tire_tire1"] == 1, "tire"] = "tire1"
    result.loc[result["tire_tire2"] == 1, "tire"] = "tire2"
    result.loc[result["tire_tire3"] == 1, "tire"] = "tire3"

    result.drop(
        [
            "brake_brake1",
            "car_model_etk800",
            "brake_brake2",
            "brake_brake3",
            "car_model_etkc",
            "car_model_hopper",
            "car_model_van",
            "transmission_transmission1",
            "transmission_transmission2",
            "transmission_transmission3",
            "tire_tire1",
            "tire_tire2",
            "tire_tire3",
        ],
        inplace=True,
        axis=1,
    )
    result = result[[col for col in result.columns if col != "result"] + ["result"]]
    result = result[
        ["car_model"] + [col for col in result.columns if col != "car_model"]
    ]

    path_dir = os.getcwd()
    filename = approach
    file_name_csv = os.path.join(path_dir, filename + ".csv")

    # The results obtained by searching process is saved in the csv file.
    result_file = result.to_csv(file_name_csv, index=False, header=True)
    return result


def change_features(file_name):
    # Here the obtained file has features brake pad, transmission and tire which is combined to one feature named brake intensity.

    path_dir = os.getcwd()
    file = path_dir + file_name
    text = open(file)

    text = "".join([i for i in text])

    text = text.replace(",brake,transmission,tire,", ",BrakeIntensity,")
    text = text.replace(",brake1,transmission3,tire1,", ",BrakeIntensity1,")
    text = text.replace(",brake1,transmission1,tire1,", ",BrakeIntensity3,")
    text = text.replace(",brake1,transmission2,tire1,", ",BrakeIntensity2,")
    text = text.replace(",brake1,transmission2,tire2,", ",BrakeIntensity5,")
    text = text.replace(",brake1,transmission1,tire3,", ",BrakeIntensity9,")
    text = text.replace(",brake1,transmission1,tire2,", ",BrakeIntensity6,")
    text = text.replace(",brake1,transmission3,tire3,", ",BrakeIntensity7,")
    text = text.replace(",brake2,transmission3,tire1,", ",BrakeIntensity10,")
    text = text.replace(",brake2,transmission1,tire2,", ",BrakeIntensity15,")
    text = text.replace(",brake2,transmission3,tire2,", ",BrakeIntensity13,")
    text = text.replace(",brake3,transmission2,tire1,", ",BrakeIntensity20,")
    text = text.replace(",brake3,transmission1,tire2,", ",BrakeIntensity24,")
    text = text.replace(",brake3,transmission3,tire3,", ",BrakeIntensity25,")
    text = text.replace(",brake1,transmission1,tire3,", ",BrakeIntensity1,")
    text = text.replace(",brake1,transmission3,tire2,", ",BrakeIntensity4,")
    text = text.replace(",brake1,transmission2,tire3,", ",BrakeIntensity8,")
    text = text.replace(",brake2,transmission2,tire1,", ",BrakeIntensity11,")
    text = text.replace(",brake2,transmission1,tire1,", ",BrakeIntensity12,")
    text = text.replace(",brake2,transmission2,tire2,", ",BrakeIntensity14,")
    text = text.replace(",brake2,transmission3,tire3,", ",BrakeIntensity16,")
    text = text.replace(",brake2,transmission2,tire3,", ",BrakeIntensity17,")
    text = text.replace(",brake2,transmission1,tire3,", ",BrakeIntensity18,")
    text = text.replace(",brake3,transmission3,tire1,", ",BrakeIntensity19,")
    text = text.replace(",brake3,transmission1,tire1,", ",BrakeIntensity21,")
    text = text.replace(",brake3,transmission3,tire2,", ",BrakeIntensity22,")
    text = text.replace(",brake3,transmission2,tire2,", ",BrakeIntensity23,")
    text = text.replace(",brake3,transmission2,tire3,", ",BrakeIntensity26,")
    text = text.replace(",brake3,transmission1,tire3,", ",BrakeIntensity27,")

    # output.csv is the output file opened in write mode
    x = open(file + ".csv", "w")

    # all the replaced text is written in the output.csv file
    x.writelines(text)  #

    x.close()

    file_new = file + ".csv"

    mydata = pd.read_csv(file_new)

    intensity_dic = {
        "BrakeIntensity3": 1,
        "BrakeIntensity2": 2,
        "BrakeIntensity1": 3,
        "BrakeIntensity6": 4,
        "BrakeIntensity5": 5,
        "BrakeIntensity4": 6,
        "BrakeIntensity9": 7,
        "BrakeIntensity8": 8,
        "BrakeIntensity7": 9,
        "BrakeIntensity12": 10,
        "BrakeIntensity11": 11,
        "BrakeIntensity10": 12,
        "BrakeIntensity15": 13,
        "BrakeIntensity14": 14,
        "BrakeIntensity13": 15,
        "BrakeIntensity18": 16,
        "BrakeIntensity17": 17,
        "BrakeIntensity16": 18,
        "BrakeIntensity21": 19,
        "BrakeIntensity20": 20,
        "BrakeIntensity19": 21,
        "BrakeIntensity24": 22,
        "BrakeIntensity23": 23,
        "BrakeIntensity22": 24,
        "BrakeIntensity27": 25,
        "BrakeIntensity26": 26,
        "BrakeIntensity25": 27,
    }
    car_dic = {"etk800": 1, "etkc": 2, "hopper": 3, "van": 4}

    mydata["Brake_Intensity"] = mydata.BrakeIntensity.map(intensity_dic)
    mydata["car_models"] = mydata.car_model.map(car_dic)
    mydata.drop(["car_model", "BrakeIntensity"], inplace=True, axis=1)
    mydata = mydata[[col for col in mydata.columns if col != "result"] + ["result"]]

    path_dir = os.getcwd()
    filename = file_new
    file_name_csv = os.path.join(path_dir, filename + ".csv")

    mydata.to_csv(file_name_csv, index=False, header=True)
    return mydata


def main(insert_option):

    if (
        insert_option == "1"
    ):  # this will run pool based sampling using Gaussian process classification with uncertainty selection strategy.
        X_raw, y_raw = data_read("\dataset_main.csv")
        result = pool_based_sampling(X_raw, y_raw, 30, "GPC_uncertain")
        mydata = change_features("\GPC_uncertain.csv")

    elif (
        insert_option == "2"
    ):  # this will run pool based sampling using Gaussian process classification with random sampling.
        X_raw, y_raw = data_read("\dataset_main.csv")
        result = pool_based_sampling(X_raw, y_raw, 200, "GPC_random")
        mydata = change_features("\GPC_random.csv")

    elif (
        insert_option == "3"
    ):  # this will run pool based sampling using Random forest classifer with uncertainty selection strategy.
        X_raw, y_raw = data_read("\dataset_main.csv")
        result = pool_based_sampling(X_raw, y_raw, 300, "RFC_uncertain")
        mydata = change_features("\RFC_uncertain.csv")

    elif (
        insert_option == "4"
    ):  # this will run pool based sampling using Random forest classifer with random sampling.
        X_raw, y_raw = data_read("\dataset_main.csv")
        result = pool_based_sampling(X_raw, y_raw, 200, "RFC_random")
        mydata = change_features("\RFC_random.csv")


if __name__ == "__main__":
    main("1")
