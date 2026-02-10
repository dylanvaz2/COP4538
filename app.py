from flask import Flask, render_template, request, redirect, url_for
import os
import json

app = Flask(__name__)

app.config['FLASK_TITLE'] = ""

# --- DATA PERSISTENCE ---
CONTACTS_FILE = 'contacts.json'

def load_contacts():
    """Load contacts from JSON file if it exists."""
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_contacts():
    """Save contacts to JSON file."""
    try:
        with open(CONTACTS_FILE, 'w') as f:
            json.dump(contacts, f, indent=2)
    except IOError as e:
        print(f"Error saving contacts: {e}")

# --- IN-MEMORY DATA STRUCTURES (Students will modify this area) ---
# Phase 1: A simple Python List to store contacts (now with persistence)
contacts = load_contacts()


# --- ROUTES ---

@app.route('/')
def index():
    """
    Displays the main page.
    Eventually, students will pass their Linked List or Tree data here.
    """
    return render_template('index.html',
                         contacts=contacts,
                         title=app.config['FLASK_TITLE'],
                         search_performed=False)

@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Students will update this to insert into their Data Structure.
    """
    name = request.form.get('name')
    email = request.form.get('email')

    # Phase 1 Logic: Append to list
    contacts.append({'name': name, 'email': email})
    save_contacts()  # Persist to file

    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_contact():
    """
    Endpoint to search for contacts by name or email.
    Students will update this to search within their Data Structure.
    """
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip().lower()

        # Phase 1 Logic: Search through list
        search_results = []
        if search_query:
            for contact in contacts:
                if (search_query in contact['name'].lower() or
                    search_query in contact['email'].lower()):
                    search_results.append(contact)

        return render_template('index.html',
                             contacts=search_results,
                             title=app.config['FLASK_TITLE'],
                             search_performed=True,
                             search_query=search_query)

    return redirect(url_for('index'))

# --- DATABASE CONNECTIVITY (For later phases) ---
# Placeholders for students to fill in during Sessions 5 and 27
def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
