# (c) TYPO by WGan 2021


import re
import os.path
import sys

from typo_outputs       import  indented_output, console_output, string_output, \
                                file_output
from typo_inputs        import  file_lines
from typo_core          import  typo_context, template_line, \
                                typo_error, typo_generator, \
                                context_reader
from typo_interpreter   import  typo_processor, typo_main
from typo_tools         import  identifier_formatter       
        
    
    
typo_main()

#try:
#    typo = typo_processor()
#    typo.set_value("template_path", "_dev/templates")
#    typo.set_value("path", "_dev/tests/outputs")
#    typo.set_value("file_name", "${class_name}.hpp")
#    typo.set_value("copyright", "WGan softerware")
#    typo.set_value("class_name", "default_output")
#    typo.set_value("simple_type_value", "m_default_output")
#    typo.import_generator("_dev1")
#    typo.import_generator("_dev2")
#    typo.generate("simple_type")
#except typo_error as err:
#    print("ERROR: " + str(err))



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
