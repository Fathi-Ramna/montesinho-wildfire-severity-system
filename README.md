# Montesinho Natural Park Wildfire Severity & Risk Alert System

A machine learning-based forest fire burned area prediction system developed as part of a final-year Data Science project. The system estimates wildfire burned area in hectares and provides demonstration risk alerts for Montesinho Natural Park (Bragança and Vinhais, Portugal).

The project includes an end-to-end Data Science workflow covering data understanding, preprocessing, exploratory data analysis, feature engineering, machine learning model training, and evaluation. A Flask-based web application provides an interactive interface for exploring the prediction system.

## Project Overview

### Primary Dataset

The project uses official Portuguese ICNF SGIF wildfire records covering 2004–2025, with 1,644 audited wildfire events located within the official Montesinho Natural Park boundary.

Historical meteorological data from NASA POWER (MERRA-2) was also investigated to examine the influence of weather conditions on burned area prediction.

### Legacy UCI Benchmark

The project includes the original UCI Forest Fires dataset containing 517 records from 2000–2003.

This dataset was used for the initial machine learning experiments and is preserved in `02_ORIGINAL_UCI_EVIDENCE/` for methodological comparison.

### Machine Learning Model

The SGIF implementation uses a chronological data split to evaluate model performance on later wildfire events.

- **Training:** 2004–2017
- **Validation:** 2018–2021
- **Testing:** 2022–2025

The selected prediction model combines:

- **80% RBF Support Vector Regression (SVR)** using a log-transformed target.
- **20% Poisson HistGradientBoostingRegressor** using the original burned area target.

The model uses 18 alert-time input features to estimate the final burned area in hectares.

### Flask Web Application

The project includes a multi-page web application developed using Flask, Bootstrap 5.3, HTML, CSS, and JavaScript.

Its main features include:

- Interactive Montesinho Natural Park map using Leaflet.js.
- Machine learning-based burned area estimation.
- Four-level colour-coded demonstration risk alerts.
- Emergency response guidance for educational purposes.
- Historical wildfire analytics and visualisations.
- Information about the machine learning methodology.
- Prediction scenario history with CSV export functionality.
- Dark and light display modes.

The web application runs locally and is intended for academic demonstration and evaluation.

## Project Structure

```text
Ramna/
│
├── 02_ORIGINAL_UCI_EVIDENCE/
│   └── Original UCI notebooks, datasets, trained models,
│       and visualisations
│
├── 03_FINAL_SGIF_NOTEBOOKS/
│   ├── data/
│   │   ├── interim/
│   │   ├── processed/
│   │   └── reference/
│   │
│   ├── Dataset/
│   │   ├── icnf_sgif/
│   │   ├── nasa_power_hourly/
│   │   └── reference/
│   │
│   ├── models/
│   ├── reports/
│   │
│   ├── 01_data_understanding.ipynb
│   ├── 02_montesinho_filtering_and_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_feature_engineering_and_preprocessing.ipynb
│   └── 05_model_training_and_evaluation.ipynb
│
├── static/
│   └── CSS, JavaScript, images, and visualisation assets
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

## Running the Application Locally

The application can be run on a local computer using Python and the required dependencies.

### 1. Clone the Repository

```bash
git clone https://github.com/Fathi-Ramna/montesinho-wildfire-severity-system.git
```

Navigate to the project folder:

```bash
cd montesinho-wildfire-severity-system
```

### 2. Create a Python Virtual Environment

The project was developed using Python 3.12.10.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Flask Application

```bash
python app.py
```

### 5. Open the Application

Open the following address in your web browser:

http://127.0.0.1:5000

The application will run locally on your computer.

## Raw Data Sources

The project uses publicly available wildfire records and historical meteorological data.

Large raw Excel workbooks and hourly meteorological JSON archives are excluded from the GitHub repository to reduce its size.

Processed datasets, trained machine learning models, and evaluation outputs are included in the project repository.

The original raw datasets may be required to reproduce the complete data preparation workflow from the beginning.

### ICNF SGIF Official Wildfire Registry

The Portuguese Institute for Nature Conservation and Forests (ICNF) provides historical wildfire records.

**Official Website:** https://www.icnf.pt/

The source records cover the following periods:

- 2001–2010
- 2011–2020
- 2021–2025

Downloaded and extracted source files should be placed in:

```text
03_FINAL_SGIF_NOTEBOOKS/Dataset/icnf_sgif/extracted/
```

### NASA POWER Meteorological Data

Historical meteorological information was obtained from NASA POWER.

**Official Website:** https://power.larc.nasa.gov/

The meteorological variables investigated include:

- `T2M` — Air temperature at 2 metres.
- `RH2M` — Relative humidity at 2 metres.
- `WS10M` — Wind speed at 10 metres.
- `PRECTOTCORR` — Corrected precipitation.

The source metadata and required coordinates are documented in:

```text
03_FINAL_SGIF_NOTEBOOKS/Dataset/reference/nasa_power/SOURCE_MANIFEST.json
```

Downloaded hourly meteorological files should be placed in:

```text
03_FINAL_SGIF_NOTEBOOKS/Dataset/nasa_power_hourly/
```

## Technologies Used

- **Programming Language:** Python 3.12
- **Web Framework:** Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5.3
- **Interactive Maps:** Leaflet.js
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **Data Visualisation:** Matplotlib
- **Development Environment:** Jupyter Notebook, Visual Studio Code
- **Model Storage:** Joblib
- **Version Control:** Git and GitHub

## Project Purpose

This project investigates the application of machine learning techniques to forest fire burned area prediction using historical wildfire records and meteorological information.

It aims to provide a structured Data Science workflow and demonstrate how machine learning predictions can be presented through an interactive web application.

The project also examines the challenges of predicting burned areas, particularly the difficulty of estimating unusually large wildfire events from historical data.

## Disclaimer

This application is an academic research and decision-support prototype developed as part of a final-year Data Science project.

The predicted burned areas are statistical estimates generated using historical wildfire data. Prediction accuracy may vary, particularly for unusually large or extreme wildfire events.

The risk alerts and emergency response guidance are provided for educational and demonstration purposes only.

This system is not an operational wildfire forecasting or emergency management tool. Its outputs must not replace official information, warnings, or instructions issued by the Portuguese Institute for Nature Conservation and Forests (ICNF) or the National Emergency and Civil Protection Authority (ANEPC).