from flask import Flask, render_template, request, jsonify
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_data():
    with open('flattened_data.json') as f:
        data = json.load(f)
        print("data loaded")
        return data

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
    
    # Normalize filter inputs to lowercase
    selected_subdomains = [s.lower() for s in selected_subdomains]
    selected_industries = [i.lower() for i in selected_industries]
    selected_technologies = [t.lower() for t in selected_technologies]

    for usecase in data:
        # Extract and normalize case data
        case_technologies = [tech["name"].lower() for tech in usecase["technologies"] if tech["value"] > 0]
        case_industries = [ind["name"].lower() for ind in usecase["industries"] if ind["value"] > 0]
        case_subdomain = usecase["subdomain"].lower()

        # Search term matching
        matches_search = (
            search_term in str(usecase["name"]).lower() or
            search_term in str(usecase.get("Challenge", "")).lower() or
            search_term in str(usecase.get("solution", "")).lower() or
            search_term in str(usecase.get("benefit", "")).lower()
        )

        # Exact matching for filters using set operations for better performance
        matches_subdomain = not selected_subdomains or case_subdomain in selected_subdomains
        matches_industry = not selected_industries or bool(set(case_industries) & set(selected_industries))
        matches_technology = not selected_technologies or bool(set(case_technologies) & set(selected_technologies))

        # All conditions must be met
        if matches_search and matches_subdomain and matches_industry and matches_technology:
            filtered_data.append(usecase)

    return filtered_data

@app.route('/')
def index():
    try:
        data = load_data()
        subdomains, industries, technologies = extract_unique_values(data)
        return render_template('index.html', 
                             subdomains=subdomains,
                             industries=industries,
                             technologies=technologies)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return "Error loading page. Please check server logs.", 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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
    try:
        logger.info("Starting Flask application...")
        app.run(host='127.0.0.1', debug=True, port=8080)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")