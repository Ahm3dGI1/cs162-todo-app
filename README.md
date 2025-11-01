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
# Pull Request Development Roadmap

This guide breaks down the Hierarchical Todo List project into **manageable PRs** that build on each other. Each PR represents a working, testable feature.

---

## 🎯 Development Strategy

### PR-9: Collapse/Expand Feature

**Goal:** Add ability to hide/show subtasks

**Branch:** `feature/collapse-expand`

**Depends On:** PR-8

#### Files to Modify:
- `backend/routes.py` (update PUT todo to handle `collapsed` field)
- `frontend/src/components/TodoItem.js` (add collapse button, conditionally render children)
- `frontend/src/App.css` (add collapse button styles)

#### Features:
- ✅ Add `collapsed` boolean field to TodoItem model
- ✅ Update endpoint accepts `collapsed` in request
- ✅ Frontend shows ▶/▼ arrow button when todo has children
- ✅ Clicking arrow toggles collapsed state
- ✅ Children hidden when collapsed = true
- ✅ Collapsed state persists in database

#### What Should Work:
- Todos with children show collapse arrow
- Clicking ▶ expands (shows children)
- Clicking ▼ collapses (hides children)
- State persists after refresh

### PR-10: Task Completion Feature

**Goal:** Mark tasks as complete/incomplete

**Branch:** `feature/task-completion`

**Depends On:** PR-9

#### Files to Modify:
- `backend/routes.py` (update PUT todo to handle `completed` field)
- `frontend/src/components/TodoItem.js` (add functional checkbox)
- `frontend/src/App.css` (add completed task styles)

#### Features:
- ✅ Checkbox toggles `completed` boolean
- ✅ Completed tasks have visual styling (strikethrough, opacity)
- ✅ Completed state persists in database
- ✅ Can toggle back to incomplete

#### What Should Work:
- Checking checkbox marks task complete
- Completed tasks show strikethrough
- Unchecking checkbox marks incomplete
- State persists after refresh

### PR-11: Move Tasks Between Lists

**Goal:** Move top-level tasks to different lists

**Branch:** `feature/move-tasks`

**Depends On:** PR-10

#### Files to Modify:
- `backend/routes.py` (add PUT `/api/todos/:id/move` endpoint)
- `frontend/src/components/TodoItem.js` (add move button/dropdown for top-level only)
- `frontend/src/App.css` (add move UI styles)

#### Features:
- ✅ Backend endpoint to move todo to different list
- ✅ Recursively update list_id for todo and all children
- ✅ Frontend shows move button only on top-level todos
- ✅ Dropdown/modal to select target list
- ✅ Moved todo appears in new list

#### What Should Work:
- Top-level todos have "Move to..." option
- User selects target list
- Todo and all subtasks move to new list
- Subtasks cannot be moved (button hidden)

### PR-12: Edit & Delete Polish

**Goal:** Improve edit/delete UX

**Branch:** `feature/edit-delete-polish`

**Depends On:** PR-11

#### Files to Modify:
- `frontend/src/components/TodoItem.js` (improve edit form, add descriptions)
- `frontend/src/App.css` (polish styles)

#### Features:
- ✅ Edit todo title inline
- ✅ Add optional description field
- ✅ Delete confirmation dialog
- ✅ Better button placement
- ✅ Loading states during operations

#### What Should Work:
- Click todo to edit in place
- Can add/edit description
- Delete asks for confirmation
- UI is polished and clear

### PR-13: Final Polish & Bug Fixes

**Goal:** Final touches, documentation, and testing

**Branch:** `feature/final-polish`

**Depends On:** PR-12

#### Files to Modify:
- `README.md` (complete documentation)
- `frontend/src/App.css` (final style tweaks)
- Any bug fixes discovered during testing

#### Tasks:
- ✅ Complete README with all sections
- ✅ Test all features end-to-end
- ✅ Fix any discovered bugs
- ✅ Add loading states where missing
- ✅ Improve error messages
- ✅ Mobile responsiveness (optional)
- ✅ Code cleanup and comments
- ✅ Remove console.logs

#### What Should Work:
- All MVP features working perfectly
- No console errors
- Clean, polished UI
- Complete documentation

## 🎯 Testing Checklist After Each PR

After merging each PR, verify:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] New feature works as expected
- [ ] Previous features still work (regression test)
- [ ] No console errors in browser
- [ ] No errors in terminal