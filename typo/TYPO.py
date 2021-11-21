# (c) TYPO by WGan 2021


import os
import sys

from typo_core import typo_error
from typo_inputs import file_lines
from typo_interpreter import command_processor, exit_typo, typo_processor


""" main function of typo interpreter - allow use typo as command line tool 
    or use it in matches processing set of orders located in a file """
def typo_main(argv):
    try:
        init_file_name = "init.typo"
        if len(argv) > 1:
            init_file_name = argv[1]
            if not os.path.isfile(init_file_name):
                raise typo_error("File '" + init_file_name + "' not found")
            
        typo = typo_processor()
        processor = command_processor(typo)
    
        init = file_lines(init_file_name)
        line_number = 1
        for init_line in init:
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
        
    except typo_error as err:
        print("FATAL: " + str(err))

    
if __name__ == "__main__":
    typo_main(sys.argv)
