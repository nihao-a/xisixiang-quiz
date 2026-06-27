import json

with open('questions.json', 'r', encoding='utf-8') as f:
    old_questions = json.load(f)

with open('questions_second_set.json', 'r', encoding='utf-8') as f:
    new_questions = json.load(f)

print(f'原有题目: {len(old_questions)} 道')
single_old = sum(1 for q in old_questions if q['type'] == 'single')
multi_old = sum(1 for q in old_questions if q['type'] == 'multiple')
print(f'  单选: {single_old}, 多选: {multi_old}')

print(f'\n新增题目: {len(new_questions)} 道')
single_new = sum(1 for q in new_questions if q['type'] == 'single')
multi_new = sum(1 for q in new_questions if q['type'] == 'multiple')
judge_new = sum(1 for q in new_questions if q['type'] == 'judge')
print(f'  单选: {single_new}, 多选: {multi_new}, 判断: {judge_new}')

all_questions = old_questions + new_questions

seen = set()
unique_questions = []
for q in all_questions:
    key = q['question'][:40]
    if key not in seen:
        seen.add(key)
        unique_questions.append(q)

print(f'\n合并后去重: {len(unique_questions)} 道')
single_all = sum(1 for q in unique_questions if q['type'] == 'single')
multi_all = sum(1 for q in unique_questions if q['type'] == 'multiple')
judge_all = sum(1 for q in unique_questions if q['type'] == 'judge')
print(f'  单选: {single_all}, 多选: {multi_all}, 判断: {judge_all}')

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(unique_questions, f, ensure_ascii=False, indent=2)

print('\n已保存到 questions.json')
