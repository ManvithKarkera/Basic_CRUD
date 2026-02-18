# Flask Todo Application

A todo list web application built with Flask and SQLAlchemy. Supports creating, reading, updating, and deleting todo items through a Bootstrap-based interface.

## Features

- Create todo items with title and description
- View all todos in a table format
- Update existing todo items
- Delete todo items
- Automatic timestamp tracking with timezone support
- Responsive design using Bootstrap 5
- SQLite database for data persistence

## Technologies Used

- Backend: Flask 3.1.2
- Database: SQLAlchemy 2.0.46 with SQLite
- Frontend: Bootstrap 5.3.8
- Python: 3.13+

## Project Structure

```
flask/
├── app.py              # Main application file
├── templates/          # HTML templates
│   ├── base.html      # Base template with Bootstrap
│   ├── index.html     # Home page with todo list
│   └── update.html    # Update todo page
├── static/            # Static files (CSS, JS, images)
├── instance/          # Instance folder (contains database)
│   └── todo.db       # SQLite database file
├── env/              # Virtual environment
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Installation

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd flask
   ```

2. Create and activate virtual environment
   
   Windows:
   ```powershell
   python -m venv env
   .\env\Scripts\activate
   ```
   
   macOS/Linux:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install flask flask-sqlalchemy
   ```

4. Run the application
   ```bash
   python app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000`

## Usage

### Creating a Todo

Enter a title and description on the home page, then click Submit.

### Updating a Todo

Click the Update button next to a todo item, modify the fields, and submit.

### Deleting a Todo

Click the Delete button next to a todo item to remove it.

## Database Schema

### Todo Model

| Column | Type | Description |
|--------|------|-------------|
| sno | Integer | Primary key, auto-incremented |
| title | String(200) | Todo title (required) |
| desc | String(500) | Todo description (required) |
| date_created | DateTime | Timestamp with UTC timezone |

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET, POST | Home page - display todos and create new ones |
| `/Update/<int:sno>` | GET, POST | Update specific todo by serial number |
| `/Delete/<int:sno>` | GET | Delete specific todo by serial number |
| `/show` | GET | Debug route to print all todos |

## Configuration

The application uses the following configurations:

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///todo.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

To modify these settings, edit the `app.py` file.

## Development

### Debug Mode

The application runs in debug mode by default for development:

```python
app.run(debug=True)
```

This enables automatic code reloading and detailed error pages. Disable this in production.

### Database Initialization

The database is created automatically on first run:

```python
with app.app_context():
    db.create_all()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Todo categories/tags
- [ ] Due dates and reminders
- [ ] Priority levels
- [ ] Search and filter functionality
- [ ] Mark todos as complete/incomplete
- [ ] Dark mode toggle
- [ ] Export todos to CSV/JSON

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Flask documentation for excellent guides
- Bootstrap for the responsive UI components
- SQLAlchemy for powerful ORM capabilities

## Contact

For questions or suggestions, please open an issue on GitHub.

---
