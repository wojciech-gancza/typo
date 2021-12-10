# (c) TYPO by WGan 2021


import datetime
import os
import re

from typo_base import typo_error, typo_generator, typo_converter


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

    def __init__(self, identifier):
        typo_error.__init__(self, "Identifier cannot start with digit but it is '" + identifier + "'")

""" problem with identifier - cannot start with digit """
class identifier_cannot_be_empty(typo_error):

    def __init__(self):
        typo_error.__init__(self, "Identifier cannot be empty")

""" formatter allowing change a multiword description into identifier """
class identifier_formatter:

    def __init__(self, identifier):
        identifier_text = str(identifier).strip()
        if identifier_text == "":
            raise identifier_cannot_be_empty()
        self.words = identifier_text.split()
        if self.words[0][0].isdigit():
            raise identifier_start_with_digit_error(identifier_text)
        for word in self.words:
            if not re.match("^[0-9_a-zA-Z]*$", word):
                raise identifier_non_alphanueric_error(word, identifier_text)

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
     

""" error - variable which need to contain path - is not defined """
class path_not_specified(typo_error):

    def __init__(self, path_name):
        typo_error.__init__(self, "Variable '" + path_name + "' is not defined but it should point to the directory.")
    
""" error - path is defined, but such path do not exist on disc """
class path_not_found(typo_error):
    
    def __init__(self, path_name, path):
        typo_error.__init__(self, "Path '" + path + "' in variable '" + path_name + "' does not exist.")
        
""" error - file name is not defined """
class file_name_is_not_defined(typo_error):

    def __init__(self, variable_name):
        typo_error.__init__(self, "Variable '" + variable_name + "' is not defined byt should contain valid file name.")

""" error - file name is malformed """
class malformed_file_name(typo_error):

    def __init__(self, variable_name, file_name):
        typo_error.__init__(self, "Value '" + file_name + "' in variable '" + variable_name + "' is wrong as a file name.")

""" error - value is required byt not supported """
class value_is_missing(typo_error):

    def __init__(self, variable_name):
        typo_error.__init__(self, "Variable '" + variable_name + "' is missing.")
     
""" error - value exists but it is not a good name for identifier """
class value_is_not_good_identifier(typo_error):

    def __init__(self, variable_name, value):
        typo_error.__init__(self, "Variable '" + variable_name + "' caontain value '" + value + "' which cannot be used as identifier.")


""" context reader contain few methods helping to read the context variables """
class context_reader:

    def __init__(self, context):
        self.context = context

    def get_path(self, path_name):
        value = self.context.get_value(path_name)
        if value is None:
            raise path_not_specified(path_name)
	    value = str(value)
        if not os.path.isdir(value):
            raise path_not_found(path_name, value)
        if value[-1] != "/":
            value += "/"
        return value

    def get_file_name(self, file_name_variable_name):
        value = self.context.get_value(file_name_variable_name)
        if value is None:
            raise file_name_is_not_defined(file_name_variable_name)
        value = str(value)
        if not re.match("^[_a-zA-Z][0-9_a-zA-Z.]*$", value):
            raise malformed_file_name(file_name_variable_name, value)
        return value   
    
    def get_value(self, value_name):
        value = self.context.get_value(value_name)
        if value is None:
            raise value_is_missing(value_name)
        return value
        
    def get_identifier(self, value_name, prefix = ""):
        value = self.get_value(value_name)
        if not re.match("[_a-zA-z][_a-zA-Z0-9]", value):
            raise value_is_not_good_identifier(value_name, value)
        return prefix + value
        

""" error when extracting user code """
class user_code_placeholder_error(typo_error):

    def __init__(self, message):
        typo_error.__init__(self, message)

""" Some function used to analyze value which might contain placeholders """
class placeholders_info:

    def __init__(self, line_text):
        self.line = line_text

    def is_just_placeholder(self):
        if re.match("^\\s*\$\{[a-zA-Z_][0-9a-zA-Z_.]*\}\\s*$", self.line):
            return True
        else:
            return False
               
    def is_user_code_placeholder(self):
        if re.match(".*\$\{user_code\}.*", self.line):
            if re.match("^\\s*\$\{user_code\}\\s*$", self.line):
                return True
            else:
                raise user_code_placeholder_error("User code placeholder must be the only one in the line.")
        else:
            return False

    def is_constant(self):
        if re.match("^.*\$\{[a-zA-Z_][0-9a-zA-Z_.]*\}.*$", self.line):
            return False
        else:
            return True
        
    def is_empty(self):
        if re.match("^\\s*$", self.line):
            return True
        else:
            return False
        
    def find_first_identifier(self):
        found = re.search("\$\{[a-zA-z][0-9_a-zA-z.]*\}", self.line)
        if not found:
            return None
        else:
            return (found.start()+2, found.end()-1)


""" generator returning timestamp """
class gen_timestamp(typo_generator):

    def generate(self, context, output):
        output.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))       
        
        
""" generator returning version of typo translator """
class gen_typo_version(typo_generator):

    def generate(self, context, output):
        output.write("1.00.Dev")
                
   
""" genertor of stored user code """
class gen_user_code(typo_generator):

    def generate(self, context, output):
        output.write_already_formatted(context.pop_user_code())
  
              
""" simple converters for use with identifiers """
class conv_CAPITALIZE_ALL(typo_converter):

    def convert(self, text):
        id = identifier_formatter(text)
        return id.CAPITALIZE_ALL()
        
class conv_lowercase_with_underscores(typo_converter):

    def convert(self, text):
        id = identifier_formatter(text)
        return id.lowercase_with_underscores()
        
class conv_UppercaseCamel(typo_converter):

    def convert(self, text):
        id = identifier_formatter(text)
        return id.UppercaseCamel()
        
class conv_lowercaseCamel(typo_converter):

    def convert(self, text):
        id = identifier_formatter(text)
        return id.lowercaseCamel()
