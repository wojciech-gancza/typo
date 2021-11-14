# (c) TYPO by WGan 2021



import unittest

from typo_core      import  typo_context       
from typo_tools     import  typo_error
    
    

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
        
        
        
unittest.main()
