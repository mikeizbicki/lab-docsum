'''
This file contains a function that behaves like the ls program in the shell.
'''

# step 1: create function with the right number of args; write the docstring
# step 2: create the doctests for that function
# step 3: get the function to pass doctest
# step 3b: may have to modify doctests to get them to pass
# step 4: you know you have enough doctests if you have 100% code coverage

import glob


def ls(folder=None):
    '''
    This function behaves just like the ls program in the shell.

    >>> 'chat.py' in ls()
    True
    >>> 'tools' in ls()
    True
    >>> 'tools/cat.py' in ls('tools')
    True
    '''
    result = ''

    if folder:
        for path in sorted(glob.glob(folder + '/*')):
            result += path + ' '
    else:
        for path in sorted(glob.glob('*')):
            result += path + ' '
    return result.strip()


tool_schema = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Optional folder to list"
                }
            },
            "required": []
        },
    },
}
