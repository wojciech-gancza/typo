# (c) TYPO by WGan 2021


from typo_tools         import  identifier_formatter       
from typo_core          import  typo_generator                         



class gen_simple_type_constructor(typo_generator):

    def generate(self, context, output):
        class_name = context.get_value("class_name")
        base_type = context.get_value("class_name")
        identifier = identifier_formatter(class_name)
        output.write(identifier.UppercaseCamel() + "(" + base_type + " " + identifier.lowercaseCamel("", "_param") + ")\n")
        output.write("{\n")
        output.increase_indent()
        output.write(identifier.lowercaseCamel() + " = " + identifier.lowercaseCamel("","_param") + "\n")
        output.decrease_indent()
        output.write("}\n")



class gen_simple_type_setter_and_getter(typo_generator):

    def generate(self, context, output):
        class_name = context.get_value("class_name")
        base_type = context.get_value("class_name")
        identifier = identifier_formatter(class_name)
        output.write("void get" + identifier.UppercaseCamel() + "(" + base_type + " " + identifier.lowercaseCamel("", "_param") + ")\n")
        output.write("{\n")
        output.increase_indent()
        output.write(identifier.lowercaseCamel() + " = " + identifier.lowercaseCamel("","_param") + "\n")
        output.decrease_indent()
        output.write("}\n")
        