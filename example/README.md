# Dummy Labeling Example Workflow

This folder contains necessary files for you to test the dummy labeling tool.

## Structure

* `test_images/`: contains 8 images from the [Food-101](https://www.kaggle.com/kmader/food41) dataset.
* `faster_rcnn_tf_outputs.json`: outputs from the [Tensorflow Hub Object Detection](https://www.tensorflow.org/hub/tutorials/object_detection) - Faster RCNN model for 4 images.
* `ssd_tf_outputs.json`: outputs from the [Tensorflow Hub Object Detection](https://www.tensorflow.org/hub/tutorials/object_detection) - SSD model for 4 images.
* `food_samples_ground_truth_labels.csv`: ground truth label for each image, as extracted from the [Food-101](https://www.kaggle.com/kmader/food41) dataset.
* `sample_config.txt`: config file that combines different model outputs and ground truth labels together. **Note that no header is needed.**

## Usage

* Once all the required packages are installed, `cd` to the package root folder (one level above this one).
* Run the following command: `python app.py --dir "example/test_images/" --config "example/sample_config.txt"`
* Open http://127.0.0.1:5000/tagger in your browser
    * Only tested on Chrome

## Need help?

Submit an issue for this project.
