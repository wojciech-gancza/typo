# (c) TYPO by WGan 2021


""" common error for all typo errors which should be reported to the user """
class typo_error(Exception):

    def __init__(self, message):
        self.text = message
        self.source = ""
        self.line = 0
        
    def __str__(self):
        text = self.text
        if self.source != "":
            text += " Found in '" + self.source + "'"
            if self.line != 0:
                text += " in line " + str(self.line)
            text += "."
        return text
    

""" base class of generators generating code """
class typo_generator:

    def generate(self, context, output):
        pass
        
               
""" bas class of converters """
class typo_converter:

    def convert(self, text):
        pass
                     
