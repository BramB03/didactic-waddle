def save_json_response(response_data, filename="response_output.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            if hasattr(response_data, 'json'):
                # If it's a requests response object
                json.dump(response_data.json(), file, indent=2, ensure_ascii=False)
            else:
                # If it's already parsed JSON data
                json.dump(response_data, file, indent=2, ensure_ascii=False)
        
        print(f"JSON response saved to {filename}")
        
    except Exception as e:
        print(f"Error saving JSON file: {e}")
