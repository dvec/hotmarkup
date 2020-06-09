# HOTMARKUP
#### Python configuration as it should be

Currently supported formats: **YAML**, **JSON**, **Pickle**

#### Main features:
 - Work with Connection object as usual data structure. You can use features like array slices or methods of `dict` and `list`
 - JS-like accessing (foo.bar.buzz instead of foo['bar']['buzz'])
 - Modifications logging via `logging` module. Example below
 - Reload on file change (pass `reload=False` to connection constructor to disable)
 - Dump file on every change (pass `dump=False` to connection constructor to disable)
 - Immutable connections (pass `mutable=False` to connection constructor to enable)
## Examples
#### Reload
```python
from hotmarkup import JsonConnection

connection = JsonConnection('example.json', default={'changed': False})
print(connection.changed)  # Out: False
with open('example.json', 'w') as f:
    f.write('{"changed": true}')
print(connection.changed)  # Out: True
```
#### Dump
```python
from hotmarkup import JsonConnection

connection = JsonConnection('example.json', default={'changed': False})
print(open('example.json').read())  # Out: {"changed": false}
connection.changed = True
print(open('example.json').read())  # Out: {"changed": true}
```
#### Logging
```python
import logging
from hotmarkup import YamlConnection

logging.basicConfig(level=logging.INFO)
connection = YamlConnection('example.yaml', default={'something_important': 'old_value'})

connection.something_important = 'new_value'
```
Output:
```
INFO:example.yaml:Loaded example.yaml config: {'something_important': 'old_value'}
INFO:example.yaml:Setting 'something_important' to 'new_value'
```
#### Counter
```python
from hotmarkup import YamlConnection

connection = YamlConnection('counter.yaml', default={'counter': 0})
connection.counter += 1
print(f'You run this program {connection.counter} times')
```
