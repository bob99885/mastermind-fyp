# Deployment

## Local Development

Create or activate the project virtual environment, install dependencies, and
start the Flask API:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs at `http://127.0.0.1:5000`. The static frontend can be served
from the project root with:

```bash
python -m http.server 8000 --directory frontend
```

Then open `http://127.0.0.1:8000/pages/home.html`.

## Docker

The container configuration is stored in `deployment/`. From the project root:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

The Flask API is exposed on port 5000. The image installs dependencies from
`requirements.txt` and starts `app.py`.

## Continuous Integration

The GitHub Actions workflow is stored at
`deployment/github_actions.yml`. To have GitHub run it automatically, copy or
move it to `.github/workflows/tests.yml`. It installs Python dependencies,
compiles the project, and runs an API smoke test on pushes and pull requests.
