from hotmarkup import YamlConnection

connection = YamlConnection('counter_example.yaml', default={'counter': 0})
connection.counter += 1
print(f'You run this program {connection.counter} times')
