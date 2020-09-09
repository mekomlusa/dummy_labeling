import os
import argparse
import ujson
import pandas as pd
from PIL import Image

def convert_outputs_to_detectron2_format(output_csv, dir_base_path):
  out_json = {}
  index = 0

  id_cat_dict = output_csv['name'].drop_duplicates().reset_index(drop=True).to_dict()
  category_dict = {v:k for k,v in id_cat_dict.items()}

  for k in output_csv['image'].drop_duplicates().reset_index(drop=True):
    out_json[k] = out_json.get(k, {})
    out_json[k]['file_name'] = k

    image = Image.open(os.path.join(dir_base_path, k))
    width, height = image.size
    out_json[k]['width'] = width
    out_json[k]['height'] = height

    annotation_list = []
    all_bb_boxes = output_csv[output_csv['image'] == k]
    for index, row in all_bb_boxes.iterrows():
      this_annotation = {}
      this_annotation['bbox'] = row[['xMin', 'yMin', 'xMax', 'yMax']].tolist()
      this_annotation['bbox_mode'] = 0 # abs position, see https://detectron2.readthedocs.io/modules/structures.html#detectron2.structures.BoxMode
      this_annotation['category_id'] = category_dict[row['name']]
      this_annotation['category_name'] = row['name']
      annotation_list.append(this_annotation)

    out_json[k]['annotations'] = annotation_list
    out_json[k]['image_id'] = index
    index += 1

  return out_json #list(out_json.values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='specify the images directory', required=True)
    parser.add_argument('--labels', help='results from the labeling tool')
    parser.add_argument("--out")
    args = parser.parse_args()

    label_csv_file = pd.read_csv(args.labels)
    converted_res_list = convert_outputs_to_detectron2_format(label_csv_file, args.dir)

    output_filename = "detectron_converted.json" if args.out is None else args.out
    with open(output_filename, 'w') as fp:
        ujson.dump(converted_res_list, fp, indent=4)
    print("Converted json has been saved as {}.".format(output_filename))