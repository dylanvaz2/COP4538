from flask import Flask, render_template, request, redirect, url_for
import os
import json
from collections import deque

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

app.config['FLASK_TITLE'] = ""

# --- DATA STRUCTURES ---

class Node:
    """Node class for LinkedList."""
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """Custom LinkedList implementation to store contacts."""
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        """Add a contact to the end of the list."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def delete(self, name, email):
        """Delete a contact by name and email."""
        if not self.head:
            return None

        # If head node is the one to delete
        if self.head.data['name'] == name and self.head.data['email'] == email:
            deleted_data = self.head.data
            self.head = self.head.next
            self.size -= 1
            return deleted_data

        # Search for the node to delete
        current = self.head
        while current.next:
            if current.next.data['name'] == name and current.next.data['email'] == email:
                deleted_data = current.next.data
                current.next = current.next.next
                self.size -= 1
                return deleted_data
            current = current.next

        return None

    def to_list(self):
        """Convert LinkedList to a Python list for rendering."""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def clear(self):
        """Clear all contacts from the list."""
        self.head = None
        self.size = 0

    def __len__(self):
        return self.size

# --- DATA PERSISTENCE ---
CONTACTS_FILE = 'contacts.json'

def load_contacts():
    """Load contacts from JSON file into LinkedList and Hash Table."""
    contacts_ll = LinkedList()
    contacts_hash = {}

    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, 'r') as f:
                data = json.load(f)
                for contact in data:
                    contacts_ll.append(contact)
                    # Hash table: name -> list of contacts (handles duplicate names)
                    contacts_hash.setdefault(contact['name'].lower(), []).append(contact)
        except (json.JSONDecodeError, IOError):
            pass

    return contacts_ll, contacts_hash

def save_contacts():
    """Save contacts to JSON file."""
    try:
        with open(CONTACTS_FILE, 'w') as f:
            json.dump(contacts_list.to_list(), f, indent=2)
    except IOError as e:
        print(f"Error saving contacts: {e}")

# --- IN-MEMORY DATA STRUCTURES ---
# LinkedList to store contacts
contacts_list = LinkedList()
# Hash Table (Dictionary) for O(1) search optimization
contacts_hash = {}
# Stack for undo operations
undo_stack = []
# Queue for redo operations
redo_queue = deque()

# Load existing contacts
contacts_list, contacts_hash = load_contacts()


# --- ROUTES ---

@app.route('/')
def index():
    """
    Displays the main page with contacts from LinkedList.
    """
    return render_template('index.html',
                         contacts=contacts_list.to_list(),
                         title=app.config['FLASK_TITLE'],
                         search_performed=False,
                         undo_available=len(undo_stack) > 0,
                         redo_available=len(redo_queue) > 0)

@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact to LinkedList and Hash Table.
    Records action in undo stack.
    """
    name = request.form.get('name')
    email = request.form.get('email')

    contact = {'name': name, 'email': email}

    # Add to LinkedList
    contacts_list.append(contact)

    # Add to Hash Table for O(1) exact-name lookup (store list to allow duplicates)
    contacts_hash.setdefault(name.lower(), []).append(contact)

    # Record action for undo (clear redo queue when new action is performed)
    undo_stack.append(('add', contact))
    redo_queue.clear()

    save_contacts()

    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_contact():
    """
    Endpoint to delete a contact from LinkedList and Hash Table.
    Records action in undo stack.
    """
    name = request.form.get('name')
    email = request.form.get('email')

    # Delete from LinkedList
    deleted_contact = contacts_list.delete(name, email)

    if deleted_contact:
        # Remove from Hash Table (remove the specific contact from the name bucket)
        name_key = name.lower()
        bucket = contacts_hash.get(name_key)
        if bucket:
            # remove entries matching both name and email
            contacts_hash[name_key] = [c for c in bucket if not (c['name'] == deleted_contact['name'] and c['email'] == deleted_contact['email'])]
            if not contacts_hash[name_key]:
                contacts_hash.pop(name_key, None)

        # Record action for undo
        undo_stack.append(('delete', deleted_contact))
        redo_queue.clear()

        save_contacts()

    return redirect(url_for('index'))

@app.route('/undo', methods=['POST'])
def undo():
    """
    Undo the last action (add or delete) using the stack.
    """
    if undo_stack:
        action, contact = undo_stack.pop()

        if action == 'add':
            # Undo add = delete the contact
            contacts_list.delete(contact['name'], contact['email'])
            # remove from hash bucket
            key = contact['name'].lower()
            bucket = contacts_hash.get(key)
            if bucket:
                contacts_hash[key] = [c for c in bucket if not (c['name'] == contact['name'] and c['email'] == contact['email'])]
                if not contacts_hash[key]:
                    contacts_hash.pop(key, None)

        elif action == 'delete':
            # Undo delete = add the contact back
            contacts_list.append(contact)
            contacts_hash.setdefault(contact['name'].lower(), []).append(contact)

        # Add to redo queue
        redo_queue.append((action, contact))

        save_contacts()

    return redirect(url_for('index'))

@app.route('/redo', methods=['POST'])
def redo():
    """
    Redo the last undone action using the queue.
    """
    if redo_queue:
        action, contact = redo_queue.popleft()

        if action == 'add':
            # Redo add = add the contact again
            contacts_list.append(contact)
            contacts_hash.setdefault(contact['name'].lower(), []).append(contact)

        elif action == 'delete':
            # Redo delete = delete the contact again
            contacts_list.delete(contact['name'], contact['email'])
            # remove from hash bucket
            key = contact['name'].lower()
            bucket = contacts_hash.get(key)
            if bucket:
                contacts_hash[key] = [c for c in bucket if not (c['name'] == contact['name'] and c['email'] == contact['email'])]
                if not contacts_hash[key]:
                    contacts_hash.pop(key, None)

        # Add back to undo stack
        undo_stack.append((action, contact))

        save_contacts()

    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_contact():
    """
    Endpoint to search for contacts using Hash Table for lookup.
    Falls back to LinkedList traversal for partial matches.
    """
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        search_results = []

        if search_query:
            search_lower = search_query.lower()

            # O(1) exact name lookup using Hash Table (returns all contacts for that name)
            if search_lower in contacts_hash:
                search_results.extend(contacts_hash[search_lower])
            else:
                # Fallback: O(n) search for partial matches in LinkedList
                all_contacts = contacts_list.to_list()
                for contact in all_contacts:
                    if (search_lower in contact['name'].lower() or
                        search_lower in contact['email'].lower()):
                        search_results.append(contact)

        return render_template('index.html',
                             contacts=search_results,
                             title=app.config['FLASK_TITLE'],
                             search_performed=True,
                             search_query=search_query,
                             undo_available=len(undo_stack) > 0,
                             redo_available=len(redo_queue) > 0)

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
