# HOTMARKUP
[![Build Status](https://travis-ci.com/dvec/hotmarkup.svg?branch=master)](https://travis-ci.com/dvec/hotmarkup)
#### Synchronize data structure with markup file

Currently supported formats: **YAML**, **JSON**, **Pickle**

#### Main features:
 - Work with Connection object as usual data structure. You can use features like array slices or methods of `dict` and `list`
 - JS-like accessing (foo.bar.buzz instead of foo['bar']['buzz'])
 - Mutations logging via `logging` module. Example below
 - Reload on file change (pass `reload=False` to connection constructor to disable)
 - Update file on every change (pass `save=False` to connection constructor to disable)
 - Immutable connections (pass `mutable=False` to connection constructor to enable)
## Installation
```shell script
pip install hotmarkup
```
## Examples
#### [Reload](https://github.com/dvec/hotmarkup/blob/master/examples/reload.py)
```python
from hotmarkup import JsonConnection

connection = JsonConnection('example.json', default={'changed': False})
print(connection.changed)  # Out: False
with open('example.json', 'w') as f:
    f.write('{"changed": true}')
print(connection.changed)  # Out: True
```
#### [Dump](https://github.com/dvec/hotmarkup/blob/master/examples/dump.py)
```python
from hotmarkup import JsonConnection

connection = JsonConnection('example.json', default={'changed': False})
print(open('example.json').read())  # Out: {"changed": false}
connection.changed = True
print(open('example.json').read())  # Out: {"changed": true}
```
#### [Logging](https://github.com/dvec/hotmarkup/blob/master/examples/log.py)
```python
import logging
from hotmarkup import YamlConnection

logging.basicConfig(level=logging.INFO)
connection = YamlConnection('example.yaml', default={'something_important': 'old_value'})
connection.something_important = 'new_value'
```
Output:
```
INFO:example.yaml:Mutation UPDATE example.yaml.something_important=new_value
```
#### [Counter](https://github.com/dvec/hotmarkup/blob/master/examples/counter.py)
```python
from hotmarkup import YamlConnection

connection = YamlConnection('counter.yaml', default={'counter': 0})
connection.counter += 1
print(f'You run this program {connection.counter} times')
```
