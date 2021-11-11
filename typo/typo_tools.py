# (c) TYPO by WGan 2021



import re

from typo_core import typo_error



""" error of convertion of identifier - non alphanumeric character """
class identifier_non_alphanueric_error(typo_error):

    def __init__(self, word, whole_identifier):
        if word == whole_identifier:
            typo_error.__init__(self, "'" + whole_identifier + \
                    "' could not be an identifier because '" + word + \
                    "' contain non alphanumeric character")
        else:
            typo_error.__init__(self, "'" + whole_identifier + \
                    "' could not be an identifier because it contain non alphanumeric character")
        


""" problem with identifier - cannot start with digit """
class identifier_start_with_digit_error(typo_error):

    def __init(self, identifier):
        typo_error.__init__(self, "Identifier cannot start with digit but it is '" + whole_identifier + "'")



""" formatter allowing change a multiword description into identifier """
class identifier_formatter:

    def __init__(self, identifier):
        identifier_text = str(identifier)
        self.words = identifier_text.split()
        for word in self.words:
            if not re.match("[_a-zA-Z][0-9_a-zA-Z]", word):
                raise identifier_non_alphanueric_error(word, identifier_text)
        if self.words[0][0].isdigit():
            raise identifier_start_with_digit_error(identifier_text)

    def CAPITALIZE_ALL(self, prefix = "", suffix = ""):
        return prefix + "_".join([word.upper() for word in self.words]) + suffix
     
    def lowercase_with_underscores(self, prefix = "", suffix = ""):
        return prefix + "_".join([word.lower() for word in self.words]) + suffix
     
    def UppercaseCamel(self, prefix = "", suffix = ""):
        return prefix + "".join([word.capitalize() for word in self.words]) + suffix
     
    def lowercaseCamel(self, prefix = "", suffix = ""):
        return prefix  + self.words[0].lower() + "".join( \
                [self.words[i].capitalize() for i in range(1, len(self.words))] \
                ) + suffix
     
    
        