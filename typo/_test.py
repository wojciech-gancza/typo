# (c) TYPO by WGan 2021



import unittest
import hashlib
import re
import shutil

from TYPO             import  typo_main
from typo_inputs      import  file_lines
from typo_outputs     import  indented_output, string_output, file_output, \
                              file_cannot_be_created, indentation, text_source, \
                              prefixing_output_decorator, sufixing_output_decorator, \
                              line_split_decorator
from typo_core        import  typo_context, module_not_loaded      
from typo_tools       import  typo_error, conv_UppercaseCamel, conv_lowercaseCamel, \
                              conv_CAPITALIZE_ALL, conv_lowercase_with_underscores, \
                              identifier_non_alphanueric_error, identifier_start_with_digit_error, \
                              context_reader, path_not_found, path_not_specified, \
                              malformed_file_name, file_name_is_not_defined, \
                              identifier_formatter, identifier_cannot_be_empty, \
                              identifier_start_with_digit_error, identifier_non_alphanueric_error, \
                              placeholders_info, user_code_placeholder_error
from typo_interpreter import  output_file_generator, template_does_not_exist, \
                              cannot_translate, wrong_generator_for_inline, \
                              error_in_generator, user_code_extractor, \
                              typo_processor, exit_typo, command_processor, \
                              cannot_execute_command, cannot_execute_command

class test_output(indented_output):

    def __init__(self):
        self.string = string_output()
        indented_output.__init__(self, self.string)
        
    def get_text(self):
        self.flush()
        return self.string.text
        
    def get_md5hex(self):
        self.flush()
        md5_hash = hashlib.md5(self.string.text)
        return md5_hash.hexdigest()        
        
class file_checker:

    def __init__(self, file_name):
        self.file_name = file_name
        self.load()
    
    def load(self):    
        self.file_content = None
        try:
            file = open(self.file_name)
            self.file_content = file.read()
            file.close()
        except:
            pass
            
    def delete(self):
        try:
            os.remove(self.file_name)
        except:
            pass
            
    def copy_from(self, name_of_file_to_copy):
        shutil.copyfile(name_of_file_to_copy, self.file_name)       
        
    def get_text(self):
        return self.file_content
        
    def get_md5hex(self):
        md5_hash = hashlib.md5(self.file_content)
        return md5_hash.hexdigest()
        
    def has(self, pattern):
        if re.search(pattern, self.file_content):
            return True
        else:
            return False
 
#-----------------------------------------------------------------       

class test_buildin_generators(unittest.TestCase):

    def test_gen_timestamp(self):
        ctx = typo_context()
        out = test_output()
        gen = ctx.create_object("gen_timestamp")
        gen.generate(ctx, out)
        txt = out.get_text()
        self.assertTrue(re.match("20[2-4][0-9]-[01][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]", out.get_text()))
       
    def test_gen_typo_version(self):
        ctx = typo_context()
        out = test_output()
        gen = ctx.create_object("gen_typo_version")
        gen.generate(ctx, out)
        self.assertEqual("1.00.Dev\n", out.get_text())
        
    def test_gen_user_code(self):
        ctx = typo_context()
        ctx.user_code = ["ABCD\n", "EFG\n", "123454\n554dxcf\n"]
        out = test_output()
        gen = ctx.create_object("gen_user_code")
        gen.generate(ctx, out)
        ctx.pop_user_code()
        gen.generate(ctx, out)
        gen.generate(ctx, out)
        gen.generate(ctx, out)
        self.assertEqual('cb90098bbeb85f7ada786b38e4848a3a', out.get_md5hex())
        

class test_of_file_lines(unittest.TestCase):

    def test_of_reading_non_existing_file(self):
        file = file_lines("_dev/tests/inputs/non_existing.txt")
        self.assertEqual(str(file), "[]")
    
    def test_of_reading_existing_file(self):
        file = file_lines("_dev/tests/inputs/example.txt")
        self.assertEqual(file[1], "how the file is read\n")
        

class test_of_context(unittest.TestCase):

    def test_simple_store_and_read(self):
        ctx = typo_context()
        ctx.set_value("ABC", "xyz")
        val = ctx.get_value("ABC")
        self.assertEqual(val, "xyz")
        val = ctx.get_value("xyz")
        self.assertEqual(val, None)

    def test_assign_list(self):
        ctx = typo_context()
        ctx.set_value("ABC", [223, 445])
        val = ctx.get_value("ABC")
        self.assertEqual(val, [223, 445])

    def test_simple_unwindowg(self):
        ctx = typo_context()
        ctx.set_value("ABC", "aaaB${cde}XY")
        ctx.set_value("cde", "FGH")
        val = ctx.get_value("ABC")
        self.assertEqual(val, "aaaBFGHXY")
        val = ctx.get_not_interpreted_value("ABC")
        self.assertEqual(val, "aaaB${cde}XY")

    def test_deep_unwinding_variables_in_array(self):
        ctx = typo_context()
        ctx.set_value("x", [ "${a}", "${b}"])
        ctx.set_value("a", [ 1, 2, 3])
        ctx.set_value("b", {"a":1, "b":2})
        val = ctx.get_value("x")
        self.assertEqual(val, [ [1, 2, 3], {"a":1, "b":2} ])
        
    def test_cascade_unwinding(self):
        ctx = typo_context()
        ctx.set_value("f", "A${b${c}d}E")
        ctx.set_value("c", "x")
        ctx.set_value("bxd", "BCD")
        val = ctx.get_value("f")
        self.assertEqual(val, "ABCDE")

    def test_of_converter(self):
        ctx = typo_context()
        ctx.set_value("f", "this is sparta")
        ctx.set_value("ff", "${f.UppercaseCamel}")
        val = ctx.get_value("ff")
        self.assertEqual(val, "ThisIsSparta")
           
    def test_of_error_on_unresolved_symbol(self):
        ctx = typo_context()
        ctx.set_value("y", [ "${a}", "${z}"])
        ctx.set_value("z", [ "${a}", "${d}"])
        try:
            val = ctx.get_value("y")
            self.assertFalse()
        except typo_error as err:
            self.assertEqual(str(err), "Value of 'a' not found during resolving value 'y'.")
                   
    def test_of_error_on_circular_dependencies(self):
        ctx = typo_context()
        ctx.set_value("a", "${b}")
        ctx.set_value("b", "${a}")
        try:
            val = ctx.get_value("a")
            self.assertFalse()
        except typo_error as err:
            self.assertEqual(str(err), "Cycle found when resolving value of 'a'")

    def test_of_user_code(self):
        ctx = typo_context()
        ctx.user_code = [ "aaa", "bbb", "ccc"]
        val = ctx.pop_user_code()
        self.assertEqual(val, "aaa")
        val = ctx.pop_user_code()
        val = ctx.pop_user_code()
        self.assertEqual(val, "ccc")
        val = ctx.pop_user_code()
        self.assertEqual(val, '')
        
    def test_of_importing_module(self):
        ctx = typo_context()
        ctx.import_module("_test_module_1")
        ctx.import_module("_test_module_2")
        try:
            ctx.import_module("_test_module_3")
            self.assertFalse()
        except module_not_loaded as err:
            self.assertEqual(str(err), "Module '_test_module_3' cannot be loaded.")
        
    def test_of_generation_of_object(self):
        ctx = typo_context()
        ctx.import_module("_test_module_1")
        ctx.import_module("_test_module_2")
        obj = ctx.create_object("test_class_1") 
        txt = obj.get()
        self.assertEqual(txt, "result 1")
        obj = ctx.create_object("test_class_2")        
        txt = obj.get()
        self.assertEqual(txt, "result 2")
        obj = ctx.create_object("test_class_3")
        self.assertEqual(obj, None)
        
class test_of_builtin_converters(unittest.TestCase):

    def test_of_UppercaseCamel_converter(self):
        conv = conv_UppercaseCamel()
        txt = "thIs is SpaRTa"
        val = conv.convert(txt)
        self.assertEqual(val, "ThisIsSparta")
        
    def test_of_UppercaseCamel_converter_error(self):
        conv = conv_UppercaseCamel()
        txt = "thIs is Sp()aRTa"
        try:
            val = conv.convert(txt)
            self.assertTrue(False)
        except identifier_non_alphanueric_error as err:
            self.assertEqual(str(err), "'thIs is Sp()aRTa' could not be an identifier because it contain non alphanumeric character")
        except Exception as err: 
            self.assertTrue(False)
        
    def test_of_lowercaseCamel_converter(self):
        conv = conv_lowercaseCamel()
        txt = "thIs is SpaRTa"
        val = conv.convert(txt)
        self.assertEqual(val, "thisIsSparta")
        
    def test_of_lowercaseCamel_converter_error(self):
        conv = conv_lowercaseCamel()
        txt = "1hIs is SpaRTa"
        try:
            val = conv.convert(txt)
            self.assertTrue(False)
        except identifier_start_with_digit_error as err:
            self.assertEqual(str(err), "Identifier cannot start with digit but it is '1hIs is SpaRTa'")
        except Exception as err: 
            self.assertTrue(False)
        
    def test_of_conv_CAPITALIZE_ALL_converter(self):
        conv = conv_CAPITALIZE_ALL()
        txt = "thIs is SpaRTa"
        val = conv.convert(txt)
        self.assertEqual(val, "THIS_IS_SPARTA")
        
    def test_of_lowercase_with_underscores_converter(self):
        conv = conv_lowercase_with_underscores()
        txt = "thIs is SpaRTa"
        val = conv.convert(txt)
        self.assertEqual(val, "this_is_sparta")
        
class test_of_output_file(unittest.TestCase):

    def test_of_writing_to_file(self):
        file = file_output("_dev/tests/outputs/test_of_file_output.txt")
        file.write("ABC")
        file.write("DE\nFGH")
        file.close()
        result = file_checker("_dev/tests/outputs/test_of_file_output.txt")
        self.assertEqual(result.get_text(), "ABCDE\nFGH")
        
    def test_of_writing_to_file_error(self):
        try:
            file = file_output("_dev/tests/bad_directory/test_of_file_output.txt")
            self.assertTrue(False)
        except file_cannot_be_created as err:
            self.assertEqual(str(err), "File '_dev/tests/bad_directory/test_of_file_output.txt' cannot be created.")
        except:
            self.assertTrue(False)
                
class test_of_output_string(unittest.TestCase):

    def test_of_writing_to_string(self):
        out = string_output()
        out.write("ABC")
        out.write("DE\nFGH")
        self.assertEqual(out.text, "ABCDE\nFGH")
        
class test_of_context_reader(unittest.TestCase):

    def test_of_taking_proper_path(self):
        ctx = typo_context()
        ctx.set_value("path", "_dev/tests/templates")
        rdr = context_reader(ctx)
        pth = rdr.get_path("path")
        self.assertEqual(pth, "_dev/tests/templates/")
    
    def test_of_taking_proper_path_with_slash_ending(self):
        ctx = typo_context()
        ctx.set_value("path", "_dev/tests/templates/")
        rdr = context_reader(ctx)
        pth = rdr.get_path("path")
        self.assertEqual(pth, "_dev/tests/templates/")
    
    def test_ot_taking_nonexisting__path_variable(self):
        ctx = typo_context()
        rdr = context_reader(ctx)
        try:
            pth = rdr.get_path("path")
            self.assertTrue(False)
        except path_not_specified as err:
            self.assertEqual(str(err), "Variable 'path' is not defined but it should point to the directory.")
        except:
            self.assertTrue(False)
    
    def test_ot_taking_wrong_path(self):
        ctx = typo_context()
        ctx.set_value("path", "_dev/test/templates/")
        rdr = context_reader(ctx)
        try:
            pth = rdr.get_path("path")
            self.assertTrue(False)
        except path_not_found as err:
            self.assertEqual(str(err), "Path '_dev/test/templates/' in variable 'path' does not exist.")
        except:
            self.assertTrue(False)
    
    def test_of_taking_proper_file_name(self):
        ctx = typo_context()
        ctx.set_value("file", "test_template.template")
        rdr = context_reader(ctx)
        fnm = rdr.get_file_name("file")
        self.assertEqual(fnm, "test_template.template")
    
    def test_of_taking_wrong_file_name(self):
        ctx = typo_context()
        ctx.set_value("file", "test_te{}ate.template")
        rdr = context_reader(ctx)
        try:  
            fnm = rdr.get_file_name("file")
            self.assertTrue(False)
        except malformed_file_name as err:
            self.assertEqual(str(err), "Value 'test_te{}ate.template' in variable 'file' is wrong as a file name.")
        except Exception as err:
            print(err)
            self.assertTrue(False)
      
    def test_of_taking_file_name_from_nonexisting_variable(self):
        ctx = typo_context()
        rdr = context_reader(ctx)
        try:  
            fnm = rdr.get_file_name("file")
            self.assertTrue(False)
        except file_name_is_not_defined as err:
            self.assertEqual(str(err), "Variable 'file' is not defined byt should contain valid file name.")
        except:
            self.assertTrue(False)
      
class test_of_context_reader(unittest.TestCase):

    def test_of_indent(self):
        i = indentation()
        self.assertEqual(i.get(), "")
        i.increase()
        self.assertEqual(i.get(), "    ")
        i.increase()
        self.assertEqual(i.get(), "        ")
        i.decrease()
        self.assertEqual(i.get(), "    ")
        i.decrease()
        self.assertEqual(i.get(), "")
      
    def test_of_different_indent_step(self):
        i = indentation(3)
        self.assertEqual(i.get(), "")
        i.increase()
        self.assertEqual(i.get(), "   ")
        i.set(12)
        self.assertEqual(i.get(), "            ")
        i.decrease()
        self.assertEqual(i.get(), "         ")
        i.decrease()
        self.assertEqual(i.get(), "      ")
        i.decrease()
        self.assertEqual(i.get(), "   ")
        i.decrease()
        self.assertEqual(i.get(), "")
        
class test_of_identifier_formatter(unittest.TestCase):

    def test_of_empty_identifier(self):
        try:
            id = identifier_formatter("")
            self.assertTrue(False)
        except identifier_cannot_be_empty as err:
            self.assertEqual(str(err), "Identifier cannot be empty")
        except:
            self.assertTrue(False)
    
    def test_of_wrong_characeter_in_identifier(self):
        try:
            id = identifier_formatter("Some 5tr&GE SeN73Nc3")
            self.assertTrue(False)
        except identifier_non_alphanueric_error as err:
            self.assertEqual(str(err), "'Some 5tr&GE SeN73Nc3' could not be an identifier because it contain non alphanumeric character")
        except:
            self.assertTrue(False)
    
    def test_of_identifier_starting_with_digit(self):
        try:
            id = identifier_formatter("5ome 5trGE SeN73Nc3")
            self.assertTrue(False)
        except identifier_start_with_digit_error as err:
            self.assertEqual(str(err), "Identifier cannot start with digit but it is '5ome 5trGE SeN73Nc3'")
        except:
            self.assertTrue(False)
    
    def test_of_CAPITALIZE_ALL_identifier(self):    
        id = identifier_formatter("Some 5tranGE SeN73Nc3")
        id_val = id.CAPITALIZE_ALL()
        self.assertEqual(id_val, "SOME_5TRANGE_SEN73NC3")
        id_val = id.CAPITALIZE_ALL("enm_")
        self.assertEqual(id_val, "enm_SOME_5TRANGE_SEN73NC3")
        id_val = id.CAPITALIZE_ALL("_", "_H_")
        self.assertEqual(id_val, "_SOME_5TRANGE_SEN73NC3_H_")
 
    def test_of_lowercase_with_underscores_identifier(self): 
        id = identifier_formatter("Some 5tranGE SeN73Nc3")
        id_val = id.lowercase_with_underscores()
        self.assertEqual(id_val, "some_5trange_sen73nc3")
        id_val = id.lowercase_with_underscores("enm_")
        self.assertEqual(id_val, "enm_some_5trange_sen73nc3")
        id_val = id.lowercase_with_underscores("_", "_H_")
        self.assertEqual(id_val, "_some_5trange_sen73nc3_H_")
        
    def test_of_UppercaseCamel_identifier(self): 
        id = identifier_formatter("Some 5tranGE SeN73Nc3")
        id_val = id.UppercaseCamel()
        self.assertEqual(id_val, "Some5trangeSen73nc3")
        id_val = id.UppercaseCamel("enm_")
        self.assertEqual(id_val, "enm_Some5trangeSen73nc3")
        id_val = id.UppercaseCamel("_", "_H_")
        self.assertEqual(id_val, "_Some5trangeSen73nc3_H_")
    
    def test_of_lowercaseCamel_identifier(self): 
        id = identifier_formatter("Some 5tranGE SeN73Nc3")
        id_val = id.lowercaseCamel()
        self.assertEqual(id_val, "some5trangeSen73nc3")
        id_val = id.lowercaseCamel("enm_")
        self.assertEqual(id_val, "enm_some5trangeSen73nc3")
        id_val = id.lowercaseCamel("_", "_H_")
        self.assertEqual(id_val, "_some5trangeSen73nc3_H_")       
     
class test_output_file_generator(unittest.TestCase):

    def test_of_build_source_code_just_generate(self):
        output_file = "_dev/tests/outputs/test_file_generator_01.out"
        template_file = "_dev/tests/templates/test_of_copying_content.template"
        try:
            os.remove(output_file)
        except:
            pass
        context = typo_context()
        generator = output_file_generator(context)
        generator.build_source_code(template_file, output_file)
        file = file_checker(output_file)
        self.assertTrue(file.has("containing no placeholders"))
    
    def test_of_build_source_code_missing_template(self):
        output_file = "_dev/tests/outputs/test_file_generator_01.out"
        template_file = "_dev/tests/templates/test_of_missing_template.template"
        context = typo_context()
        generator = output_file_generator(context)
        try:
            generator.build_source_code(template_file, output_file)
            self.assertTrue(False)
        except template_does_not_exist as err:
            self.assertEqual(str(err), "Template file '_dev/tests/templates/test_of_missing_template.template' does not exist.")
        except:
            self.assertTrue(False)
            
    def test_of_build_source_code_wih_generator(self):
        output_file = "_dev/tests/outputs/test_file_generator_02.out"
        template_file = "_dev/tests/templates/test_of_running_generator.template"
        file = file_checker(output_file)
        file.delete()
        context = typo_context()
        generator = output_file_generator(context)
        generator.build_source_code(template_file, output_file)
        file.load()
        self.assertTrue(file.has("Typo version is: 1.00.Dev. Isn.t it?"))
            
    def test_of_build_source_code_wih_value(self):
        output_file = "_dev/tests/outputs/test_file_generator_03.out"
        template_file = "_dev/tests/templates/test_of_using_value.template"
        file = file_checker(output_file)
        file.delete()
        context = typo_context()
        context.set_value("copyright", "WGan (c) 2021")
        generator = output_file_generator(context)
        generator.build_source_code(template_file, output_file)
        file.load()
        self.assertTrue(file.has("\# WGan \(c\) 2021"))
            
    def test_of_build_source_code_wih_value(self):
        output_file = "_dev/tests/outputs/test_file_generator_04.out"
        template_file = "_dev/tests/templates/test_of_using_value.template"
        file = file_checker(output_file)
        file.delete()
        context = typo_context()
        context.set_value("copyright", "WGan (c) 2021")
        generator = output_file_generator(context)
        generator.build_source_code(template_file, output_file)
        file.load()
        self.assertTrue(file.has("\# WGan \(c\) 2021"))
            
    def test_of_build_source_code_with_missing_generator(self):
        output_file = "_dev/tests/outputs/test_file_generator_04.out"
        template_file = "_dev/tests/templates/test_of_using_value.template"
        context = typo_context()
        generator = output_file_generator(context)
        try:
            generator.build_source_code(template_file, output_file)
            self.assertTrue(False)
        except cannot_translate as err:
            self.assertEqual(str(err), "Placeholder 'copyright' is not known. Found in '_dev/tests/templates/test_of_using_value.template' in line 2.")
        except Exception as err:
            self.assertTrue(False)
            
    def test_of_build_source_code_into_wrong_file(self):
        output_file = "_dev/tests/XXX/test_file_generator_04.out"
        template_file = "_dev/tests/templates/test_of_using_value.template"
        context = typo_context()
        generator = output_file_generator(context)
        try:
            generator.build_source_code(template_file, output_file)
            self.assertTrue(False)
        except file_cannot_be_created as err:
            self.assertEqual(str(err), "File '_dev/tests/XXX/test_file_generator_04.out' cannot be created. Found in '_dev/tests/templates/test_of_using_value.template' in line 1.")
        except:
            self.assertTrue(False)
                      
    def test_of_build_source_with_user_code(self):
        output_file = "_dev/tests/outputs/test_file_generator_05.out"
        template_file = "_dev/tests/templates/test_of_user_code.template"
        file = file_checker(output_file)
        file.copy_from("_dev/tests/inputs/test_file_generator_05.in")
        context = typo_context()
        generator = output_file_generator(context)
        generator.build_source_code(template_file, output_file)
        file.load()
        self.assertTrue(file.has("XXX"))
        self.assertTrue(file.has("YYY"))
        self.assertTrue(file.has("ZZZ"))
                      
    def test_of_build_source_with_orders(self):
        output_file = "_dev/tests/outputs/test_file_generator_06.out"
        template_file = "_dev/tests/templates/test_of_orders.template"
        file = file_checker(output_file)
        file.delete()
        context = typo_context()
        generator = output_file_generator(context)
        generator.build_source_code(template_file, output_file)
        file.load()
        self.assertFalse(file.has("copyright"))
        self.assertEqual(context.get_value("copyright"), "WGan (c) 2021")
                      
    def test_of_interpret_line(self):
        context = typo_context()
        generator = output_file_generator(context)
        generator.interpret_line("something=12+34")
        self.assertEqual(context.get_value("something"), 46)
        
    def test_of_translate_line(self):
        context = typo_context()
        generator = output_file_generator(context)
        output = test_output()
        generator.translate_line("Line without placeholders\n", output)
        self.assertEqual(output.get_text(), "Line without placeholders\n")
        
    def test_of_translate_line_with_placeholder(self):
        context = typo_context()
        context.set_value("here", "PLACEHOLDER")
        generator = output_file_generator(context)
        output = test_output()
        generator.translate_line("Line with placeholder ${here}\n", output)
        self.assertEqual(output.get_text(), "Line with placeholder PLACEHOLDER\n")
        
    def test_of_translate_line_with_generator(self):
        context = typo_context()
        generator = output_file_generator(context)
        output = test_output()
        generator.translate_line("Line with placeholder ${typo_version}\n", output)
        self.assertEqual(output.get_text(), "Line with placeholder 1.00.Dev\n")
        
    def test_of_translate_line_with_generator(self):
        context = typo_context()
        generator = output_file_generator(context)
        output = test_output()
        generator.translate_line("Line with placeholder ${typo_version}\n", output)
        self.assertEqual(output.get_text(), "Line with placeholder 1.00.Dev\n")
        
    def test_of_translate_line_with_multiline_generator(self):
        context = typo_context()
        context.import_module("_test_module_1")
        generator = output_file_generator(context)
        output = test_output()
        generator.translate_line("    ${test_generator}\n", output)
        self.assertEqual(output.get_text(), "    constructor(parameters)\n    {\n        // indented text\n        // multiline\n    }\n")

    def test_of_translate_line_with_multiline_generator_error(self):
        context = typo_context()
        context.import_module("_test_module_1")
        generator = output_file_generator(context)
        output = test_output()
        try:
            generator.translate_line("    ${test_generator} and some other text\n", output)
            self.assertTrue(False)
        except wrong_generator_for_inline as err:
            self.assertEqual(str(err), "Generator 'test_generator' cannot be used inline.")
        except:
            self.assertTrue(False)

    def test_of_translate_line_with_nonexisting_value(self):
        context = typo_context()
        generator = output_file_generator(context)
        output = test_output()
        try:
            generator.translate_line("Line with placeholder ${here}\n", output)
            self.assertTrue(False)
        except cannot_translate as err:
            self.assertEqual(str(err), "Placeholder 'here' is not known.")
        except:
            self.assertTrue(False)

    def test_of_translate_line_with_error_in_generator(self):
        context = typo_context()
        context.import_module("_test_module_1")
        generator = output_file_generator(context)
        output = test_output()
        try:
            generator.translate_line("  ${test_of_error}\n", output)
            self.assertTrue(False)
        except error_in_generator as err:
            self.assertEqual(str(err), "Generator 'test_of_error' raises error 'exception in 'gen_test_of_error''.")
        except Exception as err:
            print(str(err))
            self.assertTrue(False)
            
class test_placeholders_info(unittest.TestCase):

    def test_of_just_placeholder(self):
        line = placeholders_info("${placeholder}")
        self.assertTrue(line.is_just_placeholder())
        line = placeholders_info("  ${placeholder}")
        self.assertTrue(line.is_just_placeholder())
        line = placeholders_info("  ${placeholder}      ")
        self.assertTrue(line.is_just_placeholder())
        line = placeholders_info("  ${plac%eholder}      ")
        self.assertFalse(line.is_just_placeholder())
        line = placeholders_info("  ${plac%eholder}  .    ")
        self.assertFalse(line.is_just_placeholder())
        line = placeholders_info("  ${plac%eholder}   ${second}   ")
        self.assertFalse(line.is_just_placeholder())
        
    def test_is_user_code_placeholder(self):
        line = placeholders_info("${user_code}")
        self.assertTrue(line.is_user_code_placeholder())
        line = placeholders_info("  ${user_code}")
        self.assertTrue(line.is_user_code_placeholder())
        line = placeholders_info("  ${auto_code}")
        self.assertFalse(line.is_user_code_placeholder())
        
    def test_is_user_code_placeholder_error(self):
        line = placeholders_info("Here: ${user_code}")
        try:
            result = line.is_user_code_placeholder()
            self.assertTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "User code placeholder must be the only one in the line.")
        except:
            self.assertTrue(False)
            
    def test_is_empty(self):
        line = placeholders_info("")
        self.assertTrue(line.is_empty())
        line = placeholders_info("\n")
        self.assertTrue(line.is_empty())
        line = placeholders_info("    ")
        self.assertTrue(line.is_empty())
        line = placeholders_info("  \t   ")
        self.assertTrue(line.is_empty())
        line = placeholders_info("  .    . ")
        self.assertFalse(line.is_empty())
        line = placeholders_info("ABCD")
        self.assertFalse(line.is_empty())
        line = placeholders_info("${abcd}")
        self.assertFalse(line.is_empty())
        
    def test_is_constant(self):
        line = placeholders_info("ABCD")
        self.assertTrue(line.is_constant())
        line = placeholders_info("${ABCD}")
        self.assertFalse(line.is_constant())
        line = placeholders_info("")
        self.assertTrue(line.is_constant())
        line = placeholders_info(" qe q q qs addad as dc ")
        self.assertTrue(line.is_constant())
        line = placeholders_info("AB${x}CD")
        self.assertFalse(line.is_constant())
    
    def test_find_pirst_identifer(self):
        line = placeholders_info("ABCD")
        self.assertTrue(line.find_first_identifier() is None)
        line = placeholders_info("A${BC}D")
        self.assertEqual(line.find_first_identifier(), (3, 5))
        line = placeholders_info("${ABCD}")
        self.assertEqual(line.find_first_identifier(), (2, 6))
        line = placeholders_info("AB${xyz${hhhh}aa}CD")
        self.assertEqual(line.find_first_identifier(), (9, 13))

class test_user_code_extractor(unittest.TestCase):

    def test_of___init__(self):
        template = file_lines("_dev/tests/templates/test_of_user_code.template")
        user_code = user_code_extractor(template, "_dev/tests/inputs/test_file_generator_05.in")
        self.assertEqual(user_code.user_code, ["XXX\n", "YYY\n", "ZZZ\n"])
        user_code = user_code_extractor(template, "_dev/tests/inputs/test_file_generator_05_A.in")
        self.assertEqual(user_code.user_code, ["XXX\n", "\n", "ZZZ\n"])
        try:
            user_code = user_code_extractor(template, "_dev/tests/inputs/test_file_generator_05_B.in")
            self.assertTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "Cannot find ending delimiter of user code Found in '_dev/tests/inputs/test_file_generator_05_B.in' in line 8.")
        except:
            self.assertTrue(False)
                
    def test_is_user_code_placeholder(self):
        user_code = user_code_extractor([], "_dev/tests/inputs/test)file_generator_05.in")
        self.assertTrue(user_code.is_user_code_placeholder("${user_code}"))
        self.assertTrue(user_code.is_user_code_placeholder("  ${user_code}"))
        self.assertFalse(user_code.is_user_code_placeholder("  ${auto_code}"))
        
    def test_is_user_code_placeholder_error(self):
        user_code = user_code_extractor("_dev/tests/templates/test_of_user_code.template", "_dev/tests/inputs/test)file_generator_05.in")
        try:
            result = user_code.is_user_code_placeholder("x ${user_code}")
            self.assertTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "User code placeholder must be the only one in the line.")
        except:
            self.assertTrue(False)
            
    def test_of_get_line_before(self):
        user_code = user_code_extractor([], "_dev/tests/inputs/test)file_generator_05.in")
        lines = ["ABC", "AAA${B}ddd", "ds", "", "${hello}"]
        line = user_code.get_line_before(lines, 1)
        self.assertEqual(line, "ABC")
        try:
            line = user_code.get_line_before(lines, 0)
            self.assetTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "'user_code' placeholder cannot be in the first line")
        except:
            self.assetTrue(False)
        try:
            line = user_code.get_line_before(lines, 2)
            self.assetTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "Line before 'user_code' placeholder must be constant.")
        except:
            self.assertTrue(False)

    def test_of_get_line_after(self):
        user_code = user_code_extractor([], "_dev/tests/inputs/test)file_generator_05.in")
        lines = ["ABC", "AAA${B}ddd", "ds", "", "${hello}"]
        line = user_code.get_line_after(lines, 1)
        self.assertEqual(line, "ds")
        try:
            line = user_code.get_line_after(lines, 4)
            self.assetTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "'user_code' placeholder cannot be in the last line")
        except:
            self.assetTrue(False)
        try:
            line = user_code.get_line_after(lines, 3)
            self.assetTrue(False)
        except user_code_placeholder_error as err:
            self.assertEqual(str(err), "Line after 'user_code' placeholder must be constant.")
        except:
            self.assertTrue(False)

    def test_of_find_line(self):
        user_code = user_code_extractor([], "_dev/tests/inputs/test)file_generator_05.in")
        lines = ["ABC", "xyz", "x12345678", "ABC", "a12", "a34", "x99", "ABC", "F9"]
        line_number = user_code.find_line("ABC", lines, 0)
        self.assertEqual(line_number, 0)
        line_number = user_code.find_line("ABC", lines, 1)
        self.assertEqual(line_number, 3)
        line_number = user_code.find_line("ABC", lines, 4)
        self.assertEqual(line_number, 7)
        line_number = user_code.find_line("nothinf", lines, 4)
        self.assertEqual(line_number, None)
 
class test_typo_processor(unittest.TestCase):

    def test_of__init__(self):
        processor = typo_processor()
        self.assertEqual(processor.context.__class__.__name__, "typo_context")
        self.assertEqual(processor.generator.__class__.__name__, "output_file_generator")
        self.assertEqual(processor.context_reader.__class__.__name__, "context_reader")
        
    def test_of_set_value(self):
        processor = typo_processor()
        processor.set_value("var", "X234ABC")
        val = processor.context.get_value("var")
        self.assertEqual(val, "X234ABC")
        
    def test_of_import_module(self):
        processor = typo_processor()
        processor.import_module("_test_module_1")
        txt = str(processor.context.modules[0])
        self.assertEqual(txt, "<module '_test_module_1' from '/Users/wgan/Documents/DEV/typo/typo/_test_module_1.pyc'>")
        
    def test_of_generate(self):
        result = file_checker("_dev/tests/outputs/generated_by_test.txt")
        result.copy_from("_dev/tests/inputs/generated_by_test.txt")
        result.load()
        self.assertTrue(result.has(" this line should contain copyright, by it was manually deleted "))
        processor = typo_processor()
        processor.set_value("template_path", "_dev/tests/templates")
        processor.set_value("path", "_dev/tests/outputs")
        processor.set_value("file_name", "generated_by_test.txt")
        processor.set_value("copyright", "WGan (c) 2021")
        processor.set_value("id", "this is something important")
        processor.set_value("simple_type_value", "${type} ${value};")
        processor.set_value("type", "double")
        processor.set_value("value", "val")
        processor.import_module("_test_module_2")
        processor.generate("test_template")
        result.load()
        self.assertFalse(result.has(" this line should contain copyright, by it was manually deleted "))
        self.assertTrue(result.has(" just some user text inside the class "))
        
    def test_of_generate_error(self):
        result = file_checker("_dev/tests/outputs/generated_by_test.txt")
        result.copy_from("_dev/tests/inputs/generated_by_test.txt")
        result.load()
        processor = typo_processor()
        processor.set_value("template_path", "_dev/tests/templates")
        processor.set_value("path", "_dev/tests/outputs")
        processor.set_value("file_name", "generated_by_test.txt")
        processor.set_value("copyright", "WGan (c) 2021")
        processor.set_value("id", "this is something important")
        processor.set_value("simple_type_value", "${type} ${value};")
        processor.set_value("type", "double")
        processor.set_value("value", "val")
        try:
            processor.generate("test_template")
            self.assetTrue(False)
        except typo_error as err:
            self.assertEqual(str(err), "Placeholder 'another_part_of_code' is not known. Found in '_dev/tests/templates/test_template.template' in line 15.")
        except:
            self.assertTrue(False)
        
class _text_source(text_source):

    def __init__(self, text):
        self.text = text
        
    def get(self):
        return self.text
        
class test_of_output_decorators(unittest.TestCase):
    
    def test_of_prefixing_decorator(self):
        out = string_output()
        txt = _text_source("P_")
        decorated_out = prefixing_output_decorator(txt, out)
        decorated_out.write("hello")
        decorated_out.write("world\n")
        decorated_out.write("and goodbye")
        self.assertEqual(out.text, "P_helloP_world\nP_and goodbye")
        
    def test_of_sufixing_output_decorator(self):
        out = string_output()
        decorated_out = sufixing_output_decorator(out, "Xyz")
        decorated_out.write("hello")
        decorated_out.write("world\n")
        decorated_out.write("and goodbye")
        self.assertEqual(out.text, "helloXyzworld\nXyzand goodbyeXyz")
 
class test_of_line_split_decorator(unittest.TestCase):

    def test_of_splitting_lines(self):
        out = string_output()
        splitting_output = line_split_decorator(out)
        splitting_output.write("ABCD")
        self.assertEqual(out.text, "")
        self.assertEqual(splitting_output.line_buffer, "ABCD")
        splitting_output.write("EFG\nHIJ")
        self.assertEqual(out.text, "ABCDEFG")
        self.assertEqual(splitting_output.line_buffer, "HIJ")
        splitting_output.write("\n")
        self.assertEqual(out.text, "ABCDEFGHIJ")
        self.assertEqual(splitting_output.line_buffer, "")
 
class test_of_indented_output(unittest.TestCase):

    def test_of_indented_output(self):
        output = string_output()
        out = indented_output(output)
        out.write("Hello\n")
        out.write("this is in new line\n")
        out.increase_indent()
        out.write("indented once\n")
        out.increase_indent()
        out.write("indented twice\n")
        out.write_already_formatted("Injected text without indentation\n")
        out.decrease_indent()
        out.write("indented once again\nand similarely\n(C) ")
        out.decrease_indent()
        out.write("base text\n")
        pattern = "Hello\n" \
                  "this is in new line\n" \
                  "    indented once\n" \
                  "        indented twice\n" \
                  "Injected text without indentation\n" \
                  "    indented once again\n" \
                  "    and similarely\n" \
                  "(C) base text\n"
        self.assertEqual(output.text, pattern)
        
class test_of_exit_typo(unittest.TestCase):

    def test_of_passing_exit_code_by_exception(self):
        try:
            raise exit_typo(997)
        except exit_typo as err:
            self.assertEqual(err.exit_code, 997)
        except:
            self.assertTrue(False)
 
class text_of_typo_command(unittest.TestCase):

    def test_of_process_command(self):
        context = typo_context()
        processor = typo_processor(context)
        commands = command_processor(processor)
        commands.process_command("template_path = _dev/tests/templates")
        commands.process_command("path = _dev/tests/outputs")
        commands.process_command("file_name = \"generated_by_test.txt\"")
        commands.process_command("copyright = WGan (c) 2021")
        commands.process_command("import _test_module_2")
        commands.process_command("id = this is something important")
        commands.process_command("simple_type_value = ${type} ${value};")
        commands.process_command("type = double")
        commands.process_command("value = val")
        result = file_checker("_dev/tests/outputs/generated_by_test.txt")
        result.copy_from("_dev/tests/inputs/generated_by_test.txt")
        result.load()
        self.assertTrue(result.has(" this line should contain copyright, by it was manually deleted "))
        commands.process_command("test_template")
        try:
            commands.process_command("exit")
            self.assertTrue(False)
        except exit_typo:
            pass
        except:
            self.assertTrue(False)
        result.load()
        self.assertFalse(result.has(" this line should contain copyright, by it was manually deleted "))
        self.assertTrue(result.has(" just some user text inside the class "))  
        list = commands.process_command("list")
        self.assertEqual(list, "template_path = _dev/tests/templates\ncopyright = WGan (c) 2021\nfile_name = generated_by_test.txt\nvalue = val\nsimple_type_value = ${type} ${value};\npath = _dev/tests/outputs\ntype = double\nid = this is something important")

    def test_of_assignments_and_list(self):
        context = typo_context()
        processor = typo_processor(context)
        commands = command_processor(processor)
        commands._process_assignment("file_name = \"generated_by_test.txt\"")
        commands._process_assignment("copyright = WGan (c) 2021")
        text = commands._list_variables()
        self.assertEqual(text, "file_name = generated_by_test.txt\ncopyright = WGan (c) 2021")
        
    def test_of_import(self):
        context = typo_context()
        processor = typo_processor(context)
        commands = command_processor(processor)
        self.assertEqual("[]", str(context.modules))
        commands._process_import("import _test_module_2")
        self.assertEqual("[<module '_test_module_2' from '/Users/wgan/Documents/DEV/typo/typo/_test_module_2.pyc'>]", str(context.modules))
        
    def test_of_generation(self):
        context = typo_context()
        processor = typo_processor(context)
        commands = command_processor(processor)
        commands.process_command("template_path = _dev/tests/templates")
        commands.process_command("path = _dev/tests/outputs")
        commands.process_command("file_name = \"generated_by_test.txt\"")
        commands.process_command("copyright = WGan (c) 2021")
        commands.process_command("import _test_module_2")
        commands.process_command("id = this is something important")
        commands.process_command("simple_type_value = ${type} ${value};")
        commands.process_command("type = double")
        commands.process_command("value = val")
        result = file_checker("_dev/tests/outputs/generated_by_test.txt")
        result.copy_from("_dev/tests/inputs/generated_by_test.txt")
        result.load()
        self.assertTrue(result.has(" this line should contain copyright, by it was manually deleted "))
        commands._process_generation("test_template")
        result.load()
        self.assertFalse(result.has(" this line should contain copyright, by it was manually deleted "))
        self.assertTrue(result.has(" just some user text inside the class "))  
        
    def test_of_unknown_command_error(self):
        context = typo_context()
        processor = typo_processor(context)
        commands = command_processor(processor)
        try:
            commands.process_command("&^%XXXX")
            self.assertTrue(False)
        except cannot_execute_command as err:
            self.assertEqual(str(err), "I do not understand command '&^%XXXX'")
        except:
            self.assertTrue(False)
 
#-----------------------------------------------------------------       

class test_of_processing(unittest.TestCase):

    def test_processing_like_in_command_line(self):
        result = file_checker("_dev/tests/outputs/generated_by_test.txt")
        result.copy_from("_dev/tests/inputs/generated_by_test.txt")
        argv = ["test", "_dev/tests/scripts/first_test.typo"]
        result.load()
        self.assertTrue(result.has(" this line should contain copyright, by it was manually deleted "))
        typo_main(argv)
        result.load()
        self.assertFalse(result.has(" this line should contain copyright, by it was manually deleted "))
        self.assertTrue(result.has(" just some user text inside the class "))
        
#-----------------------------------------------------------------       

unittest.main()
