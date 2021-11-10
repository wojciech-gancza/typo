# (c) TYPO by WGan 2021



""" file content separated into lines """
class file_lines:

    def __init__(self, file_name):
        try:
            file = open(file_name)
            self.lines = file.readlines()
            file.close()
        except:
            self.lines = [ ]
