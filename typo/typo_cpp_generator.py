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
        return self.reader.get_identifier("class_name")

    def _get_parameter_name(self):
        return self.reader.get_identifier("parameter_name")

    def _get_member_name(self):
        return self.reader.get_identifier("member_name")

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
            return "assert(" + str(min) + " <= " + value_name + " && " + value_name + " >= " + str(max) + ");\n"
        elif not (min is None):
            return "assert(" + str(min) + " <= " + value_name + ");\n"
        else:
            return "assert(" + value_name + " >= " + str(max) + ");\n"          
        
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
        
    def _get_enum_values(self):        
        values = self._get_list("enum_values")
        return [identifier_formatter(value).CAPITALIZE_ALL() for value in values]  
        
    def _get_bitset_base_type(self):
        values = self._get_enum_values()
        values_count = len(values)
        if values_count <= 8:
            return "uint8_t"
        elif values_count <= 16:
            return "uint16_t"
        elif values_count <= 16:
            return "uint16_t"
        elif values_count <= 32:
            return "uint32_t"
        elif values_count <= 64:
            return "uint64_t"
        else:
            return "uint128_t"
    
    def _get_max_bitset_value(self):
        values = self._get_enum_values()
        values_count = len(values)
        return hex(2**values_count - 1)
        

class cpp_enum_generator(cpp_generator):

    def _generate_code(self, parameter_name, values, output):
        if len(values) == 1:
            output.write("return " + self._create_return_value(values[0]) + ";\n")
            return
        min_length = self._get_minimum_length(values)
        char_maps = [ ]
        for char_position in range(0, min_length):
            char_maps.append(self._generate_single_char_map(values, char_position))
        switch_map_index = self._get_best_switch_map(char_maps)
        switch_map = char_maps[switch_map_index]
        if len(switch_map) == 1:
            self._generate_if(parameter_name, min_length, switch_map.values()[0], output)
        else:
            self._generate_switch(parameter_name, switch_map_index, switch_map, output) 

    def _generate_if(self, parameter_name, min_length, values, output):
        output.write("if (" + parameter_name + ".size() == " + str(min_length) + ")\n{\n")
        values.sort()
        output.increase_indent()
        output.write("return " + self._create_return_value(values[0]) + ";\n")
        output.decrease_indent()
        output.write("}\nelse\n{\n")
        output.increase_indent()
        self._generate_code(parameter_name, values[1:], output)
        output.decrease_indent()
        output.write("}\n")

    def _generate_switch(self, parameter_name, switch_map_index, switch_map, output):
        class_name = self._get_class_name()
        output.write("switch(" + parameter_name + "[" + str(switch_map_index) + "])\n{\n")
        keys = switch_map.keys()
        keys.sort()
        for key in keys:
            if key == keys[-1]:
                output.write("default:\n")
            else:
                output.write("case '" + key + "':\n") 
            case_values = switch_map[key]
            output.increase_indent()
            if len(case_values) == 1:
                output.write("return " + self._create_return_value(case_values[0]) + ";\n")
            else:
                self._generate_code(parameter_name, case_values, output)
            output.decrease_indent()
        output.write("}\n")
    
    def _get_minimum_length(self, values):
        min_length = len(values[0])
        for value in values[1:]:
            value_length = len(value)
            if value_length < min_length:
                min_length = value_length
        return min_length
        
    def _generate_single_char_map(self, values, char_position):
        result_map = { }
        for value in values:
            char = value[char_position]
            if char in result_map.keys():
                result_map[char].append(value)
            else:
                result_map[char] = [ value ]
        return result_map
        
    def _get_best_switch_map(self, char_maps):
        longest_map_size = 0
        longest_map_position = 0
        for char_map_position in range(0, len(char_maps)):
            char_map = char_maps[char_map_position]
            char_map_size = len(char_map)
            if char_map_size > longest_map_size:
                longest_map_position = char_map_position
                longest_map_size = char_map_size
        return longest_map_position
        
    def _create_return_value(self, text):
        pass

class type_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_constructor", True):
            self.generate_constructor(output)
        else:
            output.write("// allow_constructor = False\n")

class type_getter(cpp_generator):

    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_getter", True):
            self.generate_getter(output)
        else:
            output.write("// allow_getter = False\n")

class type_setter(cpp_generator):

    def generate(self, context, output):
        self._set_context(context)
        if self._get_switch("allow_setter", True):
            self.generate_setter(output)
        else:
            output.write("// allow_setter = False\n")


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

class gen_simple_type_getter(type_getter):
    
    def generate_getter(self, output):
        output.write(self._get_decorated_type() + " get" + self._get_class_name() + "() const\n{\n")
        output.increase_indent()
        output.write("return " + self._get_member_name() + ";\n")
        output.decrease_indent()
        output.write("}\n")

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

class gen_numeric_type_constructor(type_constructor):
    
    def generate_constructor(self, output):
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

class gen_numeric_type_setter(type_setter):
    
    def generate_setter(self, output):
        output.write("void set" + self._get_class_name() + "(" + self._get_decorated_type() + " " + self._get_parameter_name() + ")\n{\n")
        output.increase_indent()
        parameter_name = self._get_parameter_name()
        assertion = self._get_value_range_assertion(parameter_name)
        if not (assertion is None):
            output.write(assertion)
        output.write(self._get_member_name() + " = " + parameter_name + ";\n")
        output.decrease_indent()
        output.write("}\n")


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

class gen_string_type_constructor(type_constructor):
    
    def generate_constructor(self, output):
        parameter_name = self._get_parameter_name()
        output.write("explicit " + self._get_class_name() + "(" + self._get_decorated_type() + " " + parameter_name + ")\n")
        output.write(": " + self._get_member_name() + "(" + parameter_name + ")\n")
        output.write("{\n")
        output.increase_indent()
        output.write("_check_value_assert(" + parameter_name + ");\n")
        output.decrease_indent()
        output.write("}\n")

class gen_string_type_setter(type_setter):
    
    def generate_setter(self, output):
        output.write("void set" + self._get_class_name() + "(" + self._get_decorated_type() + " " + self._get_parameter_name() + ")\n{\n")
        output.increase_indent()
        parameter_name = self._get_parameter_name()
        output.write("_check_value_assert(" + parameter_name + ");\n")
        output.write(self._get_member_name() + " = " + parameter_name + ";\n")
        output.decrease_indent()
        output.write("}\n")


class enumeration_values(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        values = self._get_enum_values()
        max_length = 0
        hex_values = []
        enum_value = self.start_value
        for value in values:
            if len(value) > max_length:
                max_length = len(value)
            hex_enum_value = hex(enum_value)
            hex_values.append(hex_enum_value)
            max_hex_length = len(hex_enum_value)
            enum_value = enum_value * self.multiply_by + self.increment_by
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
        
class gen_enumerated_type_default_constructor(cpp_generator):

    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_class_name() + "()")
        if self._get_switch("allow_default_constructor", True):
            output.write("\n")
            first_value = self._get_enum_values()[0]
            output.write(": " + self._get_member_name() + "(" + first_value + ")\n")
            output.write("{  }\n")
        else:
            output.write(" delete; // allow_default_constructor = False\n")
 
class gen_enumerated_type_constructor(type_constructor):

    def generate_constructor(self, output):
        class_name = self._get_class_name()
        parameter_name = self._get_parameter_name()
        output.write("explicit " + class_name + "(" + class_name + "::value_type " + parameter_name + ")\n")
        output.write(": " + self._get_member_name() + "(" + parameter_name + ")\n")
        output.write("{  }\n")

class gen_enumerated_type_getter(type_getter):

    def generate_getter(self, output):
        class_name = self._get_class_name()
        parameter_name = self._get_parameter_name()
        output.write("void set" + class_name + "(" + class_name + "::value_type " + parameter_name + ")\n{\n")
        output.increase_indent()
        output.write(self._get_member_name() + " = " + parameter_name + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_enumerated_type_setter(type_setter):

    def generate_setter(self, output):
        class_name = self._get_class_name()
        output.write(class_name + "::value_type get" + class_name + "()\n{\n")
        output.increase_indent()
        output.write("return " + self._get_member_name() + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_enum_string_values(cpp_generator):

    def generate(self, context, output):
        self._set_context(context)
        values = self._get_enum_values()
        for value in values[0:-1]:
            output.write("\"" + value + "\",\n")
        output.write("\"" + values[-1] + "\"")
                                 
class gen_enum_from_string_converter_code(cpp_enum_generator):
                
    def generate(self, context, output):
        self._set_context(context)
        values = self._get_enum_values()
        self._generate_code(self._get_parameter_name(), values, output)

    def _create_return_value(self, text):
        return self._get_class_name() + "(" + text + ")"

        
class gen_bit_values(enumeration_values):

    def __init__(self):
        self.start_value = 1
        self.increment_by = 0
        self.multiply_by = 2
 
class gen_bitset_type_default_constructor(cpp_generator):

    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_class_name() + "()")
        if self._get_switch("allow_constructor", True):
            output.write("\n")
            output.write(": " + self._get_member_name() + "(0)\n")
            output.write("{  }\n")
        else:
            output.write(" delete; // allow_constructor = False\n")

class gen_bitset_type_constructor(type_constructor):

    def generate_constructor(self, output):
        parameter_name = self._get_parameter_name()
        output.write("explicit " + self._get_class_name() + "(" + self._get_bitset_base_type() + " " + parameter_name + ")\n")
        output.write(": " + self._get_member_name() + "(" + parameter_name + ")\n")
        output.write("{\n")
        output.increase_indent()
        output.write("assert(" + self._get_parameter_name() + " <= " + self._get_max_bitset_value() + ");\n")
        output.write(self._get_member_name() + " = " + parameter_name + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_bitset_type_setter(type_getter):

    def generate_getter(self, output):
        class_name = self._get_class_name()
        parameter_name = self._get_parameter_name()
        output.write("void set" + class_name + "(" + self._get_bitset_base_type() + " " + parameter_name + ")\n{\n")
        output.increase_indent()
        output.write("assert(" + self._get_parameter_name() + " <= " + self._get_max_bitset_value() + ");\n")
        output.write(self._get_member_name() + " = " + parameter_name + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_bitset_type_getter(type_setter):

    def generate_setter(self, output):
        output.write(self._get_bitset_base_type() + " get" + self._get_class_name() + "()\n{\n")
        output.increase_indent()
        output.write("return " + self._get_member_name() + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_bitset_storage_item(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_bitset_base_type() + " " + self._get_member_name() + ";\n")

class gen_bitset_carrier_type(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_bitset_base_type())

class gen_bit_from_string_converter_code(cpp_enum_generator):
            
    def generate(self, context, output):
        self._set_context(context)
        values = self._get_enum_values()
        self._generate_code("bit_name", values, output)

    def _create_return_value(self, text):
        return text


