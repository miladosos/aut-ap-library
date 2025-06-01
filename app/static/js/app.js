document.addEventListener('DOMContentLoaded', function() {
    const booksTableBody = document.querySelector('#booksTable tbody');
    const usersTableBody = document.querySelector('#usersTable tbody');
    const reservationsTableBody = document.querySelector('#reservationsTable tbody');

    const fetchBooks = async (query = '') => {
        let url = '/api/v1/books';
        if (query) {
            url = `/api/v1/books/search?query=${encodeURIComponent(query)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        renderBooks(data.books);
    };

    const fetchUsers = async () => {
        const res = await fetch('/api/v1/users');
        const data = await res.json();
        renderUsers(data.users);
    };

    const renderBooks = (books) => {
        booksTableBody.innerHTML = '';
        books.forEach(book => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${book.id}</td>
                <td>${book.title}</td>
                <td>${book.author}</td>
                <td>${book.isbn}</td>
                <td>${book.is_reserved}</td>
                <td>
                    <button class="btn btn-sm btn-warning me-2" onclick="reserveBook('${book.id}')" ${book.is_reserved ? 'disabled' : ''}>Reserve</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteBook('${book.id}')">Delete</button>
                </td>
            `;
            booksTableBody.appendChild(tr);
        });
    };

    const renderUsers = (users) => {
        usersTableBody.innerHTML = '';
        users.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.id}')">Delete</button>
                </td>
            `;
            usersTableBody.appendChild(tr);
        });
    };

    const renderReservations = (books) => {
        reservationsTableBody.innerHTML = '';
        books.forEach(book => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${book.id}</td>
                <td>${book.title}</td>
                <td>${book.author}</td>
                <td>${book.isbn}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="unreserveBook('${book.id}')">Unreserve</button>
                </td>
            `;
            reservationsTableBody.appendChild(tr);
        });
    };

    window.reserveBook = async (bookId) => {
        const userId = prompt('Enter your user ID:');
        if (!userId) return;
        const res = await fetch(`/api/v1/books/${bookId}/reserve`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        if (res.ok) {
            fetchBooks();
        } else {
            alert(data.message || 'Error reserving book');
        }
    };

    window.unreserveBook = async (bookId) => {
        const userId = document.querySelector('#reservationUserId').value;
        if (!userId) return alert('Enter User ID first');
        const res = await fetch(`/api/v1/books/${bookId}/unreserve`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        if (res.ok) {
            viewReservations();
            fetchBooks();
        } else {
            alert(data.message || 'Error unreserving book');
        }
    };

    window.deleteBook = async (bookId) => {
        const res = await fetch(`/api/v1/books/${bookId}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) fetchBooks();
        else {
            alert(data.message || 'Error deleting book');
        }
    };

    window.deleteUser = async (userId) => {
        const res = await fetch(`/api/v1/users/${userId}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) fetchUsers();
        else {
            alert(data.message || 'Error deleting user');
        }
    };

    const addBookForm = document.querySelector('#addBookForm');
    addBookForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.querySelector('#bookTitle').value;
        const author = document.querySelector('#bookAuthor').value;
        const isbn = document.querySelector('#bookISBN').value;
        const res = await fetch('/api/v1/books', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, author, isbn })
        });
        const data = await res.json();
        if (res.ok) {
            addBookForm.reset();
            fetchBooks();
        } else {
            alert(data.message || 'Error adding book');
        }
    });

    const addUserForm = document.querySelector('#addUserForm');
    addUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.querySelector('#userUsername').value;
        const name = document.querySelector('#userName').value;
        const email = document.querySelector('#userEmail').value;
        const res = await fetch('/api/v1/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, name, email })
        });
        const data = await res.json();
        if (res.ok) {
            addUserForm.reset();
            fetchUsers();
        } else {
            alert(data.message || 'Error adding user');
        }
    });

    document.querySelector('#searchButton').addEventListener('click', () => {
        const query = document.querySelector('#searchQuery').value;
        if (!query) return alert('Please enter search query');
        fetchBooks(query);
    });

    document.querySelector('#viewReservationsButton').addEventListener('click', () => {
        viewReservations();
    });

    const viewReservations = async () => {
        const userId = document.querySelector('#reservationUserId').value;
        if (!userId) return alert('Enter User ID');
        const res = await fetch(`/api/v1/users/${userId}/reservations`, {
            method: 'POST', 
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        if (res.ok) {
            renderReservations(data);
        } else {
            alert(data.message || 'Error fetching reservations');
        }
    };

    // Initial fetch
    fetchBooks();
    fetchUsers();
});