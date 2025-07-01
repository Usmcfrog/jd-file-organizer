import os
import json

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "folder"
        d['children'] = [path_to_dict(os.path.join(path, item)) for item in os.listdir(path)]
    else:
        d['type'] = "file"
    return d

# Replace "your_folder_path" with the path to the folder you want to represent
folder_path = "F:\Organized Cabinet"  # Replace with the actual path

json_output = json.dumps(path_to_dict(folder_path), indent=2)

with open("folder_structure.json", "w") as json_file:
    json_file.write(json_output)
