# Montesinho Natural Park Wildfire Severity & Risk Alert System

A machine learning-based web application and end-to-end data science pipeline that estimates wildfire burned area (in hectares) and generates demonstration risk alerts for **Montesinho Natural Park (Bragança & Vinhais, Portugal)**.

## Live Demo

- **Live Web App:** *(Link will be added after Render deployment)*

## Project Overview

- **Primary Dataset:** Official Portuguese **ICNF SGIF** wildfire registry (2004–2025), containing 1,644 audited park-boundary wildfire events, with historical meteorological data obtained from **NASA POWER (MERRA-2)**.

- **Legacy Benchmark:** Includes the original **UCI Forest Fires** benchmark (2000–2003, 517 records) in `02_ORIGINAL_UCI_EVIDENCE/` for methodological comparison.

- **Model Architecture:** Uses a chronological data split:
  - Training: 2004–2017
  - Validation: 2018–2021
  - Testing: 2022–2025

  The prediction model combines **80% RBF Support Vector Regression (SVR)** with a log-transformed target and **20% Poisson HistGradientBoostingRegressor** with the original target, using 18 alert-time input features.

- **Web Application:** A multi-page application developed using **Flask and Bootstrap 5.3**, featuring:
  - Interactive Montesinho Natural Park map using Leaflet.js
  - Four-level colour-coded risk alerts
  - Emergency response guidance
  - Historical wildfire analytics
  - Machine learning model methodology
  - Prediction history with CSV export functionality

## Project Structure

```text
Ramna/
│
├── 02_ORIGINAL_UCI_EVIDENCE/
│   └── Original UCI benchmark notebooks, dataset, and visualisations
│
├── 03_FINAL_SGIF_NOTEBOOKS/
│   └── SGIF notebooks, processed datasets, trained models, and evaluation outputs
│
├── static/
│   └── CSS, JavaScript, and other frontend assets
│
├── templates/
│   └── HTML templates for the Flask application
│
├── app.py
├── requirements.txt
├── .gitignore
├── .python-version
└── README.md
```

## Running Locally

### 1. Clone the Repository

Clone the GitHub repository and open the project folder.

### 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Start the Flask Application

Run the application:

```bash
python app.py
```

### 5. Open the Web Application

Open the following address in your browser:

http://127.0.0.1:5000

## Raw Data Sources

Large raw Excel workbooks and hourly meteorological JSON archives are excluded from the GitHub repository to reduce its size.

The project uses processed datasets and trained machine learning models for the Flask application.

To reproduce the complete data preparation process, the original datasets may need to be downloaded separately.

### ICNF SGIF Official Wildfire Registry

The Portuguese Institute for Nature Conservation and Forests (ICNF) provides historical wildfire records.

**Official Website:** https://www.icnf.pt/

The project uses wildfire records covering:

- 2001–2010
- 2011–2020
- 2021–2025

Place the downloaded and extracted files in:

```text
03_FINAL_SGIF_NOTEBOOKS/Dataset/icnf_sgif/extracted/
```

### NASA POWER Meteorological Data

Historical meteorological information was obtained from NASA POWER.

**Official Website:** https://power.larc.nasa.gov/

The meteorological variables include:

- `T2M` — Air temperature at 2 metres
- `RH2M` — Relative humidity at 2 metres
- `WS10M` — Wind speed at 10 metres
- `PRECTOTCORR` — Corrected precipitation

For the required coordinates and date ranges, refer to:

```text
03_FINAL_SGIF_NOTEBOOKS/Dataset/reference/nasa_power/SOURCE_MANIFEST.json
```

Place the downloaded hourly meteorological JSON files in:

```text
03_FINAL_SGIF_NOTEBOOKS/Dataset/nasa_power_hourly/
```

## Technologies Used

- **Programming Language:** Python
- **Web Framework:** Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5.3
- **Interactive Maps:** Leaflet.js
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **Data Visualisation:** Matplotlib
- **Development Environment:** Jupyter Notebook, Visual Studio Code
- **Deployment:** Render
- **Version Control:** Git and GitHub

## Disclaimer

This application is an academic research and decision-support prototype developed as part of a final-year Data Science project.

The predicted burned areas are statistical estimates generated using historical wildfire data. Prediction accuracy may vary, particularly for unusually large or extreme wildfire events.

The risk alerts and emergency response guidance are provided for educational and demonstration purposes only.

This system is not an operational wildfire forecasting or emergency management tool. Its outputs must not replace official information, warnings, or instructions issued by the Portuguese Institute for Nature Conservation and Forests (ICNF) or the National Emergency and Civil Protection Authority (ANEPC).