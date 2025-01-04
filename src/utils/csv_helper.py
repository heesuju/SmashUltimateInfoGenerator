import csv

def csv_to_dict(directory, col_name:str = ""):
    data_list = []
    
    with open(directory, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            if col_name:
                item = str(row.get(col_name, ""))
                if item not in data_list:
                    data_list.append(item)
            else:
                data_list.append(row)
    
    return data_list

def csv_to_key_value(directory:str):
    output = {}
    
    with open(directory, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            key = row[0]
            values = row[1:]
            output[key] = values
    return output