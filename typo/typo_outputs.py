# (c) TYPO by WGan 2021


from typo_base import typo_error


""" interface to any outputs """
class output:

    def write(self, text):
        pass
        
            
""" console - each write operation denotes one line """
class console_output(output):

    def write(self, text):
        print(text)
        
                
""" base output decorator to create data flow modification of output """
class output_decorator(output):

    def __init__(self, output):
        self.output = output
        
    def write_on_output(self, text):
        self.output.write(text)
        
     
""" output splitting files """
class line_split_decorator(output_decorator):

    def __init__(self, output):
        output_decorator.__init__(self, output)
        self.line_buffer = ""
        
    def write(self, text):
        text = self.line_buffer + text
        lines = text.split("\n")  
        self.line_buffer = lines[-1]
        lines.pop(-1)
        
        for line in lines:
            self.write_on_output(line)
            

""" source of the text - used as base class of varous data """
class text_source:

    def get(self):
        pass


""" indentation allow to return indent text """
class indentation(text_source):

    def __init__(self, step):
        self.value = 0;
        self.step = step
        
    def increase(self):
        self.value = self.value + 1
        
    def decrease(self):
        self.value = self.value - 1
        
    def set(self, amount_of_spaces):
        self.value = int(amount_of_spaces / self.step)
        
    def get(self):
        return " " * (self.value * self.step)
                

""" decorates each data with prefix  """
class prefixing_output_decorator(output_decorator):

    def __init__(self, prefix_source, output):
        output_decorator.__init__(self, output)
        self.prefix_source = prefix_source
        
    def write(self, text):
        self.write_on_output(self.prefix_source.get() + text)
               
        
""" decorates each data with suffix  """
class sufixing_output_decorator(output_decorator):

    def __init__(self, output, sufix):
        output_decorator.__init__(self, output)
        self.sufix = sufix
        
    def write(self, text):
        self.write_on_output(text + self.sufix)
                
        
""" output storing indented lines with possibility to store already 
    formatted text - when contain whole lines """
class indented_output(line_split_decorator):

    def __init__(self, output, indent_step = 4):
        self.direct_output = output
        self.indent = indentation(indent_step)
        lines_output = sufixing_output_decorator(output, "\n")
        indented_output = prefixing_output_decorator(self.indent, lines_output)
        line_split_decorator.__init__(self, indented_output)

    def write_already_formatted(self, text):
        self.direct_output.write(text)
        
    def increase_indent(self):
        self.indent.increase()

    def decrease_indent(self):
        self.indent.decrease()
        
    def set_indent(self, amount_of_spaces):
        self.indent.set(amount_of_spaces)
        
    def flush(self):
        if self.line_buffer != "":
            self.write("\n")


""" output used to redirect output into string """
class string_output(output):

    def __init__(self):
        self.text = ""

    def write(self, text):
        self.text += text
                
""" when creating file - exception was raised """
class file_cannot_be_created(typo_error):

    def __init__(self, file_name):
        typo_error.__init__(self, "File '" + file_name + "' cannot be created.")

""" file output allows writing to the file on disk """
class file_output(output):

    def __init__(self, file_name):
        try:
            self.file = open(file_name, "w")
        except:
            raise file_cannot_be_created(file_name)

    def write(self, text):
        self.file.write(text)
    
    def close(self):
        self.file.close()
                
        