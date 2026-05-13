#!/usr/bin/env python3
import json
import os
import random
import time
import urllib.request

ENDPOINT_ID = os.getenv('VITE_RUNPOD_ENDPOINT_ID', 'aqzsu0jydlras1')
API_KEY = os.getenv('VITE_RUNPOD_API_KEY')
BASE = f'https://api.runpod.ai/v2/{ENDPOINT_ID}'

if not API_KEY:
    raise SystemExit('Missing VITE_RUNPOD_API_KEY in environment.')

with open('src/workflows/face-generation.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

seed = random.randint(1, 999999999999999)
wf['78']['inputs']['seed'] = seed
wf['14']['inputs']['noise_seed'] = random.randint(1, 999999999999999)
wf['73']['inputs']['seed'] = random.randint(1, 999999999999999)
wf['82']['inputs'].update({
    'brief_text': 'portrait photo of an afro-latina woman, elegant, realistic, editorial lighting',
    'ethnicity': 'Hispanic',
    'eye_color': 'green',
    'hair_structure': 'curly',
    'hair_color': 'jet black',
    'skin_tone': 'dark',
    'expression': 'confident',
    'photo_type': 'Studio white background',
})


def req(url, payload=None):
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    r = urllib.request.Request(url, data=data, headers=headers, method='GET' if payload is None else 'POST')
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

run = req(f'{BASE}/run', {'input': {'workflow': wf, 'job_name': 'latina_green_eyes_curly_darkskin'}})
job_id = run['id']
print('job_id:', job_id)

while True:
    data = req(f'{BASE}/status/{job_id}')
    status = data.get('status')
    print('status:', status)
    if status == 'COMPLETED':
        imgs = data.get('output', {}).get('images', [])
        if not imgs:
            raise SystemExit('Completed but no images in output.')
        os.makedirs('test-output', exist_ok=True)
        out_path = f'test-output/latina-green-eyes-curly-darkskin-{seed}.txt'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(imgs[0])
        print('saved base64 to', out_path)
        break
    if status in ('FAILED', 'CANCELLED', 'TIMED_OUT'):
        raise SystemExit(f'Job ended with {status}: {data}')
    time.sleep(4)
