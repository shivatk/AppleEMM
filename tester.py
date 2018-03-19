import json
a = '{"a":"b"}'

b = json.loads(a)

print(b.get('b'))
