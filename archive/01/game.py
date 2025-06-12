import os
import json
import time
import random
import sys
base_path = os.path.dirname(__file__)

def parse_the_chapter():
    separator = f'%%{"="*64}\n'
    chapter_path = os.path.join(base_path, 'mvp_chapter.mmd')
    chapter = open(chapter_path, encoding='utf-8').read().split(separator)
    del chapter[0]
    data = dict()
    for situation in chapter:
        situation = situation.splitlines()
        situation_id = situation[0].split('(')[0]
        data[situation_id] = dict()
        data[situation_id]['text'] = situation[1][2:]
        data[situation_id]['actions'] = list()
        for line_index in range(2, len(situation)):
            action_data = dict()
            action_data['direction'] = situation[line_index].split('--> ')[1]
            action_data['action_text'] = situation[line_index].split(' -- ')[1].split(' -->')[0]
            data[situation_id]['actions'].append(action_data)
    return data

def dump_to_json(data):
    test_path = os.path.join(base_path, 'parsing_debug.json')
    with open(test_path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)

def typewrite(text, delay=0.001, random_delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        current_delay = delay + random.uniform(0, random_delay)
        time.sleep(current_delay)

def play_the_game(data):
    start_situation = 'A'
    current_situation = start_situation
    while True:
        os.system("clear")
        text = data[current_situation]['text'].replace('\\n', '\n')
        if debug:
            print(text)
        else:
            typewrite(text)
        print('\n\nВаши действия:')
        for index, action in enumerate(data[current_situation]['actions']):
            print(f'{index + 1}. {action["action_text"]}')
        choice = int(input('Ваш выбор: '))
        direction = data[current_situation]['actions'][choice - 1]['direction']
        if direction == 'GAME_OVER':
            print('До свидания!')
            time.sleep(1)
            exit()
        else:
            current_situation = direction

debug = False
data = parse_the_chapter()
dump_to_json(data)
play_the_game(data)