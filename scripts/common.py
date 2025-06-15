import os
import yaml
import sys
import time
import random

base_path = os.path.dirname(__file__)

def load_scenes():
    scenes = dict()
    scenes_path = os.path.join(base_path, '..', 'scenes')
    for filename in os.listdir(scenes_path):
        filepath = os.path.join(scenes_path, filename)
        scene = yaml.safe_load(open(filepath))
        scene['text'] = remove_slash_n_from_tail(scene['text']).replace('\n', '\n    ')
        scenes[filename.replace('.yml', '')] = scene
    return scenes

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