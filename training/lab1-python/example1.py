#!/usr/bin/env python3
"""
This is my script...
"""

def main(arg1, arg2):
    """This is my main function"""
    print(arg1)
    print(arg2)    

def say_hello():
    print('hello\n')

if __name__ == '__main__':
    myarg1 = 'argval1'
    myarg2 = 'argval2'

    print(f'Running main fuction for {myarg1} and {myarg2}')
    main(myarg1, myarg2)
    print('\n')

    print('Also running main function for textval1 and textval2')
    main('textval1', 'textval2')

    print(__doc__)

    print(main.__doc__)
