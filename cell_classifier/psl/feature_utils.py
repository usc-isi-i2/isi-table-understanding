import re

word_regex = re.compile('^[a-z]+$', re.IGNORECASE)  # Todo: handle unicode characters correctly
symbol_regex = re.compile(r'^\W+$')
alphanum_regex = re.compile(r'^\w+$')
alpha_regex = re.compile(r'[a-z]', re.IGNORECASE)
special_regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

empty_cell = set(["N/A", "n/a", "", "*", "-", "**", "None"])
#empty_cell = set(["...", "N/A", "n/a", "", "NA", "NA**", "*", "-", "**", "None"])
