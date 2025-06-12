import yaml

with open('chapter.yml', encoding='utf-8') as file:
    data = yaml.safe_load(file)

print(data)