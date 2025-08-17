#!/usr/bin/env python3
from src.llm.prompts import get_prompt_template

template = get_prompt_template('few_shot')
prompt = template.format(question='Find orders from last month', schema_info='test')
lines = prompt.split('\n')

print('Lines around NEW QUESTION:')
for i, line in enumerate(lines):
    print(f'{i:2d}: {repr(line)}')
