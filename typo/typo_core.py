# (c) TYPO by WGan 2021



import datetime
import re
import os.path


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
        
        
        
""" generator returning timestamp """
class gen_timestamp(typo_generator):

    def generate(self, context, output):
        output.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
       
        
        
""" generator returning version of typo translator """
class gen_typo_version(typo_generator):

    def generate(self, context, output):
        output.write("0.1 Dev")
        
        
   
""" genertor of stored user code """
class gen_user_code(typo_generator):

    def generate(self, context, output):
        output.write_already_formatted(context.pop_user_code())
        
        

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

""" error - desired module was not loaded """
class module_not_loaded(typo_error):

    def __init__(self, module_name):
        typo_error.__init__(self, "Module '" + module_name + "' cannot be loaded.")        



""" context - all settings are defined here """
class typo_context:

    def __init__(self):
        self.values = { }
        self.user_code = [ ]
        self.modules = [ ]
        
    def set_value(self, name, value):
        self.values[name] = value
        
    def get_not_interpreted_value(self, name):
        if name in self.values.keys():
            return self.values[name]
        else:
            return None
            
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
    
    def import_module(self, module_name):
        try:
            self.modules.append(__import__(module_name))
        except:
            raise module_not_loaded(module_name)        
          
    def create_object(self, class_name):
        try:
            return eval(class_name + "()")
        except:
            pass
        for loaded_module in self.modules:
            try:    
                return eval("loaded_module." + class_name + "()")
            except:
                pass
        return None
      
    def _get_value(self, name):
        value = self.get_not_interpreted_value(name)
        translated_value = self._translate_value(value)
        return translated_value    
            
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



""" error - variable which need to contain path - is not defined """
class path_not_secified(typo_error):

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

    def __init(self, variable_name, file_name):
        typo_error.__init__(self, "Value '" + file_name + "' or variable '" + variable_name + "' is wrong as a file name.")

""" context reader contain few methods helping to read the context variables """
class context_reader:

    def __init__(self, context):
        self.context = context

    def get_path(self, path_name):
        value = self.context.get_value(path_name)
        if value is None:
            raise path_not_secified(path_name)
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
        if not re.match("[_a-zA-Z][0-9_a-zA-Z.]*", value):
            raise malformed_file_name(file_name_variable_name, value)
        return value


