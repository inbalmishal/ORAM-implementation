import json


class Bucket:
    def __init__(self, files, num_real_files):
        self.files = files
        self.num_real_files = num_real_files

    def __str__(self):
        files_str = [str(file) for file in self.files]
        json_string_files = json.dumps(files_str)
        full_string = "{real_files}{" + str(self.num_real_files) + "}"
        return full_string + json_string_files
