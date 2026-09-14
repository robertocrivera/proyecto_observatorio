/**
 * Edudemia Web GIS Map
 * Visualización geoespacial con Leaflet, radio buffer de 5 km
 * Soporte para temas: Azul Noche (predeterminado, como estaba) y Blanco
 * 100% libre de marcas de agua y sin requerimiento de API Key
 */
const EdudemiaMap = (() => {
    let mapInstance = null;
    let circleLayer = null;
    let markersLayer = null;
    let baseTileLayer = null;
    let labelsTileLayer = null;
    let currentTheme = "azul_noche";
    let lastGeoData = null;

    const THEMES = {
        azul_noche: {
            base: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            labels: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
            className: 'theme-azul-noche'
        },
        blanco: {
            base: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            labels: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
            className: 'theme-blanco'
        }
    };

    function applyTileLayers(themeKey) {
        if (!mapInstance) return;
        const config = THEMES[themeKey] || THEMES.azul_noche;
        const mapEl = document.getElementById("map");

        if (baseTileLayer && mapInstance.hasLayer(baseTileLayer)) {
            mapInstance.removeLayer(baseTileLayer);
        }
        if (labelsTileLayer && mapInstance.hasLayer(labelsTileLayer)) {
            mapInstance.removeLayer(labelsTileLayer);
        }

        if (mapEl) {
            mapEl.classList.remove("theme-azul-noche", "theme-blanco");
            mapEl.classList.add(config.className);
        }

        baseTileLayer = L.tileLayer(config.base, {
            maxZoom: 18,
            maxNativeZoom: 16,
            attribution: 'Esri, &copy; OpenStreetMap'
        }).addTo(mapInstance);

        labelsTileLayer = L.tileLayer(config.labels, {
            maxZoom: 18,
            maxNativeZoom: 16,
            opacity: 0.9
        }).addTo(mapInstance);
    }

    function setTheme(themeKey) {
        currentTheme = themeKey;
        applyTileLayers(themeKey);

        const btnAzul = document.getElementById("btnThemeAzulNoche");
        const btnBlanco = document.getElementById("btnThemeBlanco");
        if (btnAzul && btnBlanco) {
            if (themeKey === "azul_noche") {
                btnAzul.classList.add("active");
                btnBlanco.classList.remove("active");
            } else {
                btnBlanco.classList.add("active");
                btnAzul.classList.remove("active");
            }
        }

        // Re-renderizar marcadores si ya fueron cargados para conservarlos visibles
        if (lastGeoData) {
            renderSchoolsAndDemand(lastGeoData);
        }
    }

    function initMap(mapElementId = "map", centerLat = 4.6732, centerLng = -74.1448) {
        const el = document.getElementById(mapElementId);
        if (!el || typeof L === "undefined") {
            console.warn("Leaflet no está disponible o contenedor de mapa no encontrado.");
            return;
        }

        if (mapInstance) {
            mapInstance.remove();
        }

        // Crear mapa
        mapInstance = L.map(mapElementId, {
            zoomControl: true,
            attributionControl: false,
            maxZoom: 18
        }).setView([centerLat, centerLng], 13);

        // Capa de marcadores dedicada
        markersLayer = L.layerGroup().addTo(mapInstance);

        // Aplicar capas de teselas según el tema activo (Azul Noche por defecto)
        applyTileLayers(currentTheme);
    }

    function renderSchoolsAndDemand(geoData) {
        if (!mapInstance || !geoData) return;
        lastGeoData = geoData;

        const {
            centro_lat,
            centro_lng,
            radio_km = 5.0,
            colegios = [],
            estudiantes_buscadores = [],
            municipio_nombre = "Zona Consultada"
        } = geoData;

        // Asegurar que exista la capa de marcadores
        if (!markersLayer || !mapInstance.hasLayer(markersLayer)) {
            markersLayer = L.layerGroup().addTo(mapInstance);
        } else {
            markersLayer.clearLayers();
        }

        // Limpiar círculo de buffer previo si existe
        if (circleLayer && mapInstance.hasLayer(circleLayer)) {
            mapInstance.removeLayer(circleLayer);
        }

        // Mover vista al centro
        mapInstance.setView([centro_lat, centro_lng], 13);

        // Dibujar Círculo de Buffer (Radio de 5 km)
        circleLayer = L.circle([centro_lat, centro_lng], {
            color: '#00d2ff',
            weight: 2,
            opacity: 0.95,
            fillColor: '#0072ff',
            fillOpacity: 0.15,
            dashArray: '6, 8'
        }).addTo(mapInstance);

        // 1. Marcador del Punto Central / Sede Consultada
        const centerIcon = L.divIcon({
            className: 'center-pin',
            html: `<div style="background:#f59e0b; width:18px; height:18px; border-radius:50%; border:3px solid #ffffff; box-shadow:0 0 16px #f59e0b;"></div>`,
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        });

        L.marker([centro_lat, centro_lng], { icon: centerIcon })
            .bindPopup(`<b>📍 ${municipio_nombre} (Centroide)</b><br>Radio de Cobertura: ${radio_km} km`)
            .addTo(markersLayer);

        // 2. Marcadores de Colegios Oficiales y No Oficiales
        (colegios || []).forEach(col => {
            const isOficial = col.sector === 'Oficial';
            const pinColor = isOficial ? '#0072ff' : '#00d2ff';
            const iconEmoji = isOficial ? '🏛️' : '🏫';

            const schoolIcon = L.divIcon({
                className: 'school-pin',
                html: `<div style="background:${pinColor}; color:#ffffff; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2.5px solid #ffffff; box-shadow:0 0 16px ${pinColor}; font-size:14px; cursor:pointer;">${iconEmoji}</div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            });

            const popupContent = `
                <div style="font-family:sans-serif; color:#0f172a; min-width:190px;">
                    <strong style="font-size:13px; color:#0f1c3f;">${col.nombre}</strong><br>
                    <span style="font-size:11px; font-weight:bold; color:${isOficial ? '#0072ff' : '#0284c7'};">Sector: ${col.sector}</span><br>
                    <span style="font-size:11px; color:#64748b;">Ámbito: ${col.ambito}</span><br>
                    <span style="font-size:11px; color:#059669; font-weight:bold;">Distancia: ${col.distancia_km} km</span><br>
                    <span style="font-size:10px; color:#94a3b8;">${col.direccion || ''}</span>
                </div>
            `;

            L.marker([col.latitud, col.longitud], { icon: schoolIcon })
                .bindPopup(popupContent)
                .addTo(markersLayer);
        });

        // 3. Marcadores de Estudiantes Buscadores (Demanda Activa)
        (estudiantes_buscadores || []).forEach(est => {
            const seekerIcon = L.divIcon({
                className: 'seeker-pin',
                html: `<div style="background:#10b981; width:14px; height:14px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 14px #10b981; cursor:pointer;"></div>`,
                iconSize: [14, 14],
                iconAnchor: [7, 7]
            });

            L.marker([est.latitud, est.longitud], { icon: seekerIcon })
                .bindPopup(`<b>🎯 Familia Buscando Cupo</b><br>Interés: <strong>${est.grado_interes}</strong><br>A ${est.distancia_km} km de distancia`)
                .addTo(markersLayer);
        });
    }

    return {
        initMap,
        setTheme,
        renderSchoolsAndDemand
    };
})();
