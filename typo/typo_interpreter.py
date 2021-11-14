# (c) TYPO by WGan 2021



import datetime
import re
import imp
import os.path
import sys

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



""" error - template do not exist """
class template_does_not_exist(typo_error):

    def __init__(self, template_file_name):
        typo_error.__init__(self, "Template file '" + template_file_name + "' does not exist.")

""" problem with translating given name """
class cannot_translate(typo_error):

    def __init__(self, name):
        typo_error.__init__(self, "Placeholder '" + name + "' is not known.")
        
""" error: generator cannot generate inline content """
class wrong_generator_for_inline(typo_error):

    def __init__(self, name):
        typo_error.__init__(self, "Generator '" + name + "' cannot be used inline.")
        
""" error: error in generator - something wrong happened when generating content  """
class error_in_generator(typo_error):

    def __init__(self, generator_name, error_report):
        typo_error.__init__(self, "Generator '" + name + "' raises error '" + error_report + "'.")
        
""" output file generator - creates file based on template """
class output_file_generator:

    def __init__(self, context):
        self.context = context
        
    def build_source_code(self, template_file_name, source_code_file_name):
        if not os.path.isfile(template_file_name):
            raise template_does_not_exist(template_file_name)
        template = file_lines(template_file_name).lines
        self.context.user_code = user_code(template, source_code_file_name).user_code
        line_number = 1
        try:
            output_file = file_output(source_code_file_name)
            code_output = indented_output(output_file)
            for line in template:
                line_content = template_line(line)
                if len(line) >= 2 and line[0:2] == '$>':
                    self.interpret_line(line[2:].strip())
                elif line_content.is_constant():
                    output_file.write(line)
                else:
                    self.translate_line(line, code_output)
                line_number = line_number + 1
        except typo_error as err:
            if err.source == "":
                err.source = template_file_name
                err.line = line_number
            raise err
                 
    def interpret_line(self, line):
        processor = typo_processor(self.context)
        cmd = command_processor(processor)
        cmd.process_command(line)
                 
    def translate_line(self, line, output):
        line_content = template_line(line)         
        while not line_content.is_constant():
            start, end = line_content.find_first_identifier()
            identifier = line[start:end]
            generator = self.context.create_object("gen_" + identifier)
            before = line[0:start-2]
            if generator and line_content.is_just_placeholder():
                indent = len(before)
                output.set_indent(indent)
                try:
                    generator.generate(self.context, output)
                    output.flush()
                    return
                except Exception as err:
                    raise error_in_generator(identifier, str(err))
            else:
                after = line[end+1:]
                if generator:
                    try:
                        temporary_output = string_output()
                        generator.generate(self.context, temporary_output)
                        line = before + temporary_output.text + after  
                    except:
                        raise wrong_generator_for_inline(identifier)
                else:
                    value = self.context.get_value(identifier)
                    if value is None:
                        raise cannot_translate(identifier)
                    line = before + str(value) + after
            line_content = template_line(line)
        output.write_already_formatted(line)
        
        
        
""" processor - main class of TYPO programm - contain everything which is needed """
class typo_processor:

    def __init__(self, context = typo_context()):
        self.context = context
        self.generator = output_file_generator(self.context)
        self.context_reader = context_reader(self.context)
        
    def set_value(self, name, value):
        self.context.set_value(name, value)
        
    def import_module(self, generators_module_name):
        self.context.import_module(generators_module_name)
        
    def generate(self, template):
        template_path = self.context_reader.get_path("template_path")
        output_path = self.context_reader.get_path("path")
        file_name = self.context_reader.get_file_name("file_name")
        self.generator.build_source_code(template_path + template + ".template", output_path + file_name)

                
        
""" exception thrown when program should exit - this exception should be thrown
    up to level of typo module code (free code in TYPO.py) """
class exit_typo(Exception):

    def __init__(self, exit_code):
        self.exit_code = exit_code
        
""" error: command passed to processor is malformed """
class cannot_execute_command(typo_error):

    def __init__(self, command):
        typo_error.__init__(self, "I do not understand command '" + command + "'")

""" transforms command lines into operations on typo_processor """
class command_processor:

    def __init__(self, processor):
        self.processor = processor
    
    def process_command(self, command):
        if command.strip() == "":
            return
        if re.match("^\s*[_a-zA-Z][_a-zA-z0-9]*\s*=.*", command):
            return self._process_assignment(command)
        elif re.match("^\s*exit\s*$", command):
            raise exit_typo(0)
        elif re.match("^\s*list\s*$", command):
            return self._list_variables();
        elif re.match("^\s*import\s*.*", command):
            return self._process_import(command)
        elif re.match("^\s*[_a-zA-Z][_a-zA-z0-9]*\s*$", command):
            return self._process_generation(command)
        elif not re.match("^\s*#.*", command):
            raise cannot_execute_command(command)
    
    def _process_assignment(self, command):
        pos = command.find("=")
        variable_name = command[0:pos].strip()
        value_text = command[pos+1:].strip()
        try:
            # allow python constructions in assignments
            value_text = eval(value_text)
        except:
            pass
        self.processor.set_value(variable_name, value_text)
        
    def _process_import(self, command):
        found_import = re.match("^\s*import\s*", command)
        module_name = command[found_import.end():].strip()
        self.processor.import_module(module_name)
        
    def _process_generation(self, command):
        self.processor.generate(command.strip())
    
    def _list_variables(self):
        result = ""
        for key, value in self.processor.context.values.items():
            result += key + " = " + str(value) + "\n"
        return result[:-1]
    
    
 
def typo_main():
    try:
        typo = typo_processor()
        processor = command_processor(typo)
    
        init = file_lines("init.typo")
        line_number = 1
        for init_line in init.lines:
            try:
                result = processor.process_command(init_line)
            except typo_error as err:
                print("INIT ERROR: " + str(err) + " (in 'init.typo' line: " + str(line_number) + ")")
            line_number = line_number + 1
    
        while(True):
            command = raw_input("> ")
            try:
                result = processor.process_command(command)
                if not(result is None):
                    print(result)
            except typo_error as err:
                print("ERROR: " + str(err))
                
    except exit_typo as exit_info:
        sys.exit(exit_info.exit_code)
