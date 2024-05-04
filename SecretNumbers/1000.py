import csv
from itertools import product

# Mapping each number to corresponding Hebrew characters
hebrew_map = {
    '0': ['ס'],
    '1': ['י', 'מ'],
    '2': ['ב', 'ו'],
    '3': ['ג', 'צ'],
    '4': ['ד', 'ק'],
    '5': ['א', 'ע', 'ה', 'נ'],
    '6': ['ל', 'פ'],
    '7': ['ז', 'ר'],
    '8': ['ש', 'ח'],
    '9': ['ת', 'ט']
}

# Function to get all combinations of Hebrew characters for a given three-digit number
def get_combinations(num):
    num_str = f"{num:03d}"
    options = [hebrew_map[digit] for digit in num_str]
    combinations = list(product(*options))
    results = [''.join(comb) for comb in combinations]
    return results

# Calculate the maximum number of combinations possible
max_combinations = 1
for key in hebrew_map:
    max_combinations *= len(hebrew_map[key])

# Open a CSV file to write the combinations
with open('hebrew_combinations.csv', 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    header = ['Number'] + [f'Combination_{i+1}' for i in range(max_combinations)]
    writer.writerow(header)

    # Loop through 000 to 999 and write all combinations for each number in one row
    for i in range(1000):
        combinations = get_combinations(i)
        row = [f"{i:03d}"] + combinations
        writer.writerow(row)
