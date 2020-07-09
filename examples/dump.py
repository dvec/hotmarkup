from hotmarkup import JsonConnection

connection = JsonConnection('dump_example.json', override={'changed': False})
print(open('dump_example.json').read())  # Out: {"changed": false}
connection.changed = True
print(open('dump_example.json').read())  # Out: {"changed": true}
