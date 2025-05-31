const API_BASE_URL = 'http://localhost:8080/api/v1';

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = e.target.dataset.section;
        showSection(section);
    });
});

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.getElementById(`${sectionId}-section`).classList.add('active');
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
}

// Books
async function loadBooks() {
    try {
        const response = await fetch(`${API_BASE_URL}/books`);
        const books = await response.json();
        const booksList = document.getElementById('books-list');
        booksList.innerHTML = books.map(book => `
            <tr>
                <td>${book.id}</td>
                <td>${book.title}</td>
                <td>${book.author}</td>
                <td>${book.isbn}</td>
                <td>
                    <span class="status-badge ${book.is_reserved ? 'status-reserved' : 'status-available'}">
                        ${book.is_reserved ? 'Reserved' : 'Available'}
                    </span>
                </td>
                <td>
                    ${!book.is_reserved ?
            `<button class="btn btn-sm btn-success btn-action" onclick="reserveBook('${book.id}')">Reserve</button>` :
            `<button class="btn btn-sm btn-warning btn-action" onclick="cancelReservation('${book.id}')">Cancel</button>`
        }
                    <button class="btn btn-sm btn-danger btn-action" onclick="deleteBook('${book.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading books:', error);
        alert('Error loading books. Please try again.');
    }
    loadUsers();
}

// Users
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users`);
        const users = await response.json();
        const usersList = document.getElementById('users-list');
        usersList.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user["reserved_books"].length}</td>
                <td>
                    <button class="btn btn-sm btn-primary btn-action" data-bs-toggle="modal" data-bs-target="#editUserModal" 
                    onclick="sendUserId('${user.id}')">Edit</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Error loading users. Please try again.');
    }
}

// Reservations
async function loadReservations(user_id) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${user_id}/reservations`, {
            headers: {
                'userId': String(user_id)
            },
            method: "GET",
        });

        const reservations = await response.json();

        const reservationsList = document.getElementById('reservations-list');
        reservationsList.innerHTML = reservations.map(reservation => `
            <tr>
                <td>${reservation["book_id"]}</td>
                <td>${reservation["title"]}</td>
                <td>${reservation["reserved_time"]}</td>
                <td>
                    <button class="btn btn-sm btn-danger btn-action" onclick="cancelReservation('${reservation["book_id"]}')">Cancel</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading reservations:', error);
        alert('Error loading reservations. Please try again.');
    }
}

// Add Book
document.getElementById('save-book').addEventListener('click', async () => {
    const title = document.getElementById('book-title').value;
    const author = document.getElementById('book-author').value;
    const isbn = document.getElementById('book-isbn').value;
    if (!title || !author || !isbn) {
        alert('please fill the blanks');
        return;
    }


    try {
        const response = await fetch(`${API_BASE_URL}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({title, author, isbn})
        });
        if (response.status === 402) {
            alert('invalid isbn format');
            return;
        }
        if (response.status === 400) {
            alert('book already exists');
            return;
        }
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addBookModal')).hide();
            document.getElementById('add-book-form').reset();
            loadBooks();
        } else {
            const error = await response.json();
            alert(error.error || 'Error adding book');
        }
    } catch (error) {
        console.error('Error adding book:', error);
        alert('Error adding book. Please try again.');
    }
});

// Add User
document.getElementById('save-user').addEventListener('click', async () => {
    const username = document.getElementById('user-username').value;
    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    if (!username || !name || !email) {
        alert('please fill the blanks');
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username, name, email})
        });
        console.log(response.statusText)
        if (response.status === 402) {
            alert('invalid email format');
            return;
        }
        if (response.status === 403) {
            alert('invalid username(only a-Z, 0-9, _ and at least 3 character)');
            return;
        }
        if (response.status === 400) {
            alert('username already exists');
            return;
        }
        console.log(response.status, 'this is the status');
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
            document.getElementById('add-user-form').reset();
            alert('user added successfully')
            loadUsers();
        } else {
            const error = await response.json();
            alert(error.error || 'Error adding user');
        }
    } catch (error) {
        console.log(error, 'this is the error');
        console.error('Error adding user:', error);
        alert('Error adding user. Please try again.');
    }
});


// Edit User
var editing_user_id

function sendUserId(user_id) {
    editing_user_id = user_id
}

document.getElementById('edit-user').addEventListener('click', async () => {
    const username = document.getElementById('user-new-username').value;
    const name = document.getElementById('user-new-name').value;
    const email = document.getElementById('user-new-email').value;
    try {

        const response = await fetch(`${API_BASE_URL}/users/${editing_user_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username, name, email})
        });
        console.log(response.statusText)
        if (response.status === 402) {
            alert('invalid email format');
            return;
        }
        if (response.status === 403) {
            alert('invalid username(only a-Z, 0-9, _ and at least 3 character)');
            return;
        }
        if (response.status === 400) {
            alert('username already exists');
            return;
        }
        console.log(response.status, 'this is the status');
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
            document.getElementById('add-user-form2').reset();
            alert('user edited successfully')
            loadUsers();
        } else {
            const error = await response.json();
            alert(error.error || 'Error adding user');
        }
    } catch (error) {
        console.log(error, 'this is the error');
        console.error('Error adding user:', error);
        alert('Error adding user. Please try again.');
    }
});

// Reserve Book
async function reserveBook(bookId) {
    const user_id = prompt('Please enter your user ID:');
    if (!user_id) return;

    try {

        console.log(user_id);
        const response = await fetch(`${API_BASE_URL}/books/${bookId}/reserve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({user_id})
        });

        if (response.ok) {
            loadBooks();
            alert('Book reserved successfully!');
        } else {
            const error = await response.json();
            alert(error.error || 'Error reserving book');
        }
    } catch (error) {
        console.error('Error reserving book:', error);
        alert('Error reserving book. Please try again.');
    }
}

// Cancel Reservation
async function cancelReservation(bookId) {
    const user_id = prompt('Please enter your user ID:');
    if (!user_id) return;

    try {
        const response = await fetch(`${API_BASE_URL}/books/${bookId}/reserve`, {
            method: 'DELETE',
            headers: {
                'userId': String(user_id)
            },
        });
        if (response.status === 400) {
            alert('user ID is wrong');
            return;
        }
        if (response.ok) {
            loadBooks();
            loadReservations(String(user_id));
            alert('Reservation cancelled successfully!');
        } else {
            const error = await response.json();
            alert(error.error || 'Error cancelling reservation');
        }
    } catch (error) {
        console.error('Error cancelling reservation:', error);
        alert('Error cancelling reservation. Please try again.');
    }
}

// Delete Book
async function deleteBook(bookId) {
    if (!confirm('Are you sure you want to delete this book?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/books/${bookId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadBooks();
            alert('Book deleted successfully!');
        } else {
            const error = await response.json();
            alert(error.error || 'Error deleting book');
        }
    } catch (error) {
        console.error('Error deleting book:', error);
        alert('Error deleting book. Please try again.');
    }
}

// View Reservations
document.getElementById('view-reservations').addEventListener('click', () => {
    const userId = document.getElementById('user-id').value;
    if (!userId) {
        alert('Please enter a user ID');
        return;
    }
    loadReservations(userId);
});

// Initial load
loadBooks();
loadUsers(); 