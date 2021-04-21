This is our training folder. It contains all files related to our model training.

It is advisable to create a separate training folder each time we wish to train on a different dataset.

Typical folder structure:
	training_demo/
	├─ annotations/ - stores all .csv files and the respective TF .record files, which contain list of annotations for our dataset images.
	├─ exported-models/ - stores exported versions of our trained model(s). 
	├─ images/ - contains copies of all the images in our dataset, as well as respective .xml files produced for each one, once labelImg is used to annotate objects. 
	│  ├─ test/ 
	│  └─ train/
	├─ models/ - contains a sub-folder for each of the training jobs. Each subfolder will contain the training pipeline config file .config, as well as all files generated during the training and evalutation of our model.
	├─ pre-trained-models/ - contains the downloaded pre-trained models, which shall be used as a starting checkpoint for our training jobs. 
	└─ README.md - this file. Can also include general info about the training conditions of our model, which can be helpful if you have a few training folders. 
	
Link to tutorial - https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/training.html#evaluation-sec