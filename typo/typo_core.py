# (c) TYPO by WGan 2021



import datetime
import re

from typo_outputs  import  string_output, file_output, indented_output
from typo_inputs   import  file_lines



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
        
        
        
""" Some function used to analyze template line """
class template_line:

    def __init__(self, line_text):
        self.line = line_text

    def is_just_placeholder(self):
        if re.match("^\\s*\$\{[a-zA-Z_][0-9a-zA-Z_]*\}\\s*$", self.line):
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
        if re.match("^.*\$\{[a-zA-Z_][0-9a-zA-Z_]*\}.*$", self.line):
            return False
        else:
            return True
        
    def is_empty(self):
        if re.match("^\\s*$", self.line):
            return True
        else:
            return False
        
    def find_first_identifier(self):
        found = re.search("\$\{[a-zA-z][0-9_a-zA-z]*\}", self.line)
        if not found:
            return None
        else:
            return (found.start()+2, found.end()-1)



""" error - identifier not found when tranlating value """
class identifier_not_found(typo_error):

    def __init__(self, symbol):
        typo_error.__init__(self, "Variable '" + symbol + "' not found in context")
        self.symbol = symbol
        
    def set_name(self, name):
        self.text = "Value of '" + self.symbol + "' not found during resolving value '" + name + "'."



""" error of resolving variables - cycle was found """
class loop_error_when_resolving(typo_error):
 
    def __init__(self, name):
        typo_error.__init__(self, "Cycle found when resolving value of '" + name + "'")



""" context - all settings are defined here """
class typo_context:

    def __init__(self):
        self.values = { }
        self.user_code = [ ]
        
    def set_value(self, name, value):
        self.values[name] = value
        
    def get_not_interpreted_value(self, name):
        if name in self.values.keys():
            return self.values[name]
        else:
            return None
            
    def _get_value(self, name):
        value = self.get_not_interpreted_value(name)
        translated_value = self._translate_value(value)
        return translated_value    
            
    def get_value(self, name):
        try:
            return self._get_value(name)
        except identifier_not_found as err:
            err.set_name(name)
            raise err
        except RuntimeError:
            raise loop_error_when_resolving(name)

    def pop_user_code(self):
        if self.user_code == [ ]:
            return ""
        else:
            value = self.user_code[0]
            self.user_code.pop(0)
            return value
    
    def _translate_value(self, value):
        if isinstance(value, str):
            return self._translate_text(value)
        if isinstance(value, list):
            return [ self._translate_value(text) for text in value]
        else:
            return value
        
    def _translate_text(self, text):
        line = template_line(text)
        if line.is_constant():
            return text
        start, end = line.find_first_identifier()
        identifier_name = text[start:end]
        value = self._get_value(identifier_name)
        if value is None:
            raise identifier_not_found(identifier_name)
        before = text[:start-2]
        after = text[end+1:]
        if before != "" or after != "":
            value = before + str(value) + after
        return self._translate_value(value)
