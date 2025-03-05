from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def load_data():
    with open('flattened_data.json') as f:
        return json.load(f)

def extract_unique_values(data): 
    subdomains = set()
    industries = set()
    technologies = set()
    
    for usecase in data:
        subdomains.add(usecase['subdomain'])
        for industry in usecase['industries']:
            if industry['value'] > 0:
                industries.add(industry['name'])
        for technology in usecase['technologies']:
            if technology['value'] > 0:
                technologies.add(technology['name'])

    return sorted(list(subdomains)), sorted(list(industries)), sorted(list(technologies))

def filter_data(data, search_term, selected_subdomains, selected_industries, selected_technologies):
    filtered_data = []
    search_term = search_term.lower() if search_term else ""
    
    # Convert selected filters to lowercase for case-insensitive comparison
    selected_subdomains = [s.lower() for s in selected_subdomains] if selected_subdomains else []
    selected_industries = [i.lower() for i in selected_industries] if selected_industries else []
    selected_technologies = [t.lower() for t in selected_technologies] if selected_technologies else []
    
    for usecase in data:
        # Get only active technologies and industries (value = 1)
        case_technologies = [tech["name"] for tech in usecase["technologies"] if tech["value"] > 0]
        case_industries = [ind["name"] for ind in usecase["industries"] if ind["value"] > 0]
        case_subdomain = usecase["subdomain"].lower()
        
        # Create a clean version of the usecase with properly formatted arrays
        clean_usecase = {
            **usecase,
            "technologies": case_technologies,  # Only names of active technologies
            "industries": case_industries      # Only names of active industries
        }
        
        matches_search = (
            search_term in str(clean_usecase["name"]).lower() or
            search_term in str(clean_usecase.get("Challenge", "")).lower() or
            search_term in str(clean_usecase.get("solution", "")).lower() or
            search_term in str(clean_usecase.get("benefit", "")).lower()
        )
        
        # Check if ANY of the selected filters match using lowercase comparison
        matches_subdomain = not selected_subdomains or case_subdomain in selected_subdomains
        matches_industry = not selected_industries or any(ind.lower() in selected_industries for ind in case_industries)
        matches_technology = not selected_technologies or any(tech.lower() in selected_technologies for tech in case_technologies)

        if matches_search and matches_subdomain and matches_industry and matches_technology:
            filtered_data.append(clean_usecase)
    
    return filtered_data

@app.route('/')
def index():
    data = load_data()
    subdomain_options, industry_options, technology_options = extract_unique_values(data)
    return render_template('index.html', subdomains=subdomain_options, industries=industry_options, technologies=technology_options)

@app.route('/filter', methods=['GET'])
def filter_cases():
    data = load_data()
    search_term = request.args.get('search', '')
    selected_subdomains = request.args.getlist('subdomains')
    selected_industries = request.args.getlist('industries')
    selected_technologies = request.args.getlist('technologies')
    
    filtered_data = filter_data(data, search_term, selected_subdomains, selected_industries, selected_technologies)
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
