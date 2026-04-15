'''
This file contains the main chat application logic/REPL for the LLM program.
It coordinates the LLM conversation flow and manages both manual slash-command
tool usage and automatic tool usage.
'''

import json
import os
from groq import Groq
from tools.calculate import calculate, tool_schema

from dotenv import load_dotenv
load_dotenv()

# in python class names are in CamelCase:
# non-class names (e.g. function/variable) are in snake_case:


class Chat:
    '''
    The Chat class manages conversations with the language model.
    It sends user input to the GROQ API, handles the
    calling of tools if needed, and returns the response.
    It also stores message history.

    >>> chat = Chat()
    >>> 'Bob' in chat.send_message('my name is Bob', temperature=0.0)
    True
    >>> 'Bob' in chat.send_message('what is my name?', temperature=0.0)
    True

    >>> chat2 = Chat()
    >>> 'I don’t have any information' in chat2.send_message(
    ...     'what is my name?',
    ...     temperature=0.0
    ... )
    True

    >>> result = chat.send_message('calculate 2 + 2', temperature=0.0)
    [tool] function_name=calculate, function_args={'expression': '2 + 2'}
    >>> '4' in result or 'result' in result
    True
    '''

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODEL = "openai/gpt-oss-120b"

    def __init__(self):
        ''' Initialize Chat object with default prompt
        and empty message history.'''
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Write output in 1-2 sentences. Always use tools for "
                    "tasks when appropriate. Don't bold the answer."
                    )
            }
        ]

    def send_message(self, message, temperature=0.8):
        '''Send a message to the language model and return response.'''
        self.messages.append(
            {
                # system: never change; user: changes a lot
                # the message that you are sending to the AI
                'role': 'user',
                'content': message
            }
        )
        # define tools
        tools = [tool_schema]

        # in order to make non deterministic code deterministic:
        # in this case, has a 'temperature' param that controls randomness:
        # the higher the value, the more randomness;
        # higher temperature = more creativity
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            # model="llama-3.1-8b-instant",
            model=self.MODEL,
            temperature=temperature,
            seed=0,
            tools=tools,
            tool_choice="auto"
        )

        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls

        # Step 2: Check if the model wants to call tools
        if tool_calls:
            # Map function names to implementations
            available_functions = {
                "calculate": calculate,
            }

            # Add the assistant's response to conversation
            self.messages.append(response_message)

            # Step 3: Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    expression=function_args.get("expression")
                )
                print(
                    f"[tool] function_name={function_name}, "
                    f"function_args={function_args}"
                    )

                # Add tool response to conversation
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

            # Step 4: Get final response from model
            second_response = self.client.chat.completions.create(
                model='openai/gpt-oss-120b',
                messages=self.messages,
                temperature=temperature,
                seed=0
            )
            result = second_response.choices[0].message.content
            self.messages.append({
                'role': 'assistant',
                'content': result
            })
        # tell LLM what we were previously talking about
        else:
            result = chat_completion.choices[0].message.content
            self.messages.append({
                'role': 'assistant',
                'content': result
            })
        return result

# this makes the user interface nicer by saying 'chat>'
# repl: reads input and evaluates input


def repl(temperature=0.8):
    '''
    Runs an interactive chat loop that processes user input,
    handles automatic and manual slash commands, and
    returns the model's response.

    # doctests for manual LLM calls
    >>> def monkey_input(prompt, user_inputs=['/ls tools']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0) # doctest: +ELLIPSIS
    chat> /ls tools
    ...
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/cat tools/ls.py']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0) # doctest: +ELLIPSIS
    chat> /cat tools/ls.py
    ...
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/ls']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)  # doctest: +ELLIPSIS
    chat> /ls
    ...
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/cat']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /cat
    Invalid usage of cat
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/grep import tools/grep.py']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0) # doctest: +ELLIPSIS
    chat> /grep import tools/grep.py
    ...
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/grep onlyonearg']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /grep onlyonearg
    Invalid usage of grep
    <BLANKLINE>


    >>> def monkey_input(prompt, user_inputs=['/calculate 1 + 3']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /calculate 1 + 3
    {"result": 4}
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/calculate']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /calculate
    Invalid usage of calculate
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/', '']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0) # doctest: +ELLIPSIS
    chat> /
    chat>
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/unknown']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /unknown
    Command unknown
    <BLANKLINE>

    >>> def monkey_input(
    ...     prompt,
    ...     user_inputs=['Hello, I am monkey.', 'Goodbye.']
    ... ):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0) # doctest: +ELLIPSIS
    chat> Hello, I am monkey.
    ...
    chat> Goodbye.
    ...
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/unknown']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /unknown
    Command unknown
    <BLANKLINE>
    '''

    # import readline
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')

            # manual tool call
            if user_input.startswith('/'):
                parts = user_input[1:].split()
                if not parts:
                    continue

                command = parts[0]
                args = parts[1:]

                if command == 'ls':
                    from tools.ls import ls
                    if len(args) == 0:
                        print(ls())
                    else:
                        print(ls(args[0]))
                elif command == 'cat':
                    from tools.cat import cat
                    if len(args) == 1:
                        print(cat(args[0]))
                    else:
                        print('Invalid usage of cat')
                elif command == 'grep':
                    from tools.grep import grep
                    if len(args) == 2:
                        print(grep(args[0], args[1]))
                    else:
                        print('Invalid usage of grep')
                elif command == 'calculate':
                    from tools.calculate import calculate
                    if len(args) >= 1:
                        expression = ' '.join(args)
                        print(calculate(expression))
                    else:
                        print('Invalid usage of calculate')
                else:
                    print('Command unknown')

                continue
            # automatic LLM call
            else:
                if not user_input.strip():
                    continue
                response = chat.send_message(
                    user_input,
                    temperature=temperature
                    )
                print(response)
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == '__main__':
    repl()
