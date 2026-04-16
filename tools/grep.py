'''
This file contains a tool that searches files for matches to a regex.
'''

import glob
import re


def grep(pattern, path):
    '''
    This tool searches files for matches to a regex (pattern).

    >>> isinstance(grep('howdy', __file__), str)
    True

    >>> grep('this_is_not_match', __file__)
    ''

    >>> 'import re' in grep('import re', 'tools/grep.py')
    True

    >>> grep('anything', '/private/password')
    ''

    >>> grep('anything', '../private.txt')
    ''

    >>> grep('anything', None)
    ''

    >>> with open('bad_encoding.bin', 'wb') as f:
    ...     _ = f.write(bytes([255]))
    >>> grep('anything', 'bad_encoding.bin')
    ''

    '''
    result = ''

    try:
        if path.startswith('/') or '..' in path:
            return ''

        files = glob.glob(path)
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if re.search(pattern, line):
                            result += line
            except Exception:
                continue
    except Exception:
        return ''

    return result


tool_schema = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search for a pattern in a file",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Text to search for"
                },
                "path": {
                    "type": "string",
                    "description": "File to search in"
                }
            },
            "required": ["pattern", "path"]
        },
    },
}
