# Hierarchical Todo List Application

A modern, full-stack hierarchical todo list application with user authentication, project management, and nested subtasks.

## ✨ Features

### Core Functionality
- ✅ **User Authentication** - Secure login/register with session management
- ✅ **Project Management** - Create, edit, and delete projects (todo lists)
- ✅ **Hierarchical Tasks** - Support for 3 levels of nesting (task → subtask → sub-subtask)
- ✅ **Task Operations** - Create, read, update, and delete tasks at any level
- ✅ **Collapse/Expand** - Hide or show subtasks with smooth animations
- ✅ **Task Completion** - Mark tasks as complete with cascade completion to children
- ✅ **Move Tasks** - Move top-level tasks between projects
- ✅ **Inline Editing** - Edit task titles and descriptions in place
- ✅ **Keyboard Shortcuts** - Esc to cancel, Ctrl+Enter to save

### User Experience
- ✅ **Dashboard View** - Clean project selection interface
- ✅ **Responsive Design** - Works on desktop and mobile devices
- ✅ **Optimistic Updates** - Instant UI feedback for better UX
- ✅ **Loading States** - Visual feedback during operations
- ✅ **Error Handling** - Graceful error messages and recovery
- ✅ **Session Persistence** - Stay logged in across page refreshes

### Technical Features
- ✅ **RESTful API** - Well-structured backend endpoints
- ✅ **Database Models** - SQLAlchemy with proper relationships
- ✅ **Modern React** - Functional components with hooks
- ✅ **Beautiful UI** - Purple gradient theme with smooth animations
- ✅ **Security** - Password hashing, session management, authorization checks

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup
```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd client
npm install
npm start
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
cs162-todo-app/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── config/        # API configuration
│   │   ├── App.js         # Main app component
│   │   └── App.css        # Global styles
│   └── package.json
├── server/                # Flask backend
│   ├── app.py            # Main application
│   ├── models.py         # Database models
│   ├── routes.py         # API routes
│   ├── auth.py           # Authentication logic
│   └── requirements.txt
└── README.md
```

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/current` - Get current user

### Projects
- `GET /api/projects` - List all user projects
- `POST /api/projects` - Create new project
- `PUT /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project

### Todos
- `GET /api/todos/:project_id` - Get todos for project
- `POST /api/todos` - Create new todo
- `PUT /api/todos/:id` - Update todo
- `DELETE /api/todos/:id` - Delete todo
- `POST /api/todos/:id/move` - Move todo to different project

## 📚 Technology Stack

### Frontend
- **React** - UI framework
- **Fetch API** - HTTP client
- **CSS3** - Styling with gradients and animations

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **Werkzeug** - Password hashing

## 🎨 Design Philosophy

- **Minimalist** - Clean, focused interface
- **Intuitive** - Common patterns and clear affordances
- **Responsive** - Adapts to different screen sizes
- **Performant** - Optimistic updates for instant feedback
- **Accessible** - Proper ARIA labels and keyboard navigation
