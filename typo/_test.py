# (c) TYPO by WGan 2021



import unittest
import hashlib
import re

from typo_inputs    import  file_lines
from typo_outputs   import  indented_output, string_output
from typo_core      import  typo_context, module_not_loaded      
from typo_tools     import  typo_error
    
    
    
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
        
                
unittest.main()
