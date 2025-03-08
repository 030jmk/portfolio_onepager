# AI Use Case Explorer

A Flask web application that displays and filters AI use cases using a responsive card-based interface.

## Prerequisites

- Python 3.11+
- pip (Python package installer)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/030jmk/portfolio_onepager.git
    cd portfolio_onepager
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory and add the following environment variables:
    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    ```

## Running the Application

1. Start the Flask application:
    ```bash
    flask run
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000` to view the application.

## Project Structure

```
portfolio_onepager/
│
├── app.py
├── requirements.txt
├── .env
├── README.md
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js
└── templates/
    └── index.html
```


