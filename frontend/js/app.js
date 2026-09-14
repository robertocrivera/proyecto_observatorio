/**
 * Edudemia - Application Logic & Controllers
 * Orquesta la interactividad de la plataforma, filtros reactivos, modales y prescripción
 */

document.addEventListener("DOMContentLoaded", async () => {
    // Referencias al DOM
    const depSelect = document.getElementById("depSelect");
    const munSelect = document.getElementById("munSelect");
    const ambSelect = document.getElementById("ambSelect");
    const btnSearch = document.getElementById("btnSearch");
    
    // Indicadores y Métricas
    const metricDescenso = document.getElementById("metricDescenso");
    const metricColegios = document.getElementById("metricColegios");
    const metricAmbitos = document.getElementById("metricAmbitos");
    
    // Paneles de Resumen
    const countOficiales = document.getElementById("countOficiales");
    const countNoOficiales = document.getElementById("countNoOficiales");
    const radioKmSpan = document.getElementById("radioKmSpan");
    const pctUrbano = document.getElementById("pctUrbano");
    const pctRuralCentro = document.getElementById("pctRuralCentro");
    const pctRuralDisperso = document.getElementById("pctRuralDisperso");

    // Formulario de Lead Magnet (Estático y Modal)
    const staticLeadForm = document.getElementById("staticLeadForm");
    const modalLeadForm = document.getElementById("modalLeadForm");
    const leadModal = document.getElementById("leadModal");
    const btnDownloadReport = document.getElementById("btnDownloadReport");
    const downloadContainer = document.getElementById("downloadContainer");

    // Formulario de Comparativa Estratégica
    const stratForm = document.getElementById("stratForm");
    const btnPresetFederici = document.getElementById("btnPresetFederici");
    const btnPresetGimnasio = document.getElementById("btnPresetGimnasio");
    const stratResultsContainer = document.getElementById("stratResultsContainer");

    // Inicializar Mapa Web GIS
    EdudemiaMap.initMap("map", 4.6732, -74.1448);

    // 1. Cargar Departamentos Iniciales
    async function loadDepartamentos() {
        try {
            const departamentos = await EdudemiaAPI.getDepartamentos();
            depSelect.innerHTML = "";
            departamentos.forEach(d => {
                const opt = document.createElement("option");
                opt.value = d.id;
                opt.textContent = d.nombre;
                depSelect.appendChild(opt);
            });

            if (departamentos.length > 0) {
                await loadMunicipios(departamentos[0].id);
            }
        } catch (err) {
            showToast("No se pudo conectar con el backend. Verifique que el servidor esté activo.", "error");
        }
    }

    // 2. Cargar Municipios por Departamento
    async function loadMunicipios(departamentoId) {
        try {
            const municipios = await EdudemiaAPI.getMunicipios(departamentoId);
            munSelect.innerHTML = "";
            municipios.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m.id;
                opt.textContent = m.nombre;
                opt.dataset.lat = m.latitud;
                opt.dataset.lng = m.longitud;
                munSelect.appendChild(opt);
            });

            if (municipios.length > 0) {
                await ejecutarConsultaDemografica();
            }
        } catch (err) {
            console.error("Error al cargar municipios:", err);
        }
    }

    // 3. Ejecutar Consulta Demográfica y Actualizar Dashboard
    async function ejecutarConsultaDemografica() {
        const deptoId = parseInt(depSelect.value) || 1;
        const munId = parseInt(munSelect.value) || 1;
        const ambito = ambSelect.value || "Urbano";

        // Feedback visual
        metricDescenso.innerHTML = '<span class="spinner spinner-cyan"></span>';

        try {
            const data = await EdudemiaAPI.consultarDemografia(deptoId, munId, ambito);

            // Actualizar Métricas Circulares
            const varSign = data.variacion_porcentual > 0 ? "+" : "";
            metricDescenso.textContent = `${varSign}${data.variacion_porcentual}%`;
            metricColegios.textContent = `${data.radio_cobertura_km} km`;
            metricAmbitos.textContent = "3 Opciones";

            // Actualizar Gráfico de Barras Dinámico Neón
            EdudemiaCharts.renderBarChart("barChartContainer", data.serie_historica);

            // Actualizar Resumen de Oferta
            if (countOficiales) countOficiales.textContent = data.total_colegios_oficiales;
            if (countNoOficiales) countNoOficiales.textContent = data.total_colegios_no_oficiales;
            if (radioKmSpan) radioKmSpan.textContent = `${data.radio_cobertura_km} km`;

            // Actualizar Segmentación Territorial
            if (pctUrbano) pctUrbano.textContent = `${data.resumen_ambito["Urbano"] || 0}%`;
            if (pctRuralCentro) pctRuralCentro.textContent = `${data.resumen_ambito["Rural Centro"] || 0}%`;
            if (pctRuralDisperso) pctRuralDisperso.textContent = `${data.resumen_ambito["Rural Disperso"] || 0}%`;

            // Cargar datos geoespaciales a 5 km a la redonda
            const selectedOpt = munSelect.selectedOptions[0];
            const lat = selectedOpt ? parseFloat(selectedOpt.dataset.lat) : data.latitud;
            const lng = selectedOpt ? parseFloat(selectedOpt.dataset.lng) : data.longitud;
            await loadGeoMap(lat, lng, 5.0, munId);

        } catch (err) {
            metricDescenso.textContent = "N/A";
            showToast(err.message, "error");
        }
    }

    // 4. Módulo GIS: Cargar Colegios y Demanda en 5 km
    async function loadGeoMap(lat, lng, radioKm, municipioId) {
        try {
            const geoData = await EdudemiaAPI.getColegiosEnRadio(lat, lng, radioKm, municipioId);
            EdudemiaMap.renderSchoolsAndDemand(geoData);

            // Actualizar sidebar del mapa
            const listEl = document.getElementById("schoolsListMini");
            const geoTotalSchools = document.getElementById("geoTotalSchools");
            const geoTotalDemand = document.getElementById("geoTotalDemand");

            if (geoTotalSchools) geoTotalSchools.textContent = geoData.total_colegios;
            if (geoTotalDemand) geoTotalDemand.textContent = geoData.total_estudiantes_buscando;

            if (listEl) {
                if (geoData.colegios.length === 0) {
                    listEl.innerHTML = '<p style="color:var(--text-muted); font-size:0.8rem;">No hay instituciones registradas en este radio.</p>';
                } else {
                    listEl.innerHTML = geoData.colegios.map(col => `
                        <div class="school-item-mini ${col.sector.toLowerCase()}">
                            <p class="name">${col.nombre}</p>
                            <p class="meta">${col.sector} • ${col.ambito} • <strong>${col.distancia_km} km</strong></p>
                        </div>
                    `).join("");
                }
            }
        } catch (err) {
            console.error("Error al cargar mapa GIS:", err);
        }
    }

    // 5. Gestión del Modal de Captura de Lead (Módulo B)
    window.openModal = function() {
        leadModal.style.display = "flex";
    };

    window.closeModal = function() {
        leadModal.style.display = "none";
    };

    // Cerrar modal al hacer clic en el backdrop
    leadModal.addEventListener("click", (e) => {
        if (e.target === leadModal) closeModal();
    });

    // Envío de Formulario Lead (Static Form en White Section)
    if (staticLeadForm) {
        staticLeadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const nombre = document.getElementById("staticLeadName").value.trim();
            const correo = document.getElementById("staticLeadEmail").value.trim();
            const habeas = document.getElementById("staticLeadHabeas").checked;

            await procesarRegistroLead(nombre, correo, habeas, staticLeadForm);
        });
    }

    // Envío de Formulario Lead (Modal Form)
    if (modalLeadForm) {
        modalLeadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const nombre = document.getElementById("modalLeadName").value.trim();
            const correo = document.getElementById("modalLeadEmail").value.trim();
            const habeas = document.getElementById("modalLeadHabeas").checked;

            await procesarRegistroLead(nombre, correo, habeas, modalLeadForm);
        });
    }

    async function procesarRegistroLead(nombre, correo, habeas, formEl) {
        if (!habeas) {
            showToast("Debe autorizar el tratamiento de datos personales conforme a la Ley 1581.", "error");
            return;
        }

        const submitBtn = formEl.querySelector("button[type='submit']");
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Procesando...';

        try {
            const munId = parseInt(munSelect.value) || 1;
            const res = await EdudemiaAPI.registrarLead({
                nombre: nombre,
                correo_institucional: correo,
                tratamiento_datos_aceptado: habeas,
                municipio_id: munId,
                ambito: ambSelect.value || "Urbano"
            });

            showToast("¡Registro exitoso! Diagnóstico desbloqueado.", "success");

            // Configurar botón de descarga inmediata
            if (btnDownloadReport) {
                const downloadUrl = EdudemiaAPI.getDownloadUrl(munId, ambSelect.value || "Urbano");
                btnDownloadReport.onclick = () => window.open(downloadUrl, "_blank");
                if (downloadContainer) downloadContainer.style.display = "block";
            }

            // Desbloquear sección de estrategia en la UI
            const stratSection = document.getElementById("estrategia-prescriptiva");
            if (stratSection) {
                stratSection.scrollIntoView({ behavior: 'smooth' });
            }

            // Cambiar modal a estado desbloqueado
            document.getElementById("modalHeaderTitle").textContent = "✅ Diagnóstico Desbloqueado";
            document.getElementById("modalHeaderDesc").textContent = `Session Pass emitido: ${res.token_descarga}. Ya puede descargar su informe.`;

        } catch (err) {
            showToast(err.message, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    // 6. Comparativa y Motor de Recomendaciones Prescriptivas (Módulo C.2 con Paywall)
    let selectedPlanId = "trimestral";
    let selectedPayMethod = "PSE";

    window.openSubscriptionModal = function() {
        const subModal = document.getElementById("subscriptionModal");
        if (subModal) {
            // Rellenar datos si ya existen en el formulario
            const colNom = document.getElementById("colegioNombre").value;
            const subCol = document.getElementById("subColegioNombre");
            if (subCol && colNom) subCol.value = colNom;
            subModal.style.display = "flex";
        }
    };

    window.closeSubscriptionModal = function() {
        const subModal = document.getElementById("subscriptionModal");
        if (subModal) subModal.style.display = "none";
    };

    // Cerrar con click fuera
    const subModalEl = document.getElementById("subscriptionModal");
    if (subModalEl) {
        subModalEl.addEventListener("click", (e) => {
            if (e.target === subModalEl) closeSubscriptionModal();
        });
    }

    window.selectPlan = function(planId) {
        selectedPlanId = planId;
        ["mensual", "trimestral", "anual"].forEach(p => {
            const card = document.getElementById(`cardPlan${p.charAt(0).toUpperCase() + p.slice(1)}`);
            const radio = document.getElementById(`radio${p.charAt(0).toUpperCase() + p.slice(1)}`);
            if (card) {
                if (p === planId) {
                    card.classList.add("selected");
                    if (radio) radio.checked = true;
                } else {
                    card.classList.remove("selected");
                    if (radio) radio.checked = false;
                }
            }
        });

        const btnText = document.getElementById("btnSubmitSubText");
        if (btnText) {
            if (planId === "mensual") {
                btnText.textContent = "🚀 Activar Suscripción Mensual ($189.000 COP) y Ejecutar Motor";
            } else if (planId === "trimestral") {
                btnText.textContent = "🚀 Activar Suscripción Trimestral ($489.000 COP) y Ejecutar Motor";
            } else {
                btnText.textContent = "🚀 Activar Suscripción Anual ($1.690.000 COP) y Ejecutar Motor";
            }
        }
    };

    window.selectPaymentMethod = function(method) {
        selectedPayMethod = method;
        ["PSE", "Card", "Invoice"].forEach(m => {
            const el = document.getElementById(`payMethod${m}`);
            if (el) el.classList.remove("selected");
        });

        const pseBox = document.getElementById("pseFields");
        const cardBox = document.getElementById("cardFields");
        const invBox = document.getElementById("invoiceFields");

        if (pseBox) pseBox.style.display = "none";
        if (cardBox) cardBox.style.display = "none";
        if (invBox) invBox.style.display = "none";

        if (method === "PSE") {
            const el = document.getElementById("payMethodPSE");
            if (el) el.classList.add("selected");
            if (pseBox) pseBox.style.display = "block";
        } else if (method === "TARJETA") {
            const el = document.getElementById("payMethodCard");
            if (el) el.classList.add("selected");
            if (cardBox) cardBox.style.display = "block";
        } else if (method === "FACTURA_INSTITUCIONAL") {
            const el = document.getElementById("payMethodInvoice");
            if (el) el.classList.add("selected");
            if (invBox) invBox.style.display = "block";
        }
    };

    // Checkout de suscripción simulada
    const subForm = document.getElementById("subscriptionCheckoutForm");
    if (subForm) {
        subForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const colNombre = document.getElementById("subColegioNombre").value.trim();
            const correo = document.getElementById("subCorreo").value.trim();
            const bancoPse = document.getElementById("subBancoPse") ? document.getElementById("subBancoPse").value : "Bancolombia";

            const submitBtn = subForm.querySelector("button[type='submit']");
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Procesando Transacción COP...';

            try {
                const res = await EdudemiaAPI.activarSuscripcionSimulada({
                    plan_id: selectedPlanId,
                    colegio_nombre: colNombre,
                    correo_directivo: correo,
                    metodo_pago: selectedPayMethod,
                    banco_o_franquicia: selectedPayMethod === "PSE" ? bancoPse : selectedPayMethod
                });

                showToast(`🎉 ¡Suscripción activada! Licencia: ${res.subscription_token}`, "success");
                closeSubscriptionModal();

                // Ejecutar inmediatamente el motor prescriptivo
                await ejecutarMotorPrescriptivo();

            } catch (err) {
                showToast(err.message, "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    if (btnPresetFederici) {
        btnPresetFederici.addEventListener("click", () => {
            document.getElementById("colegioNombre").value = "Colegio Carlo Federici (IED)";
            document.getElementById("colegioSector").value = "Oficial";
            document.getElementById("mat2021").value = 95;
            document.getElementById("mat2022").value = 82;
            document.getElementById("mat2023").value = 74;
            document.getElementById("mat2024").value = 63;
        });
    }

    if (btnPresetGimnasio) {
        btnPresetGimnasio.addEventListener("click", () => {
            document.getElementById("colegioNombre").value = "Gimnasio Moderno Fontibón";
            document.getElementById("colegioSector").value = "No Oficial";
            document.getElementById("mat2021").value = 45;
            document.getElementById("mat2022").value = 40;
            document.getElementById("mat2023").value = 33;
            document.getElementById("mat2024").value = 27;
        });
    }

    function renderLockedState() {
        if (!stratResultsContainer) return;
        stratResultsContainer.innerHTML = `
            <div class="locked-box">
                <div class="locked-icon-pulse">🔒</div>
                <h3 style="color:#fff; font-size:1.3rem; margin-bottom:0.5rem;">Módulo Exclusivo para Colegios Suscritos</h3>
                <p style="color:#cbd5e1; max-width:440px; font-size:0.88rem; line-height:1.5;">
                    El motor de cruce analítico y prescripción estratégica requiere una suscripción institucional activa (Plataforma Hermana).
                </p>
                <div style="display:flex; gap:12px; margin-top:1rem; font-size:0.8rem; color:var(--accent-cyan);">
                    <span>✓ Planes desde $189.000 COP</span>
                    <span>✓ Pago PSE / Tarjeta</span>
                    <span>✓ Licencia Inmediata</span>
                </div>
                <button class="btn-open-plans" onclick="openSubscriptionModal()">
                    ⭐ Ver Planes y Desbloquear Diagnóstico
                </button>
            </div>
        `;
    }

    if (stratForm) {
        stratForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // REGLA ESTRICTA DE NEGOCIO: SIN SUSCRIPCIÓN NO PUEDE USARSE
            if (!EdudemiaAPI.hasSubscription()) {
                showToast("Se requiere un plan de suscripción en Pesos Colombianos para ejecutar el diagnóstico prescriptivo.", "info");
                openSubscriptionModal();
                return;
            }

            await ejecutarMotorPrescriptivo();
        });
    }

    async function ejecutarMotorPrescriptivo() {
        const colegioNombre = document.getElementById("colegioNombre").value || "Mi Colegio";
        const sector = document.getElementById("colegioSector").value;
        const munId = parseInt(munSelect.value) || 1;
        const ambito = ambSelect.value || "Urbano";

        const mat2021 = parseInt(document.getElementById("mat2021").value) || 0;
        const mat2022 = parseInt(document.getElementById("mat2022").value) || 0;
        const mat2023 = parseInt(document.getElementById("mat2023").value) || 0;
        const mat2024 = parseInt(document.getElementById("mat2024").value) || 0;

        const payload = {
            municipio_id: munId,
            colegio_nombre: colegioNombre,
            sector: sector,
            ambito: ambito,
            matricula_historica: [
                { año: 2021, grado: "Transición", numero_estudiantes: mat2021 },
                { año: 2022, grado: "Transición", numero_estudiantes: mat2022 },
                { año: 2023, grado: "Transición", numero_estudiantes: mat2023 },
                { año: 2024, grado: "Transición", numero_estudiantes: mat2024 }
            ]
        };

        const submitBtn = stratForm.querySelector("button[type='submit']");
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Analizando Matrícula y Proyecciones...';
        }

        try {
            const result = await EdudemiaAPI.compararEstrategia(payload);
            renderRecommendations(result);
            showToast("Diagnóstico prescriptivo generado con éxito para colegio suscrito.", "success");
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = "⚡ Ejecutar Motor de Diagnóstico Prescriptivo";
            }
        }
    }

    function renderRecommendations(result) {
        if (!stratResultsContainer) return;

        const subData = EdudemiaAPI.getSubscriptionData() || {
            plan_nombre: "Plan Trimestral Pro",
            precio_formateado: "$489.000 COP",
            subscription_token: EdudemiaAPI.getSubscriptionToken() || "SUB-COP-ACTIVE"
        };

        let recsHtml = `
            <div class="sub-active-banner">
                <div>
                    <strong>⭐ Licencia Activa:</strong> ${subData.plan_nombre} (${subData.precio_formateado})
                    <span style="font-size:0.75rem; color:var(--accent-cyan); margin-left:8px;">ID: ${subData.subscription_token}</span>
                </div>
                <span style="color:var(--success-green); font-weight:bold;">● ACTIVO</span>
            </div>

            <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <h3 style="margin:0; font-size:1.15rem; color:#fff;">📊 Balance Estratégico: <strong>${result.colegio_nombre}</strong></h3>
                    <span class="badge-pill">Variación Interna: <strong>${result.variacion_matricula_institucional}%</strong></span>
                </div>
                <div style="display:flex; gap:15px; margin-top:0.8rem; font-size:0.85rem; color:var(--text-muted);">
                    <span>📉 Descenso Natalidad Territorial: <strong>${result.variacion_natalidad_territorial}%</strong></span>
                    <span>🏫 Competencia en 5 km: <strong>${result.colegios_competencia_radio_5km}</strong></span>
                    <span>🎯 Familias Buscando Cupo: <strong>${result.estudiantes_buscando_cupo_5km}</strong></span>
                </div>
            </div>
            <h4 style="color:var(--accent-cyan); font-size:1rem; margin-bottom:1rem;">🚀 Recomendaciones Prescriptivas Accionables:</h4>
        `;

        result.recomendaciones.forEach(rec => {
            recsHtml += `
                <div class="rec-card ${rec.tipo}">
                    <div class="rec-title">${rec.titulo}</div>
                    <div class="rec-desc">${rec.descripcion}</div>
                    <div class="rec-impact">💡 Impacto Proyectado: ${rec.impacto_estimado}</div>
                </div>
            `;
        });

        recsHtml += `
            <div style="margin-top: 1.5rem; text-align: center; display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
                <button class="btn-portal" onclick="window.open(EdudemiaAPI.getDownloadUrl(), '_blank')">
                    📄 Descargar Radiografía Completa en PDF / JSON
                </button>
            </div>
        `;

        stratResultsContainer.innerHTML = recsHtml;
    }

    // Estado inicial: Si no está suscrito, mostrar Paywall bloqueado
    if (!EdudemiaAPI.hasSubscription()) {
        renderLockedState();
    }

    // 7. Event Listeners de Filtros Reactivos
    depSelect.addEventListener("change", async (e) => {
        await loadMunicipios(parseInt(e.target.value));
    });

    munSelect.addEventListener("change", async () => {
        await ejecutarConsultaDemografica();
    });

    ambSelect.addEventListener("change", async () => {
        await ejecutarConsultaDemografica();
    });

    if (btnSearch) {
        btnSearch.addEventListener("click", () => {
            ejecutarConsultaDemografica();
            openModal();
        });
    }

    // Inicializar carga de datos
    await loadDepartamentos();
});

// Sistema de Notificaciones Toast
function showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "✅" : (type === "error" ? "⚠️" : "ℹ️");
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

