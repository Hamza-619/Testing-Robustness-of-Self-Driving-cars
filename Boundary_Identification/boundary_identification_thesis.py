#from ActiveLearning import main
#from ActiveLearning import data_read
#from ActiveLearning import pool_based_sampling
#from ActiveLearning import change_features
import numpy as np
import pandas as pd
import csv
import os
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from random import randint
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from random import randint
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier

def data_read(file_name):
    path_dir = os.getcwd()
    file = path_dir + file_name
    mydata =  pd.read_csv(file)
    return mydata

def seperate_testcases(mydata):
    fail_testcases = mydata[mydata['result'] == 0]
    fail_testcases_array = np.asarray(fail_testcases)
    pass_testcases = mydata[mydata['result'] == 1]
    pass_testcases_array = np.asarray(pass_testcases)

    min_max_scaler = MinMaxScaler()
    fail_testcases_array = min_max_scaler.fit_transform(fail_testcases_array)
    min_max_scaler = MinMaxScaler()
    pass_testcases_array = min_max_scaler.fit_transform(pass_testcases_array)

    pass_testcases_forDb = pass_testcases_array[:, :3]
    fail_testcases_forDb = fail_testcases_array[:, :3]

    return pass_testcases_forDb, fail_testcases_forDb


def cluster_scenarios(X):

    # Function is adapted from https://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html. Modification is done as required by the framework.

    X_tranform = X # data already normalize
    # Compute DBSCAN
    db = DBSCAN(eps=0.7, min_samples=5).fit(X_tranform)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_


    # Number of clusters in labels, noise is ignored
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    get_clusters = [X[labels == i] for i in range(n_clusters_)]

    # Define variable to get list of clusters obtained
    total_clusters = list()


    for i in range(n_clusters_):
        store_cluster = np.full((get_clusters[i].shape[0], get_clusters[i].shape[1]+1),float(i))

        store_cluster[:,:-1] = get_clusters[i]

        total_clusters.append(store_cluster)

    total_clusters = np.concatenate(total_clusters)
    group_of_cluster = total_clusters.shape[1]

    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)

    sub_clusters = list()

    for i in range(group_of_cluster):
        create_subcluster = (total_clusters[:,3] ==i)
        print(create_subcluster)

        group_of_cluster_main = total_clusters[create_subcluster]

        sub_clusters.append(group_of_cluster_main)

    print(group_of_cluster)
    return group_of_cluster, sub_clusters


def compare_testcases(group_of_cluster_pass, group_of_cluster_fail, sub_groups_pass, sub_groups_fail, epsilon_value ):

    boundary_identified = list()

    #Compare pass and fail clusters

    for i in range(group_of_cluster_pass):
        for j in range(group_of_cluster_fail):
            if (len(sub_groups_pass[i]) > 0) and (len(sub_groups_fail[j]) > 0):

                check_len_pass = len(sub_groups_pass[i])
                check_len_fail = len(sub_groups_fail[j])
                if(check_len_pass < check_len_fail ):
                    min_neighbor = check_len_pass
                else:
                    min_neighbor = check_len_fail


                X_raw = sub_groups_pass[i]
                y_raw = sub_groups_fail[j]

                # Implementation of KNN

                X_train = X_raw[:,:3]
                y_train = X_raw[:,-1]
                y_fail_testcases = y_raw[:, :3]

                if min_neighbor>=7:
                    knn = KNeighborsClassifier(n_neighbors=7)
                else:
                    knn = KNeighborsClassifier(min_neighbor)

                knn.fit(X_train, y_train)

                boundary_found = list()
                distance = list()

                # Distance obtained is compared with epsilon between pass and fail test cases

                for testcases in y_fail_testcases:
                    distance_testcases = knn.kneighbors([testcases])
                    distance.append(distance_testcases)

                    # Epsilon value is checked with distances obtained
                    compare_distance = distance_testcases[0] <=  epsilon_value

                    testcase_boundary_dist = distance_testcases[1][compare_distance]

                    testcase_boundary_dist_len = len(testcase_boundary_dist)

                    if (testcase_boundary_dist_len != 0 ):
                        for i in range(testcase_boundary_dist_len):
                            similar_boundary = (*testcases, *X_train[testcase_boundary_dist[i],:])
                            boundary_found.append(similar_boundary)
                return boundary_found


            boundary_testcases = boundary_testcases + boundary_found

            return boundary_testcases


def main(insert_option): # this will run pool based sampling using Gaussian process classification with uncertainty selection strategy.

    if insert_option == '1':
        #X_raw, y_raw = data_read('\dataset_main_all_vehicle_onehot_main.csv')
        #result = pool_based_sampling(X_raw, y_raw, 300, "GPC_uncertain")
        mydata = data_read('\GPC_uncertain_activeLearning_main.csv')
        x_pass, x_fail = seperate_testcases(mydata)
        group_of_cluster_pass, sub_groups_pass  = cluster_scenarios(x_pass)
        group_of_cluster_fail, sub_groups_fail  = cluster_scenarios(x_fail)
        boundary_testcases = compare_testcases(group_of_cluster_pass, group_of_cluster_fail, sub_groups_pass, sub_groups_fail, 0.05 )
        print(len(boundary_testcases))
        out_df = pd.DataFrame(boundary_list,columns=[ 'Speed1', 'BrakeIntent1','Car_model1','Speed2','BrakeIntent2','Car_model2'])
        path_dir = os.getcwd()
        filename = 'GPC_uncertain_boundary'
        file_name_csv = os.path.join(path_dir, filename + ".csv")
        out_df.to_csv (file_name_csv, index = False, header=True)





    elif insert_option == '2': # this will run pool based sampling using Gaussian process classification with random sampling.
        #X_raw, y_raw = data_read('\dataset_main_all_vehicle_onehot_main.csv')
        #result = pool_based_sampling(X_raw, y_raw, 200, "GPC_random")
        mydata = data_read('\GPC_random_activeLearning_main.csv')
        x_pass, x_fail = seperate_testcases(mydata)
        group_of_cluster_pass, sub_groups_pass  = cluster_scenarios(x_pass)
        group_of_cluster_fail, sub_groups_fail  = cluster_scenarios(x_fail)
        boundary_list = compare_testcases(group_of_cluster_pass, group_of_cluster_fail, sub_groups_pass, sub_groups_fail, 0.05 )
        print(len(boundary_list))
        out_df = pd.DataFrame(boundary_list,columns=[ 'Speed1', 'BrakeIntent1','Car_model1','Speed2','BrakeIntent2','Car_model2'])
        path_dir = os.getcwd()
        filename = 'GPC_random_boundary'
        file_name_csv = os.path.join(path_dir, filename + ".csv")
        out_df.to_csv (file_name_csv, index = False, header=True)


    elif insert_option == '3':
        #X_raw, y_raw = data_read('\dataset_main_all_vehicle_onehot_main.csv')
        #result = pool_based_sampling(X_raw, y_raw, 300, "RFC_uncertain")
        mydata = data_read('\RFC_uncertain_activeLearning_main.csv')
        x_pass, x_fail = seperate_testcases(mydata)
        group_of_cluster_pass, sub_groups_pass  = cluster_scenarios(x_pass)
        group_of_cluster_fail, sub_groups_fail  = cluster_scenarios(x_fail)
        boundary_list = compare_testcases(group_of_cluster_pass, group_of_cluster_fail, sub_groups_pass, sub_groups_fail, 0.05 )
        print(len(boundary_list))
        out_df = pd.DataFrame(boundary_list,columns=[ 'Speed1', 'BrakeIntent1','Car_model1','Speed2','BrakeIntent2','Car_model2'])
        path_dir = os.getcwd()
        filename = 'RFC_uncertain_boundary'
        file_name_csv = os.path.join(path_dir, filename + ".csv")
        out_df.to_csv (file_name_csv, index = False, header=True)  # this will run pool based sampling using Random forest classifer with uncertainty selection strategy.


    elif insert_option == '4': # this will run pool based sampling using Random forest classifer with random sampling.
        #X_raw, y_raw = data_read('\dataset_main_all_vehicle_onehot_main.csv')
        #result = pool_based_sampling(X_raw, y_raw, 200, "RFC_random")
        mydata = data_read('\RFC_random_activeLearning_main.csv')
        x_pass, x_fail = seperate_testcases(mydata)
        group_of_cluster_pass, sub_groups_pass  = cluster_scenarios(x_pass)
        group_of_cluster_fail, sub_groups_fail  = cluster_scenarios(x_fail)
        boundary_list = compare_testcases(group_of_cluster_pass, group_of_cluster_fail, sub_groups_pass, sub_groups_fail, 0.05 )
        print(len(boundary_list))
        out_df = pd.DataFrame(boundary_list,columns=[ 'Speed1', 'BrakeIntent1','Car_model1','Speed2','BrakeIntent2','Car_model2'])
        path_dir = os.getcwd()
        filename = 'RFC_random_boundary'
        file_name_csv = os.path.join(path_dir, filename + ".csv")
        out_df.to_csv (file_name_csv, index = False, header=True)



if __name__ == "__main__":
    main('4')
