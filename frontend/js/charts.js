/**
 * Edudemia Dynamic Neon Charts
 * Generación de gráficos de barras SVG reactivos con estética Cyberpunk Neón
 */
const EdudemiaCharts = (() => {
    function renderBarChart(containerId, serieHistorica = []) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!serieHistorica || serieHistorica.length === 0) {
            container.innerHTML = '<div style="margin:auto; color:var(--text-muted); font-size:0.85rem;">Sin datos para el ámbito seleccionado</div>';
            return;
        }

        const maxNacimientos = Math.max(...serieHistorica.map(d => d.nacimientos), 1);

        let html = '';
        serieHistorica.forEach(item => {
            const heightPct = Math.round((item.nacimientos / maxNacimientos) * 85);
            const formattedVal = item.nacimientos.toLocaleString('es-CO');

            html += `
                <div class="bar-col" title="Año ${item.año}: ${formattedVal} nacimientos">
                    <span class="bar-tooltip">${formattedVal}</span>
                    <div class="bar" style="height: ${heightPct}%;"></div>
                    <span class="bar-label">${item.año}</span>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    return {
        renderBarChart
    };
})();

