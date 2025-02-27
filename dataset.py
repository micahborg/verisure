import json

# Read the text file
with open("Snapshot.txt", "r", encoding="utf-8") as file:
    text_data = file.read()

# Convert text to JSON format
json_data = {"content": text_data}

# Convert dictionary to JSON string
exported_json_str = json.dumps(json_data, indent=4)  # This variable will be imported


