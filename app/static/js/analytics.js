async function loadTiles() {
  const r = await fetch("/api/metrics/overview");
  const d = await r.json();
  const tiles = document.getElementById("tiles");
  tiles.innerHTML = `
    <div class="tile"><div>Total Users</div><h2>${d.total_users}</h2></div>
    <div class="tile"><div>Total Movies</div><h2>${d.total_movies}</h2></div>
    <div class="tile"><div>Total Ratings</div><h2>${d.total_ratings}</h2></div>
    <div class="tile"><div>Avg Ratings/User</div><h2>${d.avg_ratings_per_user}</h2></div>
    <div class="tile"><div>Coverage %</div><h2>${d.coverage_pct}%</h2></div>
  `;
}
async function loadChart() {
  // top genres by count (client computes from /api/movies pages 1..N small demo)
  let page = 1,
    size = 50,
    done = false,
    genresCount = {};
  while (!done && page <= 10) {
    const r = await fetch(`/api/movies?page=${page}&size=${size}`);
    const data = await r.json();
    if (!data.length) done = true;
    data.forEach((m) => {
      if (m.genres) {
        m.genres.split("|").forEach((g) => {
          const key = g.trim();
          if (!key) return;
          genresCount[key] = (genresCount[key] || 0) + 1;
        });
      }
    });
    page++;
  }
  const labels = Object.keys(genresCount).slice(0, 12);
  const values = labels.map((k) => genresCount[k]);
  const ctx = document.getElementById("chart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Top Genres (by movies)", data: values }],
    },
    options: { responsive: true, plugins: { legend: { display: true } } },
  });
}
loadTiles();
loadChart();
