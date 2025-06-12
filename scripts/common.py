import os
import yaml
import sys
import time
import random

base_path = os.path.dirname(__file__)

def load_situations():
    situations = dict()
    situations_path = os.path.join(base_path, '..', 'situations')
    for filename in os.listdir(situations_path):
        filepath = os.path.join(situations_path, filename)
        situation = yaml.safe_load(open(filepath))
        situation['text'] = '    ' + remove_slash_n_from_tail(situation['text']).replace('\n', '\n    ')
        situations[filename.replace('.yml', '')] = situation
    return situations

def typewrite(text, delay=0.001, random_delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        current_delay = delay + random.uniform(0, random_delay)
        time.sleep(current_delay)
        
def remove_slash_n_from_tail(text):
    while text.endswith('\n'):
        text = text[:-2]
    return text