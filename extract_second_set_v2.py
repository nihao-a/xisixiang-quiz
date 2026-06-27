import fitz
import re
import json
import os

def extract_all_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def parse_pdf1_all(text):
    questions = []
    
    text = re.sub(r'\r', '', text)
    text = re.sub(r' +', ' ', text)
    
    lines = text.split('\n')
    all_text = ''
    for line in lines:
        line = line.strip()
        if line:
            all_text += line + '\n'
    
    i = 0
    lines = all_text.split('\n')
    
    current_q = None
    collecting_opts = False
    
    def save_current():
        nonlocal current_q
        if current_q and current_q.get('question'):
            if current_q['type'] == 'judge':
                if current_q.get('answer') is not None:
                    questions.append(current_q)
            elif len(current_q.get('options', [])) >= 2 and current_q.get('answer'):
                questions.append(current_q)
        current_q = None
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        q_match = re.match(r'^(\d+)[\.．](.*)', line)
        new_judge_match = re.match(r'^【新】(.*)', line)
        
        is_new_judge = False
        q_text_start = ''
        
        if q_match and not re.match(r'^[A-D][\.\．、]', line):
            q_num = int(q_match.group(1))
            q_text_start = q_match.group(2).strip()
            
            if q_num < 1 or q_num > 500:
                i += 1
                continue
            
            save_current()
            
            current_q = {
                'number': q_num,
                'question': q_text_start,
                'options': [],
                'answer': None,
                'type': None,
                'explanation': ''
            }
            collecting_opts = False
            i += 1
            continue
        
        if new_judge_match:
            save_current()
            q_text_start = new_judge_match.group(1).strip()
            current_q = {
                'number': 0,
                'question': q_text_start,
                'options': [],
                'answer': None,
                'type': None,
                'explanation': ''
            }
            collecting_opts = False
            i += 1
            continue
        
        if current_q is None:
            i += 1
            continue
        
        ans_match = re.search(r'正确答案[：:]\s*(对|错|[A-Z]+)', line)
        if ans_match:
            ans_val = ans_match.group(1).strip()
            
            if ans_val in ['对', '错']:
                current_q['type'] = 'judge'
                current_q['answer'] = [1] if ans_val == '对' else [0]
                current_q['options'] = ['错误', '正确']
            else:
                ans_letters = ans_val.upper()
                if len(ans_letters) >= 1 and all(c in 'ABCDEFGH' for c in ans_letters):
                    current_q['type'] = 'multiple' if len(ans_letters) > 1 else 'single'
                    current_q['answer'] = [ord(c) - ord('A') for c in ans_letters]
            
            rest = line[ans_match.end():].strip()
            if rest and len(rest) > 2:
                current_q['explanation'] = rest
            
            collecting_opts = False
            i += 1
            continue
        
        if '解析' in line and current_q.get('answer') is not None:
            exp_start = line[line.find('解析'):].strip()
            if current_q['explanation']:
                current_q['explanation'] += '\n' + exp_start
            else:
                current_q['explanation'] = exp_start
            i += 1
            
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                if re.match(r'^(\d+)[\.．]', next_line) or re.match(r'^【新】', next_line) or re.search(r'正确答案[：:]', next_line):
                    break
                if len(next_line) > 2:
                    current_q['explanation'] += '\n' + next_line
                i += 1
            continue
        
        opt_match = re.match(r'^([A-H])[\.\．、](.*)', line)
        if opt_match and current_q.get('answer') is None:
            opt_letter = opt_match.group(1)
            opt_text = opt_match.group(2).strip()
            
            current_q['options'].append(opt_text)
            collecting_opts = True
            i += 1
            
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                if re.match(r'^[A-H][\.\．、]', next_line):
                    break
                if re.search(r'正确答案[：:]', next_line):
                    break
                if re.match(r'^(\d+)[\.．]', next_line) and not re.match(r'^[A-H][\.\．、]', next_line):
                    break
                
                if current_q['options']:
                    current_q['options'][-1] += next_line
                i += 1
            continue
        
        if current_q.get('answer') is None and not collecting_opts:
            current_q['question'] += line
        elif collecting_opts and current_q['options']:
            current_q['options'][-1] += line
        
        i += 1
    
    save_current()
    
    valid_questions = []
    seen = set()
    for q in questions:
        key = q['question'][:40]
        if key in seen:
            continue
        seen.add(key)
        
        if q['type'] == 'judge':
            valid_questions.append({
                'type': 'judge',
                'question': q['question'],
                'options': q['options'],
                'answer': q['answer'],
                'explanation': q.get('explanation', '')
            })
        elif len(q['options']) >= 2 and q['answer']:
            max_ans = max(q['answer']) if q['answer'] else -1
            if max_ans < len(q['options']):
                valid_questions.append({
                    'type': q['type'],
                    'question': q['question'],
                    'options': q['options'],
                    'answer': q['answer'],
                    'explanation': q.get('explanation', '')
                })
    
    return valid_questions

def main():
    base_dir = r'C:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\第二套试题'
    pdf1_path = os.path.join(base_dir, '习思想选择题（刷这套）.pdf')
    
    print('=' * 60)
    print('提取 PDF1: 习思想选择题（刷这套）.pdf')
    text1 = extract_all_text(pdf1_path)
    qs = parse_pdf1_all(text1)
    
    single = [q for q in qs if q['type'] == 'single']
    multi = [q for q in qs if q['type'] == 'multiple']
    judge = [q for q in qs if q['type'] == 'judge']
    
    print(f'\n总提取: {len(qs)} 道')
    print(f'  单选题: {len(single)} 道')
    print(f'  多选题: {len(multi)} 道')
    print(f'  判断题: {len(judge)} 道')
    
    output_path = r'c:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\试题与解析\questions_second_set.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)
    
    print(f'\n已保存到: {output_path}')
    
    print('\n=== 前3道单选题 ===')
    for i, q in enumerate(single[:3]):
        ans = ''.join([chr(65+a) for a in q['answer']])
        print(f'  {i+1}. {q["question"][:30]}... 答案:{ans} 选项:{len(q["options"])}')
    
    print('\n=== 前3道多选题 ===')
    for i, q in enumerate(multi[:3]):
        ans = ''.join([chr(65+a) for a in q['answer']])
        print(f'  {i+1}. {q["question"][:30]}... 答案:{ans} 选项:{len(q["options"])}')
    
    print('\n=== 前3道判断题 ===')
    for i, q in enumerate(judge[:3]):
        ans = '正确' if q['answer'][0] == 1 else '错误'
        print(f'  {i+1}. {q["question"][:40]}... 答案:{ans}')
        if q.get('explanation'):
            print(f'     解析: {q["explanation"][:30]}...')

if __name__ == '__main__':
    main()
