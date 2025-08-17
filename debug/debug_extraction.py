#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.generator import GroqLLM
from src.llm.prompts import get_prompt_template

# Create the prompt
template = get_prompt_template('few_shot')
prompt = template.format(question='Find orders from last month', schema_info='test')

# Debug the extraction
g = GroqLLM()
lines = prompt.strip().split('\n')

print("Debugging question extraction:")
print("-" * 40)

# Check for NEW QUESTION marker
new_question_found = False
for i, line in enumerate(lines):
    if "=== NEW QUESTION ===" in line:
        print(f"Found NEW QUESTION marker at line {i}: {repr(line)}")
        new_question_found = True
        # Look for the next "Question:" line after this marker
        for j in range(i + 1, len(lines)):
            print(f"  Checking line {j}: {repr(lines[j])}")
            if lines[j].strip().startswith("Question:"):
                question = lines[j].replace("Question:", "").strip()
                print(f"  Found question after NEW QUESTION marker: '{question}'")
                break

print(f"new_question_found: {new_question_found}")

# Test the actual extraction
result = g._extract_question_from_prompt(prompt)
print(f"Final extraction result: {repr(result)}")
