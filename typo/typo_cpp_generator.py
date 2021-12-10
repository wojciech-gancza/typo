# (c) TYPO by WGan 2021


from typo_base import typo_generator, typo_converter
from typo_tools import context_reader


class cpp_converter(typo_converter):

    def _is_simple_type(self, type):
        if type in ["int", "unsigned", "double", "float", "byte", "char", "long"]:
            return True
        else:
            return False


class conv_add_reference(cpp_converter):

    def convert(self, text):
        if self._is_simple_type(text):
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
            val = ""
        return val


class gen_simple_type_default_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_class_name() + "()\n")
        output.write(": " + self._get_member_name() + "(" + self._get_default_value() + ")\n")
        output.write("{  }\n")

class gen_simple_type_constructor(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write("explicit " + self._get_class_name() + "(" + self._get_decorated_type() + " " + self._get_parameter_name() + ")\n")
        output.write(": " + self._get_member_name() + "(" + self._get_parameter_name() + ")\n")
        output.write("{  }\n")

class gen_simple_type_getter(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_decorated_type() + " get" + self._get_class_name() + "() const\n{\n")
        output.increase_indent()
        output.write("return " + self._get_member_name() + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_simple_type_setter(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write("void set" + self._get_class_name() + "(" + self._get_decorated_type() + " " + self._get_parameter_name() + ")\n{\n")
        output.increase_indent()
        output.write(self._get_member_name() + " = " + self._get_parameter_name() + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_simple_type_assignment(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        class_name = self._get_class_name()
        parameter_name = self._get_parameter_name()
        member_name = self._get_member_name()
        output.write("const " + class_name + " & operator=(const " + class_name + " & " + parameter_name + ")\n{\n")
        output.increase_indent()
        output.write(self._get_member_name() + " = " + parameter_name + "." + member_name + ";\n")
        output.decrease_indent()
        output.write("}\n")

class gen_storage_item(cpp_generator):
    
    def generate(self, context, output):
        self._set_context(context)
        output.write(self._get_bare_type() + " " + self._get_member_name() + ";\n")
