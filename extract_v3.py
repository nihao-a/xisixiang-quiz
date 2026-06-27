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

def parse_pdf1_all_v3(text):
    questions = []
    
    text = re.sub(r'\r', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    ans_pattern = re.compile(
        r'(\d+)[\.\．](.+?)正确答案[：:]\s*(对|错|[A-Z]+)',
        re.DOTALL
    )
    
    for m in ans_pattern.finditer(text):
        q_num = int(m.group(1))
        q_content = m.group(2).strip()
        ans_val = m.group(3).strip()
        
        if q_num < 1 or q_num > 500:
            continue
        
        q_content = re.sub(r'\s+', '', q_content)
        
        if ans_val in ['对', '错']:
            q_type = 'judge'
            answer = [1] if ans_val == '对' else [0]
            options = ['错误', '正确']
            
            q_text = q_content.strip()
            q_text = re.sub(r'[()（）]$', '', q_text).strip()
            
            if len(q_text) < 5:
                continue
            
            questions.append({
                'number': q_num,
                'type': q_type,
                'question': q_text,
                'options': options,
                'answer': answer,
                'explanation': ''
            })
        else:
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
    
    print('=' * 60)
    print('提取 PDF1: 习思想选择题（刷这套）.pdf')
    text1 = extract_all_text(pdf1_path)
    qs = parse_pdf1_all_v3(text1)
    
    single = [q for q in qs if q['type'] == 'single']
    multi = [q for q in qs if q['type'] == 'multiple']
    judge = [q for q in qs if q['type'] == 'judge']
    
    print(f'\n总提取: {len(qs)} 道')
    print(f'  单选题: {len(single)} 道')
    print(f'  多选题: {len(multi)} 道')
    print(f'  判断题: {len(judge)} 道')
    
    print(f'\n题号范围: {min(q["number"] for q in qs)} - {max(q["number"] for q in qs)}')
    
    bad_single = [q for q in single if len(q['options']) < 4]
    bad_multi = [q for q in multi if len(q['options']) < 4]
    print(f'\n单选题选项<4: {len(bad_single)} 道')
    print(f'多选题选项<4: {len(bad_multi)} 道')
    
    if bad_single[:5]:
        print('\n单选题选项<4的前5道:')
        for q in bad_single[:5]:
            print(f'  第{q["number"]}题: {q["question"][:25]}... 选项数:{len(q["options"])}')
    
    output_path = r'c:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\试题与解析\questions_second_set.json'
    
    result = []
    for q in qs:
        result.append({
            'type': q['type'],
            'question': q['question'],
            'options': q['options'],
            'answer': q['answer'],
            'explanation': q.get('explanation', '')
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f'\n已保存到: {output_path}')
    
    print('\n=== 前3道单选题 ===')
    for i, q in enumerate(single[:3]):
        ans = ''.join([chr(65+a) for a in q['answer']])
        print(f'  第{q["number"]}题: {q["question"][:30]}... 答案:{ans} 选项:{len(q["options"])}')
    
    print('\n=== 前3道多选题 ===')
    for i, q in enumerate(multi[:3]):
        ans = ''.join([chr(65+a) for a in q['answer']])
        print(f'  第{q["number"]}题: {q["question"][:30]}... 答案:{ans} 选项:{len(q["options"])}')
    
    print('\n=== 前3道判断题 ===')
    for i, q in enumerate(judge[:3]):
        ans = '正确' if q['answer'][0] == 1 else '错误'
        print(f'  第{q["number"]}题: {q["question"][:35]}... 答案:{ans}')

if __name__ == '__main__':
    main()
