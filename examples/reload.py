from hotmarkup import JsonConnection

connection = JsonConnection('reload_example.json', default={'changed': False})
print(connection.changed)  # Out: False
with open('reload_example.json', 'w') as f:
    f.write('{"changed": true}')
print(connection.changed)  # Out: True
