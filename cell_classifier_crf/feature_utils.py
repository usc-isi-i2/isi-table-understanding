import re

# TODO: None of these regexes recognize symbols: Eg. $, ..., etc
word_regex = re.compile('^[a-z]+$', re.IGNORECASE)  # Todo: handle unicode characters correctly
symbol_regex = re.compile(r'^\W+$')
alphanum_regex = re.compile(r'^\w+$')
alpha_regex = re.compile(r'[a-z]', re.IGNORECASE)

# TODO: empty may not be the right classification for these cells
# some are actually data cells whose value is not available #can we add a new class NA?
empty_cell = set(["...", "N/A", "n/a", ""])
