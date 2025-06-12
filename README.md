# SoftDesk Support API

## Overview

SoftDesk Support API is a robust backend solution for managing projects, issues, and comments within a collaborative environment. It provides a comprehensive set of RESTful endpoints for user authentication, project creation and management, assignment of contributors, and detailed issue and comment tracking.

This application is built with Django REST Framework, ensuring a scalable, secure, and well-structured API.

## Features

* **User Management:**
    * User registration (signup)
    * User authentication via JWT (JSON Web Tokens)
    * User profile viewing, updating, and deletion (with granular permissions for self-management and admin control)
* **Project Management:**
    * Create, view, update, and delete projects.
    * Define project types (Back-end, Front-end, iOS, Android).
    * Automatically assigns project author as a contributor.
* **Contributor Management:**
    * Add and remove contributors to/from projects (only by project author).
    * List all contributors for a specific project.
* **Issue Tracking:**
    * Create, view, update, and delete issues within projects.
    * Assign issues to project contributors.
    * Categorize issues with tags (Bug, Feature, Task) and priorities (Low, Medium, High).
    * Track issue status (To Do, In Progress, Finished).
* **Comment System:**
    * Add, view, update, and delete comments on issues.
    * Comments are linked to specific issues and authors.
* **Robust Permissions:** Granular access control ensuring only authorized users can perform specific actions (e.g., only authors can modify/delete their resources).
* **API Documentation:** Interactive API documentation via Swagger UI.
* **Code Quality:** Enforced code style and quality checks using Flake8.
* **Dependency Management:** Managed via Poetry.

## Getting Started

Follow these instructions to set up and run the SoftDesk Support API on your local machine.

### Prerequisites

* **Python:** Version 3.10 or higher (Python 3.12 was used during development).
* **Poetry:** A dependency management and packaging tool for Python.
    * Installation instructions: `https://python-poetry.org/docs/#installation`
* **Git:** For cloning the repository.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd softdesk-support # Or whatever your project's root directory is named
    ```

2.  **Install dependencies using Poetry:**
    This will create a virtual environment (if one doesn't exist) and install all project dependencies.
    ```bash
    poetry install
    ```

3.  **Activate the virtual environment:**
    ```bash
    poetry shell
    ```
    (You'll need to run this command each time you open a new terminal session to work on the project, or simply prefix your commands with `poetry run`.)

### Database Setup

1.  **Apply migrations:**
    This creates the necessary database schema based on your Django models.
    ```bash
    python manage.py migrate
    ```

2.  **Create a superuser (admin account):**
    This will allow you to access the Django admin panel and manage users, projects, etc.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email, and password.

### Running the Application

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be accessible at `http://127.0.0.1:8000/` by default.

## API Documentation (Swagger UI)

The API is self-documented using `drf-spectacular` and can be explored via an interactive Swagger UI.

1.  **Ensure your Django server is running** (as per "Running the Application" above).
2.  **Open your web browser** and navigate to:
    `http://127.0.0.1:8000/api/schema/swagger-ui/`

    You can also access the OpenAPI schema directly at `http://127.0.0.1:8000/api/schema/` or the Redoc UI at `http://127.0.0.1:8000/api/schema/redoc/`.

## API Testing (Postman Collection)

A Postman collection is provided for easy testing of the API endpoints.

1.  **Download and install Postman:** If you don't have it already.
    `https://www.postman.com/downloads/`

2.  **Import the Postman Collection:**
    * Open Postman.
    * Click on `File > Import` (or the `Import` button in the sidebar).
    * Select the provided `softdesk-support.postman_collection.json` file from your project directory.

3.  **Set up Environment Variables in Postman:**
    The collection uses environment variables like `{{host}}`, `{{port}}`, `{{AUTHOR_TOKEN}}`, etc.
    * In Postman, click the "Environment quick look" eye icon (top right, next to the environment dropdown).
    * Click "Add" to create a new environment (e.g., "SoftDesk Local").
    * Add the following variables:
        * `host`: `127.0.0.1`
        * `port`: `8000`
        * `AUTHOR_TOKEN`: (Leave empty initially, will be populated after login)
        * `CONTRIBUTOR_TOKEN`: (Leave empty initially)
        * `NONCONTRIBUTOR_TOKEN`: (Leave empty initially)
        * `PROJECT_ID`: (Leave empty initially)
        * `ISSUE_ID`: (Leave empty initially)
        * `COMMENT_ID`: (Leave empty initially)
    * Select your newly created environment from the dropdown.

4.  **Execute Requests:**
    * Start with the user authentication requests (e.g., `signup`, `login`) to obtain JWT tokens.
    * Copy the `access` tokens and paste them into the `AUTHOR_TOKEN`, `CONTRIBUTOR_TOKEN`, or `NONCONTRIBUTOR_TOKEN` environment variables in Postman as appropriate.
    * Proceed to test other functionalities, replacing `{{project_id}}`, `{{issue_id}}`, `{{comment_id}}` as you create resources.

## Code Quality

This project adheres to Python best practices and uses static analysis for code quality.

* **Flake8:** Used to enforce PEP8 style guidelines and detect common Python code issues.
    * **Installation:** `poetry add flake8 --group dev`
    * **Usage:** From the project root, run `flake8 .`
    * All identified warnings and errors should be addressed to maintain code consistency and readability.

* **PEP20 (The Zen of Python):** While not enforced by an automated tool, the codebase strives to embody the principles of PEP20, emphasizing readability, explicitness, simplicity, and clear design. This is maintained through diligent code reviews and adherence to Python idioms.

---