# secrets.py

import os

class MySecrets:
    def __init__(self, secrets_file='config/my_secrets.txt'):
        self._secrets_file = secrets_file
        self._keys = {}
        self._load_secrets()

    def _load_secrets(self):
        if not os.path.exists(self._secrets_file):
            os.makedirs(os.path.dirname(self._secrets_file), exist_ok=True)
            open(self._secrets_file, 'w').close()
        with open(self._secrets_file, 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                self._keys[key] = value

    def add_key(self, key, value):
        self._keys[key] = value
        with open(self._secrets_file, 'a') as file:
            file.write(f'{key}={value}\n')

    def __getattr__(self, key):
        if key in self._keys:
            return self._keys[key]
        raise AttributeError(f"'Secrets' object has no attribute '{key}'")

# Initialize an instance of Secrets
sh = MySecrets()

# Add initial keys (optional)

# Usage in other scripts
# from secrets import MySecrets
# print(sh.openai)
# sh.add_key('census', 'your_census_api_key_here')
