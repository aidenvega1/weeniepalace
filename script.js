<script>
/*
AI-Assisted Ranking Logic
This does NOT replace the ML model.
It prioritizes candidates for human inspection.
*/
fetch("results/candidates.csv")
    .then(response => response.text())
    .then(text => {
        const rows = text.trim().split("\n").slice(1);
        let objects = [];
        rows.forEach(row => {
            const cols = row.split(",");
            objects.push({
                source_id: cols[0],
                mean_mag: parseFloat(cols[1]),
                std_mag: parseFloat(cols[2]),
                amplitude: parseFloat(cols[3]),
                skewness: parseFloat(cols[4]),
                kurtosis: parseFloat(cols[5]),
                ls_power: parseFloat(cols[6])
            });
        });
        
        // --- AI-Assisted Priority Score ---
        objects.forEach(obj => {
            obj.ai_score =
                (obj.amplitude * 2.0) +
                (obj.std_mag * 1.5) +
                (Math.abs(obj.skewness) * 0.8) +
                (Math.abs(obj.kurtosis) * 0.5) +
                (obj.ls_power * 1.2);
        });
        
        // Sort by AI priority
        objects.sort((a, b) => b.ai_score - a.ai_score);
        
        const tbody = document.querySelector("#aiTable tbody");
        objects.forEach((obj, index) => {
            const tr = document.createElement("tr");
            tr.style.cursor = "pointer";
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${obj.source_id}</td>
                <td>${obj.amplitude.toFixed(2)}</td>
                <td>${obj.std_mag.toFixed(2)}</td>
                <td>${obj.ai_score.toFixed(2)}</td>
            `;
            tr.onclick = () => {
                const img = document.getElementById("aiLightcurve");
                img.src = `results/lightcurves/${obj.source_id}.png`;
                img.style.display = "block";
            };
            tbody.appendChild(tr);
        });
    })
    .catch(error => {
        console.error("Error loading candidates:", error);
        const tbody = document.querySelector("#aiTable tbody");
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ff6b6b;">Error loading data. Make sure candidates.csv exists in the results folder.</td></tr>`;
    });
</script>