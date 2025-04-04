# Tutor Display

A Python application with a PyQt6 GUI designed to display tutor shift schedules. It shows which tutors are currently on shift, the classes they tutor, and the overall schedule for the day.

**This is an internal project and should not be shared outside of authorized team members.**

## Features

- **PyQt6 GUI**: User-friendly interface for displaying tutor schedules.
- **Custom Widgets**: Modular custom widgets for enhanced UI elements.
- **Real-Time Tutor Display**: Shows active tutors, their subjects, and daily schedules.
- **SharePoint Integration**:
  - Fetches pictures from SharePoint and saves them in an autogenerated `Images/` folder.
  - Retrieves data from a SharePoint Excel file.
- **Constants Management**: Easy-to-modify constants in `constants.py`.

## Installation

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Set Up a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Create the `.env` File

Before running the application, create a file called`'.env'` in the project directory using the following template:

```
TUTOR_CENTER_PATH="URL TO THE MAIN TUTOR CENTER SHAREPOINT"
TUTOR_CENTER_EMAIL="USERNAME"
TUTOR_CENTER_PASSWORD="PASSWORD"
```

You can find the Sharepoint url by going to the root directory of the sharepoint and then copy the url.

### 5. Create the Directory for the Tutor Images

```
mkdir Images
```

### 5. Run the Application

```sh
python main.py
```

## Configuration

- **Sensitive files** (`daily_schedules.json`, `tutor_data.json`, `.env` and `\Images`) should never be removed from `.gitignore`
- The `Images/` folder will be automatically generated when `get_pictures.py` runs.
- `tutor_data.json` and `daily_schedules.json` are autogenerated and should not be manually modified.

## File Overview

| File                | Description                                    |
| ------------------- | ---------------------------------------------- |
| `main.py`           | Entry point, defines the GUI.                  |
| `custom_widgets.py` | Contains custom PyQt6 widgets.                 |
| `get_pictures.py`   | Fetches pictures from SharePoint.              |
| `excel.py`          | Retrieves and processes SharePoint Excel data. |
| `constants.py`      | Stores constants for easy configuration.       |
| `.gitignore`        | Ensures sensitive files remain untracked.      |

## Contributing

Pull requests are welcome. Ensure that changes maintain compatibility with the existing structure.

## License

MIT License

