from flask import Flask, request, jsonify
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

app = Flask(__name__)

# Customize SIMBAD fields
Simbad.add_votable_fields(
    "otype",
    "flux(V)",
    "ra(d)",
    "dec(d)"
)

@app.route("/query", methods=["GET"])
def query_object():
    ra = request.args.get("ra")
    dec = request.args.get("dec")

    if not ra or not dec:
        return jsonify({"error": "RA and DEC required"}), 400

    coord = SkyCoord(float(ra), float(dec), unit="deg")

    result = Simbad.query_region(coord, radius=5 * u.arcmin)

    if result is None:
        return jsonify({"message": "No objects found"})

    objects = []
    for row in result:
        objects.append({
            "name": row["MAIN_ID"].decode("utf-8"),
            "type": row["OTYPE"],
            "ra": float(row["RA_d"]),
            "dec": float(row["DEC_d"]),
            "visual_mag": row["FLUX_V"]
        })

    return jsonify(objects)

if __name__ == "__main__":
    app.run(debug=True)
