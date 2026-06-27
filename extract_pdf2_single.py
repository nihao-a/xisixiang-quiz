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

def parse_single_only(text, max_q_num=200):
    answers = {}
    
    ans_matches = re.findall(r'(\d+)\s*\.?\s*【答案】\s*([A-D]+)', text)
    for q_num_str, ans_letters in ans_matches:
        q_num = int(q_num_str)
        if len(ans_letters) == 1:
            answers[q_num] = ord(ans_letters[0].upper()) - ord('A')
    
    print(f'  单选题答案数量: {len(answers)}')
    
    q_section = text[:text.find('【答案】')] if '【答案】' in text else text
    
    q_starts = {}
    for m in re.finditer(r'(?m)^(\d+)[\.\．]\s', q_section):
        q_num = int(m.group(1))
        if 1 <= q_num <= max_q_num and q_num in answers:
            if q_num not in q_starts:
                q_starts[q_num] = m.end()
    
    print(f'  找到题目起始位置: {len(q_starts)} 个')
    
    sorted_nums = sorted(q_starts.keys())
    questions = []
    
    for idx, q_num in enumerate(sorted_nums):
        start = q_starts[q_num]
        
        next_start = len(q_section)
        for j in range(idx + 1, len(sorted_nums)):
            if q_starts[sorted_nums[j]] > start:
                next_start = q_starts[sorted_nums[j]]
                break
        
        q_content = q_section[start:next_start].strip()
        q_content = re.sub(r'\s+', '', q_content)
        
        opt_matches = list(re.finditer(r'[A-D][\.．、]', q_content))
        
        if len(opt_matches) < 4:
            continue
        
        q_text = q_content[:opt_matches[0].start()].strip()
        q_text = re.sub(r'[()（）]$', '', q_text).strip()
        
        if len(q_text) < 5:
            continue
        
        options = []
        valid = True
        for i, om in enumerate(opt_matches[:4]):
            opt_start = om.end()
            opt_end = opt_matches[i+1].start() if i+1 < len(opt_matches[:4]) else len(q_content)
            opt_text = q_content[opt_start:opt_end].strip()
            
            bad_patterns = ['2024考研', '第一部分', '习题190', '背诵手册', '单项选择', '多项选择', '一、题目']
            if any(p in opt_text for p in bad_patterns):
                valid = False
                break
            
            if opt_text and len(opt_text) > 1:
                options.append(opt_text)
        
        if not valid or len(options) < 4:
            continue
        
        ans_idx = answers[q_num]
        if ans_idx >= len(options):
            continue
        
        questions.append({
            'number': q_num,
            'question': q_text,
            'options': options,
            'answer': [ans_idx],
            'type': 'single'
        })
    
    return questions

def main():
    base_dir = r'C:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\第二套试题'
    
    pdf2_path = os.path.join(base_dir, '新思想习题190.pdf')
    text2 = extract_all_text(pdf2_path)
    
    print('提取 PDF2 单选题:')
    qs2 = parse_single_only(text2)
    print(f'  成功提取 {len(qs2)} 道单选题')
    
    print('\n前5题预览:')
    for q in qs2[:5]:
        ans = chr(65 + q['answer'][0])
        print(f'  第{q["number"]}题: {q["question"][:30]}... 答案:{ans}')
    
    print('\n后5题预览:')
    for q in qs2[-5:]:
        ans = chr(65 + q['answer'][0])
        print(f'  第{q["number"]}题: {q["question"][:30]}... 答案:{ans}')

if __name__ == '__main__':
    main()
