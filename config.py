import os
from pathlib import Path

def get_api_key():
    config_file = Path.home() / '.reservation_calendar' / 'config.txt'
    
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            f.write('YOUR_API_KEY')
    
    with open(config_file) as f:
        return f.read().strip()