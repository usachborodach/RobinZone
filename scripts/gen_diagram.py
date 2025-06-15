import os
import common

scenes = common.load_scenes()
diagram = ['flowchart TD']

for id, scene in scenes.items():
    object_manifest = f"{id}(\"{id.replace('_', ' ')}\")"
    diagram.append(object_manifest)
    if 'actions' in scene.keys():
        if isinstance(scene['actions'], list):
            for action in scene['actions']:
                diagram.append(f"{id} -- {action['text']} --> {action['next']}")

diagram = '\n'.join(diagram)
base_path = os.path.dirname(__file__)
output_path = os.path.join(base_path, '..', 'diagram.mmd')
with open(output_path, 'w', encoding='utf-8') as fp:
    fp.write(diagram)