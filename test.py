import csv



with open("data/character_names.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        print(f"{(row[0]).upper()}=\"{row[0]}\"")