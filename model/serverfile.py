class ServerFile:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def __str__(self):
        return "{filename}" + self.filename + "{data}" + self.data
