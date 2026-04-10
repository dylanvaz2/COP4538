from flask import Flask, render_template, request, redirect, url_for
import os
import json
import heapq
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

        if self.head.data['name'] == name and self.head.data['email'] == email:
            deleted_data = self.head.data
            self.head = self.head.next
            self.size -= 1
            return deleted_data

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
        self.head = None
        self.size = 0

    def __len__(self):
        return self.size


# --- BINARY SEARCH TREE (for contact categories) ---

class BSTNode:
    """Node in the Category BST. Key is the category string."""
    def __init__(self, category):
        self.category = category
        self.contacts = []      # contacts in this category
        self.left = None
        self.right = None


class CategoryBST:
    """
    Binary Search Tree organising contacts by category.
    Tree hierarchy: category -> department -> team
    BST key = category name (alphabetically ordered).
    """
    def __init__(self):
        self.root = None

    def insert(self, contact):
        category = contact.get('category', 'general') or 'general'
        self.root = self._insert(self.root, category.lower(), contact)

    def _insert(self, node, category, contact):
        if node is None:
            n = BSTNode(category)
            n.contacts.append(contact)
            return n
        if category == node.category:
            node.contacts.append(contact)
        elif category < node.category:
            node.left = self._insert(node.left, category, contact)
        else:
            node.right = self._insert(node.right, category, contact)
        return node

    def remove_contact(self, contact):
        """Remove a specific contact from its category node."""
        category = (contact.get('category', 'general') or 'general').lower()
        node = self._find(self.root, category)
        if node:
            node.contacts = [
                c for c in node.contacts
                if not (c['name'] == contact['name'] and c['email'] == contact['email'])
            ]

    def _find(self, node, category):
        if node is None:
            return None
        if category == node.category:
            return node
        elif category < node.category:
            return self._find(node.left, category)
        else:
            return self._find(node.right, category)

    def search_category(self, category):
        """Return all contacts in the given category."""
        node = self._find(self.root, category.lower())
        return node.contacts if node else []

    def inorder(self):
        """In-order traversal — returns list of {category, department_groups}
        sorted alphabetically by category."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        if node.contacts:
            # Group contacts within the category by department -> team
            dept_map = {}
            for c in node.contacts:
                dept = c.get('department', '') or 'General'
                team = c.get('team', '') or 'General'
                dept_map.setdefault(dept, {}).setdefault(team, []).append(c)
            result.append({'category': node.category, 'departments': dept_map})
        self._inorder(node.right, result)

    def rebuild(self, contacts):
        """Rebuild the entire BST from a list of contacts."""
        self.root = None
        for c in contacts:
            self.insert(c)


# --- VIP PRIORITY QUEUE (max-heap via negated priority) ---

class VIPHeap:
    """
    Max-heap priority queue for VIP contacts.
    Contacts with higher priority surface to the top.
    Heap entry: (-priority, id, contact_dict)
    """
    def __init__(self):
        self._heap = []

    def push(self, contact):
        priority = contact.get('priority', 1) or 1
        heapq.heappush(self._heap, (-priority, contact['id'], contact))

    def remove(self, contact):
        """Mark-and-filter removal (heapq has no direct remove)."""
        self._heap = [
            item for item in self._heap
            if not (item[2]['name'] == contact['name'] and
                    item[2]['email'] == contact['email'])
        ]
        heapq.heapify(self._heap)

    def get_sorted(self):
        """Return VIP contacts sorted by priority descending."""
        return [item[2] for item in sorted(self._heap)]

    def rebuild(self, contacts):
        self._heap = []
        for c in contacts:
            if c.get('is_vip'):
                self.push(c)

    def __len__(self):
        return len(self._heap)


# --- SORTING & SEARCHING ALGORITHMS ---

def quick_sort(arr, key='name'):
    """Quick Sort implementation for sorting contacts by a given key."""
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    pivot_val = pivot[key].lower() if isinstance(pivot[key], str) else pivot[key]

    left, middle, right = [], [], []
    for item in arr:
        item_val = item[key].lower() if isinstance(item[key], str) else item[key]
        if item_val < pivot_val:
            left.append(item)
        elif item_val == pivot_val:
            middle.append(item)
        else:
            right.append(item)

    return quick_sort(left, key) + middle + quick_sort(right, key)


def binary_search(sorted_contacts, target, key='name'):
    """Binary Search on a sorted list of contacts by a given key."""
    low, high = 0, len(sorted_contacts) - 1
    if isinstance(target, str):
        target = target.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_contacts[mid][key]
        if isinstance(mid_val, str):
            mid_val = mid_val.lower()

        if mid_val == target:
            return sorted_contacts[mid]
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return None


def find_contact_by_id(contacts, target_id):
    """Quick Sort by id then Binary Search — O(n log n) sort + O(log n) search."""
    sorted_contacts = quick_sort(contacts, key='id')
    return binary_search(sorted_contacts, target_id, key='id')


# --- DATA PERSISTENCE ---
CONTACTS_FILE = 'contacts.json'

def _defaults(contact, max_id):
    """Back-fill missing fields added in later versions."""
    if 'id' not in contact:
        max_id += 1
        contact['id'] = max_id
    contact.setdefault('category', 'general')
    contact.setdefault('department', '')
    contact.setdefault('team', '')
    contact.setdefault('is_vip', False)
    contact.setdefault('priority', 1)
    return contact, max(max_id, contact['id'])


def load_contacts():
    """Load contacts from JSON into LinkedList, Hash Table, BST, and VIP Heap."""
    ll = LinkedList()
    hash_table = {}
    bst = CategoryBST()
    vip = VIPHeap()
    max_id = 0

    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, 'r') as f:
                data = json.load(f)
            for contact in data:
                contact, max_id = _defaults(contact, max_id)
                ll.append(contact)
                hash_table.setdefault(contact['name'].lower(), []).append(contact)
                bst.insert(contact)
                if contact.get('is_vip'):
                    vip.push(contact)
        except (json.JSONDecodeError, IOError):
            pass

    return ll, hash_table, bst, vip, max_id


def save_contacts():
    """Save contacts to JSON file."""
    try:
        with open(CONTACTS_FILE, 'w') as f:
            json.dump(contacts_list.to_list(), f, indent=2)
    except IOError as e:
        print(f"Error saving contacts: {e}")


# --- IN-MEMORY DATA STRUCTURES ---
contacts_list = LinkedList()
contacts_hash = {}
category_bst = CategoryBST()
vip_heap = VIPHeap()
next_id = 0
undo_stack = []
redo_queue = deque()

contacts_list, contacts_hash, category_bst, vip_heap, next_id = load_contacts()


# --- HELPERS ---

def _add_to_structures(contact):
    """Add a contact to all in-memory structures."""
    contacts_list.append(contact)
    contacts_hash.setdefault(contact['name'].lower(), []).append(contact)
    category_bst.insert(contact)
    if contact.get('is_vip'):
        vip_heap.push(contact)


def _remove_from_structures(contact):
    """Remove a contact from all in-memory structures."""
    contacts_list.delete(contact['name'], contact['email'])
    key = contact['name'].lower()
    bucket = contacts_hash.get(key, [])
    contacts_hash[key] = [
        c for c in bucket
        if not (c['name'] == contact['name'] and c['email'] == contact['email'])
    ]
    if not contacts_hash[key]:
        contacts_hash.pop(key, None)
    category_bst.remove_contact(contact)
    if contact.get('is_vip'):
        vip_heap.remove(contact)


# --- ROUTES ---

@app.route('/')
def index():
    all_contacts = contacts_list.to_list()
    vip_contacts = vip_heap.get_sorted()
    vip_ids = {c['id'] for c in vip_contacts}
    regular_contacts = [c for c in all_contacts if c['id'] not in vip_ids]
    category_tree = category_bst.inorder()

    return render_template('index.html',
                           vip_contacts=vip_contacts,
                           regular_contacts=regular_contacts,
                           category_tree=category_tree,
                           title=app.config['FLASK_TITLE'],
                           search_performed=False,
                           undo_available=len(undo_stack) > 0,
                           redo_available=len(redo_queue) > 0)


@app.route('/add', methods=['POST'])
def add_contact():
    global next_id
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    category = request.form.get('category', 'general').strip() or 'general'
    department = request.form.get('department', '').strip()
    team = request.form.get('team', '').strip()
    is_vip = request.form.get('is_vip') == 'on'
    priority = int(request.form.get('priority', 1) or 1)
    priority = max(1, min(10, priority))  # clamp 1–10

    next_id += 1
    contact = {
        'id': next_id,
        'name': name,
        'email': email,
        'category': category,
        'department': department,
        'team': team,
        'is_vip': is_vip,
        'priority': priority,
    }

    _add_to_structures(contact)
    undo_stack.append(('add', contact))
    redo_queue.clear()
    save_contacts()

    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_contact():
    name = request.form.get('name')
    email = request.form.get('email')

    # Find the full contact object before removing (need all fields for BST/heap)
    all_contacts = contacts_list.to_list()
    target = next(
        (c for c in all_contacts if c['name'] == name and c['email'] == email),
        None
    )

    if target:
        _remove_from_structures(target)
        undo_stack.append(('delete', target))
        redo_queue.clear()
        save_contacts()

    return redirect(url_for('index'))


@app.route('/undo', methods=['POST'])
def undo():
    if undo_stack:
        action, contact = undo_stack.pop()
        if action == 'add':
            _remove_from_structures(contact)
        elif action == 'delete':
            _add_to_structures(contact)
        redo_queue.append((action, contact))
        save_contacts()
    return redirect(url_for('index'))


@app.route('/redo', methods=['POST'])
def redo():
    if redo_queue:
        action, contact = redo_queue.popleft()
        if action == 'add':
            _add_to_structures(contact)
        elif action == 'delete':
            _remove_from_structures(contact)
        undo_stack.append((action, contact))
        save_contacts()
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search_contact():
    """
    Search using Quick Sort + Binary Search (exact name match).
    Falls back to linear scan for partial / email matches.
    """
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        search_results = []

        if search_query:
            search_lower = search_query.lower()
            all_contacts = contacts_list.to_list()

            sorted_contacts = quick_sort(all_contacts, key='name')
            exact = binary_search(sorted_contacts, search_lower, key='name')

            if exact:
                idx = sorted_contacts.index(exact)
                left = idx - 1
                while left >= 0 and sorted_contacts[left]['name'].lower() == search_lower:
                    search_results.append(sorted_contacts[left])
                    left -= 1
                search_results.reverse()
                search_results.append(exact)
                right = idx + 1
                while right < len(sorted_contacts) and sorted_contacts[right]['name'].lower() == search_lower:
                    search_results.append(sorted_contacts[right])
                    right += 1
            else:
                for contact in all_contacts:
                    if (search_lower in contact['name'].lower() or
                            search_lower in contact['email'].lower()):
                        search_results.append(contact)

        return render_template('index.html',
                               contacts=search_results,
                               vip_contacts=[],
                               regular_contacts=search_results,
                               category_tree=[],
                               title=app.config['FLASK_TITLE'],
                               search_performed=True,
                               search_query=search_query,
                               undo_available=len(undo_stack) > 0,
                               redo_available=len(redo_queue) > 0)

    return redirect(url_for('index'))


# --- DATABASE CONNECTIVITY (For later phases) ---
def get_postgres_connection():
    pass

def get_mssql_connection():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
