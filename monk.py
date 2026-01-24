PLOT_DIR = os.path.join(OUTPUT_DIR, "lightcurves")
os.makedirs(PLOT_DIR, exist_ok=True)

print("Generating light curves for candidate objects...")

for _, row in candidates.iterrows():
    sid = row["source_id"]
    obj_data = df[df["source_id"] == sid]

    plt.figure(figsize=(6, 4))
    plt.scatter(obj_data["mjd"], obj_data["w1mpro"], s=12, alpha=0.6)
    plt.gca().invert_yaxis()
    plt.xlabel("MJD")
    plt.ylabel("W1 Magnitude")
    plt.title(f"Source {sid}")
    plt.tight_layout()

    plt.savefig(os.path.join(PLOT_DIR, f"{sid}.png"), dpi=120)
    plt.close()

print("All candidate light curves generated.")
