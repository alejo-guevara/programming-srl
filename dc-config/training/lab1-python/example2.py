#!/usr/bin/env python3
"""This is my python script."""

# import the standard python module ‘os’
import os

# import the ‘say_hello’ function from the ‘example1’ python script   
from example1 import say_hello

def show_files():
    working_dir = os.getcwd()
    file_list = os.listdir(working_dir)
    for f in file_list:
        if os.path.isfile(f):  # print only files
            print(f)

if __name__ == '__main__':
    say_hello() # from the imported example1 python script
    show_files()
    
