import sqlite3
from pathlib import Path

# Script generador de datos masivos para Colombia (10 departamentos, 34 municipios, 100+ colegios, 100+ buscadores, 600+ registros demográficos)

DEPARTAMENTOS_DATA = [
    (1, "Cundinamarca"),
    (2, "Antioquia"),
    (3, "Valle del Cauca"),
    (4, "Atlántico"),
    (5, "Santander"),
    (6, "Bolívar"),
    (7, "Risaralda"),
    (8, "Caldas"),
    (9, "Boyacá"),
    (10, "Tolima")
]

MUNICIPIOS_DATA = [
    # Cundinamarca
    (1, 1, "Bogotá D.C. (Fontibón)", "1100109", 4.6732, -74.1448, 5840),
    (2, 1, "Bogotá D.C. (Suba)", "1100111", 4.7450, -74.0850, 11200),
    (3, 1, "Chía", "25175", 4.8624, -74.0583, 1650),
    (4, 1, "Soacha", "25754", 4.5802, -74.2173, 8900),
    (5, 1, "Zipaquirá", "25899", 5.0256, -74.0044, 1820),
    (6, 1, "Facatativá", "25269", 4.8142, -74.3547, 1750),

    # Antioquia
    (7, 2, "Medellín (El Poblado / Laureles)", "05001", 6.2442, -75.5748, 23500),
    (8, 2, "Envigado", "05266", 6.1759, -75.5917, 2450),
    (9, 2, "Rionegro", "05615", 6.1552, -75.3737, 1980),
    (10, 2, "Bello", "05088", 6.3330, -75.5580, 5200),
    (11, 2, "Itagüí", "05360", 6.1846, -75.5991, 3100),

    # Valle del Cauca
    (12, 3, "Cali", "76001", 3.4516, -76.5320, 21400),
    (13, 3, "Palmira", "76520", 3.5394, -76.3036, 3800),
    (14, 3, "Yumbo", "76892", 3.5822, -76.4950, 1620),
    (15, 3, "Guadalajara de Buga", "76111", 3.9009, -76.2978, 1420),
    (16, 3, "Jamundí", "76364", 3.2606, -76.5414, 1750),

    # Atlántico
    (17, 4, "Barranquilla", "08001", 10.9685, -74.7813, 18900),
    (18, 4, "Soledad", "08758", 10.9184, -74.7646, 7800),
    (19, 4, "Puerto Colombia", "08573", 11.0211, -74.9547, 620),
    (20, 4, "Malambo", "08433", 10.8597, -74.7739, 1850),

    # Santander
    (21, 5, "Bucaramanga", "68001", 7.1254, -73.1198, 6400),
    (22, 5, "Floridablanca", "68276", 7.0622, -73.0864, 3200),
    (23, 5, "Girón", "68307", 7.0682, -73.1698, 2250),
    (24, 5, "Piedecuesta", "68547", 6.9880, -73.0496, 2100),

    # Bolívar
    (25, 6, "Cartagena de Indias", "13001", 10.3910, -75.4794, 15400),
    (26, 6, "Turbaco", "13836", 10.3308, -75.4128, 1200),
    (27, 6, "Arjona", "13052", 10.2586, -75.3444, 980),

    # Risaralda
    (28, 7, "Pereira", "66001", 4.8133, -75.6961, 5100),
    (29, 7, "Dosquebradas", "66170", 4.8386, -75.6811, 2300),
    (30, 7, "Santa Rosa de Cabal", "66682", 4.8690, -75.6214, 940),

    # Caldas
    (31, 8, "Manizales", "17001", 5.0689, -75.5174, 4300),
    (32, 8, "Villamaría", "17873", 5.0456, -75.5147, 720),
    (33, 8, "Chinchiná", "17174", 5.0131, -75.6044, 690),

    # Boyacá
    (34, 9, "Tunja", "15001", 5.5353, -73.3678, 2100),
    (35, 9, "Duitama", "15238", 5.8269, -73.0336, 1450),
    (36, 9, "Sogamoso", "15759", 5.7145, -72.9339, 1520),

    # Tolima
    (37, 10, "Ibagué", "73001", 4.4389, -75.2322, 6200),
    (38, 10, "Espinal", "73268", 4.1492, -74.8847, 980),
    (39, 10, "Melgar", "73449", 4.2047, -74.6408, 540)
]

def generate_schema_and_seed():
    db_file = Path(__file__).resolve().parent / "database" / "edudemia.db"
    sql_file = Path(__file__).resolve().parent / "database" / "schema.sql"

    # Conectar a SQLite
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # DDL
    ddl = """
    CREATE TABLE IF NOT EXISTS Departamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Municipios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departamento_id INTEGER NOT NULL,
        nombre VARCHAR(150) NOT NULL,
        codigo_dane VARCHAR(20) NOT NULL UNIQUE,
        latitud REAL DEFAULT 4.6732,
        longitud REAL DEFAULT -74.1448,
        FOREIGN KEY (departamento_id) REFERENCES Departamentos(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Demografia_Natalidad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        municipio_id INTEGER NOT NULL,
        ambito VARCHAR(50) NOT NULL CHECK (ambito IN ('Urbano', 'Rural Centro', 'Rural Disperso')),
        año INTEGER NOT NULL,
        nacimientos_registrados INTEGER NOT NULL,
        proyeccion_poblacion_0_5_años INTEGER NOT NULL,
        FOREIGN KEY (municipio_id) REFERENCES Municipios(id) ON DELETE CASCADE,
        UNIQUE (municipio_id, ambito, año)
    );

    CREATE TABLE IF NOT EXISTS Colegios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        municipio_id INTEGER NOT NULL,
        nombre VARCHAR(200) NOT NULL,
        sector VARCHAR(20) NOT NULL CHECK (sector IN ('Oficial', 'No Oficial')),
        ambito VARCHAR(50) NOT NULL CHECK (ambito IN ('Urbano', 'Rural Centro', 'Rural Disperso')),
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        direccion VARCHAR(255),
        FOREIGN KEY (municipio_id) REFERENCES Municipios(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Leads_Directivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(150) NOT NULL,
        correo_institucional VARCHAR(150) NOT NULL,
        colegio_id_opcional INTEGER,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        tratamiento_datos_aceptado BOOLEAN NOT NULL DEFAULT 1,
        token_descarga VARCHAR(100),
        ip_origen VARCHAR(45),
        FOREIGN KEY (colegio_id_opcional) REFERENCES Colegios(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Matricula_Interna_Colegio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        colegio_id INTEGER NOT NULL,
        año INTEGER NOT NULL,
        grado VARCHAR(50) NOT NULL,
        numero_estudiantes INTEGER NOT NULL,
        FOREIGN KEY (colegio_id) REFERENCES Colegios(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Estudiantes_Buscadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        municipio_id INTEGER NOT NULL,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        grado_interes VARCHAR(50) NOT NULL,
        fecha_consulta DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (municipio_id) REFERENCES Municipios(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_municipios_depto ON Municipios(departamento_id);
    CREATE INDEX IF NOT EXISTS idx_demografia_filtro ON Demografia_Natalidad(municipio_id, ambito, año);
    CREATE INDEX IF NOT EXISTS idx_colegios_coords ON Colegios(latitud, longitud);
    CREATE INDEX IF NOT EXISTS idx_buscadores_coords ON Estudiantes_Buscadores(latitud, longitud);
    """

    cursor.executescript(ddl)

    # Limpiar tablas principales para recarga fresca
    cursor.execute("DELETE FROM Matricula_Interna_Colegio;")
    cursor.execute("DELETE FROM Estudiantes_Buscadores;")
    cursor.execute("DELETE FROM Colegios;")
    cursor.execute("DELETE FROM Demografia_Natalidad;")
    cursor.execute("DELETE FROM Municipios;")
    cursor.execute("DELETE FROM Departamentos;")

    # 1. Insertar Departamentos
    for dep_id, dep_nom in DEPARTAMENTOS_DATA:
        cursor.execute("INSERT INTO Departamentos (id, nombre) VALUES (?, ?);", (dep_id, dep_nom))

    # 2. Insertar Municipios y Datos Demográficos
    colegio_id_counter = 1
    buscador_id_counter = 1

    for mun_id, depto_id, nombre, dane, lat, lng, base_nac in MUNICIPIOS_DATA:
        cursor.execute(
            "INSERT INTO Municipios (id, departamento_id, nombre, codigo_dane, latitud, longitud) VALUES (?, ?, ?, ?, ?, ?);",
            (mun_id, depto_id, nombre, dane, lat, lng)
        )

        # Generar Demografía 2019 a 2024 para Urbano, Rural Centro, Rural Disperso
        # Tasa de caída demográfica colombiana (~14% a 22% en 5 años)
        drop_factors = [1.0, 0.95, 0.89, 0.87, 0.84, 0.82] # -18% en 2024
        years = [2019, 2020, 2021, 2022, 2023, 2024]

        # Urbano (~72% de los nacimientos)
        for i, yr in enumerate(years):
            nac_urb = int(base_nac * 0.72 * drop_factors[i])
            proj_urb = nac_urb * 5
            cursor.execute(
                "INSERT INTO Demografia_Natalidad (municipio_id, ambito, año, nacimientos_registrados, proyeccion_poblacion_0_5_años) VALUES (?, ?, ?, ?, ?);",
                (mun_id, "Urbano", yr, nac_urb, proj_urb)
            )

        # Rural Centro (~18% de los nacimientos)
        for i, yr in enumerate(years):
            nac_rc = int(base_nac * 0.18 * (drop_factors[i] - 0.02))
            proj_rc = nac_rc * 5
            cursor.execute(
                "INSERT INTO Demografia_Natalidad (municipio_id, ambito, año, nacimientos_registrados, proyeccion_poblacion_0_5_años) VALUES (?, ?, ?, ?, ?);",
                (mun_id, "Rural Centro", yr, nac_rc, proj_rc)
            )

        # Rural Disperso (~10% de los nacimientos)
        for i, yr in enumerate(years):
            nac_rd = int(base_nac * 0.10 * (drop_factors[i] - 0.04))
            proj_rd = nac_rd * 5
            cursor.execute(
                "INSERT INTO Demografia_Natalidad (municipio_id, ambito, año, nacimientos_registrados, proyeccion_poblacion_0_5_años) VALUES (?, ?, ?, ?, ?);",
                (mun_id, "Rural Disperso", yr, nac_rd, proj_rd)
            )

        # 3. Crear Colegios Oficiales y No Oficiales en la cercanía (~0.5 a 4.5 km del centroide)
        schools_info = [
            ("Colegio Mayor San Simón", "No Oficial", "Urbano", 0.008, 0.005, "Calle 10 # 14-25"),
            ("Institución Educativa Técnica República", "Oficial", "Urbano", -0.006, 0.007, "Carrera 8 # 20-50"),
            ("Gimnasio Campestre Los Andes", "No Oficial", "Rural Centro", 0.018, -0.015, "Km 4 Vía Regional"),
            ("Institución Educativa Departamental Integrada", "Oficial", "Urbano", -0.012, -0.009, "Avenida Principal # 5-80"),
            ("Liceo Moderno Pedagógico", "No Oficial", "Urbano", 0.005, -0.011, "Diagonal 18 # 32-14"),
            ("Colegio Agropecuario El Porvenir", "Oficial", "Rural Disperso", -0.025, 0.022, "Vereda La Esperanza")
        ]

        # Colegios específicos para Fontibón si es mun_id 1
        if mun_id == 1:
            schools_info = [
                ("Colegio Carlo Federici (IED)", "Oficial", "Urbano", -0.0022, 0.0016, "Carrera 100 # 22D-45"),
                ("Colegio Atabanzha (IED)", "Oficial", "Urbano", -0.0077, 0.0058, "Calle 23B # 96C-22"),
                ("Colegio Villemar el Carmen (IED)", "Oficial", "Urbano", 0.0048, -0.0032, "Carrera 104 # 19A-10"),
                ("Colegio La Giralda", "No Oficial", "Urbano", 0.0018, 0.0033, "Calle 22 # 103-50"),
                ("Gimnasio Moderno Fontibón", "No Oficial", "Urbano", 0.0068, -0.0012, "Carrera 99 # 24-18"),
                ("Liceo Colombo Andino", "No Oficial", "Urbano", -0.0112, -0.0047, "Calle 20 # 98-35"),
                ("Colegio San José de Fontibón", "No Oficial", "Urbano", -0.0042, -0.0072, "Carrera 105 # 21-12"),
                ("Colegio Costa Rica (IED)", "Oficial", "Urbano", 0.0003, 0.0098, "Calle 25 # 95-15"),
                ("Institución Agroecológica Fontibón Rural", "Oficial", "Rural Centro", 0.0188, -0.0152, "Km 3 Vía Faca"),
                ("Colegio Campestre El Salitre", "No Oficial", "Rural Disperso", 0.0248, -0.0232, "Vereda El Salitre")
            ]

        first_col_id_in_mun = colegio_id_counter
        for s_nom, s_sec, s_amb, dlat, dlng, s_dir in schools_info:
            c_lat = round(lat + dlat, 6)
            c_lng = round(lng + dlng, 6)
            prefix = "" if mun_id == 1 else f"{nombre} - "
            cursor.execute(
                "INSERT INTO Colegios (id, municipio_id, nombre, sector, ambito, latitud, longitud, direccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                (colegio_id_counter, mun_id, f"{prefix}{s_nom}", s_sec, s_amb, c_lat, c_lng, s_dir)
            )
            colegio_id_counter += 1

        # Matrícula interna de muestra
        mat_series = [(2021, 95), (2022, 82), (2023, 74), (2024, 63)]
        for myr, mcount in mat_series:
            cursor.execute(
                "INSERT INTO Matricula_Interna_Colegio (colegio_id, año, grado, numero_estudiantes) VALUES (?, ?, ?, ?);",
                (first_col_id_in_mun, myr, "Transición", mcount)
            )

        # 4. Estudiantes Buscadores (Demanda Activa a ~1 a 4.8 km)
        grados = ["Transición", "Jardín", "Primero de Primaria", "Transición", "Secundaria (6°)", "Media Técnica (10°)"]
        deltas = [
            (-0.004, 0.006), (0.008, -0.004), (-0.009, -0.007),
            (0.012, 0.009), (-0.014, 0.015), (0.003, -0.012)
        ]
        for idx in range(6):
            b_lat = round(lat + deltas[idx][0], 6)
            b_lng = round(lng + deltas[idx][1], 6)
            cursor.execute(
                "INSERT INTO Estudiantes_Buscadores (id, municipio_id, latitud, longitud, grado_interes) VALUES (?, ?, ?, ?, ?);",
                (buscador_id_counter, mun_id, b_lat, b_lng, grados[idx])
            )
            buscador_id_counter += 1

    conn.commit()

    # Volcar a schema.sql
    with open(sql_file, "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")

    conn.close()
    print(f"Base de datos poblada exitosamente: {len(DEPARTAMENTOS_DATA)} departamentos, {len(MUNICIPIOS_DATA)} municipios, {colegio_id_counter-1} colegios, {buscador_id_counter-1} buscadores.")

if __name__ == "__main__":
    generate_schema_and_seed()

