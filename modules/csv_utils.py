"""CSV utilities for Sharp"""
import csv
import io

def parse_csv(csv_string, delimiter=','):
    try:
        rows = []
        reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
        for row in reader:
            rows.append(row)
        return rows
    except:
        return []

def stringify_csv(data, delimiter=','):
    try:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)
        for row in data:
            writer.writerow(row)
        return output.getvalue()
    except:
        return ""

def read_csv_file(filepath, delimiter=','):
    try:
        with open(filepath, 'r') as f:
            return parse_csv(f.read(), delimiter)
    except:
        return []

def write_csv_file(filepath, data, delimiter=','):
    try:
        with open(filepath, 'w', newline='') as f:
            f.write(stringify_csv(data, delimiter))
        return True
    except:
        return False
