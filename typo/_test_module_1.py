# (c) TYPO by WGan 2021


from typo_base import typo_generator


class test_class_1:

    def get(self):
        return "result 1"
        
        
class gen_test_generator(typo_generator):

    def generate(self, context, output):
        output.write("constructor(parameters)\n{\n")
        output.increase_indent()
        output.write("// indented text\n// multiline\n")
        output.decrease_indent()
        output.write("}")
        
