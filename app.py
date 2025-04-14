import json
import logging
from flask import Flask, render_template, request, jsonify
from typing import List, Dict, Tuple, Any, Set # Added type hinting

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Global Data Store ---
USE_CASE_DATA: List[Dict[str, Any]] = []
UNIQUE_SUBDOMAINS: List[str] = []
UNIQUE_INDUSTRIES: List[str] = []
UNIQUE_TECHNOLOGIES: List[str] = []

def load_and_prepare_data(filepath: str = 'flattened_data.json') -> None:
    """Loads data from JSON and extracts unique filter values."""
    global USE_CASE_DATA, UNIQUE_SUBDOMAINS, UNIQUE_INDUSTRIES, UNIQUE_TECHNOLOGIES
    try:
        with open(filepath) as f:
            USE_CASE_DATA = json.load(f)
        logger.info(f"Successfully loaded {len(USE_CASE_DATA)} use cases from {filepath}")

        subdomains: Set[str] = set()
        industries: Set[str] = set()
        technologies: Set[str] = set()

        for usecase in USE_CASE_DATA:
            subdomains.add(usecase['subdomain'])
            for industry in usecase.get('industries', []): # Use .get for safety
                if industry.get('value', 0) > 0:
                    industries.add(industry.get('name', '')) # Use .get for safety
            for technology in usecase.get('technologies', []): # Use .get for safety
                if technology.get('value', 0) > 0:
                    technologies.add(technology.get('name', '')) # Use .get for safety

        # Filter out any empty strings that might have resulted from .get defaults
        UNIQUE_SUBDOMAINS = sorted(list(filter(None, subdomains)))
        UNIQUE_INDUSTRIES = sorted(list(filter(None, industries)))
        UNIQUE_TECHNOLOGIES = sorted(list(filter(None, technologies)))
        logger.info("Extracted unique filter values.")

    except FileNotFoundError:
        logger.error(f"Error: Data file not found at {filepath}. Application cannot start properly.")
        # Depending on requirements, you might exit or run with empty data
        USE_CASE_DATA = []
    except json.JSONDecodeError:
        logger.error(f"Error: Invalid JSON format in {filepath}. Application cannot start properly.")
        USE_CASE_DATA = []
    except Exception as e:
        logger.error(f"An unexpected error occurred during data loading: {str(e)}")
        USE_CASE_DATA = []

# --- Call data loading function when the app starts ---
load_and_prepare_data()
# -------------------------

def filter_data(
    data: List[Dict[str, Any]],
    search_term: str,
    selected_subdomains: List[str],
    selected_industries: List[str],
    selected_technologies: List[str]
) -> List[Dict[str, Any]]:
    """Filters the loaded use case data based on criteria."""
    filtered_data = []
    search_term_lower = search_term.lower() if search_term else ""

    # Pre-compute lowercase sets for faster lookups inside the loop
    selected_subdomains_set = set(s.lower() for s in selected_subdomains)
    selected_industries_set = set(i.lower() for i in selected_industries)
    selected_technologies_set = set(t.lower() for t in selected_technologies)

    for usecase in data:
        # Search term matching (already handles missing keys via .get)
        matches_search = (
            not search_term_lower or # If no search term, always matches
            search_term_lower in str(usecase.get("name", "")).lower() or
            search_term_lower in str(usecase.get("Challenge", "")).lower() or
            search_term_lower in str(usecase.get("solution", "")).lower() or
            search_term_lower in str(usecase.get("benefit", "")).lower()
        )

        if not matches_search: # Early exit if search doesn't match
            continue

        # Extract and normalize case data (using .get for safety)
        case_subdomain_lower = usecase.get("subdomain", "").lower()
        # Create sets directly for efficient intersection
        case_technologies_set = {
            tech.get("name", "").lower()
            for tech in usecase.get("technologies", []) if tech.get("value", 0) > 0
        }
        case_industries_set = {
            ind.get("name", "").lower()
            for ind in usecase.get("industries", []) if ind.get("value", 0) > 0
        }

        # Filter matching
        matches_subdomain = not selected_subdomains_set or case_subdomain_lower in selected_subdomains_set
        matches_industry = not selected_industries_set or bool(case_industries_set & selected_industries_set)
        matches_technology = not selected_technologies_set or bool(case_technologies_set & selected_technologies_set)

        # All conditions must be met
        if matches_subdomain and matches_industry and matches_technology:
            filtered_data.append(usecase)

    return filtered_data

@app.route('/')
def index():
    try:
        # Use the globally loaded unique values
        return render_template('index.html',
                             subdomains=UNIQUE_SUBDOMAINS,
                             industries=UNIQUE_INDUSTRIES,
                             technologies=UNIQUE_TECHNOLOGIES)
    except Exception as e:
        # Log the error specific to rendering the template
        logger.error(f"Error rendering index template: {str(e)}")
        # Avoid showing detailed errors to the user in production
        return "An error occurred while loading the page.", 500


@app.errorhandler(404)
def page_not_found(e):
    # It's good practice to log 404s if you want to track broken links
    logger.warning(f"404 Not Found: {request.path}")
    return render_template('404.html'), 404

@app.route('/filter', methods=['GET'])
def filter_cases():
    try:
        search_term = request.args.get('search', '')
        # Use consistent naming (e.g., 'subdomain' singular for the parameter)
        # Match the names used in the frontend JavaScript fetch URL
        selected_subdomains = request.args.getlist('subdomain') # Adjust if frontend uses 'subdomains'
        selected_industries = request.args.getlist('industry') # Adjust if frontend uses 'industries'
        selected_technologies = request.args.getlist('technology') # Adjust if frontend uses 'technologies'

        # Use the globally loaded data
        filtered_results = filter_data(USE_CASE_DATA, search_term, selected_subdomains, selected_industries, selected_technologies)
        return jsonify(filtered_results)
    except Exception as e:
        logger.error(f"Error during filtering: {str(e)}")
        # Return a JSON error response for API consistency
        return jsonify({"error": "An error occurred during filtering."}), 500


if __name__ == '__main__':
    # Check if data loaded successfully before running
    if not USE_CASE_DATA:
         logger.critical("Application failed to start: Use case data could not be loaded.")
    else:
        logger.info("Starting Flask application...")
        # Use debug=False and run with a production WSGI server (like Gunicorn or uWSGI) for deployment
        # For development:
        app.run(host='127.0.0.1', debug=True, port=8080)
        # For production (example using Gunicorn):
        # gunicorn -w 4 -b 127.0.0.1:8080 app:app
