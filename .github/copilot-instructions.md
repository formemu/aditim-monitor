<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# ADITIM Monitor - AI Coding Agent Instructions

## Project Overview

ADITIM Monitor is a client-server task management system for metalworking workshop. The system tracks production tasks for creating profiles/tools and other manufacturing work, allowing managers to create tasks and workers to view prioritized task queues.

## Client-Server Architecture

### Server Component (`src/server/`)
- **FastAPI Application** (`src/server/main.py`): REST API server with SQLAlchemy models
- **Database Models** (`src/server/models/`): SQLAlchemy declarative models for tasks, profiles, products
- **API Routes** (`src/server/api/`): CRUD operations for tasks, directories, and status management
- **Database** (`aditim.db`): SQLite database with tables for tasks, products, profiles, directories

### Client Component (`src/client/`)
- **PySide6 Application** (`src/client/main.py`): Desktop GUI application
- **UI Forms** (`src/client/ui/`): Qt Designer .ui files for task dialogs and main windows
- **HTTP Client** (`src/client/api_client.py`): httpx-based communication with server
- **Task Management** (`src/client/widgets/`): Custom widgets for drag-drop task reordering

## Key Database Schema

### Core Entities
```python
# Task model with two types: profile tools and other work
Task: id, id_product, id_profile, equipment, deadline, position, id_type_work, id_status, id_departament

# Profile tools (extrusion tools with 7 standard equipment types)
Profile: id, article, sketch
ProfileComponent: id, name, id_profile

# Products (other manufacturing work with custom equipment)
Product: id, name, id_departament, sketch
ProductComponent: id, name, id_product

# Directory tables
DirQueueStatus: id, name  # (Новая, В работе, Выполнена, Отменена)
DirTypeWork: id, name # (Новый инструмент, новый вариант, добавить к существующему, переделать, доработка)
DirDepartament: id, name
DirComponent: id, name
```

## Task Types & Business Logic

### Profile Tasks (Tab 1: "Инструмент на экструзию")
- Fixed equipment types: плиты 1-4, пальцы, усреднитель, кондуктор
- Work types: новый инструмент, новый вариант, добавить к существующему, переделать, доработка
- Example: "Профиль 1322214.1 - плиты 1-4, версия 2"

### Product Tasks (Tab 2: "Другое")  
- Custom equipment list (user-defined components)
- Flexible naming and quantity
- Department assignment required

### Priority & Queue Management
- Tasks ordered by `position` field (queue position)
- Drag-drop reordering in PySide6 interface updates position values
- Active tasks (≤10) displayed on main worker screen
- Full task management in separate manager window

## API Patterns & Endpoints

### RESTful Structure
```
GET /api/tasks/                    # Get tasks with status filter
POST /api/tasks/                   # Create new task
PUT /api/tasks/{id}               # Update task (including status)
PUT /api/tasks/{id}/position      # Update task position (drag-drop)
GET /api/directories/statuses/     # Get status options
GET /api/directories/departments/  # Get department options
```

### Request/Response Patterns
- Use Pydantic schemas for validation: `TaskCreate`, `TaskUpdate`, `TaskResponse`
- Equipment stored as JSON field or separate junction table
- Position updates should recalculate other task positions

## PySide6 UI Patterns

### Main Application Structure
- **Worker View**: QTableWidget with status filter, max 10 active tasks, drag-drop reordering
- **Manager View**: Separate QDialog with full task CRUD, create/edit task dialogs
- **Task Dialog**: QTabWidget with profile/product tabs (`dialogtask.ui`)

### UI Components
- Use QComboBox for departments, work types, status selection
- QCheckBox group for profile equipment selection
- QListWidget for product equipment with add/remove/edit buttons
- QDateEdit for deadlines
- QRadioButton group for profile work types

### Drag-Drop Implementation
```python
# Enable drag-drop in QTableWidget for position reordering
table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
# Override dropEvent to call API for position updates
```

## Development Workflows

### Running Server
```bash
cd src/server
python main.py  # Starts FastAPI on localhost:8000
```

### Running Client
```bash
cd src/client  
python main.py  # Starts PySide6 application
```

### Database Operations
```bash
# SQLAlchemy models auto-create tables
# Use Alembic for schema migrations if needed
alembic init alembic
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

## Code Style Conventions

### 🧱 General Design Principles
- **SOLID**: Code should be open for extension, closed for modification. Separate responsibilities between classes
- **DRY (Don't Repeat Yourself)**: Avoid logic duplication. Extract repeating fragments into separate methods or classes
- **KISS (Keep It Simple, Stupid)**: Don't overcomplicate. Simple and clear code is priority

### Python Standards
- **Tools**: Use `black`, `flake8`, `mypy` for code formatting and linting
- **Indentation**: 4 spaces
- **Naming Conventions**:
  - Classes: CamelCase (`TaskManager`, `ProfileDialog`)
  - Functions and variables: snake_case (`get_task_list`, `current_status`)
  - Constants: UPPER_SNAKE_CASE (`MAX_ACTIVE_TASKS`, `DEFAULT_STATUS`)
- **Line length**: Maximum 79 characters
- **Empty lines**:
  - One empty line between methods
  - Two empty lines between classes
- **Docstrings**: Add docstring to every class and public method
- **Type hints**: Required for all functions

### 🔧 PySide6 Patterns

#### 📦 Imports
```python
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
```
Use explicit imports instead of `import *`

#### 🏗️ Widget Creation
- Initialize GUI in class `__init__`
- Separate GUI logic into dedicated method (`setup_ui()`)
- Signal connection logic in `connect_signals()`

#### 📣 Signals and Slots
- Use `@Slot()` decorators for slots
- Use typed signals when possible: `Signal(str)` instead of `Signal()`
- Avoid "magic" connections like `connectSlotsByName`
- Connect events via `connect` (e.g., `self.button.clicked.connect(self.on_button_clicked)`)
- Disconnect signals when destroying objects
- Avoid anonymous lambdas where not necessary

#### 🧰 Resources Usage
- Use `.qrc` files for images and other resources
- Import them via `import qrc_resources` after compilation

#### Design and Styles
- Use QSS instead of hardcoded styles in code
- Create separate style files: `resources/styles/main.qss`, `resources/styles/dialogs.qss`
- Store file paths in constants: `MAIN_STYLE_PATH = "resources/styles/main.qss"`
- Load styles via `self.setStyleSheet()` using path constants
- Extract colors, sizes, fonts into constants when not defined in QSS:
```python
# constants.py
COLORS = {
    "PRIMARY": "#2196F3",
    "SECONDARY": "#FFC107", 
    "SUCCESS": "#4CAF50",
    "ERROR": "#F44336"
}

FONTS = {
    "HEADER": ("Arial", 16, "bold"),
    "BODY": ("Arial", 12, "normal"),
    "SMALL": ("Arial", 10, "normal")
}

SIZES = {
    "BUTTON_HEIGHT": 32,
    "ICON_SIZE": 24,
    "MARGIN": 10
}

PATHS = {
    "MAIN_STYLE": "resources/styles/main.qss",
    "DIALOG_STYLE": "resources/styles/dialogs.qss", 
    "ICONS": "resources/icons/",
    "IMAGES": "resources/images/"
}
```

#### 🧑‍💻 OOP Practices
- All widgets should be part of a class, not global
- Use inheritance when necessary
- Use `super()` for calling parent methods
- Prefer composition over inheritance

#### 🧽 Qt Memory Management
- Qt automatically manages memory through parent-child system
- Ensure all widgets are added to parent container or layout
- Avoid memory leaks through improper signal/slot usage

#### 🧬 Asynchronous Operations
- For long operations use:
  - `QThread`
  - `QRunnable + QThreadPool`
  - `asyncqt + asyncio` (if applicable)
- Don't block the main thread!

### 🔄 Real-time Updates
- Client updates every 5 seconds or on demand
- Use WebSockets or polling for real-time task status changes
- All operations must be asynchronous to prevent UI freezing

### File Organization
```
src/
├── server/
│   ├── main.py              # FastAPI app
│   ├── models/              # SQLAlchemy models  
│   ├── api/                 # Route handlers grouped by entities
│   └── schemas/             # Pydantic models
├── client/
│   ├── main.py              # PySide6 app entry
│   ├── ui/                  # .ui files
│   ├── widgets/             # Custom widgets
│   ├── api_client.py        # HTTP client
│   ├── constants.py         # UI constants (colors, sizes, paths)
│   └── resources/           # Static resources
│       ├── styles/          # QSS style files
│       │   ├── main.qss     # Main application styles
│       │   └── dialogs.qss  # Dialog-specific styles
│       ├── icons/           # Application icons
│       ├── images/          # Images and graphics
│       └── resources.qrc    # Qt resource file
└── shared/                  # Common utilities
```

## 🛡️ Error Handling & Best Practices

### Exception Handling
- Handle exceptions, especially when working with external resources
- Use `try...except` where necessary
- Don't ignore errors — at least log them
- Use structured logging with proper levels

### Code Quality
- ✨ Extract repeating functionality: If the same code appears twice — make it a method or function
- 📚 Comments: Write docstrings for classes and methods. Explain non-obvious logic inside methods
- Use comments for separating blocks (`#region ... #endregion`)

### Async Best Practices
- All database operations should be async
- Use httpx for async HTTP requests in client
- FastAPI endpoints should use async/await
- PySide6 long operations must use QThread to prevent UI blocking

## Critical Implementation Notes

- Equipment for profiles: store as bit flags or JSON for 7 standard types
- Task position: implement as integer sequence, recalculate on reorder
- Status filtering: use query parameters, not separate endpoints
- UI responsiveness: use QThread for API calls to prevent freezing
- Russian locale: ensure proper UTF-8 encoding in database and API
