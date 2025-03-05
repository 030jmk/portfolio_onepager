import json

def modify_json_file(input_file, output_file):
    try:
        # Read the JSON file
        with open(input_file, 'r') as file:
            data = json.load(file)

        # Example manipulations:
        
        # 1. Sort data by subdomain name
        for domain in data:
            domain['subdomains'].sort(key=lambda x: x['name'])

        # 2. Sort technologies by name
        for domain in data:
            for subdomain in domain['subdomains']:
                for process in subdomain['processes']:
                    for usecase in process['usecases']:
                        usecase['technologies'].sort(key=lambda x: x['name'])

        # 3. Sort industries by name
        for domain in data:
            for subdomain in domain['subdomains']:
                for process in subdomain['processes']:
                    for usecase in process['usecases']:
                        usecase['industries'].sort(key=lambda x: x['name'])

        # Write the modified content to new file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Successfully modified {input_file} and saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def flatten_json_structure(input_file, output_file):
    try:
        # Read the JSON file
        with open(input_file, 'r') as file:
            data = json.load(file)

        # Create flattened structure
        flattened_usecases = []
        
        for domain in data:
            for subdomain in domain['subdomains']:
                subdomain_name = subdomain['name']
                for process in subdomain['processes']:
                    process_name = process.get('name', 'Default Process')
                    for usecase in process['usecases']:
                        # Create new usecase object with subdomain and process as attributes
                        flattened_usecase = {
                            **usecase,
                            'subdomain': subdomain_name,
                            'process': process_name
                        }
                        flattened_usecases.append(flattened_usecase)

        # Sort usecases by subdomain and name
        flattened_usecases.sort(key=lambda x: (x['subdomain'], x['name']))

        # Write the modified content to new file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(flattened_usecases, file, indent=4, ensure_ascii=False)

        print(f"Successfully flattened {input_file} and saved to {output_file}")
        print(f"Total number of use cases: {len(flattened_usecases)}")

    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    input_json = "data.json"
    output_json = "data_modified.json"
    modify_json_file(input_json, output_json)

    input_json = "data.json"
    output_json = "flattened_data.json"
    flatten_json_structure(input_json, output_json)