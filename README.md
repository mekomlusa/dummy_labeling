# Dummy Labeling

Convert image datasets that are originally for classification to object detection.

You may want to check out [its sister project](https://github.com/mekomlusa/simple_image_annotator) too.

What differentiates this tool from the simple image annotator: once outputs from existing object detection models are saved, they could be loaded directly to the tool and served as a starting point. See the process workflow image below.

## Description
I need to train a model that could automatically detect food on an uploaded image. However, there is no open sourced food image datasets for the object detection task. There are a handful of food images for classification, though. So why don't we use best of the both worlds: **classification labels** provided as ground truths, and **bounding boxes** from pre-trained object detection models? Then, I just need the best bounding box and assign it with the ground truth label.

*Load outputs from SSD result, select & Save*
![ssd1](./ssd1.png)

*Saved results*
![result](./confirmed.png)

## Process Workflow

![workflow](./workflow.png)

To see how bounding boxes and ground truth labels are obtained, refer to the notebook under `data_prep`. Note: the notebook only shows one way. You are more than welcome to use your own ground truth labels and model output files, but if so you might need to tweak the code (mainly `app.py`) a bit.

## Usage

To quickly get started and see the tool in action, check out the `example/` folder.

* Prereq: Python >= 3.6, also install all the required packages: `pip install -r requirements.txt`
* `cd` into this directory after cloning the repo
* Get bounding boxes and labels using existing tools. If you'd like to utilize TF Object Detection API, check out [this notebook](\data_prep\TF_Object_detection_API_demo_with_food_data.ipynb).
* Gather the ground truth text file and OD outputs (json) and put it in a secured place.
* Create a config file similar to `example/sample_config.txt`.
* Start the app:
```
$ python app.py --dir /images/directory --config path/to/config.txt
```
* You can also specify the file you would like the annotations output to (`out.csv` is the default)
```
$ python app.py --dir /images/directory --config path/to/config.txt --out test.csv
```
* Open http://127.0.0.1:5000/tagger in your browser
    * Only tested on Chrome

## Output
* In keeping with simplicity, the output is to a csv file with the following fields
    * *id* - id of the bounding box within the image
    * *name* - name of the bounding box within the image
    * *image* - image the bounding box is associated with
    * *xMin* - min x value of the bounding box
    * *xMax* - max x value of the bounding box
    * *yMin* - min y value of the bounding box
    * *yMax* - max y value of the bounding box

## HOWTOs
* Use the dropdown menu to select the algorithm you'd like to use as a starting point.
  * Technically, there is no limitation as to how many algorithms you may load to this tool. However, for performance reasons (especially if you have tons of images to draw bounding boxes on) I will recommend only load 1 or 2 algorithm files in.
* Draw a bounding box
  * Click on the image in the location of the first corner of the bounding box you would like to add
  * Click again for the second corner (ideally the entirely opposite direction - say the first corner is top left, the second corner should be bottom right) and the box will be drawn.
  * **Note: you cannot draw new bounding boxes on pre-loaded algorithm results (e.g. faster r-cnn outputs from TF Hub Object Detection API).**
* Add a label for a box
  * For the box you would like to give a label, find its id (noted in the top left corner of the box)
  * Find the label with the corresponding number
  * Enter the name you want in the input field
  * Press enter
  * **Note: you cannot add labels for new bounding boxes on pre-loaded algorithm results (e.g. faster r-cnn outputs from TF Hub Object Detection API).**
* Change the label for a box
  * For the box you would like to change its label, find its id (noted in the top left corner of the box)
  * Click the input field next to it (background color should change from light grey to white)
  * Enter new label name and press enter. Note that the results will be saved under the "confirmed" tab.
* Save labels
  * Once you're done with labeling the whole image, click the "Save" button. **Note: changes will not saved if you don't click that button!**
* Move to the next image
  * Click the blue right arrow button at the top of the page
* Move to the previous image
  * Click the blue left arrow button at the top of the page
* Remove label
  * Click the red button on the label you would like to remove
  * **Click "Save"**, or changes will not write to the output csv file.
* Check generated data
  * At the top level of the directory where the program was run, there should be a file called `out.csv` that contains the generate data. Or if you have specified the `--out` parameter, the file should be there.
