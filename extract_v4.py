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

def extract_questions_from_section(text, is_judge=False):
    questions = []
    
    text = re.sub(r'\r', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    if is_judge:
        pattern = re.compile(
            r'(\d+)[\.\．]\s*(.+?)正确答案[：:]\s*(对|错)',
            re.DOTALL
        )
        for m in pattern.finditer(text):
            q_num = int(m.group(1))
            q_text = m.group(2).strip()
            ans_val = m.group(3).strip()
            
            q_text = re.sub(r'\s+', '', q_text)
            q_text = re.sub(r'[()（）]$', '', q_text).strip()
            
            if len(q_text) < 5:
                continue
            
            answer = [1] if ans_val == '对' else [0]
            questions.append({
                'number': q_num,
                'type': 'judge',
                'question': q_text,
                'options': ['错误', '正确'],
                'answer': answer,
                'explanation': ''
            })
    else:
        pattern = re.compile(
            r'(\d+)[\.\．]\s*(.+?)正确答案[：:]\s*([A-Z]+)',
            re.DOTALL
        )
        for m in pattern.finditer(text):
            q_num = int(m.group(1))
            q_content = m.group(2).strip()
            ans_val = m.group(3).strip()
            
            q_content = re.sub(r'\s+', '', q_content)
            
            opt_matches = list(re.finditer(r'[A-H][\.\．、]', q_content))
            
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
                
                bad_patterns = ['正确答案', '解析：', '解析:']
                if any(p in opt_text for p in bad_patterns):
                    break
                
                if opt_text and len(opt_text) > 1:
                    options.append(opt_text)
            
            if len(options) < 2:
                continue
            
            ans_letters = ans_val.upper()
            if not all(c in 'ABCDEFGH' for c in ans_letters):
                continue
            
            answer = [ord(c) - ord('A') for c in ans_letters]
            max_ans = max(answer) if answer else -1
            if max_ans >= len(options):
                continue
            
            q_type = 'multiple' if len(answer) > 1 else 'single'
            
            questions.append({
                'number': q_num,
                'type': q_type,
                'question': q_text,
                'options': options,
                'answer': answer,
                'explanation': ''
            })
    
    return questions

def main():
    base_dir = r'C:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\第二套试题'
    pdf1_path = os.path.join(base_dir, '习思想选择题（刷这套）.pdf')
    
    text = extract_all_text(pdf1_path)
    text = re.sub(r'\r', '', text)
    
    multi_start = text.find('二. 多选题')
    judge_start = text.find('三. 判断题')
    
    if multi_start < 0:
        multi_start = text.find('二、多选题')
    if judge_start < 0:
        judge_start = text.find('三、判断题')
    
    print(f'多选题位置: {multi_start}')
    print(f'判断题位置: {judge_start}')
    
    single_text = text[:multi_start] if multi_start > 0 else text
    multi_text = text[multi_start:judge_start] if (multi_start > 0 and judge_start > 0) else ''
    judge_text = text[judge_start:] if judge_start > 0 else ''
    
    print('\n' + '=' * 60)
    print('【单选题】')
    single_qs = extract_questions_from_section(single_text, is_judge=False)
    single_qs = [q for q in single_qs if q['type'] == 'single']
    print(f'  提取到: {len(single_qs)} 道')
    if single_qs:
        print(f'  编号范围: {min(q["number"] for q in single_qs)} - {max(q["number"] for q in single_qs)}')
    
    print('\n' + '=' * 60)
    print('【多选题】')
    multi_qs = extract_questions_from_section(multi_text, is_judge=False)
    multi_qs = [q for q in multi_qs if q['type'] == 'multiple']
    print(f'  提取到: {len(multi_qs)} 道')
    if multi_qs:
        print(f'  编号范围: {min(q["number"] for q in multi_qs)} - {max(q["number"] for q in multi_qs)}')
    
    print('\n' + '=' * 60)
    print('【判断题】')
    judge_qs = extract_questions_from_section(judge_text, is_judge=True)
    print(f'  提取到: {len(judge_qs)} 道')
    if judge_qs:
        print(f'  编号范围: {min(q["number"] for q in judge_qs)} - {max(q["number"] for q in judge_qs)}')
    
    all_qs = single_qs + multi_qs + judge_qs
    
    print(f'\n' + '=' * 60)
    print(f'总计: {len(all_qs)} 道')
    print(f'  单选: {len(single_qs)}')
    print(f'  多选: {len(multi_qs)}')
    print(f'  判断: {len(judge_qs)}')
    
    result = []
    for q in all_qs:
        result.append({
            'type': q['type'],
            'question': q['question'],
            'options': q['options'],
            'answer': q['answer'],
            'explanation': q.get('explanation', '')
        })
    
    output_path = r'c:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\试题与解析\questions_second_set.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f'\n已保存到: {output_path}')

if __name__ == '__main__':
    main()
