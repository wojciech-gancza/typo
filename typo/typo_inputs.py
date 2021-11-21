# (c) TYPO by WGan 2021


""" file content separated into lines """
class file_lines(list):

    def __init__(self, file_name):
        try:
            file = open(file_name)
            for line in file.readlines():
                self.append(line)
            file.close()
        except:
            pass
