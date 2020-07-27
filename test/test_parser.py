
from pathlib import Path
import behave
from behave import parser

p = parser.Parser()
text = Path('001新建测试集.feature').read_text(encoding='utf-8')
    
feature = p.parse(text)
print(feature.line, feature.name)
for s in feature.scenarios:
    print(s.line, s.name)
    for step in s.steps:
        print(step.line, step.step_type, step.name)
        
    
#print(feature.name)
#print(feature.name)
