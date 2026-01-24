import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astroquery.irsa import Irsa
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.stats import skew, kurtosis
from scipy.signal import lombscargle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')

# -----------------------------
# CONFIG
# -----------------------------
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RA_CENTER = 180.0     # degrees
DEC_CENTER = 0.0      # degrees
SEARCH_RADIUS = 0.5   # degrees (small region for testing)
MIN_OBS = 15          # minimum number of observations

# -----------------------------
# QUERY NEOWISE DATA
# -----------------------------
print("Querying NEOWISE data from NASA IRSA...")
coord = SkyCoord(RA_CENTER, DEC_CENTER, unit="deg")

try:
    table = Irsa.query_region(
        coord,
        catalog="neowiser_p1bs_psd",
        spatial="Cone",
        radius=SEARCH_RADIUS * u.deg
    )
    df = table.to_pandas()
    print(f"Total observations downloaded: {len(df)}")
except Exception as e:
    print(f"Error querying IRSA: {e}")
    print("This may be due to network issues or API changes.")
    exit(1)

# Keep good-quality data only
if "ph_qual" in df.columns:
    df = df[df["ph_qual"] == "A"]
else:
    print("Warning: 'ph_qual' column not found. Proceeding without quality filter.")

# Check for required columns
required_cols = ["source_id", "mjd", "w1mpro"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"Error: Missing required columns: {missing_cols}")
    print(f"Available columns: {df.columns.tolist()}")
    exit(1)

df = df[required_cols].dropna()

if len(df) == 0:
    print("No data remaining after filtering. Try adjusting search parameters.")
    exit(1)

# -----------------------------
# BUILD LIGHT CURVES
# -----------------------------
features = []
print("Extracting variability features...")

for source_id, group in df.groupby("source_id"):
    if len(group) < MIN_OBS:
        continue
    
    time = group["mjd"].values
    mag = group["w1mpro"].values
    
    mean_mag = np.mean(mag)
    std_mag = np.std(mag)
    amplitude = np.max(mag) - np.min(mag)
    skewness = skew(mag)
    kurt = kurtosis(mag)
    
    # Lomb-Scargle periodogram
    try:
        freq = np.linspace(0.01, 1.0, 1000)
        power = lombscargle(time, mag - mean_mag, freq)
        max_power = np.max(power)
    except:
        max_power = 0.0
    
    features.append([
        source_id,
        mean_mag,
        std_mag,
        amplitude,
        skewness,
        kurt,
        max_power
    ])

if len(features) == 0:
    print(f"No objects found with at least {MIN_OBS} observations.")
    print("Try reducing MIN_OBS or increasing SEARCH_RADIUS.")
    exit(1)

features_df = pd.DataFrame(
    features,
    columns=[
        "source_id",
        "mean_mag",
        "std_mag",
        "amplitude",
        "skewness",
        "kurtosis",
        "ls_power"
    ]
)

print(f"Objects with valid light curves: {len(features_df)}")

# -----------------------------
# MACHINE LEARNING: ANOMALY DETECTION
# -----------------------------
X = features_df.drop(columns=["source_id"])
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=300,
    contamination=0.05,
    random_state=42
)
features_df["anomaly_score"] = model.fit_predict(X_scaled)

# -1 = anomalous
candidates = features_df[features_df["anomaly_score"] == -1]

# -----------------------------
# SAVE RESULTS
# -----------------------------
candidates.to_csv(
    os.path.join(OUTPUT_DIR, "candidates.csv"),
    index=False
)
print(f"\nAnomalous candidate objects found: {len(candidates)}")
print("Saved to results/candidates.csv")

# -----------------------------
# PLOT EXAMPLE LIGHT CURVE
# -----------------------------
if len(candidates) > 0:
    example_id = candidates.iloc[0]["source_id"]
    example_data = df[df["source_id"] == example_id]
    
    plt.figure(figsize=(8, 4))
    plt.scatter(example_data["mjd"], example_data["w1mpro"], s=15, alpha=0.6)
    plt.gca().invert_yaxis()
    plt.xlabel("Modified Julian Date")
    plt.ylabel("W1 Magnitude")
    plt.title(f"Infrared Light Curve (Source {example_id})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "example_lightcurve.png"), dpi=150)
    plt.show()
    print("Example light curve saved.")
else:
    print("\nNo anomalous candidates found to plot.")

print("\nAnalysis complete!")


!float 

angel in a monkey