import json

with open('questions.json', 'r', encoding='utf-8') as f:
    old_questions = json.load(f)

with open('questions_second_set.json', 'r', encoding='utf-8') as f:
    new_questions = json.load(f)

print(f'原有题目: {len(old_questions)} 道')
types_old = {}
for q in old_questions:
    types_old[q['type']] = types_old.get(q['type'], 0) + 1
for k, v in types_old.items():
    print(f'  {k}: {v}')

print(f'\n新增题目: {len(new_questions)} 道')
types_new = {}
for q in new_questions:
    types_new[q['type']] = types_new.get(q['type'], 0) + 1
for k, v in types_new.items():
    print(f'  {k}: {v}')

all_questions = old_questions + new_questions

seen = set()
unique_questions = []
for q in all_questions:
    key = q['question'][:40]
    if key not in seen:
        seen.add(key)
        unique_questions.append(q)

print(f'\n合并后去重: {len(unique_questions)} 道')
types_all = {}
for q in unique_questions:
    types_all[q['type']] = types_all.get(q['type'], 0) + 1
for k, v in types_all.items():
    print(f'  {k}: {v}')

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(unique_questions, f, ensure_ascii=False, indent=2)

print('\n已保存到 questions.json')
