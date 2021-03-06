# (c) TYPO by WGan 2021


import os
import re

from typo_base import typo_error
from typo_core import typo_context
from typo_inputs import file_lines
from typo_outputs import file_output, indented_output, string_output
from typo_tools import context_reader, placeholders_info, user_code_placeholder_error, \
            placeholders_info

""" user code extractor """
class user_code_extractor:

    def __init__(self, template, source_code_file_name):
        self.user_code = [ ]
        source_file = file_lines(source_code_file_name)
        source_file_lines_count = len(source_file)
        source_file_line = 0
        for line_number in range(0, len(template)):
            try:
                if self.is_user_code_placeholder(template[line_number]):
                    before = self.get_line_before(template, line_number)
                    after = self.get_line_after(template, line_number)
                    line_before = self.find_line(before, source_file, source_file_line)
                    if line_before is None:
                        self.user_code.append("\n")
                    else:
                        line_after = self.find_line(after, source_file, line_before)
                        if line_after is None:
                            raise user_code_placeholder_error("Cannot find ending delimiter of user code")
                        source_file_line = line_after
                        user_code = ""
                        for line_number in range(line_before+1, line_after):
                            user_code += source_file[line_number]
                        self.user_code.append(user_code)
            except typo_error as err:
                err.source = source_code_file_name
                err.line = line_number + 1
                raise err 
                
    def is_user_code_placeholder(self, line):
        line = placeholders_info(line)
        return line.is_user_code_placeholder()

    def get_line_before(self, lines, index):
        if index == 0:
            raise user_code_placeholder_error("'user_code' placeholder cannot be in the first line")
        line = lines[index-1]
        if placeholders_info(line).is_constant():
            return line
        else:
            raise user_code_placeholder_error("Line before 'user_code' placeholder must be constant.")

    def get_line_after(self, lines, index):
        if index == len(lines)-1:
            raise user_code_placeholder_error("'user_code' placeholder cannot be in the last line")
        line = lines[index+1]
        if placeholders_info(line).is_constant():
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
        typo_error.__init__(self, "Generator '" + generator_name + "' raises error '" + error_report + "'.")
        
""" output file generator - creates file based on template """
class output_file_generator:

    def __init__(self, context):
        self.context = context
        
    def build_source_code(self, template_file_name, source_code_file_name):
        if not os.path.isfile(template_file_name):
            raise template_does_not_exist(template_file_name)
        template = file_lines(template_file_name)
        self.context.user_code = user_code_extractor(template, source_code_file_name).user_code
        line_number = 1
        try:
            output_file = file_output(source_code_file_name)
            code_output = indented_output(output_file)
            for line in template:
                line_content = placeholders_info(line)
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
        line_content = placeholders_info(line)         
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
                    except Exception as err:
                        raise wrong_generator_for_inline(identifier)
                else:
                    value = self.context.get_value(identifier)
                    if value is None:
                        raise cannot_translate(identifier)
                    line = before + str(value) + after
            line_content = placeholders_info(line)
        output.write_already_formatted(line)
               
        
""" processor - main class of TYPO programm - contain everything which is needed """
class typo_processor:

    def __init__(self, context = None):
        if context is None:
            self.context = typo_context()
        else:
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
        if re.match("^\s*[_a-zA-Z][_.a-zA-z0-9]*\s*=.*", command):
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
