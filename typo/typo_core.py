# (c) TYPO by WGan 2021


from typo_base import typo_error
from typo_tools import placeholders_info, gen_timestamp, gen_typo_version, \
    gen_user_code, conv_CAPITALIZE_ALL, conv_lowercase_with_underscores, \
    conv_UppercaseCamel, conv_lowercaseCamel


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
        except Exception as err:
            pass
        for loaded_module in self.modules:
            try:    
                return eval("loaded_module." + class_name + "()")
            except:
                pass
        return None
      
    def _get_value(self, name):
        converter = None
        value = self.get_not_interpreted_value(name)
        if value is None:
            stripped_name, converter = self._strip_and_get_converter(name)
            value = self.get_not_interpreted_value(stripped_name)
            if value is None:
                return None
        translated_value = self._translate_value(value)
        if not(converter is None):
            translated_value = converter.convert(translated_value)
        return translated_value    
            
    def _translate_value(self, value):
        if isinstance(value, str):
            return self._translate_text(value)
        if isinstance(value, list):
            return [ self._translate_value(text) for text in value]
        else:
            return value
        
    def _strip_and_get_converter(self, name):
        split_on = name.rfind(".")
        bare_name = name[0:split_on]
        converter_name = name[split_on+1:]
        converter = self.create_object("conv_" + converter_name)
        if converter:
            return bare_name, converter
        else:
            return name, None
        
    def _translate_text(self, text):
        line = placeholders_info(text)
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
  