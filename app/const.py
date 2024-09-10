from typing import Final, Dict, Any
from app.version import __version__
from pathlib import Path

# Application params
app_title: Final[str] = "PSE"
app_description: Final[str] = ""

app_params:   Final[Dict[str, Any]] = {
    "title": app_title, 
    "description": app_description,
    "version": __version__,
    "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
    "root_path": ""
    }

# Uvicorn params
host: Final = "0.0.0.0"
port: Final = 8000

uvicorn_params:   Final[Dict[str, Any]] = {
    "host": host, 
    "port": port
    }

# Paths params
# File names
env_file_name:          Path    =   Path('.env')
# Folder names
app_folder_name:        Path    =   Path('app')
templates_folder_name:  Path    =   Path('templates')
static_folder_name:     Path    =   Path('static')
# Paths
main_path:              Path    =   Path(__file__).resolve().parents[1]
env_path:               Path    =   main_path / env_file_name
app_path:               Path    =   main_path / app_folder_name
templates_path:         Path    =   app_path / templates_folder_name
static_path:            Path    =   app_path / static_folder_name