# GUEST API
## Installation
### Clone the project

```bash
git clone repository_url
```
### Install dependencies
```bash
cd project_location

python -m venv venv
venv\Scripts\activate # on windows
source venv/bin/activate

pip install -r requirements.txt
```

### Run
```bash
python manage.py runserver #u machine only
python manage.py runserver 0.0.0.0:8000
```

## Push
```bash
git status # view changes
git add . # Add files to be commited
git commit -m "Any message of a change u did"
git push origin main
```