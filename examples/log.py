import logging
from hotmarkup import YamlConnection

logging.basicConfig(level=logging.INFO)
connection = YamlConnection('log_example.yaml', default={'something_important': 'old_value'})

connection.something_important = 'new_value'
