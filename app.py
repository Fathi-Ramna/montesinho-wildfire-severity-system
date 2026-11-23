from datetime import datetime
import json
import math
from pathlib import Path

from flask import Flask, Response, redirect, render_template, request, url_for
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 1. File Paths, Configuration & Startup Artifact Loading
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
NB_DIR = BASE_DIR / "03_FINAL_SGIF_NOTEBOOKS"
MODELS_DIR = NB_DIR / "models"
TABLES_DIR = NB_DIR / "reports" / "tables" / "icnf_sgif"
HISTORY_FILE = BASE_DIR / "prediction_history.json"


def load_table(filename):
    """Load a pre-computed notebook CSV summary table as a list of dictionaries."""
    return pd.read_csv(TABLES_DIR / filename).to_dict(orient="records")


# Load frozen ensemble bundles and 2004-2017 training standardization stats
SGIF_BUNDLE = joblib.load(MODELS_DIR / "final_recommended_model.joblib")
WEATHER_BUNDLE = joblib.load(MODELS_DIR / "weather_enriched_final_blend.joblib")
TRAINING_STATS = (
    pd.read_csv(TABLES_DIR / "preprocessing_training_statistics.csv")
    .set_index("feature")
    .to_dict(orient="index")
)

# Load scenario presets, operational risk tiers, and analytics summary tables
APP_CONFIG = json.loads((BASE_DIR / "static" / "data" / "app_config.json").read_text(encoding="utf-8"))
PRESET_SCENARIOS = APP_CONFIG["presets"]
RISK_TIERS = APP_CONFIG["risk_tiers"]
DEFAULT_FORM_DATA = dict(PRESET_SCENARIOS["drought_high"])

WEATHER_BY_MONTH = load_table("weather_by_month.csv")
PERM_IMPORTANCE = load_table("model_validation_grouped_permutation_importance.csv")
FINAL_TEST_METRICS = load_table("model_final_test_metrics.csv")
VALIDATION_FAMILY_BEST = load_table("model_validation_family_best.csv")
SIZE_GROUP_ERRORS = load_table("model_test_error_by_fire_size.csv")
DATASET_AMENDMENT = load_table("report_dataset_amendment_summary.csv")
EDA_SIZE_GROUPS = load_table("eda_fire_size_groups.csv")


# ---------------------------------------------------------------------------
# 2. Preprocessing, Prediction, and Operational Risk Alert Helpers
# ---------------------------------------------------------------------------
def parse_form_inputs(raw_form):
    """Extract and validate form inputs, falling back cleanly to defaults."""
    parsed = {}
    for key, default_val in DEFAULT_FORM_DATA.items():
        if isinstance(default_val, (int, float)):
            try:
                parsed[key] = float(raw_form.get(key, default_val))
            except (TypeError, ValueError):
                parsed[key] = float(default_val)
        else:
            parsed[key] = str(raw_form.get(key, default_val)).strip() or default_val

    if parsed["municipality"] not in ("Bragança", "Vinhais"):
        parsed["municipality"] = "Bragança"
    parsed["weather_rain_mm_24h"] = max(0.0, parsed["weather_rain_mm_24h"])

    # Sync HH:MM time string and decimal alert_hour in both directions
    raw_time = str(raw_form.get("alert_time", "")).strip()
    if ":" in raw_time:
        try:
            hh, mm = raw_time.split(":")[:2]
            hours, minutes = max(0, min(23, int(hh))), max(0, min(59, int(mm)))
            parsed["alert_time"] = f"{hours:02d}:{minutes:02d}"
            parsed["alert_hour"] = round(hours + minutes / 60.0, 2)
            return parsed
        except ValueError:
            pass

    parsed["alert_hour"] = round(max(0.0, min(23.99, parsed["alert_hour"])), 2)
    h_int = int(parsed["alert_hour"])
    m_int = max(0, min(59, int(round((parsed["alert_hour"] - h_int) * 60))))
    parsed["alert_time"] = f"{h_int:02d}:{m_int:02d}"
    return parsed


def build_feature_vector(form_data, feature_names):
    """Build cyclical temporal features and return (X_unscaled, X_scaled) arrays."""
    try:
        dt = datetime.strptime(form_data["alert_date"], "%Y-%m-%d")
    except ValueError:
        dt = datetime(2025, 8, 18)

    month = dt.month
    day_of_year = dt.timetuple().tm_yday
    hour = float(form_data["alert_hour"])

    raw_features = {
        "month_sin": math.sin(2.0 * math.pi * month / 12.0),
        "month_cos": math.cos(2.0 * math.pi * month / 12.0),
        "doy_sin": math.sin(2.0 * math.pi * day_of_year / 365.25),
        "doy_cos": math.cos(2.0 * math.pi * day_of_year / 365.25),
        "hour_sin": math.sin(2.0 * math.pi * hour / 24.0),
        "hour_cos": math.cos(2.0 * math.pi * hour / 24.0),
        "is_weekend": 1.0 if dt.weekday() >= 5 else 0.0,
        "municipality_vinhais": 1.0 if form_data["municipality"] == "Vinhais" else 0.0,
        "x_etrs89_km": float(form_data["x_etrs89_km"]),
        "y_etrs89_km": float(form_data["y_etrs89_km"]),
        "FFMC": float(form_data["FFMC"]),
        "DMC": float(form_data["DMC"]),
        "DC": float(form_data["DC"]),
        "ISI": float(form_data["ISI"]),
        "BUI": float(form_data["BUI"]),
        "FWI": float(form_data["FWI"]),
        "DSR": float(form_data["DSR"]),
        "fwi_missing_flag": 0.0,
        "weather_temp_c": float(form_data["weather_temp_c"]),
        "weather_rh_pct": float(form_data["weather_rh_pct"]),
        "weather_wind_mps": float(form_data["weather_wind_mps"]),
        "weather_rain_prev_24h_log1p": math.log1p(max(0.0, float(form_data["weather_rain_mm_24h"]))),
        "weather_missing_flag": 0.0,
    }

    unscaled = [raw_features[col] for col in feature_names]
    scaled = [
        (raw_features[col] - TRAINING_STATS[col]["training_mean_after_imputation"])
        / TRAINING_STATS[col]["training_std_after_imputation"]
        if col in TRAINING_STATS
        else raw_features[col]
        for col in feature_names
    ]
    return np.array([unscaled], dtype=float), np.array([scaled], dtype=float)


def run_blend_bundle(bundle, form_data):
    """Evaluate a saved SVR (log-space) + Poisson HistGBR (raw-space) model bundle."""
    X_unscaled, X_scaled = build_feature_vector(form_data, bundle["features"])
    svr_ha = max(0.0, math.expm1(float(bundle["svr_model"].predict(X_scaled)[0])))
    pois_ha = max(0.0, float(bundle["poisson_model"].predict(X_unscaled)[0]))
    w_svr = float(bundle["weights"]["svr_log"])
    w_pois = float(bundle["weights"]["poisson_raw"])
    blend_ha = w_svr * svr_ha + w_pois * pois_ha
    return round(blend_ha, 2), round(svr_ha, 2), round(pois_ha, 2)


def compute_dryness_indicators(form_data):
    """Compute 0-99% fuel dryness and atmospheric humidity stress bars."""
    return {
        "ffmc_pct": max(10, min(99, int(round(float(form_data["FFMC"]))))),
        "dc_pct": max(5, min(99, int(round(float(form_data["DC"]) / 8.0)))),
        "rh_stress_pct": max(5, min(99, int(round(100.0 - float(form_data["weather_rh_pct"]))))),
    }


def get_risk_alert_and_advisory(predicted_ha):
    """Map predicted burned area (ha) to our 4-tier operational risk protocol."""
    if predicted_ha < 1.0:
        return RISK_TIERS["low"]
    if predicted_ha < 10.0:
        return RISK_TIERS["moderate"]
    if predicted_ha < 100.0:
        return RISK_TIERS["high"]
    return RISK_TIERS["extreme"]


def predict_fire_severity(form_data):
    """Run both SGIF-Only (80/20) and Weather-Enriched (90/10) blends plus UI indicators."""
    sgif_blend_ha, sgif_svr_ha, sgif_pois_ha = run_blend_bundle(SGIF_BUNDLE, form_data)
    weather_blend_ha, weather_svr_ha, weather_pois_ha = run_blend_bundle(WEATHER_BUNDLE, form_data)
    risk_info = get_risk_alert_and_advisory(sgif_blend_ha)

    pitches = sgif_blend_ha * 1.4
    pitches_str = (
        "< 0.5 football pitch"
        if pitches < 0.6
        else f"~{max(1, round(pitches))} football pitch{'es' if round(pitches) != 1 else ''}"
    )

    if sgif_blend_ha < 1.0:
        marker_pct = max(6, min(24, int(sgif_blend_ha * 24)))
        hist_pct = 22 if sgif_blend_ha < 0.4 else 38
    elif sgif_blend_ha < 10.0:
        marker_pct = int(25 + (sgif_blend_ha - 1.0) / 9.0 * 30)
        hist_pct = 68
    elif sgif_blend_ha < 100.0:
        marker_pct = int(55 + (math.log10(sgif_blend_ha) - 1.0) * 27)
        hist_pct = 94
    else:
        marker_pct = min(96, int(82 + min(14, (sgif_blend_ha - 100.0) / 15.0)))
        hist_pct = 99

    return {
        "sgif_blend_ha": sgif_blend_ha,
        "sgif_svr_ha": sgif_svr_ha,
        "sgif_poisson_ha": sgif_pois_ha,
        "weather_blend_ha": weather_blend_ha,
        "weather_svr_ha": weather_svr_ha,
        "weather_poisson_ha": weather_pois_ha,
        "pitches_str": pitches_str,
        "marker_pct": marker_pct,
        "hist_pct": hist_pct,
        **compute_dryness_indicators(form_data),
        "risk": risk_info,
    }


def make_history_entry(form_data, pred):
    """Build a structured history record for a single scenario assessment."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_date": form_data["alert_date"],
        "alert_hour": form_data["alert_time"],
        "municipality": form_data["municipality"],
        "coords": f"({form_data['x_etrs89_km']:.1f}, {form_data['y_etrs89_km']:.1f})",
        "weather_summary": (
            f"{form_data['weather_temp_c']:.1f}°C | {form_data['weather_rh_pct']:.0f}% RH | "
            f"{form_data['weather_wind_mps']:.1f} m/s | {form_data['weather_rain_mm_24h']:.1f} mm"
        ),
        "fwi_summary": f"FWI {form_data['FWI']:.1f} (DC {form_data['DC']:.0f}, DMC {form_data['DMC']:.0f})",
        "sgif_blend_ha": pred["sgif_blend_ha"],
        "weather_blend_ha": pred["weather_blend_ha"],
        "badge_label": pred["risk"]["badge_label"],
        "bootstrap_class": pred["risk"]["bootstrap_class"],
        "hex_color": pred["risk"]["hex_color"],
    }


def load_prediction_history():
    """Load recent scenario tests from local JSON, seeding defaults on first launch."""
    if not HISTORY_FILE.exists():
        entries = [
            make_history_entry(PRESET_SCENARIOS[k], predict_fire_severity(PRESET_SCENARIOS[k]))
            for k in ["drought_high", "extreme_wind", "august_moderate", "spring_low", "winter_wet"]
        ]
        HISTORY_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
        return entries
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def log_prediction_history(form_data, pred):
    """Prepend a new prediction test entry and retain the latest 25 runs."""
    history = [make_history_entry(form_data, pred)] + load_prediction_history()
    history = history[:25]
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    return history


# ---------------------------------------------------------------------------
# 3. Multi-Page Flask Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    preset_key = request.args.get("preset", "").strip()
    preset_loaded = preset_key in PRESET_SCENARIOS
    form_data = dict(PRESET_SCENARIOS[preset_key]) if preset_loaded else dict(DEFAULT_FORM_DATA)
    return render_template(
        "predictor.html",
        active_page="predictor",
        form_data=form_data,
        presets=PRESET_SCENARIOS,
        prediction=None,
        dryness=compute_dryness_indicators(form_data),
        preset_loaded=preset_loaded,
        history_count=len(load_prediction_history()),
    )


@app.route("/predict", methods=["POST"])
def predict():
    form_data = parse_form_inputs(request.form)
    prediction = predict_fire_severity(form_data)
    history = log_prediction_history(form_data, prediction)
    return render_template(
        "predictor.html",
        active_page="predictor",
        form_data=form_data,
        presets=PRESET_SCENARIOS,
        prediction=prediction,
        dryness=compute_dryness_indicators(form_data),
        preset_loaded=False,
        history_count=len(history),
    )


@app.route("/analytics", methods=["GET"])
def analytics():
    return render_template(
        "analytics.html",
        active_page="analytics",
        perm_importance=PERM_IMPORTANCE,
        weather_by_month=WEATHER_BY_MONTH,
        eda_size_groups=EDA_SIZE_GROUPS,
        history_count=len(load_prediction_history()),
    )


@app.route("/methodology", methods=["GET"])
def methodology():
    return render_template(
        "methodology.html",
        active_page="methodology",
        validation_family_best=VALIDATION_FAMILY_BEST,
        final_test_metrics=FINAL_TEST_METRICS,
        size_group_errors=SIZE_GROUP_ERRORS,
        dataset_amendment=DATASET_AMENDMENT,
        history_count=len(load_prediction_history()),
    )


@app.route("/history", methods=["GET"])
def history_page():
    history = load_prediction_history()
    return render_template(
        "history.html",
        active_page="history",
        history=history,
        history_count=len(history),
    )


@app.route("/export-history", methods=["GET"])
def export_history():
    cols = [
        "timestamp", "alert_date", "alert_hour", "municipality", "coords",
        "weather_summary", "fwi_summary", "sgif_blend_ha", "weather_blend_ha", "badge_label",
    ]
    df = pd.DataFrame(load_prediction_history()).reindex(columns=cols)
    return Response(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=montesinho_prediction_history.csv"},
    )


@app.route("/clear-history", methods=["POST"])
def clear_history():
    HISTORY_FILE.write_text("[]\n", encoding="utf-8")
    return redirect(url_for("history_page"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
