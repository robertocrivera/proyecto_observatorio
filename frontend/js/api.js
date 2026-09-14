/**
 * Edudemia API Client
 * Centraliza las peticiones HTTP Fetch al Backend FastAPI
 */
const EdudemiaAPI = (() => {
    // Determinar URL base de la API
    const getBaseUrl = () => {
        if (window.location.protocol.startsWith("http")) {
            return `${window.location.origin}/api/v1`;
        }
        return "http://127.0.0.1:8000/api/v1";
    };

    const BASE_URL = getBaseUrl();
    const TOKEN_STORAGE_KEY = "edudemia_session_token";
    const SUBSCRIPTION_STORAGE_KEY = "edudemia_subscription_token";
    const SUBSCRIPTION_DATA_KEY = "edudemia_subscription_data";

    // Manejo genérico de respuestas JSON y errores
    async function request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, { ...options, headers });
            
            if (response.status === 429) {
                throw new Error("Límite de peticiones excedido (Rate Limiting). Espere un momento.");
            }

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                const message = errData.detail || `Error en el servidor: ${response.status} ${response.statusText}`;
                throw new Error(message);
            }

            return await response.json();
        } catch (error) {
            console.error(`[API Error] ${endpoint}:`, error);
            throw error;
        }
    }

    return {
        // Token management
        setSessionToken(token) {
            localStorage.setItem(TOKEN_STORAGE_KEY, token);
        },
        getSessionToken() {
            return localStorage.getItem(TOKEN_STORAGE_KEY);
        },
        hasSessionToken() {
            return Boolean(localStorage.getItem(TOKEN_STORAGE_KEY));
        },

        // Módulo A: Demografía y Censo DANE
        async getDepartamentos() {
            return await request("/demografia/departamentos");
        },

        async getMunicipios(departamentoId) {
            return await request(`/demografia/municipios?departamento_id=${departamentoId}`);
        },

        async consultarDemografia(departamentoId, municipioId, ambito) {
            const params = new URLSearchParams();
            if (departamentoId) params.append("departamento_id", departamentoId);
            if (municipioId) params.append("municipio_id", municipioId);
            if (ambito) params.append("ambito", ambito);
            return await request(`/demografia/consulta?${params.toString()}`);
        },

        // Módulo B: Captura de Lead y Habeas Data
        async registrarLead(leadData) {
            const res = await request("/leads/registrar", {
                method: "POST",
                body: JSON.stringify(leadData)
            });
            if (res.token_descarga) {
                this.setSessionToken(res.token_descarga);
            }
            return res;
        },

        getDownloadUrl(municipioId = 1, ambito = "Urbano") {
            const token = this.getSessionToken() || "DEMO-SESSION";
            return `${BASE_URL}/leads/descargar-reporte?token=${encodeURIComponent(token)}&municipio_id=${municipioId}&ambito=${encodeURIComponent(ambito)}`;
        },

        // Módulo C.1: Geolocalización Haversine 5 km
        async getColegiosEnRadio(lat, lng, radioKm = 5.0, municipioId = 1) {
            return await request(`/geo/colegios-redonda?lat=${lat}&lng=${lng}&radio_km=${radioKm}&municipio_id=${municipioId}`);
        },

        // Módulo C.2: Comparativa y Prescripción
        async compararEstrategia(payload) {
            return await request("/estrategia/comparar", {
                method: "POST",
                body: JSON.stringify(payload)
            });
        },

        // Módulo de Suscripciones en Pesos Colombianos (Paywall COP)
        async getPlanesSuscripcion() {
            return await request("/suscripcion/planes");
        },

        async activarSuscripcionSimulada(payload) {
            const res = await request("/suscripcion/activar-simulacion", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            if (res.subscription_token) {
                this.setSubscriptionToken(res.subscription_token, res);
            }
            return res;
        },

        setSubscriptionToken(token, fullData = {}) {
            localStorage.setItem(SUBSCRIPTION_STORAGE_KEY, token);
            localStorage.setItem(SUBSCRIPTION_DATA_KEY, JSON.stringify(fullData));
        },

        getSubscriptionToken() {
            return localStorage.getItem(SUBSCRIPTION_STORAGE_KEY);
        },

        getSubscriptionData() {
            const raw = localStorage.getItem(SUBSCRIPTION_DATA_KEY);
            return raw ? JSON.parse(raw) : null;
        },

        hasSubscription() {
            return Boolean(localStorage.getItem(SUBSCRIPTION_STORAGE_KEY));
        },

        clearSubscription() {
            localStorage.removeItem(SUBSCRIPTION_STORAGE_KEY);
            localStorage.removeItem(SUBSCRIPTION_DATA_KEY);
        }
    };
})();

