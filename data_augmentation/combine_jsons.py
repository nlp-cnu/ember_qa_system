import argparse
import json
import os

#function to combine a directory of json files into a single json file
def combine_files(dir_of_files, output_file):
    # get all files in dir
    files = os.listdir(dir_of_files)

    # read each json file
    combined = []
    for file_name in files:
        if file_name[-5:] == '.json':
            with open(os.path.join(dir_of_files,file_name), 'r') as f:
                data=json.loads(f.read())
                combined.extend(data["questions"])

    # output the combined file
    with open(output_file, 'w') as out:
        json.dump(combined, out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_jsons_dir", help="The filepath to directory containing .json files")
    parser.add_argument("output_path", help="The filepath to output the combined json file to") 

    args = parser.parse_args()
    path_to_json = args.path_to_jsons_dir
    output_path = args.output_path

    combine_files(path_to_json, output_path)
