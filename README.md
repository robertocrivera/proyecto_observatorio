# 🌐 Edudemia - Observatorio Demográfico Educativo Colombia

Plataforma Web GIS, EdTech y Lead Management diseñada para directivos docentes, rectores y coordinadores en Colombia. Permite monitorear la transición demográfica (caída de natalidad DANE), mapear la oferta educativa circundante en un radio de 5 km mediante la fórmula de Haversine y generar diagnósticos estratégicos prescriptivos basados en datos de matrícula interna.

---

## 🏛️ 1. Estructura y Arquitectura del Proyecto

El proyecto sigue una arquitectura en capas desacoplada y limpia aplicando principios **SOLID**:

```
proyecto_observatorio/
├── backend/
│   ├── app/
│   │   ├── main.py                       # Servidor FastAPI, CORS y montaje estático
│   │   ├── core/                         # Configuración, sanitización XSS, tokens y Rate Limiting
│   │   ├── db/                           # Conexión SQLAlchemy y Seeder automático DANE
│   │   ├── models/                       # 7 Modelos relacionales ORM
│   │   ├── schemas/                      # Validación y serialización con Pydantic v2
│   │   ├── repositories/                 # Consultas aisladas de datos (Repositories)
│   │   ├── services/                     # Lógica de negocio (Haversine 5km, Prescripción, Leads)
│   │   └── controllers/                  # Controladores y rutas REST (/api/v1/...)
│   ├── requirements.txt                  # Dependencias de Python
│   ├── run.py                            # Script de ejecución local
│   └── test_api.py                       # Suite de pruebas unitarias y de integración
├── database/
│   ├── schema.sql                        # DDL relacional y seeds DANE/SIMAT para SQLite/PostgreSQL
│   └── edudemia.db                       # Base de datos SQLite generada automáticamente
├── frontend/
│   ├── index.html                        # Interfaz de usuario modo oscuro neón
│   ├── css/
│   │   └── styles.css                    # Estilos CSS3 neón (#081226, #0f1c3f, #00d2ff, #0072ff)
│   ├── js/
│   │   ├── api.js                        # Cliente HTTP Fetch centralizado
│   │   ├── charts.js                     # Gráficos dinámicos reactivos
│   │   ├── map.js                        # Visualizador Web GIS Leaflet con buffer de 5 km
│   │   └── app.js                        # Controlador de eventos, estados de carga y modales
│   └── assets/
│       └── img/
│           └── logo.jpg                  # Logo oficial de Edudemia
├── index.html                            # Punto de entrada raíz
└── README.md                             # Documentación técnica
```

---

## 🚀 2. Instrucciones de Ejecución Local

### Paso 1: Requisitos
- Python 3.10+ instalado.
- Dependencias básicas (ya presentes o instalables con `pip install -r backend/requirements.txt`).

### Paso 2: Iniciar el Servidor Backend
Desde la raíz del proyecto o dentro de `backend/`, ejecute:

```bash
python backend/run.py
```
O directamente con `uvicorn`:
```bash
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

El servidor iniciará automáticamente en:
- **Plataforma Web (Frontend):** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Documentación Interactiva Swagger (OpenAPI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación Alternativa ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

*(Nota: También puede abrir directamente `frontend/index.html` en cualquier navegador web; el cliente HTTP detecta automáticamente la API local).*

### Paso 3: Ejecutar la Suite de Pruebas Automatizadas
Para verificar el 100% de la funcionalidad de la base de datos, filtros, geolocalización Haversine, registro de leads y motor de recomendaciones:

```bash
python backend/test_api.py
```

---

## 📊 3. Modelo de Datos Relacional (7 Tablas)

1. **`Departamentos`**: Cundinamarca, Antioquia, Valle del Cauca.
2. **`Municipios`**: Bogotá D.C. (Fontibón), Medellín, Cali, con códigos DANE y centroides geográficos.
3. **`Demografia_Natalidad`**: Series históricas (2019-2024) discriminadas por ámbitos: `Urbano`, `Rural Centro`, `Rural Disperso`.
4. **`Colegios`**: Instituciones oficiales y privadas georreferenciadas con coordenadas reales.
5. **`Leads_Directivos`**: Registro de directivos docentes con verificación estricta de consentimiento **Habeas Data (Ley 1581 de 2012)** y tokens de sesión.
6. **`Matricula_Interna_Colegio`**: Histórico institucional por grado para diagnósticos comparativos.
7. **`Estudiantes_Buscadores`**: Focos de geodemanda con intención activa de matrícula.

---

## 🔒 4. Seguridad y Cumplimiento Normativo

- **Rate Limiting:** Protección contra ataques DoS y scraping en los endpoints de leads mediante ventana deslizante por IP (HTTP 429 Too Many Requests).
- **Habeas Data (Colombia Ley 1581 de 2012):** Validación estricta en frontend y backend del consentimiento explícito antes de procesar datos de directivos.
- **Sanitización de Entradas:** Filtrado de caracteres de control y secuencias HTML peligrosas (XSS/SQLi) en el servicio de seguridad.
- **Tokens de Sesión Criptográficos:** Generación de identificadores de sesión resistentes a colisiones (`EDU-...`) para el desbloqueo de descargas y módulos de upsell.

---

## 🛰️ 5. Geolocalización Haversine y Web GIS

El backend implementa la fórmula ortodrómica de Haversine:
$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
Donde $r = 6371\text{ km}$. El mapa interactivo Leaflet renderiza:
- Círculo buffer de 5 km en azul/cian neón sobre capa oscura Esri Dark Canvas (100% gratuita y sin requerimiento de API Key).
- Marcadores diferenciados: Colegios Oficiales (Azul), Colegios No Oficiales (Cian) y Familias Buscando Cupo (Verde Esmeralda).

---

## ☁️ 6. Recomendaciones de Escalabilidad para Entorno Cloud

Para llevar Edudemia a producción a escala nacional (1.122 municipios de Colombia):

1. **Base de Datos & GIS Empresarial:**
   - Migrar de SQLite a **PostgreSQL con extensión PostGIS**. Permite consultas espaciales indexadas vía `ST_DWithin` y `ST_DistanceSphere` con soporte para millones de registros de estudiantes y colegios.
2. **Caché y Rate Limiting Distribuido:**
   - Implementar **Redis** para almacenar el censo demográfico en memoria caché y gestionar el rate limiting distribuido con algoritmos Leaky Bucket / Token Bucket.
3. **Contenerización (Docker & Kubernetes):**
   - Empaquetar la aplicación en un contenedor Docker con imagen base `python:3.12-slim` y servidor ASGI `uvicorn` con múltiples `workers` gestionados por Gunicorn.
4. **Despliegue Serverless o PaaS:**
   - **Backend:** Desplegable en **Render**, **Railway**, **Fly.io** o **AWS ECS / Fargate**.
   - **Frontend:** Alojable en **Vercel**, **Cloudflare Pages** o **AWS S3 + CloudFront CDN** para entrega estática global con tiempos de carga inferiores a 200 ms.
5. **Generación de Reportes PDF:**
   - Para producción, integrar librerías como `WeasyPrint` o servicios headless de Chromium en Lambda para renderizar PDFs institucionales con gráficos vectoriales y membretes oficiales.

