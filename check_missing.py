import fitz
import re

doc = fitz.open(r'C:\Users\不知道叫什么\Desktop\学习\大三下\毛概习概\复习\第二套试题\习思想选择题（刷这套）.pdf')
text = ''
for i in range(len(doc)):
    text += doc[i].get_text()

text = re.sub(r'\r', '', text)

for target in ['5．', '15．', '30．']:
    m = text.find(target)
    if m >= 0:
        print(f'=== 第 {target} 题附近 ===')
        print(text[max(0,m-50):m+500])
        print()
