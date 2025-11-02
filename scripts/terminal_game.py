import os
import common
import random

start_situation = 'nachalo'
use_typewrite = True

situations = common.load_scenes()


current_situation = start_situation
while True:
    os.system("clear")
    text = situations[current_situation]['text']
    if use_typewrite:
        common.typewrite(text)
    else:
        print(text)
    print(f"\n\n{'=' * 80}\n    Ваши действия:")
    actions = situations[current_situation]['actions']
    random.shuffle(actions)    
    for index, action in enumerate(actions):
        print(f'{index + 1}. {action["text"]}')
    choice = int(input('Ваш выбор: ')) - 1
    current_situation = situations[current_situation]['actions']['next']