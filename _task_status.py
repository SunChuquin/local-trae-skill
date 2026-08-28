import urllib.request, json

r = urllib.request.urlopen('http://127.0.0.1:8000/api/documents/upload-tasks', timeout=5)
d = json.loads(r.read().decode('utf-8'))
for t in d.get('data', []):
    print(f"{t['filename'][:45]:45s} | {t['status']:10s} | {t.get('phase',''):10s} | {t.get('done',0)}/{t.get('total',0)} | {t.get('error','')}")
