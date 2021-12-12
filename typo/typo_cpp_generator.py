# (c) TYPO by WGan 2021


from typo_base import typo_generator, typo_converter
from typo_tools import context_reader, identifier_formatter


class cpp_info:

    def get_simple_types(self):
        return ["int", "unsigned", "double", "float", "byte", "char", "long", \
                "unsigned long", "unsigned long long", "long double", "int8_t", \
                "uint8_t", "int16_t", "uint16_t", "int32_t", "uint32_t", \
                "int64_t", "uint64_t", "int128_t", "uint128_t"]
                
    def get_float_types(self):
        return ["float", "double", "long double"]
        
    def is_simple_type(self, type_name):
        return type_name in self.get_simple_types()
        
    def is_float_type(self, type_name):
        return type_name in self.get_float_types()
        
    def get_default_value_of_simple_type(self, simple_type):
        if self.is_float_type(simple_type):
            return "0.0"
        elif self.is_simple_type(simple_type):
            return "0"
        else:
            return ""

class conv_add_reference(typo_converter):

    def convert(self, text):
        if cpp_info().is_simple_type(text):
            return text
        else:
            return "const " + text + " &"


class cpp_generator(typo_generator):

    def _set_context(self, context):
        self.reader = context_reader(context)

    def _get_class_name(self):
        return self.reader.get_identifier("type_name.UppercaseCamel")

    def _get_parameter_name(self):
        return self.reader.get_identifier("type_name.lowercaseCamel", "p_")

    def _get_member_name(self):
        return self.reader.get_identifier("type_name.lowercaseCamel", "m_")

    def _get_bare_type(self):
        return self.reader.get_value("base_type")

    def _get_decorated_type(self):
        return self.reader.get_value("base_type.add_reference")

    def _get_default_value(self):
        val = self.reader.context.get_value("default_value")
        if val is None:
            type_name = self._get_bare_type()
            val = cpp_info().get_default_value_of_simple_type(type_name)
        return str(val)
        
    def _get_value_range_assertion(self, value_name):
        min = self.reader.context.get_value("min_value")
        max = self.reader.context.get_value("max_value")
        if min is None and max is None:
            return None
        elif not (min is None) and not (max is None):
            return "assert(" + str(min) + " <= " + value_name + " && " + value_name + " >= " + str(max) + ")\n"
        elif not (min is None):
            return "assert(" + str(min) + " <= " + value_name + ")\n"
        else:
            return "assert(" + value_name + " >= " + str(max) + ")\n"          
        
    def _get_switch(self, switch_name, default_value):
        value = self.reader.context.get_value(switch_name)
        if value is None:
            value = default_value
        if value in (True, "T", "t", "Y", "y", "YES", "Yes", "yes"):
            return True
        elif value in (False, "F", "f", "N", "n", "NO", "No", "no", "", None):
            return False
        elif not value:
            return False
        else:
            return True
            
    def _get_list(self, variable_name):
        value = self.reader.context.get_value(variable_name)
        if type(value) is list:
            return value
        else:
            return [x.strip() for x in value.split(",")]


class gen_simple_type_copy_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_class_name() + "(const " + self._get_class_name() + " & " + self._get_parameter_name() + ")")
        if self._get_switch("allow_copy_constructor", True):
            output.write("\n")
            output.write(": " + self._get_member_name() + "(" + self._get_parameter_name() + "." + self._get_member_name() + ")\n")
            output.write("{  }\n")
        else:
            output.write(" delete; // allow_copy_constructor = False\n")

class gen_simple_type_assignment(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        class_name = self._get_class_name()
        parameter_name = self._get_parameter_name()
        output.write("const " + class_name + " & operator=(const " + class_name + " & " + parameter_name + ")")
        if self._get_switch("allow_assignment", True):
            member_name = self._get_member_name()
            output.write("\n{\n")
            output.increase_indent()
            output.write(self._get_member_name() + " = " + parameter_name + "." + member_name + ";\n")
            output.write("return *this;\n")
            output.decrease_indent()
            output.write("}\n")
        else:
            output.write(" delete; // allow_assignment = False\n")

class gen_simple_type_getter(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_getter", True):
            output.write(self._get_decorated_type() + " get" + self._get_class_name() + "() const\n{\n")
            output.increase_indent()
            output.write("return " + self._get_member_name() + ";\n")
            output.decrease_indent()
            output.write("}\n")
        else:
            output.write("// allow_getter = False\n")

class gen_simple_storage_item(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_bare_type() + " " + self._get_member_name() + ";\n")


class gen_numeric_type_default_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_class_name() + "()")
        if self._get_switch("allow_default_constructor", True):
            output.write("\n")
            output.write(": " + self._get_member_name() + "(" + self._get_default_value() + ")\n")
            output.write("{  }\n")
        else:
            output.write(" delete; // allow_default_constructor = False\n")

class gen_numeric_type_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_constructor", True):
            parameter_name = self._get_parameter_name()
            output.write("explicit " + self._get_class_name() + "(" + self._get_decorated_type() + " " + parameter_name + ")\n")
            output.write(": " + self._get_member_name() + "(" + parameter_name + ")\n")
            assertion = self._get_value_range_assertion(parameter_name)
            if not (assertion is None):
                output.write("{\n")
                output.increase_indent()
                output.write(assertion)
                output.decrease_indent()
                output.write("}\n")
            else:
                output.write("{  }\n")
        else:
            output.write("// allow_constructor = False\n")

class gen_numeric_type_setter(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_setter", True):
            output.write("void set" + self._get_class_name() + "(" + self._get_decorated_type() + " " + self._get_parameter_name() + ")\n{\n")
            output.increase_indent()
            parameter_name = self._get_parameter_name()
            assertion = self._get_value_range_assertion(parameter_name)
            if not (assertion is None):
                output.write(assertion)
            output.write(self._get_member_name() + " = " + parameter_name + ";\n")
            output.decrease_indent()
            output.write("}\n")
        else:
            output.write("// allow_setter = False\n")


class gen_string_type_default_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_class_name() + "()")
        if self._get_switch("allow_default_constructor", True):
            output.write("\n")
            output.write(": " + self._get_member_name() + "(" + self._get_default_value() + ")\n")
            output.write("{  }\n")
        else:
            output.write(" delete; // allow_default_constructor = False\n")

class gen_string_type_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_constructor", True):
            parameter_name = self._get_parameter_name()
            output.write("explicit " + self._get_class_name() + "(" + self._get_decorated_type() + " " + parameter_name + ")\n")
            output.write(": " + self._get_member_name() + "(" + parameter_name + ")\n")
            output.write("{\n")
            output.increase_indent()
            output.write("_check_value_assert(" + parameter_name + ");\n")
            output.decrease_indent()
            output.write("}\n")
        else:
            output.write("// allow_constructor = False\n")

class gen_string_type_setter(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_setter", True):
            output.write("void set" + self._get_class_name() + "(" + self._get_decorated_type() + " " + self._get_parameter_name() + ")\n{\n")
            output.increase_indent()
            parameter_name = self._get_parameter_name()
            output.write("_check_value_assert(" + parameter_name + ");\n")
            output.write(self._get_member_name() + " = " + parameter_name + ";\n")
            output.decrease_indent()
            output.write("}\n")
        else:
            output.write("// allow_setter = False\n")


class enumeration_values(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        values = self._get_list("enum_values")
        values = [identifier_formatter(value).CAPITALIZE_ALL() for value in values]
        max_length = 0
        hex_values = []
        enum_value = 1
        for value in values:
            if len(value) > max_length:
                max_length = len(value)
            hex_enum_value = hex(enum_value)
            hex_values.append(hex_enum_value)
            enum_value = enum_value * self.multiply_by + self.increment_by
            max_hex_length = len(hex_enum_value)
        lines = []
        for i in range(0, len(values)):
            value = values[i] + (" " * (max_length-len(values[i])))
            hex_value = hex_values[i]
            lines.append(value + " = " + hex_value[0:2] + ("0" * (max_hex_length-len(hex_value))) + hex_value[2:])
        values = lines    
        if values != []:
            for value in values[0:-1]:
                output.write(value + ",\n")
            output.write(values[-1] + "\n")            
      
      
class gen_enumerated_values(enumeration_values):

    def __init__(self):
        self.start_value = 0
        self.increment_by = 1
        self.multiply_by = 1
                
                
class gen_bit_values(enumeration_values):

    def __init__(self):
        self.start_value = 0
        self.increment_by = 0
        self.multiply_by = 2
                