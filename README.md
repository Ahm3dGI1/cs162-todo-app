# Pull Request Development Roadmap

This guide breaks down the Hierarchical Todo List project into **manageable PRs** that build on each other. Each PR represents a working, testable feature.

---

## 📋 PR Sequence Overview

| PR # | Feature | Complexity | Est. Time |
|------|---------|------------|-----------|
| PR-1 | Project Setup & Database | Easy | 30 min |
| PR-2 | User Authentication Backend | Medium | 1 hour |
| PR-3 | User Authentication Frontend | Medium | 1 hour |
| PR-4 | Todo Lists Backend | Medium | 1 hour |
| PR-5 | Todo Lists Frontend | Medium | 1.5 hours |
| PR-6 | Basic Todos Backend | Hard | 1.5 hours |
| PR-7 | Basic Todos Frontend | Hard | 2 hours |
| PR-8 | Hierarchical Todos (Subtasks) | Hard | 2 hours |
| PR-9 | Collapse/Expand Feature | Medium | 1 hour |
| PR-10 | Task Completion Feature | Easy | 45 min |
| PR-11 | Move Tasks Feature | Medium | 1 hour |
| PR-12 | Edit & Delete Features | Medium | 1 hour |
| PR-13 | Polish & Bug Fixes | Easy | 1 hour |


## 📦 Detailed PR Breakdown


### PR-4: Todo Lists Backend

**Goal:** API for creating and managing todo lists

**Branch:** `feature/lists-backend`

**Depends On:** PR-2 (needs auth)

#### Files to Create/Modify:
- `backend/routes.py` (new file - list routes)
- `backend/app.py` (register routes blueprint)

#### Features:
- ✅ GET `/api/lists` - Get all user's lists
- ✅ POST `/api/lists` - Create new list
- ✅ PUT `/api/lists/:id` - Update list name
- ✅ DELETE `/api/lists/:id` - Delete list
- ✅ All routes protected with `@login_required`


---

### PR-5: Todo Lists Frontend

**Goal:** UI for managing todo lists

**Branch:** `feature/lists-frontend`

**Depends On:** PR-3, PR-4

#### Files to Create/Modify:
- `frontend/src/components/ListSelector.js` (new file)
- `frontend/src/App.js` (add list state and management)
- `frontend/src/App.css` (add list selector styles)

#### Features:
- ✅ Sidebar showing all lists
- ✅ Create new list button + form
- ✅ Select/highlight active list
- ✅ Delete list button
- ✅ Auto-select first list on load

#### What Should Work:
- User sees sidebar with "+ New List" button
- User can create multiple lists
- Clicking a list selects it (highlights)
- User can delete a list (with confirmation)
- Main content area shows selected list name

---

### PR-6: Basic Todos Backend (Top-Level Only)

**Goal:** API for creating and managing top-level todos (no subtasks yet)

**Branch:** `feature/todos-backend`

**Depends On:** PR-4

#### Files to Modify:
- `backend/routes.py` (add todo routes)

#### Features:
- ✅ GET `/api/todos/:list_id` - Get all todos in a list
- ✅ POST `/api/todos` - Create new todo (parent_id = null only)
- ✅ PUT `/api/todos/:id` - Update todo
- ✅ DELETE `/api/todos/:id` - Delete todo
- ✅ Authorization checks (user owns the todo)

#### Note:
**For this PR, ignore parent_id completely. Only create top-level todos.**

---

### PR-7: Basic Todos Frontend (Top-Level Only)

**Goal:** UI for managing top-level todos

**Branch:** `feature/todos-frontend`

**Depends On:** PR-5, PR-6

#### Files to Create/Modify:
- `frontend/src/components/TodoList.js` (new file - list container)
- `frontend/src/components/TodoItem.js` (new file - single todo, non-recursive for now)
- `frontend/src/App.js` (render TodoList component)
- `frontend/src/App.css` (add todo styles)

#### Features:
- ✅ Display todos for selected list
- ✅ "+ Add Task" button
- ✅ Create new todo form
- ✅ Display todo title
- ✅ Edit todo (inline or modal)
- ✅ Delete todo button
- ✅ Basic checkbox (not functional yet)

#### What Should Work:
- User sees list of todos for selected list
- User can add new todos
- User can edit todo titles
- User can delete todos
- No subtasks, completion, or collapse yet

---

### PR-8: Hierarchical Todos (Add Subtasks)

**Goal:** Enable creating subtasks up to 3 levels

**Branch:** `feature/hierarchical-todos`

**Depends On:** PR-7

#### Files to Modify:
- `backend/routes.py` (update create todo to handle parent_id, add depth validation)
- `frontend/src/components/TodoItem.js` (make recursive, add "+ subtask" button)
- `frontend/src/App.css` (add indentation styles for depth)

#### Backend Changes:
- ✅ Allow `parent_id` in POST `/api/todos`
- ✅ Validate depth limit (max depth = 2, meaning 3 levels: 0, 1, 2)
- ✅ Return hierarchical structure in GET `/api/todos/:list_id`
- ✅ Calculate and return `depth` for each todo

#### Frontend Changes:
- ✅ Make TodoItem recursive (renders itself for children)
- ✅ Add "+ Add Subtask" button on each todo
- ✅ Show depth with indentation (different styles for depth-0, depth-1, depth-2)
- ✅ Disable "Add Subtask" button at depth 2
- ✅ Display depth limit message

#### What Should Work:
- User can add subtask to any todo
- User can add sub-subtask to subtasks
- System prevents adding 4th level
- Visual indentation shows hierarchy
- Deleting parent deletes all children