# HTTP server for reddit top month parser client.

This program is a Python application for handling requests from the parser client.

## Installation

Clone the repository from GitHub. To work with mongodb server use "mongodb_release_features" and to work with
postgresql server use "postgresql_release_features".

Then create a virtual environment, and install all the dependencies.

```bash
git clone https://github.com/DvMaxim/TopMonthRedditParser.git -b <NECESSARY_BRANCH_NAME>
python -m venv env
env\Scripts\activate.bat
python -m pip install -r requirements.txt
```

## Usage

Initialize the virtual environment, and run the script

```bash
env\Scripts\activate.bat

python server.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.



