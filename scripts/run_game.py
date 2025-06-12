import os
import subprocess
import common

game_path = os.path.join(common.base_path, 'game.py')
subprocess.run(["gnome-terminal", "--geometry", "100x30", "--", "python3", game_path])