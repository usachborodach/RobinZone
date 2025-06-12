import os
import common

situations = common.load_situations()
diagram = ['flowchart TD']

for id, situation in situations.items():
    object_manifest = f"{id}(\"{id.replace('_', ' ')}\")"
    diagram.append(object_manifest)
    if 'actions' in situation.keys():
        if isinstance(situation['actions'], list):
            for action in situation['actions']:
                diagram.append(f"{id} -- {action['text']} --> {action['situation']}")

diagram = '\n'.join(diagram)
base_path = os.path.dirname(__file__)
output_path = os.path.join(base_path, '..', 'diagram.mmd')
with open(output_path, 'w', encoding='utf-8') as fp:
    fp.write(diagram)