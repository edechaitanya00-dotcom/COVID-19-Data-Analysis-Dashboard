# COVID-19 Data Analysis Dashboard

A beginner-friendly BTech mini project made with Python, Streamlit, Pandas, and Plotly.

## Included files
- `app.py` — complete dashboard code
- `requirements.txt` — Python libraries needed
- `run_windows.bat` — optional Windows launcher
- The COVID-19 CSV is **not** included because it is large. The app reads it from the official Our World in Data source on the first run if you have internet access.

## Before starting
Install Python (Python 3.12 is a good choice if you are new) and Visual Studio Code.

During Python installation on Windows, select **Add Python to PATH**.

## Run in VS Code
1. Extract the ZIP file.
2. Open VS Code.
3. Select **File > Open Folder**.
4. Select the extracted `COVID19_Dashboard` folder.
5. Select **Terminal > New Terminal**.
6. Run these commands one by one:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

7. The terminal will show a local address, usually `http://localhost:8501`. Open it in your browser.

If PowerShell blocks activation, use Command Prompt in VS Code or run `python -m pip install -r requirements.txt` without activating the environment.

## Dataset
Official source:
https://covid.ourworldindata.org/data/owid-covid-data.csv

Optional: download the CSV and save it beside `app.py` as `owid-covid-data.csv`. If that file exists, the app uses it instead of reading the online source.

## Main features
- Country/location selector
- Date range filter
- Summary cards for total reported cases, deaths, and people vaccinated
- Charts for total cases, total deaths, and new cases
- Comparison of locations
- Data table and CSV download

## Important note
This is an educational project. COVID-19 reporting differs by country and time; data may be incomplete or revised. Do not present the figures as a complete count of all infections.

## If you get an error
- `python is not recognized`: install Python and reopen VS Code.
- `No module named streamlit`: run `python -m pip install -r requirements.txt`.
- Dataset download error: check your internet connection, or download the CSV from the official source above and save it beside `app.py`.
- Port already in use: run `python -m streamlit run app.py --server.port 8502`.
