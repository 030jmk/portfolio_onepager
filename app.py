from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def load_data():
    with open('data.json') as f:
        return json.load(f)

def extract_unique_values(data):
    subdomains = set()
    industries = set()
    technologies = set()
    
    for domain in data:
        for subdomain in domain['subdomains']:
            subdomains.add(subdomain['name'])
            for process in subdomain['processes']:
                for usecase in process['usecases']:
                    for industry in usecase['industries']:
                        industries.add(industry['name'])
                    for technology in usecase['technologies']:
                        if technology['value'] > 0:
                            technologies.add(technology['name'])

    return list(subdomains), list(industries), list(technologies)

def filter_data(data, search_term, selected_subdomains, selected_industries, selected_technologies):
    filtered_data = []
    search_term = search_term.lower() if search_term else ""
    for domain in data:
        for subdomain in domain['subdomains']:
            for process in subdomain['processes']:
                for usecase in process['usecases']:
                    case_subdomains = [subdomain['name'].lower()]
                    case_industries = [industry['name'].lower() for industry in usecase['industries']]
                    case_technologies = [technology['name'].lower() for technology in usecase['technologies'] if technology['value'] > 0]
                    
                    matches_search = (
                        search_term in str(usecase['name']).lower() or
                        search_term in str(usecase.get('Challenge', '')).lower() or
                        search_term in str(usecase.get('solution', '')).lower() or
                        search_term in str(usecase.get('benefit', '')).lower() or
                        search_term in str(usecase.get('impact', '')).lower() or
                        search_term in str(usecase.get('complexity', '')).lower()
                    )

                    if (
                        matches_search and
                        (not selected_subdomains or any(sd in case_subdomains for sd in map(str.lower, selected_subdomains))) and
                        (not selected_industries or any(ind in case_industries for ind in map(str.lower, selected_industries))) and
                        (not selected_technologies or any(tech in case_technologies for tech in map(str.lower, selected_technologies)))
                    ):
                        filtered_data.append({
                            **usecase,
                            'subdomain': subdomain['name'],
                            'industries': case_industries,
                            'technologies': case_technologies
                        })
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
    app.run(debug=True)
