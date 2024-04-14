#!/usr/bin/env python3

import sys
import unicodedata
import re

"""
Tool to convert text based possession and series result table into markdown.

Example usage:
# python3 main.py
(<Ctrl-V> to paste the text, and then <Ctrl-D> to end input.

Testing:
# python3 main.py < testdata.txt | diff - test-golden.txt
(See if no diff is shown. If the logic is changed, update the test data.)
"""


MAX_SINGLE_COLUMN_SPACES = 15

PLACEHOLDER_FOR_SPACE = '<SPACE>'


def preprocess_line(line: str):
    # Normalize, including zenkaku -> hankaku
    line = unicodedata.normalize('NFKC', line)

    # Remove spaces before '('
    line = re.sub('\s+\(', '(', line)

    # Replace all spaces inside brace into a placeholder
    line = re.sub(r"\([^\)]+\)", lambda m: m.group(0).replace(" ", PLACEHOLDER_FOR_SPACE), line)
    return line


def process_item_before_print(item: str):
    # Append a space before '('
    item = item.replace('(', ' (')

    # Replace back placeholder for a space
    item = item.replace(PLACEHOLDER_FOR_SPACE, ' ')

    return item


rows = []
# First, parse into table:
for line in sys.stdin:
    line = preprocess_line(line)

    chunks = [] # non-empty string chunks.
    num_spaces = [0] # num_spaces[i] = number of spaces before chunks[i]
    for i, token in enumerate(line.split(' ')):
        if len(token.strip()) > 0:
            chunks.append(token.strip())
            num_spaces.append(0)
        else:
            num_spaces[-1] += 1

    if len(chunks) == 1:
        if num_spaces[0] == 0:
            rows.append(chunks + ['', ''])
        elif num_spaces[0] <= MAX_SINGLE_COLUMN_SPACES:
            rows.append([''] + chunks + [''])
        else:
            rows.append(['', ''] + chunks)
    elif len(chunks) == 2:
        if num_spaces[0] > 0:
            # assume the first colum doesn't exist.
            rows.append([''] +  chunks)
        else:
            if num_spaces[1] > MAX_SINGLE_COLUMN_SPACES:
                rows.append(chunks[:1] + [''] + chunks[1:])
            else:
                rows.append(chunks + [''])
    elif len(chunks) == 3:
        rows.append(chunks)
    else:
        raise Exception("Unexpected pattern of strings: " + line)

for i, row in enumerate(rows):
    row = map(process_item_before_print, row)
    print('| ' + ' | '.join(row) + ' |')
    if i == 0:
        print('|--|--|--|')
