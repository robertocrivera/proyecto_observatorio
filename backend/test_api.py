import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

class TestEdudemiaAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_departamentos(self):
        res = self.client.get("/api/v1/demografia/departamentos")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 3)
        nombres = [d["nombre"] for d in data]
        self.assertIn("Cundinamarca", nombres)
        self.assertIn("Antioquia", nombres)
        self.assertIn("Valle del Cauca", nombres)

    def test_02_municipios(self):
        res = self.client.get("/api/v1/demografia/municipios?departamento_id=1")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["nombre"], "Bogotá D.C. (Fontibón)")

    def test_03_demografia_consulta(self):
        res = self.client.get("/api/v1/demografia/consulta?departamento_id=1&municipio_id=1&ambito=Urbano")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("variacion_porcentual", data)
        self.assertIn("serie_historica", data)
        self.assertGreater(len(data["serie_historica"]), 0)
        self.assertIn("total_colegios_oficiales", data)

    def test_04_geo_haversine_radio_5km(self):
        res = self.client.get("/api/v1/geo/colegios-redonda?lat=4.6732&lng=-74.1448&radio_km=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_colegios"], 0)
        self.assertGreater(data["total_estudiantes_buscando"], 0)
        self.assertIn("demanda_por_grado", data)
        # Comprobar que todos los colegios retornados están a <= 5.0 km
        for col in data["colegios"]:
            self.assertLessEqual(col["distancia_km"], 5.0)

    def test_05_lead_habeas_data_validation(self):
        # Fallar si no acepta habeas data
        invalid_lead = {
            "nombre": "Director Prueba",
            "correo_institucional": "director@prueba.edu.co",
            "tratamiento_datos_aceptado": False
        }
        res = self.client.post("/api/v1/leads/registrar", json=invalid_lead)
        self.assertEqual(res.status_code, 422)

        # Aceptar si cumple
        valid_lead = {
            "nombre": "Rectora María Gómez",
            "correo_institucional": "rectora.maria@gimnasiofontibon.edu.co",
            "tratamiento_datos_aceptado": True,
            "municipio_id": 1
        }
        res2 = self.client.post("/api/v1/leads/registrar", json=valid_lead)
        self.assertEqual(res2.status_code, 200)
        resp_json = res2.json()
        self.assertTrue(resp_json["success"])
        self.assertIn("token_descarga", resp_json)

        # Descarga con token
        token = resp_json["token_descarga"]
        res_down = self.client.get(f"/api/v1/leads/descargar-reporte?token={token}")
        self.assertEqual(res_down.status_code, 200)
        self.assertIn("EDUDEMIA COLOMBIA", res_down.json()["titulo"])

    def test_06_estrategia_comparativa_y_recomendaciones(self):
        payload = {
            "municipio_id": 1,
            "colegio_nombre": "Colegio San José",
            "sector": "No Oficial",
            "ambito": "Urbano",
            "matricula_historica": [
                {"año": 2021, "grado": "Transición", "numero_estudiantes": 60},
                {"año": 2024, "grado": "Transición", "numero_estudiantes": 38}
            ]
        }
        res = self.client.post("/api/v1/estrategia/comparar", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("recomendaciones", data)
        self.assertGreaterEqual(len(data["recomendaciones"]), 2)
        tipos = [r["tipo"] for r in data["recomendaciones"]]
        self.assertIn("ALERTA_CRITICA", tipos)
        self.assertIn("OPORTUNIDAD_MERCADO", tipos)

    def test_07_suscripcion_planes_cop(self):
        res = self.client.get("/api/v1/suscripcion/planes")
        self.assertEqual(res.status_code, 200)
        planes = res.json()
        self.assertEqual(len(planes), 3)
        ids = [p["id"] for p in planes]
        self.assertIn("mensual", ids)
        self.assertIn("trimestral", ids)
        self.assertIn("anual", ids)
        # Validar precios en COP
        precios = {p["id"]: p["precio_cop"] for p in planes}
        self.assertEqual(precios["mensual"], 189000)
        self.assertEqual(precios["trimestral"], 489000)
        self.assertEqual(precios["anual"], 1690000)

    def test_08_activar_suscripcion_simulada(self):
        payload = {
            "plan_id": "trimestral",
            "colegio_nombre": "Gimnasio Moderno Fontibón",
            "correo_directivo": "rector@gimnasio.edu.co",
            "metodo_pago": "PSE",
            "banco_o_franquicia": "Bancolombia"
        }
        res = self.client.post("/api/v1/suscripcion/activar-simulacion", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["subscription_token"].startswith("SUB-COP-"))
        self.assertEqual(data["precio_formateado"], "$489.000 COP")
        self.assertEqual(data["metodo_pago"], "PSE")

if __name__ == "__main__":
    unittest.main()

