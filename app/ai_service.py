"""
Servicio de pronósticos con Google Gemini 2.5 Flash.
Genera 3 pronósticos por cada reporte/gráfica.
"""
import os
import re
from dotenv import load_dotenv

load_dotenv()


def _get_client():
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key or api_key == 'tu_api_key_aqui':
        return None, None
    from google import genai
    client = genai.Client(api_key=api_key)
    return client, 'gemini-2.5-flash'


def _parse_forecasts(text):
    """Extrae exactamente 3 pronósticos de una respuesta numerada."""
    items = re.findall(
        r'(?:^|\n)\s*[1-3][\.\)]\s*\*{0,2}(.+?)(?=\n\s*[2-3][\.\)]|\Z)',
        text, re.DOTALL
    )
    result = [re.sub(r'\*+', '', i).strip().replace('\n', ' ') for i in items[:3]]
    if len(result) < 3:
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.strip().isdigit()]
        result = lines[:3]
    while len(result) < 3:
        result.append("Sin datos suficientes para este pronóstico.")
    return result[:3]


def pronostico_ventas(datos_meses):
    """
    Genera 3 pronósticos de ventas basados en el historial mensual.
    datos_meses: lista de dicts con 'periodo', 'ordenes', 'ventas'
    """
    client, model = _get_client()
    if not client:
        return _sin_api()

    resumen = "\n".join(
        f"- {d['periodo']}: {d['ordenes']} órdenes, Bs. {d['ventas']:.2f} en ventas"
        for d in datos_meses
    )

    prompt = f"""Eres un analista financiero para TechStore, una tienda de accesorios de
computadoras en Bolivia. Analiza este historial de ventas mensuales:

{resumen}

Genera EXACTAMENTE 3 pronósticos concretos y específicos para los próximos meses.
Cada pronóstico debe ser accionable y mencionar cifras o porcentajes estimados.
Responde SOLO con la lista numerada del 1 al 3, en español, sin introducción ni conclusión.
Máximo 2 líneas por pronóstico."""

    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return _parse_forecasts(response.text)
    except Exception as e:
        return [f"Error de conexión con Gemini: {str(e)[:80]}",
                "Verifica tu API key en el archivo .env",
                "Obtén tu key gratis en aistudio.google.com"]


def pronostico_productos(datos_productos):
    """
    Genera 3 pronósticos de inventario basados en los productos más vendidos.
    datos_productos: lista de dicts con 'producto', 'cantidad', 'ingreso'
    """
    client, model = _get_client()
    if not client:
        return _sin_api()

    resumen = "\n".join(
        f"- {d['producto']}: {d['cantidad']} unidades vendidas, Bs. {d['ingreso']:.2f} de ingreso"
        for d in datos_productos[:10]
    )

    prompt = f"""Eres un analista de inventarios para TechStore, una tienda de accesorios
de computadoras en Bolivia. Estos son los productos más vendidos:

{resumen}

Genera EXACTAMENTE 3 pronósticos o recomendaciones de inventario concretas.
Menciona productos específicos de la lista y sugiere acciones con cantidades o porcentajes.
Responde SOLO con la lista numerada del 1 al 3, en español, sin introducción ni conclusión.
Máximo 2 líneas por pronóstico."""

    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return _parse_forecasts(response.text)
    except Exception as e:
        return [f"Error de conexión con Gemini: {str(e)[:80]}",
                "Verifica tu API key en el archivo .env",
                "Obtén tu key gratis en aistudio.google.com"]


def pronostico_servicios(datos_estados):
    """
    Genera 3 pronósticos operacionales basados en la distribución de servicios.
    datos_estados: lista de dicts con 'estado', 'cantidad', 'costo'
    """
    client, model = _get_client()
    if not client:
        return _sin_api()

    resumen = "\n".join(
        f"- {d['estado']}: {d['cantidad']} servicios, Bs. {d['costo']:.2f} facturado"
        for d in datos_estados
    )
    total = sum(d['cantidad'] for d in datos_estados)

    prompt = f"""Eres un analista operacional para TechStore, un servicio técnico de
computadoras en Bolivia. Esta es la distribución actual de {total} servicios técnicos:

{resumen}

Genera EXACTAMENTE 3 pronósticos operacionales concretos sobre tiempos de entrega,
carga de trabajo o ingresos esperados. Menciona porcentajes o días estimados.
Responde SOLO con la lista numerada del 1 al 3, en español, sin introducción ni conclusión.
Máximo 2 líneas por pronóstico."""

    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return _parse_forecasts(response.text)
    except Exception as e:
        return [f"Error de conexión con Gemini: {str(e)[:80]}",
                "Verifica tu API key en el archivo .env",
                "Obtén tu key gratis en aistudio.google.com"]


def _sin_api():
    return [
        "Configura tu API key de Gemini para ver pronósticos con IA.",
        "Crea el archivo .env con: GEMINI_API_KEY=tu_key",
        "Obtén tu key gratuita en: aistudio.google.com/apikey",
    ]
