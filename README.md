# Hierarchical Todo List Application

A modern, full-stack hierarchical todo list application with user authentication, multi-project management, and nested subtasks supporting up to 3 levels of hierarchy.

## ✨ Features

### Core Functionality
- ✅ **User Authentication** - Secure registration/login with bcrypt password hashing and session management
- ✅ **Multi-Project Management** - Create, edit, and delete multiple independent projects
- ✅ **Hierarchical Tasks** - Support for 3 levels of nesting (task → subtask → sub-subtask)
- ✅ **Full Task CRUD** - Create, read, update, and delete tasks at any level
- ✅ **Task Priorities** - Low, Medium, High priority levels with visual badges
- ✅ **Collapse/Expand** - Hide or show subtasks with smooth animations
- ✅ **Task Completion** - Mark tasks as complete with cascade completion to children
- ✅ **Advanced Move Operations** - Move tasks between projects and reparent within hierarchies
- ✅ **Inline Editing** - Edit task titles, descriptions, and priorities in place
- ✅ **Keyboard Shortcuts** - Esc to cancel, Ctrl+Enter to save
- ✅ **Account Management** - Change password functionality

### User Experience
- 🎨 **Modern Dashboard** - Beautiful purple gradient theme with glassmorphism effects
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- ⚡ **Optimistic Updates** - Instant UI feedback for better responsiveness
- 🔄 **Loading States** - Visual feedback during async operations
- 💬 **Error Handling** - Graceful error messages and recovery
- 🔐 **Session Persistence** - Stay logged in across page refreshes (7-day sessions)
- 🎯 **Empty States** - Helpful prompts when no data exists
- 🍔 **Sidebar Navigation** - Hamburger menu for easy navigation

### Security Features
- 🔒 **Password Hashing** - Bcrypt with salt for secure password storage
- 🛡️ **Authorization Checks** - User-scoped data access (users can only see their own data)
- 🍪 **Secure Sessions** - HTTP-only cookies with CSRF protection
- 🚫 **Input Validation** - Server-side and client-side validation
- 🔑 **Password Requirements** - Minimum 6 characters, username minimum 3 characters

### Data Integrity
- 📊 **Depth Validation** - Prevents exceeding 3-level hierarchy
- 🔄 **Circular Dependency Prevention** - Cannot move parent under its own child
- 🗑️ **Cascade Deletion** - Deleting parent automatically deletes all children
- ✅ **Cascade Completion** - Completing parent marks all children as complete
- 🔍 **Ownership Validation** - All operations verify user ownership

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 14+** - [Download](https://nodejs.org/)
- **npm** or **yarn** - Comes with Node.js

### Backend Setup

1. **Navigate to server directory:**
   ```bash
   cd server
   ```

2. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

   Server will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to client directory:**
   ```bash
   cd client
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   App will open at `http://localhost:3000`

### First Time Use

1. Navigate to `http://localhost:3000`
2. Click **"Register"** to create an account
3. Fill in username, email, and password (min 6 characters)
4. You'll be automatically logged in
5. Create your first project
6. Start adding tasks!

## 📁 Project Structure

```
cs162-todo-app/
├── client/                          # React frontend
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── __tests__/          # Component tests
│   │   │   ├── Dashboard.js        # Project dashboard
│   │   │   ├── Login.js            # Login form
│   │   │   ├── Register.js         # Registration form
│   │   │   ├── TodoList.js         # Project view with tasks
│   │   │   ├── TodoItem.js         # Individual task component
│   │   │   ├── Sidebar.js          # Navigation sidebar
│   │   │   ├── ProtectedRoute.js   # Auth route wrapper
│   │   │   └── ErrorBoundary.js    # Error boundary
│   │   ├── pages/                   # Page components
│   │   │   ├── LoginPage.js        # Login/Register page
│   │   │   ├── DashboardPage.js    # Dashboard page
│   │   │   └── ProjectPage.js      # Project detail page
│   │   ├── config/
│   │   │   └── api.js              # API endpoint configuration
│   │   ├── App.js                  # Main app component
│   │   ├── App.css                 # Global styles
│   │   └── index.js                # Entry point
│   ├── package.json
│   └── package-lock.json
│
├── server/                          # Flask backend
│   ├── tests/                       # Test suite
│   │   ├── __init__.py
│   │   ├── test_auth.py            # Authentication tests
│   │   ├── test_projects.py        # Project CRUD tests
│   │   └── test_todos.py           # Todo tests (CRUD, hierarchy, move)
│   ├── instance/                    # SQLite database (auto-generated)
│   │   └── todos.db
│   ├── app.py                       # Application factory
│   ├── models.py                    # Database models (User, TodoList, TodoItem)
│   ├── routes.py                    # API routes for projects and todos
│   ├── auth.py                      # Authentication routes and decorators
│   ├── conftest.py                  # Pytest configuration and fixtures
│   ├── requirements.txt             # Production dependencies
│   ├── requirements-dev.txt         # Development/testing dependencies
│   ├── add_priority_column.py       # Database migration script
│   └── add_order_column.py          # Database migration script
│
├── README.md                        # This file
├── TESTING.md                       # Testing documentation
└── .gitignore                       # Git ignore rules
```

## 🎯 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/logout` | Logout current user | Yes |
| GET | `/api/auth/current` | Get current user info | No (returns 401 if not logged in) |
| POST | `/api/auth/change-password` | Change user password | Yes |

**Example Register Request:**
```json
POST /api/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

### Project Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/projects` | List all user projects | Yes |
| GET | `/api/projects/:id` | Get specific project | Yes |
| POST | `/api/projects` | Create new project | Yes |
| PUT | `/api/projects/:id` | Update project name | Yes |
| DELETE | `/api/projects/:id` | Delete project (cascade deletes todos) | Yes |

**Example Create Project Request:**
```json
POST /api/projects
{
  "name": "Work Tasks"
}
```

### Todo Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/todos/:project_id` | Get all todos for project (hierarchical) | Yes |
| POST | `/api/todos` | Create new todo | Yes |
| PUT | `/api/todos/:id` | Update todo (title, description, priority, completed, collapsed) | Yes |
| DELETE | `/api/todos/:id` | Delete todo (cascade deletes children) | Yes |
| POST | `/api/todos/:id/reparent` | Move/reparent todo to new location | Yes |

**Example Create Todo Request:**
```json
POST /api/todos
{
  "project_id": 1,
  "title": "Complete project documentation",
  "description": "Add comprehensive README and API docs",
  "priority": "high",
  "parent_id": null  // Optional: ID of parent task
}
```

**Example Reparent Todo Request:**
```json
POST /api/todos/5/reparent
{
  "new_parent_id": 3,     // null for top-level
  "new_project_id": 1,    // Can move to different project
  "new_order": 0
}
```

## 📚 Technology Stack

### Frontend
- **React 19.2.0** - UI library with functional components and hooks
- **React Router 7.9.5** - Client-side routing
- **FontAwesome 7.1.0** - Icon library
- **Fetch API** - HTTP client for API calls
- **CSS3** - Modern styling with gradients, animations, and glassmorphism
- **React Testing Library** - Component testing

### Backend
- **Flask 3.1.2** - Lightweight web framework
- **Flask-SQLAlchemy 3.1.1** - ORM for database operations
- **Flask-CORS 6.0.1** - Cross-Origin Resource Sharing support
- **SQLite** - Embedded relational database
- **Werkzeug 3.1.3** - Password hashing utilities
- **pytest 8.0.0** - Testing framework

### Development Tools
- **pytest-flask** - Flask testing utilities
- **pytest-cov** - Code coverage reporting
- **Jest** - JavaScript testing framework (included with Create React App)

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### TodoLists Table (Projects)
```sql
CREATE TABLE todo_lists (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### TodoItems Table
```sql
CREATE TABLE todo_items (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    collapsed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'medium',
    depth INTEGER DEFAULT 0,
    order_index INTEGER DEFAULT 0,
    list_id INTEGER NOT NULL,
    parent_id INTEGER,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES todo_lists(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES todo_items(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 🎨 UI/UX Design

### Color Scheme
- **Primary Gradient:** Purple to Indigo (`#9333EA` → `#6366F1`)
- **Background:** Dark gradient (`#0F172A` → `#1E293B`)
- **Text:** White with proper contrast ratios
- **Accents:** Various purple/indigo shades for depth

### Key Design Patterns
- **Glassmorphism** - Translucent cards with backdrop blur
- **Smooth Animations** - CSS transitions for all interactive elements
- **Visual Hierarchy** - Clear distinction between levels using indentation
- **Priority Indicators** - Color-coded badges (Low: Blue, Medium: Yellow, High: Red)
- **Hover States** - Interactive feedback on all clickable elements
- **Empty States** - Helpful prompts when no data exists

## 🧪 Testing

Comprehensive test suite with 55+ backend tests and sample frontend tests.

### Run Backend Tests
```bash
cd server
pip install -r requirements-dev.txt
pytest -v
```

### Run Frontend Tests
```bash
cd client
npm test
```

### Generate Coverage Reports
```bash
# Backend
cd server
pytest --cov=. --cov-report=html

# Frontend
cd client
npm test -- --coverage
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## 🔒 Security Best Practices

1. **Passwords** - Hashed with bcrypt (never stored in plaintext)
2. **Sessions** - HTTP-only cookies prevent XSS attacks
3. **Authorization** - Every endpoint validates user ownership
4. **Input Validation** - Server-side validation on all inputs
5. **CORS** - Configured to only allow requests from frontend origin
6. **SQL Injection** - Prevented by SQLAlchemy ORM parameterization
7. **Password Requirements** - Minimum length enforcement

## 📝 Usage Examples

### Creating a Hierarchical Task Structure

1. **Create a project:** "Website Redesign"
2. **Create top-level task:** "Frontend Development"
3. **Add subtask:** "Create landing page"
4. **Add sub-subtask:** "Design hero section"

Result:
```
📁 Website Redesign
  ├─ Frontend Development (depth 0)
  │   └─ Create landing page (depth 1)
  │       └─ Design hero section (depth 2)
```

### Moving Tasks

You can move tasks:
- From subtask to top-level
- From one parent to another
- To a different project entirely
- System prevents moves that would exceed depth limit

## 🐛 Troubleshooting

### Backend Issues

**Database not found:**
```bash
# Database is auto-created on first run
# If issues persist, delete instance/todos.db and restart
```

**Import errors:**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

**Port already in use:**
```bash
# Change port in app.py (line 71-75)
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Frontend Issues

**API connection refused:**
```bash
# Ensure backend is running on port 5000
# Check client/package.json has "proxy": "http://localhost:5000"
```

**Module not found:**
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Deployment

### Backend Deployment

1. **Set environment variables:**
   ```bash
   export SECRET_KEY='your-production-secret-key'
   export FLASK_ENV=production
   ```

2. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

### Frontend Deployment

1. **Build production bundle:**
   ```bash
   cd client
   npm run build
   ```

2. **Serve static files** with Nginx, Apache, or hosting service

### Recommended Platforms
- **Backend:** Heroku, Railway, Render, PythonAnywhere
- **Frontend:** Vercel, Netlify, GitHub Pages
- **Database:** PostgreSQL (replace SQLite in production)

## 🤝 Contributing

This is a student project for CS162. While not accepting external contributions, feel free to fork and adapt for your own use.

## 📄 License

Educational project - use freely for learning purposes.

## 👨‍💻 Author

Created as a CS162 course project demonstrating full-stack web development with React and Flask.

## 🙏 Acknowledgments

- Flask documentation and community
- React documentation and ecosystem
- FontAwesome for icons
- CS162 course staff and materials

## 📚 Further Learning

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Note:** This application is designed for educational purposes. For production use, consider:
- PostgreSQL instead of SQLite
- Redis for session storage
- JWT tokens instead of server-side sessions
- Rate limiting and additional security measures
- Comprehensive logging and monitoring
- Automated backups
