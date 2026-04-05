import os
from groq import Groq

from dotenv import load_dotenv
load_dotenv()

# in python class names are in CamelCase: 
# non-class names (e.g. function/variable) are in snake_case: 
class Chat:
    '''
    >>> def monkey_input(prompt, user_inputs=['Hello, I am monkey.', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> Hello, I am monkey.
    Ooh ooh ah ah, hello there little monkey.
    chat> Goodbye.
    Ooh ooh ah ah, see you later monkey.
    <BLANKLINE>
    '''
    '''
    >>> chat = Chat()
    >>> chat.send_message('my name is Bob', temperature=0.0)
    "Hello Bob, it's nice to meet you."
    >>> chat.send_message('what is my name?', temperature=0.0)
    'Your name is Bob.'

    >>> chat2 = Chat()
    >>> chat2.send_message('what is my name?', temperature=0.0)
    "I don't have any information about your name. I'm a text-based AI assistant and our conversation just started, so I don't have any prior knowledge about you."
    '''
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences"
            },
        ]
    def send_message(self, message, temperature=0.8):
        self.messages.append(
            {
                # system: never change; user: changes a lot 
                # the message that you are sending to the AI
                'role': 'user', 
                'content': message
            }
        )
        # in order to make non deterministic code deterministic: 
        # in this case, has a 'temperature' param that controls randomness: 
        # the higher the value, the more randomness; 
        # higher temperature = more creativity
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.1-8b-instant",
            temperature=temperature,
        )
        result = chat_completion.choices[0].message.content
        self.messages.append({
            'role': 'assistant',
            'content': result
        })
        # tell LLM what we were previously talking about
        return result

# this makes the user interface nicer by saying 'chat>'
# repl: reads input and evaluates input
'''
if __name__ == '__main__': 
    chat = Chat()
    try:
        while True: 
                user_input = input('chat>')
                response = chat.send_message(user_input)
                print(response)
    except KeyboardInterrupt:
        print()
'''

def repl(temperature=0.8):
    import readline
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')
            response = chat.send_message(user_input, temperature = temperature)
            print(response)
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    repl()

