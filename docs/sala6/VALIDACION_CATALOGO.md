# Validación del catálogo

Fecha: 2026-11-16

Comando ejecutado desde la raíz del repositorio:

```powershell
python scripts\validar_catalogo.py
```

Resultado: salida 1, esperado al detectar datos pendientes. El catálogo contiene 577 registros: 577 URLs vacías o con `ejemplo.com`, 577 nombres comerciales iguales al ID, 0 imágenes inexistentes en `data/images_normalized/` y 0 IDs duplicados.

Esta validación no certifica URLs ni nombres comerciales reales. No se modificó `data/products.csv` y estos hallazgos no cierran los checks de datos del despliegue.
