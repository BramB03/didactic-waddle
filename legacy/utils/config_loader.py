import json
import os

def load_config():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the config file relative to the script directory
    config_path = os.path.join(script_dir, '..', '.config', 'config.json')

    # Load the configuration file
    with open(config_path, 'r') as file:
        config = json.load(file)

    return config