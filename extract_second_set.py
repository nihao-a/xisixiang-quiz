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

def split_options_from_line(line):
    opts = []
    pattern = re.compile(r'([A-D])[、.．](.+?)(?=[A-D][、.．]|$)')
    matches = pattern.findall(line)
    for m in matches:
        opts.append((m[0], m[1].strip()))
    return opts

def parse_pdf1_questions(text):
    questions = []
    
    text = re.sub(r'\r', '', text)
    text = re.sub(r' +', ' ', text)
    
    pattern = re.compile(
        r'(\d+)．(.+?)(?=\d+．|正确答案)',
        re.DOTALL
    )
    
    ans_pattern = re.compile(r'正确答案：([A-D]+)')
    
    pos = 0
    while True:
        m = pattern.search(text, pos)
        if not m:
            break
        
        q_num = int(m.group(1))
        q_content = m.group(2).strip()
        
        ans_m = ans_pattern.search(text, m.end())
        answer = None
        if ans_m and ans_m.start() - m.end() < 500:
            ans_letters = ans_m.group(1).upper()
            answer = [ord(c) - ord('A') for c in ans_letters]
        
        q_content = re.sub(r'\s+', '', q_content)
        
        opt_matches = list(re.finditer(r'[A-D][、.．]', q_content))
        
        if len(opt_matches) >= 2:
            q_text = q_content[:opt_matches[0].start()].strip()
            q_text = re.sub(r'[()（）]$', '', q_text).strip()
            
            options = []
            for i, om in enumerate(opt_matches):
                opt_letter = q_content[om.start()]
                opt_start = om.end()
                opt_end = opt_matches[i+1].start() if i+1 < len(opt_matches) else len(q_content)
                opt_text = q_content[opt_start:opt_end].strip()
                if opt_text:
                    options.append(opt_text)
            
            if len(options) >= 2 and answer is not None:
                q_type = 'multiple' if len(answer) > 1 else 'single'
                questions.append({
                    'number': q_num,
                    'question': q_text,
                    'options': options,
                    'answer': answer,
                    'type': q_type
                })
        
        pos = m.end()
    
    return questions

def parse_pdf2_questions_and_answers(text):
    questions = []
    answers = {}
    
    text = re.sub(r'\r', '', text)
    
    ans_section_match = re.search(r'【答案】', text)
    if ans_section_match:
        q_text_part = text[:ans_section_match.start()]
        ans_text_part = text[ans_section_match.start():]
    else:
        q_text_part = text
        ans_text_part = ''
    
    ans_matches = re.findall(r'(\d+)\s*\.?\s*【答案】\s*([A-D]+)', ans_text_part)
    for q_num_str, ans_letters in ans_matches:
        q_num = int(q_num_str)
        answers[q_num] = [ord(c) - ord('A') for c in ans_letters.upper()]
    
    q_text_part = re.sub(r' +', ' ', q_text_part)
    
    pattern = re.compile(
        r'(\d+)[\.．]\s*(.+?)(?=\d+[\.．]\s|$)',
        re.DOTALL
    )
    
    for m in pattern.finditer(q_text_part):
        q_num = int(m.group(1))
        if q_num > 200:
            continue
        if q_num not in answers:
            continue
            
        q_content = m.group(2).strip()
        q_content = re.sub(r'\s+', '', q_content)
        
        if re.match(r'^(一|二|三|四)[)）]', q_content) or '单项选择' in q_content or '多项选择' in q_content:
            continue
        
        opt_matches = list(re.finditer(r'[A-D][\.．、]', q_content))
        
        if len(opt_matches) >= 2:
            q_text = q_content[:opt_matches[0].start()].strip()
            q_text = re.sub(r'[()（）]$', '', q_text).strip()
            
            options = []
            for i, om in enumerate(opt_matches):
                opt_start = om.end()
                opt_end = opt_matches[i+1].start() if i+1 < len(opt_matches) else len(q_content)
                opt_text = q_content[opt_start:opt_end].strip()
                if opt_text:
                    options.append(opt_text)
            
            if len(options) >= 2:
                answer = answers[q_num]
                q_type = 'multiple' if len(answer) > 1 else 'single'
                questions.append({
                    'number': q_num,
                    'question': q_text,
                    'options': options,
                    'answer': answer,
                    'type': q_type
                })
    
    return questions

def main():
    base_dir = r'C:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\第二套试题'
    
    pdf1_path = os.path.join(base_dir, '习思想选择题（刷这套）.pdf')
    pdf2_path = os.path.join(base_dir, '新思想习题190.pdf')
    
    print('=' * 60)
    print('提取 PDF1: 习思想选择题（刷这套）.pdf')
    text1 = extract_all_text(pdf1_path)
    qs1 = parse_pdf1_questions(text1)
    print(f'  提取到 {len(qs1)} 道有效题目')
    
    bad1 = [q for q in qs1 if len(q['options']) < 4]
    if bad1:
        print(f'  其中选项少于4个: {len(bad1)} 道')
        for q in bad1[:5]:
            print(f'    第{q["number"]}题: {q["question"][:20]}... 选项数:{len(q["options"])}')
    
    print('\n' + '=' * 60)
    print('提取 PDF2: 新思想习题190.pdf')
    text2 = extract_all_text(pdf2_path)
    qs2 = parse_pdf2_questions_and_answers(text2)
    print(f'  提取到 {len(qs2)} 道有效题目')
    
    bad2 = [q for q in qs2 if len(q['options']) < 4]
    if bad2:
        print(f'  其中选项少于4个: {len(bad2)} 道')
        for q in bad2[:5]:
            print(f'    第{q["number"]}题: {q["question"][:20]}... 选项数:{len(q["options"])}')
    
    all_new_questions = []
    seen_questions = set()
    
    for q in qs1 + qs2:
        key = q['question'][:40]
        if key not in seen_questions:
            seen_questions.add(key)
            all_new_questions.append({
                'type': q['type'],
                'question': q['question'],
                'options': q['options'],
                'answer': q['answer'],
                'explanation': ''
            })
    
    print(f'\n' + '=' * 60)
    print(f'两套题共 {len(all_new_questions)} 道不重复题目')
    single_count = sum(1 for q in all_new_questions if q['type'] == 'single')
    multi_count = sum(1 for q in all_new_questions if q['type'] == 'multiple')
    print(f'  单选题: {single_count} 道')
    print(f'  多选题: {multi_count} 道')
    
    output_path = r'c:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\试题与解析\questions_second_set.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_new_questions, f, ensure_ascii=False, indent=2)
    
    print(f'\n已保存到: {output_path}')
    
    print('\n前5道题预览：')
    for i, q in enumerate(all_new_questions[:5]):
        ans = ''.join([chr(65+a) for a in q['answer']])
        print(f'  {i+1}. [{q["type"]}] {q["question"][:30]}... 答案:{ans} 选项数:{len(q["options"])}')

if __name__ == '__main__':
    main()
