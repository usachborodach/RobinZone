import os

base_path = os.path.dirname(__file__)
yml_path = os.path.join(base_path, '..', 'yml')
scenes_path = os.path.join(base_path, '..', 'scenes')
for filename in os.listdir(yml_path):
    print(filename)
    content = open(f'{yml_path}/{filename}', encoding='utf-8').read()
    with open(f'{scenes_path}/{filename[:-3]}md', 'w', encoding='utf-8') as file:
        file.write(content)