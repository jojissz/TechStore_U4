TECHSTORE U4 - PROYECTO COMPLETADO A PARTIR DE LOS ZIP DEL MAESTRO

ESTRUCTURA
 app/            logica y API, con descuentos y operaciones nuevas
 datos/          CSV originales SIN CAMBIOS
 cargar_csv.py   cargador original colocado en la raiz correcta
 tests/          tests de escenarios E01-E15

REQUISITOS: Python 3.11+ y VS Code (opcional)

PASO 1. Abre en VS Code ESTA carpeta TechStore_U4_Completo.
PASO 2. Abre Terminal > Nueva terminal y ejecuta:
  py -m pip install -r requirements.txt
PASO 3. Comprueba la carga de los 16 pedidos:
  py cargar_csv.py
PASO 4. Ejecuta todas las pruebas:
  py -m pytest -v
PASO 5. Arranca la API:
  py -m uvicorn app.api:app --reload
PASO 6. Abre en navegador:
  http://127.0.0.1:8000/docs

EN LA API:
 GET /orders                         ver los 16 pedidos
 GET /orders/O001                    ver el pedido O001
 GET /orders/O001/discount           10% y cantidad descontada
 POST /orders/O001/confirm           confirmar pedido
 POST /orders/O001/ship               enviar (tracking_number)
 POST /orders/O001/deliver            entregar desde SHIPPED
 POST /orders/O001/return             devolver desde SHIPPED
 POST /orders/O001/cancel             cancelar desde CONFIRMED

ATENCION:
 - En Swagger /docs el tracking_number se introduce en los parametros de consulta.
 - Las operaciones van cambiando el pedido guardado en memoria.
 - Para repetir un escenario desde cero, reinicia el servidor.
 - Para entregar o devolver un pedido, primero confirmar y enviar.
 - No cambies ni muevas los archivos CSV.
 - Los tests usan pedidos nuevos y no alteran los de la API.
 - No se añade base de datos: la memoria se reinicia al apagar el servidor.
 - Los descuentos se calculan al consultarlos, sin modificar el subtotal original.
 - Ejecutar comandos desde la carpeta TechStore_U4_Completo, NO desde datos.

REGLAS DEL DOCENTE:
 10%: VIP Y total > 500 Y unidades >= 4 Y sin promocion
  5%: total > 5000 Y sin promocion
 Prioridad 10% si aplican ambas; si ninguna, 0%.
 Limite: maximo 20 unidades por pedido.
