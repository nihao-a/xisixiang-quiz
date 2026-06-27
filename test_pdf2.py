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

def parse_pdf2_improved(text):
    answers = {}
    
    ans_matches = re.findall(r'(\d+)\s*\.?\s*【答案】\s*([A-D]+)', text)
    for q_num_str, ans_letters in ans_matches:
        q_num = int(q_num_str)
        answers[q_num] = [ord(c) - ord('A') for c in ans_letters.upper()]
    
    print(f'  找到答案: {len(answers)} 个')
    
    q_section = text[:text.find('【答案】')] if '【答案】' in text else text
    
    q_positions = []
    for m in re.finditer(r'(?m)^(\d+)[\.\．]\s', q_section):
        q_num = int(m.group(1))
        if 1 <= q_num <= 200:
            q_positions.append((q_num, m.start(), m.end()))
    
    print(f'  找到题目起始位置: {len(q_positions)} 个')
    
    q_starts = {}
    for q_num, start, end in q_positions:
        if q_num not in q_starts:
            q_starts[q_num] = (start, end)
    
    questions = []
    
    sorted_nums = sorted(q_starts.keys())
    print(f'  题目编号范围: {sorted_nums[0]} - {sorted_nums[-1]}')
    print(f'  不重复题目数: {len(sorted_nums)}')
    
    for idx, q_num in enumerate(sorted_nums):
        if q_num not in answers:
            continue
            
        start, q_start_content = q_starts[q_num]
        
        next_q_num = None
        next_start = len(q_section)
        for j in range(idx + 1, len(sorted_nums)):
            candidate = sorted_nums[j]
            if candidate != q_num and q_starts[candidate][0] > start:
                next_q_num = candidate
                next_start = q_starts[candidate][0]
                break
        
        q_content = q_section[q_start_content:next_start].strip()
        
        q_content = re.sub(r'\s+', '', q_content)
        
        opt_matches = list(re.finditer(r'[A-D][\.．、]', q_content))
        
        if len(opt_matches) < 2:
            continue
        
        q_text = q_content[:opt_matches[0].start()].strip()
        q_text = re.sub(r'[()（）]$', '', q_text).strip()
        
        if len(q_text) < 5:
            continue
        
        options = []
        for i, om in enumerate(opt_matches):
            opt_start = om.end()
            opt_end = opt_matches[i+1].start() if i+1 < len(opt_matches) else len(q_content)
            opt_text = q_content[opt_start:opt_end].strip()
            
            bad_patterns = ['2024考研', '第一部分', '习题190', '背诵手册', '单项选择', '多项选择']
            if any(p in opt_text for p in bad_patterns):
                break
            
            if opt_text:
                options.append(opt_text)
        
        if len(options) < 2:
            continue
        
        answer = answers[q_num]
        max_ans_idx = max(answer) if answer else -1
        if max_ans_idx >= len(options):
            continue
        
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
    pdf2_path = os.path.join(base_dir, '新思想习题190.pdf')
    
    text2 = extract_all_text(pdf2_path)
    qs2 = parse_pdf2_improved(text2)
    print(f'\n  成功提取: {len(qs2)} 道题目')
    
    single = sum(1 for q in qs2 if q['type'] == 'single')
    multi = sum(1 for q in qs2 if q['type'] == 'multiple')
    print(f'  单选: {single}, 多选: {multi}')
    
    bad = [q for q in qs2 if len(q['options']) < 4]
    print(f'  选项<4的: {len(bad)} 道')
    
    for q in qs2[:5]:
        ans = ''.join([chr(65+a) for a in q['answer']])
        print(f'    第{q["number"]}题 [{q["type"]}] {q["question"][:30]}... 答案:{ans} 选项:{len(q["options"])}')

if __name__ == '__main__':
    main()
