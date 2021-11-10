# (c) TYPO by WGan 2021


import re

from typo_outputs       import  indented_output, console_output, string_output, \
                                file_output
from typo_inputs        import  file_lines
from typo_core          import  typo_context, template_line, \
                                typo_error, typo_generator                         
from typo_interpreter   import  output_file_generator
from typo_tools         import  identifier_formatter       
    
    

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



try:
    typo = output_file_generator(typo_context())
    typo.context.set_value("copyright", "WGan softerware")
    typo.context.set_value("class_name", "some strange name of a class")
    typo.context.set_value("base_type", "long")
    typo.build_source_code("_dev/templates/simple_type.template", "_dev/tests/outputs/default_output.txt")
except typo_error as err:
    print("ERROR: " + str(err))



#test of context
ctx = typo_context()
ctx.set_value("x", [ "${a}", "${b}"])
ctx.set_value("a", [ 1, 2, 3])
ctx.set_value("b", {"a":1, "b":2})
val = ctx.get_value("x")
print(val)
print(type(val).__name__)

ctx.set_value("y", [ "${a}", "${z}"])
ctx.set_value("z", [ "${a}", "${d}"])
try:
    val = ctx.get_value("y")
    print(val)
except typo_error as err:
    print("ERROR: " + str(err))
    
ctx.set_value("f", "A${b${c}d}E")
ctx.set_value("c", "x")
ctx.set_value("bxd", "BCD")
print(ctx.get_value("f"))

ctx.set_value("a", "${b}")
ctx.set_value("b", "${a}")
try:
   print(ctx.get_value("a"))
except typo_error as err:
    print("ERROR: " + str(err))

#out = indented_output(console_output())
#
#out.write("Hello\n")
#out.write("this is in new line\n")
#out.increase_indent()
#out.write("indented once\n")
#out.increase_indent()
#out.write("indented twice\n")
#out.write_already_formatted("Injected text without indentation")
#out.decrease_indent()
#out.write("indented once again\nand similarely\n(C) ")
#out.decrease_indent()
#out.write("base text\n")
#
#file = file_lines("templates/simple_type.template")
#for line in file.lines:
#    out.write(line)

#context = typo_context()
#translator = typo_translator(context)
#context.set_value("copyright", "WGan softerware ")
#timestamp = translator.translate_name("timestamp")
#print(timestamp)
#copyright = translator.translate_name("copyright")
#print(copyright)
#
#print(translator.translate_line("before${timestamp}after${copyright}end"))


#try:
#    print(translator.translate_line("before${hgw} xxx"))
#except typo_error as  e:
#    e.source = "code"
#    e.line = 40
#    print(e)

#try:
#    source_name = "templates/simple_type.template"
#    file = file_lines(source_name)
#    out = indented_output(console_output())
#    context = typo_context()
#    translator = typo_translator(context)
#
#    context.set_value("copyright", "// (c) WGan softerware 2021")
#    
#    for line in file.lines:
#        translated_line = translator.translate_line(line)
#        out.write(translated_line)
#
#except typo_error as  e:
#    e.source = source_name
#    print("ERROR: " + str(e))
