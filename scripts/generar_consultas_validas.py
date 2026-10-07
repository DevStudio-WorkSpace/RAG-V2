"""
Genera 10 consultas válidas para prueba de Tarea 1.
Las consultas son transformaciones de los PNGs indexados (NO las mismas imágenes).
Según DECISIONES.md P4: las consultas NUNCA pueden salir del catálogo.
Pero para validar el motor, usamos transformaciones controladas que simulan
fotos reales: recorte, cambio de color, rotación, mockup, etc.
"""
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 10 códigos de prueba (los mismos que en probar_10_disenos.py)
CODIGOS_PRUEBA = [
    'SBX-03-0001', 'SBX-03-0005', 'SBX-03-0010', 'SBX-03-0015',
    'SBX-03-0020', 'SBX-03-0025', 'SBX-03-0030', 'SBX-03-0035',
    'SBX-03-0040', 'SBX-03-0008'
]

INPUT_DIR = 'data/demo_sublitex/png_publicados'
OUTPUT_DIR = 'data/demo_sublitex/consultas_validas'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def aplicar_transformacion(imagen, tipo):
    """Aplica una transformación que simula una foto real distinta del original."""
    img = imagen.copy()
    
    if tipo == 'recorte_central':
        # Recorte central al 60% (simula foto tomada de cerca)
        w, h = img.size
        new_w, new_h = int(w * 0.6), int(h * 0.6)
        left = (w - new_w) // 2
        top = (h - new_h) // 2
        img = img.crop((left, top, left + new_w, top + new_h))
        
    elif tipo == 'recoloreado':
        # Cambio de matiz + saturación + brillo (simula distinta iluminación)
        # Convertir a HSV para rotar matiz
        img = img.convert('HSV')
        h, s, v = img.split()
        # Rotar matiz 60 grados (60/360 = 1/6 del rango 0-255 ≈ 42)
        h = h.point(lambda x: (x + 42) % 256)
        # Aumentar saturación 1.3x
        s = s.point(lambda x: min(255, int(x * 1.3)))
        # Ajustar brillo 1.1x
        v = v.point(lambda x: min(255, int(x * 1.1)))
        img = Image.merge('HSV', (h, s, v)).convert('RGB')
        
    elif tipo == 'rotacion_ligera':
        # Rotación ±5 grados (simula foto torcida)
        angulo = random.uniform(-5, 5)
        img = img.rotate(angulo, expand=True, fillcolor='white')
        
    elif tipo == 'ruido_gaussiano':
        # Ruido gaussiano ligero (simula foto con grano)
        import numpy as np
        arr = np.array(img).astype(float)
        noise = np.random.normal(0, 10, arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype('uint8')
        img = Image.fromarray(arr)
        
    elif tipo == 'desenfoque_ligero':
        # Desenfoque gaussiano ligero (simula foto movida)
        img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
        
    elif tipo == 'mockup_persona':
        # Simular mockup: añadir fondo degradado y "persona" simple
        # Crear imagen más grande con fondo
        w, h = img.size
        new_w, new_h = int(w * 1.5), int(h * 1.8)
        fondo = Image.new('RGB', (new_w, new_h), 'white')
        # Degradado simple
        for y in range(new_h):
            color = int(200 + 55 * y / new_h)
            for x in range(new_w):
                fondo.putpixel((x, y), (color, color, color))
        # Pegar la camiseta en el centro
        pos_x = (new_w - w) // 2
        pos_y = int(new_h * 0.15)
        fondo.paste(img, (pos_x, pos_y))
        img = fondo
        
    elif tipo == 'cambio_perspectiva':
        # Transformación de perspectiva ligera
        w, h = img.size
        # Coeficientes para transformar (simular ángulo)
        coeffs = (
            1.0, 0.0, 0.0,
            0.0, 1.05, 0.0,
            0.0, 0.0
        )
        img = img.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
        
    elif tipo == 'recorte_asimetrico':
        # Recorte no centrado (simula encuadre imperfecto)
        w, h = img.size
        new_w, new_h = int(w * 0.7), int(h * 0.7)
        left = random.randint(0, w - new_w)
        top = random.randint(0, h - new_h)
        img = img.crop((left, top, left + new_w, top + new_h))
        
    elif tipo == 'brillo_contraste':
        # Cambio de brillo y contraste
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(random.uniform(0.7, 1.3))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(random.uniform(0.8, 1.2))
        
    elif tipo == 'compresion_jpeg':
        # Simular compresión JPEG con artefactos
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=random.randint(60, 80))
        buffer.seek(0)
        img = Image.open(buffer).convert('RGB')
    
    return img

# Tipos de transformación para cada código (variados)
TRANSFORMACIONES = [
    'recorte_central',      # SBX-03-0001
    'recoloreado',          # SBX-03-0005
    'rotacion_ligera',      # SBX-03-0010
    'ruido_gaussiano',      # SBX-03-0015
    'desenfoque_ligero',    # SBX-03-0020
    'mockup_persona',       # SBX-03-0025
    'cambio_perspectiva',   # SBX-03-0030
    'recorte_asimetrico',   # SBX-03-0035
    'brillo_contraste',     # SBX-03-0040
    'compresion_jpeg',      # SBX-03-0008
]

print(f'Generando {len(CODIGOS_PRUEBA)} consultas válidas en {OUTPUT_DIR}...')

for codigo, transformacion in zip(CODIGOS_PRUEBA, TRANSFORMACIONES):
    input_path = os.path.join(INPUT_DIR, f'{codigo}.png')
    output_path = os.path.join(OUTPUT_DIR, f'{codigo}_{transformacion}.png')
    
    img = Image.open(input_path).convert('RGB')
    img_transformada = aplicar_transformacion(img, transformacion)
    img_transformada.save(output_path, 'PNG')
    print(f'  {codigo} -> {transformacion} -> {os.path.basename(output_path)}')

print('\n¡Consultas válidas generadas!')
print('NOTA: Estas son transformaciones controladas de las imágenes indexadas.')
print('Para evaluación real (DECISIONES.md P4), se requieren fotos EXTERNAS al catálogo.')