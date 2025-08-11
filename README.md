Sure! Here's your README in markdown format:

```markdown
# Financial Data API Aggregator

A robust and scalable Flask-based API that provides standardized financial data for public companies from various countries. It acts as a middleware, fetching data from external financial APIs, processing it, and serving it through a clean, unified interface with a powerful two-layer database caching system to ensure high performance and reliability.

---

## Key Features

- **Multi-Country Support:** Easily extensible to support financial data from any country's API provider thanks to a Service Factory pattern.
- **Two-Layer Caching:**
  - **Search Caching:** Caches search results for a short duration (default: 1 hour) to reduce redundant API calls.
  - **Data Caching:** Caches detailed company financial data for a longer duration (default: 24 hours) for near-instantaneous responses on subsequent requests.
- **Scalable Architecture:** Built with Flask Blueprints for modular routes and SQLAlchemy for a robust ORM layer.
- **Database Migrations:** Uses Flask-Migrate to manage database schema changes, making updates seamless.
- **Easy Configuration:** Manages configuration and sensitive keys using a `.env` file.
- **Simple Setup:** Get the API up and running with just a few commands.

---

## Technology Stack

- **Backend:** Flask
- **Database ORM:** Flask-SQLAlchemy
- **Database Migrations:** Flask-Migrate
- **Database:** Supports PostgreSQL (recommended for production) and SQLite (for development)
- **Dependencies:** `requests` for API calls, `python-dotenv` for environment management

---

## Project Structure

```

.
├── migrations/             # Database migration scripts
├── routes/                 # Flask Blueprints for API endpoints
│   ├── company.py
│   ├── info.py
│   └── search.py
├── services/               # Business logic and external API interaction
│   ├── base\_api.py
│   ├── factory.py
│   └── us\_api.py
├── utils/                  # Helper functions
│   └── helpers.py
├── app.db                  # SQLite database file (default)
├── app.py                  # Main Flask application entry point
├── config.py               # Application configuration
├── logging\_config.py       # Basic logging setup
├── models.py               # SQLAlchemy database models
└── requirements.txt        # Python dependencies

````

---

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- Python 3.8+
- pip package manager

### 2. Clone the Repository

```bash
git clone https://github.com/shubhamc1947/company-data.git
cd company-data
````

### 3. Create and Activate a Virtual Environment

**For Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a file named `.env` in the root of the project directory and add the API key for the financial data provider.

```env
# Get your key from https://financialmodelingprep.com/
API_KEY_US="your_api_key_here"

# Optional: To use PostgreSQL, uncomment and set the following line.
# DATABASE_URL="postgresql://user:password@host:port/database_name"
```

### 6. Set Up the Database

The application defaults to using a simple `app.db` (SQLite) file. If you want to use PostgreSQL, make sure you have it installed and have set the `DATABASE_URL` in your `.env` file.

Run the following commands to initialize the database and create all the necessary tables:

```bash
# Initialize the migration environment (only run this once)
flask db init

# Create the migration script based on the models
flask db migrate -m "Initial database setup"

# Apply the migration to the database
flask db upgrade
```

This will create the `company`, `company_profile`, `financial_statement`, and `search_cache` tables.

### 7. Run the Application

```bash
flask run
```

The API will now be running on [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## API Endpoints

### Info Routes

* **GET /**
  Get general information about the API, its features, and available endpoints.

* **GET /examples**
  Returns a list of popular company examples that are guaranteed to work.

* **GET /test**
  A quick health check endpoint to verify that the external API connection is working.

### Search Route

* **GET /search/<country>/\<company\_name>**
  Searches for companies matching the `company_name` in the specified `country`.

  * `country`: The two-letter country code (e.g., `us`).

  **Example:**

  ```bash
  curl http://127.0.0.1:5000/search/us/Apple
  ```

### Company Data Route

* **GET /company/<country>/\<company\_name>**
  Fetches detailed financial metrics for the best-matched company. This is the primary endpoint and utilizes the full caching system.

  **Example:**

  ```bash
  curl http://127.0.0.1:5000/company/us/Tesla
  ```

---

## Extensibility

### Adding a New Country API

The project is designed to be easily extended. To add support for a new country (e.g., the United Kingdom):

1. **Create a New Service:**
   Create a file `services/uk_api.py` that inherits from `BaseCompanyAPI` and implements the `search_company` and `get_company_data` methods for the UK's data provider.

2. **Update the Factory:**
   In `services/factory.py`, import your new `UKCompanyAPI` and add it to the `_services` dictionary with the key `'uk'`.

```python
# services/factory.py
from services.us_api import USCompanyAPI
from services.uk_api import UKCompanyAPI  # <-- Import new service

class APIServiceFactory:
    _services = {
        'us': USCompanyAPI(),
        'uk': UKCompanyAPI(),  # <-- Add new service
    }
    # ... rest of the file
```

---

Feel free to contribute or raise issues!

---

**License:** MIT License
**Author:** Shubham Chaturvedi

