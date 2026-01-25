async function search() {
    const ra = document.getElementById("ra").value;
    const dec = document.getElementById("dec").value;
    const resultsDiv = document.getElementById("results");

    resultsDiv.innerHTML = "Searching NASA databases...";

    const response = await fetch(
        `http://127.0.0.1:5000/query?ra=${ra}&dec=${dec}`
    );

    const data = await response.json();

    if (!Array.isArray(data)) {
        resultsDiv.innerHTML = "No objects found.";
        return;
    }

    resultsDiv.innerHTML = "";

    data.forEach(obj => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `
            <strong>${obj.name}</strong><br>
            Type: ${obj.type}<br>
            RA: ${obj.ra}<br>
            DEC: ${obj.dec}<br>
            V Mag: ${obj.visual_mag ?? "N/A"}
        `;
        resultsDiv.appendChild(div);
    });
}