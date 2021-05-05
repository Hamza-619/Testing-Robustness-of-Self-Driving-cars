# Testing-Robustness-of-Self-Driving-cars
Master Thesis - University of Passau

A python framework  is implemented to test the **robustness of self-driving software by identifying their performance boundary**, i.e. region where the **AI** takes the transition from one mode to another due to small change in the environment. The framework includes active learning technology which effectively selects and labels the potential boundary test scenarios. Here active learning employs two learners, **Gaussian Process Classification **and** **Random Forest Classifier****, to supervise the searching process. The searching process uses **active learning's pool base sampling** to explore the samples in the pool of scenarios and selects the samples which show high coverage in various situation. Once the samples are selected and labelled by active learning **uncertainty section strategy** , the clustering algorithm **DBSCAN** groups the labelled samples, into the pass and fail subgroups. From the subgroups of the pass and fail samples, similar test case samples distances are selected using **KNN**. Lastly, boundary identification compares the distance between similar test cases and boundary width. For the test subject of the framework, **BeamNG** **AI** and **DeepDriving** are the two **AI** selected.

For running the framework, **BeamNG** Research has to be installed as simulator - *https://beamng.gmbh/research/*
For using **DeepDriving** as AI with the framework, **DeepDriving** projected need to be installed -  *https://bitbucket.org/Netzeband/deepdriving/wiki/Home*

In this repo, the boundary is identified integrating **BeamNG** **AI**.
