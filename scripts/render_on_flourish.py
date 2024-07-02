import csv
import json
import requests
from collections import Counter

def read_data_file(file_path):
    if file_path.endswith('.csv'):
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = [row for row in reader]
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as jsonfile:
            data = json.load(jsonfile)
    else:
        raise ValueError("Unsupported file format. Please use CSV or JSON.")
    return data

def determine_chart_type(data):
    if isinstance(data, list) and len(data) > 0:
        keys = data[0].keys()
        num_columns = len(keys)
        num_numeric = sum(1 for key in keys if all(row[key].replace('.','').isdigit() for row in data))
        
        if num_columns == 2 and num_numeric == 1:
            return "pie"
        elif num_columns >= 3 and num_numeric >= 2:
            return "scatter"
        elif any(key.lower() in ['date', 'time', 'year', 'month'] for key in keys):
            return "line"
        else:
            return "bar"
    else:
        raise ValueError("Invalid data format")

def prepare_data_for_chart(data, chart_type):
    if chart_type == "pie":
        categories = [row[list(row.keys())[0]] for row in data]
        values = [float(row[list(row.keys())[1]]) for row in data]
        return {"categories": categories, "values": values}
    
    elif chart_type == "scatter":
        x_axis = [float(row[list(row.keys())[1]]) for row in data]
        y_axis = [float(row[list(row.keys())[2]]) for row in data]
        labels = [row[list(row.keys())[0]] for row in data]
        return {"x_axis": x_axis, "y_axis": y_axis, "labels": labels}
    
    elif chart_type == "line":
        time_key = next(key for key in data[0].keys() if key.lower() in ['date', 'time', 'year', 'month'])
        value_key = next(key for key in data[0].keys() if key != time_key)
        x_axis = [row[time_key] for row in data]
        y_axis = [float(row[value_key]) for row in data]
        return {"x_axis": x_axis, "y_axis": y_axis}
    
    elif chart_type == "bar":
        categories = [row[list(row.keys())[0]] for row in data]
        values = [float(row[list(row.keys())[1]]) for row in data]
        return {"categories": categories, "values": values}

def create_chart(data, chart_type):
    flourish_data = {
        "chart_type": chart_type,
        "data": prepare_data_for_chart(data, chart_type)
    }
    
    api_key = my_secrets['flourish_api_key']
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.flourish.studio/v1/charts",
        headers=headers,
        data=json.dumps(flourish_data)
    )
    
    if response.status_code == 201:
        chart_url = response.json().get("url")
        print(f"Chart created successfully: {chart_url}")
        return chart_url
    else:
        print(f"Failed to create chart: {response.text}")
        return None

def process_data_file(file_path):
    data = read_data_file(file_path)
    chart_type = determine_chart_type(data)
    return create_chart(data, chart_type)

# Example usage
file_path = "path/to/your/data/file.csv"  # or "path/to/your/data/file.json"
chart_url = process_data_file(file_path)
if chart_url:
    print(f"Chart created successfully. You can view it at: {chart_url}")
else:
    print("Failed to create chart.")