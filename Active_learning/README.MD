Each car model can only be integrated with available car parts for that model. Car parts for Van don't work with car parts for hopper.
Putting all car models with their car in one file with their settings required too many loops and hence sometimes crashing of the test scenario.
Therefore sperate python files are created for each car model and car parameter option in BeamNG_scenario folder.

The result of all the test cases with each car models from BeamNG is saved in the CSV file. 
The active learning query asks for the label for the selected test case, and instead of obtaining the label at runtime, the label is provided from the CSV file which already has the result stored.

To obtain result at runtime, the query y_pool[query_index] has to be changed to BeamNG. It has been commented on the code.
