# (c) TYPO by WGan 2021


class test_class_2:

    def get(self):
        return "result 2"
        

class gen_another_part_of_code:

    def generate(self, context, output):
        value = context.get_value("value")
        output.write("value is: '" + value + "'")
