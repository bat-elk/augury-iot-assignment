# augury-iot-assignment

### Project Structure:

augury-iot-assignment/
├─ iot/
│  ├─ __init__.py
│  ├─ Augury_api.py      # Fake API 
│  ├─ Node.py            # Node 
│  └─ Endpoint.py        # Endpoint 
├─ tests/
│  └─ required_tests.robot  # 3 required scenarios
├─ requirements.txt
└─ README.md


---

## Requirements
- **Python 3.6+**  
  (This repo is pinned to `robotframework==4.1.3`, which supports Python 3.6.)
- `pip`, `venv`
- (Optional) VS Code

---

## Setup

### 1) Create & activate a virtual environment
**Windows – Git Bash**
py -m venv .venv
source .venv/Scripts/activate

### 2) Ensure pip is available inside the venv (Python 3.6 tip)
python -m ensurepip --upgrade

### 3) Install dependencies (from this repo’s pinned requirements)
pip install -r requirements.txt    # installs: robotframework==4.1.3

### 4) Run the whole suite
python -m robot -P . tests/
