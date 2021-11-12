# (c) TYPO by WGan 2021



import datetime
import re
import imp

from typo_outputs        import  string_output, file_output, indented_output
from typo_inputs         import  file_lines
from typo_core           import  typo_context, template_line, \
                                 typo_error, typo_generator, context_reader                        



""" error when extracting user code """
class user_code_placeholder_error(typo_error):

    def __init__(self, message):
        typo_error.__init__(self, message)



""" user code extractor """
class user_code:

    def __init__(self, template, source_code_file_name):
        self.user_code = [ ]
        source_file = file_lines(source_code_file_name)
        source_file_lines_count = len(source_file.lines)
        source_file_line = 0
        for line_number in range(0, len(template)):
            try:
                if self.is_user_code_placeholder(template[line_number]):
                    before = self.get_line_before(template, line_number)
                    after = self.get_line_after(template, line_number)
                    line_before = self.find_line(before, source_file.lines, source_file_line)
                    if line_before is None:
                        self.user_code.append("\n")
                    else:
                        line_after = self.find_line(after, source_file.lines, line_before)
                        if line_after is None:
                            raise user_code_placeholder_error("Cannot find ending delimiter of user code")
                        source_file_line = line_after + 1
                        user_code = ""
                        for line_number in range(line_before+1, line_after):
                            user_code += source_file.lines[line_number]
                        self.user_code.append(user_code)
            except typo_error as err:
                err.source = source_code_file_name
                err.line = line_number + 1
                raise err 
                
    def is_user_code_placeholder(self, line):
        if re.match(".*\$\{user_code\}.*", line):
            if re.match("\s*\$\{user_code\}\s*", line):
                return True
            else:
                raise user_code_placeholder_error("'user_code' placeholder must be the only text in template line.")
        else:
            return False

    def get_line_before(self, lines, index):
        if index == 0:
            raise user_code_placeholder_error("'user_code' placeholder cannot be in the first line")
        line = lines[index-1]
        if template_line(line).is_constant():
            return line
        else:
            raise user_code_placeholder_error("Line before 'user_code' placeholder must be constant.")

    def get_line_after(self, lines, index):
        if index == len(lines)-1:
            raise user_code_placeholder_error("'user_code' placeholder cannot be in the last line")
        line = lines[index+1]
        if template_line(line).is_constant():
            return line
        else:
            raise user_code_placeholder_error("Line after 'user_code' placeholder must be constant.")

    def find_line(self, pattern, lines, start_from):
        for line_number in range(start_from, len(lines)):
            if lines[line_number] == pattern:
                return line_number
        return None


""" problem with translating given name """
class cannot_translate(typo_error):

    def __init__(self, name):
        typo_error.__init__(self, "Placeholder '" + name + "' is not known.")
        
""" error - desired module was not loaded """
class module_not_loaded(typo_error):

    def __init__(self, module_name):
        typo_error.__init__(self, "Module '" + module_name + "' cannot be loaded.")        

""" output file generator - creates file based on template """
class output_file_generator:

    def __init__(self, context):
        self.context = context
        self.generator_modules = [ ]
        
    def import_generator(self, generators_module_name):
        try:
            self.generator_modules.append(__import__(generators_module_name))
            print(self.generator_modules)
        except:
            raise module_not_loaded(generators_module_name)
                
    def build_source_code(self, template_file_name, source_code_file_name):
        template = file_lines(template_file_name).lines
        self.context.user_code = user_code(template, source_code_file_name).user_code
        line_number = 1
        try:
            output_file = file_output(source_code_file_name)
            code_output = indented_output(output_file)
            for line in template:
                line_content = template_line(line)
                if line_content.is_constant():
                    output_file.write(line)
                else:
                    self.translate_line(line, code_output)
                line_number = line_number + 1
        except typo_error as err:
            if err.source == "":
                err.source = template_file_name
                err.line = line_number
                raise err
                
    def get_generator(self, name):
        try:
            return eval("gen_" + name + "()")
        except:
            pass
        for generator in self.generator_modules:
            try:    
                return eval("generator.gen_" + name + "()")
            except:
                pass
        return None
      
    def translate_line(self, line, output):
        line_content = template_line(line)         
        while not line_content.is_constant():
            start, end = line_content.find_first_identifier()
            identifier = line[start:end]
            generator = self.get_generator(identifier)
            before = line[0:start-2]
            if generator and line_content.is_just_placeholder():
                indent = len(before)
                output.set_indent(indent)
                generator.generate(self.context, output)
                output.flush()
                return
            else:
                after = line[end+1:]
                if generator:
                    temporary_output = string_output()
                    generator.generate(self.context, temporary_output)
                    line = before + temporary_output.text + after    
                else:
                    value = self.context.get_value(identifier)
                    if value is None:
                        raise cannot_translate(identifier)
                    line = before + str(value) + after
            line_content = template_line(line)
        output.write_already_formatted(line)
        
        
        
""" processor - main class of TYPO programm - contain everything which is needed """
class typo_processor:

    def __init__(self):
        self.context = typo_context()
        self.generator = output_file_generator(self.context)
        self.context_reader = context_reader(self.context)
        
    def set_value(self, name, value):
        self.context.set_value(name, value)
        
    def import_generator(self, generators_module_name):
        self.generator.import_generator(generators_module_name)
        
    def generate(self, template):
        template_path = self.context_reader.get_path("template_path")
        output_path = self.context_reader.get_path("path")
        file_name = self.context_reader.get_file_name("file_name")
        self.generator.build_source_code(template_path + template + ".template", output_path + file_name)

                
        
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
        
        
