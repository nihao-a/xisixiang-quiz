import json

qs = json.load(open('questions_second_set.json', encoding='utf-8'))
single = [q for q in qs if q['type']=='single']
multi = [q for q in qs if q['type']=='multiple']

print('总题数:', len(qs))
print('单选:', len(single), '多选:', len(multi))
print()

print('=== 前5道单选题 ===')
for i, q in enumerate(single[:5]):
    print(f'{i+1}. {q["question"][:50]}')
    for j, opt in enumerate(q['options']):
        print(f'   {chr(65+j)}. {opt[:40]}')
    ans = ''.join([chr(65+a) for a in q['answer']])
    print(f'   答案: {ans}')
    print()

print('=== 前3道多选题 ===')
for i, q in enumerate(multi[:3]):
    print(f'{i+1}. {q["question"][:50]}')
    for j, opt in enumerate(q['options']):
        print(f'   {chr(65+j)}. {opt[:40]}')
    ans = ''.join([chr(65+a) for a in q['answer']])
    print(f'   答案: {ans}')
    print()
