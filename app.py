import sys
from os import walk
import os
import imghdr
import csv
import argparse
import ujson

from flask import Flask, redirect, url_for, request, flash
from flask import render_template
from flask import send_file
import pandas as pd
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('bye'))
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]

    if not app.config["EDITING"]:
        labels = render_saved_labels(app.config['SELECTED_LABEL_ENGINE'])
        app.config["LABELS"] = labels
        # if len(render_saved_labels('confirmed')) == 0:
        #     app.config["LABELS"] = labels
        # else:
        #     #app.config['SELECTED_LABEL_ENGINE'] = 'confirmed'
        #     app.config["LABELS"] = render_saved_labels('confirmed')
    else:
        #app.config['SELECTED_LABEL_ENGINE'] = 'confirmed'
        labels = app.config["LABELS"]

    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_start = not (app.config["HEAD"] == 0)
    grount_truth_label = app.config["IMAGE_SETTINGS"]['ground_truth'][image]
    available_labels = set(app.config["IMAGE_SETTINGS"].keys())
    available_labels.remove('ground_truth')
    available_labels.add('confirmed')

    already_has_labels = len(labels) > 0
    return render_template('tagger.html', not_end=not_end, has_label=already_has_labels, 
        not_start=not_start, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, 
        len=len(app.config["FILES"]), gt_label=grount_truth_label, preset_labels=available_labels,
        selected_label_method=app.config['SELECTED_LABEL_ENGINE'])

@app.route('/next')
def next():
    # load next image & existing labels
    app.config["HEAD"] = app.config["HEAD"] + 1
    return redirect(url_for('tagger'))

@app.route('/prev')
def prev():
    app.config["HEAD"] = app.config["HEAD"] - 1
    return redirect(url_for('tagger'))

# newly saved route
@app.route('/savenew')
def savenew():
    image = app.config["FILES"][app.config["HEAD"]]
    if len(app.config["LABELS"]) > 0:
        with open(app.config["OUT"], 'a') as f: # normal cases
            for label in app.config["LABELS"]:
                f.write(image + "," +
                        label["id"] + "," +
                        label["name"] + "," +
                        str(round(float(label["xMin"]))) + "," +
                        str(round(float(label["xMax"]))) + "," +
                        str(round(float(label["yMin"]))) + "," +
                        str(round(float(label["yMax"]))) + "\n")
    else: # remove all
        saved_output = pd.read_csv(app.config["OUT"])
        labels_without_this_image = saved_output[saved_output['image'] != image]
        labels_without_this_image = labels_without_this_image.reset_index(drop=True)
        labels_without_this_image.to_csv(app.config["OUT"], index=False)

    if app.config['SELECTED_LABEL_ENGINE'] != 'confirmed':
        flash('Changes saved. Switch to the "confirmed" option to see saved labels.', 'success')
    else:
        flash('Saved successfully!', 'success')

    app.config["EDITING"] = False

    return redirect(url_for('tagger'))

# modify labels route
@app.route('/modify')
def modify():
    image = app.config["FILES"][app.config["HEAD"]]
    saved_output = pd.read_csv(app.config["OUT"])
    labels_without_this_image = saved_output[saved_output['image'] != image].copy(deep=True)
    labels_without_this_image = labels_without_this_image.reset_index(drop=True)

    current_df_len = len(labels_without_this_image) + 1
    for i in range(len(app.config["LABELS"])):
        labels_without_this_image.loc[current_df_len + i] = [image] + list(app.config["LABELS"][i].values())

    labels_without_this_image.to_csv(app.config["OUT"], index=False)

    if app.config['SELECTED_LABEL_ENGINE'] != 'confirmed':
        flash('Changes saved. Switch to the "confirmed" option to see saved labels.', 'success')
    else:
        flash('Saved successfully!', 'success')

    app.config["EDITING"] = False

    return redirect(url_for('tagger'))

@app.route("/selected_label_method", methods=['POST', 'GET'])
def selected_label_method():
    if request.method == "POST":            
        selected_val = request.form['labelset']
    
    app.config['SELECTED_LABEL_ENGINE'] = selected_val

    return redirect(url_for('tagger'))

@app.route('/add/<id>')
def add(id):
    app.config["EDITING"] = True
    if app.config['SELECTED_LABEL_ENGINE'] != 'confirmed':
        flash('Sorry, you are not allowed to draw new bounding boxes in this mode.', 'warning')
        return redirect(url_for('tagger'))

    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    app.config["EDITING"] = True
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]: # reindex for display
        label["id"] = str(int(label["id"]) - 1)
    print(app.config["LABELS"])
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    app.config["EDITING"] = True
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    return send_file(images + f)

@app.route('/clearall')
def clearall():
    app.config["LABELS"] = []

    image = app.config["FILES"][app.config["HEAD"]]
    saved_output = pd.read_csv(app.config["OUT"])

    if image in saved_output['image'].values:
        labels_without_this_image = saved_output[saved_output['image'] != image]
        labels_without_this_image = labels_without_this_image.reset_index(drop=True)
        labels_without_this_image.to_csv(app.config["OUT"], index=False)
        flash('Cleared all successfully!', 'success')
        #app.config["EDITING"] = False

    return redirect(url_for('tagger'))

# non app route methods
def read_pre_label_files(config_path):
    '''
    Read configuration file in. It is expected to be similar to `sample_config.txt`. 
    Note that "ground_truth" is a reserved keyword in the config file.
    '''
    res_dict = {}

    assert (os.path.isfile(config_path)), 'ERROR: config file not found.'

    with open(config_path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            key, val = line.split(',')
            res_dict[key] = val

    return res_dict

def render_saved_labels(choice):
    """
    Render saved labels from json/csv as per choice indicated. Choice will be the keys from the config file.
    """
    image = app.config["FILES"][app.config["HEAD"]]
    saved_labels_list = []

    if choice == 'confirmed':
        saved_output = pd.read_csv(app.config["OUT"])
        past_labels = saved_output[saved_output['image'] == image]
        if len(past_labels) > 0:
            past_labels = past_labels.sort_values(by=['id', 'image'], ascending=[True, False])
            for _, row in past_labels.iterrows():
                saved_labels_list.append({"id": str(row['id']), "name": str(row['name']), "xMin": str(row['xMin']),
                                            "xMax": str(row['xMax']), "yMin": str(row['yMin']), "yMax": str(row['yMax'])})
    else: # tested for tf-hub OD API output. See accompanied notebook for more info. Adapted for your case.
        preset_labels = app.config["IMAGE_SETTINGS"][choice]
        if image in preset_labels:
            past_labels = preset_labels[image]
            for i in range(len(past_labels['detection_class_entities'])):
                xMin = str(past_labels['detection_boxes'][i][1] * past_labels['image_size'][0])
                xMax = str(past_labels['detection_boxes'][i][3] * past_labels['image_size'][0]) 
                yMin = str(past_labels['detection_boxes'][i][0] * past_labels['image_size'][1]) 
                yMax = str(past_labels['detection_boxes'][i][2] * past_labels['image_size'][1])
                saved_labels_list.append({"id": str(i+1), "name": past_labels['detection_class_entities'][i], "xMin": xMin,
                                            "xMax": xMax, "yMin": yMin, "yMax": yMax})
    return saved_labels_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='specify the images directory', required=True)
    parser.add_argument('--config', help='config text file - see README for details')
    parser.add_argument("--out")
    args = parser.parse_args()

    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.config["FILES"] = []
    app.config["EDITING"] = False

    directory = args.dir
    if directory[len(directory) - 1] != "/":
            directory += "/"
    app.config["IMAGES"] = directory

    files = []
    acceptable_file_extensions = ['.png', '.jpg', '.gif', '.jpeg']
    for (dirpath, dirnames, filenames) in walk(app.config["IMAGES"]):
        for f in filenames:
            if os.path.splitext(f)[1] in acceptable_file_extensions:
                files.append(f)
        break
    if files == None:
        print("Error: No files. Exiting.")
        exit()
    app.config["FILES"] = files

    config_setting = read_pre_label_files(args.config)
    inflated_configs = {} # expand config setting

    for key, val in config_setting.items():
        if key == 'ground_truth': # reserved keyword
            with open(config_setting[key], mode='r') as infile:
                reader = csv.reader(infile)
                ground_truth_labels_dict = {rows[0]:rows[1] for rows in reader}
            inflated_configs[key] = ground_truth_labels_dict
        else: # everything else is expected to be json
            with open(config_setting[key], 'r') as fp:
                inflated_configs[key] = ujson.loads(fp.read()) 
            # temp_df = pd.read_csv(config_setting[key]) # old df setting
            # inflated_configs[key] = temp_df
    
    app.config["IMAGE_SETTINGS"] = inflated_configs
    app.config['SELECTED_LABEL_ENGINE'] = 'confirmed'
    
    if args.out == None:
        app.config["OUT"] = "out.csv"
    else:
        app.config["OUT"] = args.out

    if not os.path.exists(app.config["OUT"]):
        with open(app.config["OUT"],'w') as f:
            f.write("image,id,name,xMin,xMax,yMin,yMax\n")

    app.run(debug="True")
