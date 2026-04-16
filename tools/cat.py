'''
This file contains a tool that opens a file and outputs contents as a string.
'''


def cat(filename):
    '''
    This tool opens a file and outputs the contents as a string.

    >>> isinstance(cat(__file__), str)
    True

    >>> cat('fake_file.txt')
    'Error: file not found'

    >>> with open('test_utf16.txt', 'w', encoding='utf-16') as f:
    ...     _ = f.write('howdy')
    >>> cat('test_utf16.txt')
    'howdy'

    >>> with open('bad_encoding.bin', 'wb') as f:
    ...     _ = f.write(bytes([255]))
    >>> cat('bad_encoding.bin')
    'Error: cannot read file'

    >>> cat(None)
    'Error: cannot read file'
    '''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except UnicodeDecodeError:
        try:
            with open(filename, 'r', encoding='utf-16') as f:
                return f.read()
        except Exception:
            return 'Error: cannot read file'
    except Exception:
        return 'Error: cannot read file'


tool_schema = {
    "type": "function",
    "function": {
        "name": "cat",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Path to the file"
                }
            },
            "required": ["filename"]
        },
    },
}
