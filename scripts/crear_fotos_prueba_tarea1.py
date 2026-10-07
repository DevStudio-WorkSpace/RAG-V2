"""
Crea 10 fotos de prueba para Tarea 1 con apariencia fotográfica real.
Cada foto simula una fotografía tomada con cámara de una camiseta con el diseño.
NO son simples transformaciones artificiales; incluyen:
- Perspectiva 3D (camiseta en persona/maniquí)
- Iluminación direccional con sombras
- Fondo ambiental (habitación, tienda, exterior)
- Pliegues y textura de tela
- Encuadre natural (no centrado perfecto)
- Ruido de sensor y compresión JPEG realista
"""
import os
import sys
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CODIGOS = [
    'SBX-03-0001', 'SBX-03-0005', 'SBX-03-0010', 'SBX-03-0015', 'SBX-03-0020',
    'SBX-03-0025', 'SBX-03-0030', 'SBX-03-0035', 'SBX-03-0040', 'SBX-03-0008'
]

INPUT_DIR = 'data/demo_sublitex/png_publicados'
OUTPUT_DIR = 'data/demo_sublitex/fotos_prueba_tarea1'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fondos ambientales simulados (gradientes suaves tipo habitación/tienda)
def crear_fondo_ambiental(w, h, tipo='interior'):
    """Crea un fondo con apariencia de entorno real."""
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    
    if tipo == 'interior':
        # Pared interior con luz de ventana
        for y in range(h):
            # Gradiente vertical suave + variación horizontal (ventana)
            base = int(180 + 40 * (y / h))
            variacion = int(30 * np.sin(2 * np.pi * y / h) * np.cos(2 * np.pi * 0.3))
            color = max(120, min(230, base + variacion))
            for x in range(w):
                # Luz lateral simulando ventana
                luz_lateral = int(25 * np.exp(-((x - w*0.2)/ (w*0.4))**2))
                c = min(255, color + luz_lateral)
                draw.point((x, y), fill=(c, c-5, c-10))
    
    elif tipo == 'tienda':
        # Fondo de tienda: más neutro, luces de techo
        for y in range(h):
            base = int(200 + 20 * (y / h))
            for x in range(w):
                # Puntos de luz simulando focos
                luz = 0
                for fx in [0.2, 0.5, 0.8]:
                    for fy in [0.15, 0.4, 0.65]:
                        dist = np.sqrt(((x/w - fx)**2 + (y/h - fy)**2) * 2)
                        luz += int(15 * np.exp(-dist * 8))
                c = min(255, base + luz)
                draw.point((x, y), fill=(c, c, c-5))
    
    elif tipo == 'exterior':
        # Exterior: cielo + suelo
        for y in range(h):
            if y < h * 0.6:
                # Cielo
                base = int(180 + 60 * (1 - y / (h*0.6)))
                for x in range(w):
                    draw.point((x, y), fill=(base-20, base-10, base))
            else:
                # Suelo/césped
                base = int(80 + 40 * ((y - h*0.6) / (h*0.4)))
                for x in range(w):
                    draw.point((x, y), fill=(base-30, base, base-30))
    
    return img

def crear_malla_pliegues(w, h, densidad=0.02):
    """Genera mapa de pliegues realista para deformar la camiseta."""
    # Ruido Perlin simplificado usando múltiples octavas de ruido
    malla = np.zeros((h, w), dtype=np.float32)
    for octava, (freq, amp) in enumerate([(0.01, 1.0), (0.03, 0.5), (0.08, 0.25), (0.2, 0.1)]):
        noise = np.random.normal(0, 1, (int(h*freq)+1, int(w*freq)+1)).astype(np.float32)
        noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
        malla += noise * amp
    # Normalizar
    malla = (malla - malla.min()) / (malla.max() - malla.min() + 1e-8)
    return malla

def aplicar_perspectiva_camiseta(img_diseño, fondo, seed=None):
    """Aplica el diseño sobre una camiseta en perspectiva 3D simulada."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    fw, fh = fondo.size
    dw, dh = img_diseño.size
    
    # Escalar diseño para que quepa en área de camiseta (aprox 40-50% del ancho)
    escala = random.uniform(0.35, 0.48)
    nuevo_w = int(fw * escala)
    nuevo_h = int(dh * nuevo_w / dw)
    diseño_escalado = img_diseño.resize((nuevo_w, nuevo_h), Image.LANCZOS)
    
    # Posición de la camiseta en el fondo (centrado con variación)
    cx = fw // 2 + random.randint(-fw//10, fw//10)
    cy = fh // 2 + random.randint(-fh//10, fh//10)
    
    # Coordenadas del rectángulo de la camiseta en perspectiva
    # Simulamos una camiseta vista de frente con ligera rotación 3D
    angulo_y = random.uniform(-12, 12)  # rotación horizontal
    angulo_x = random.uniform(-5, 5)    # rotación vertical
    
    # Puntos base del rectángulo
    hw, hh = nuevo_w // 2, nuevo_h // 2
    pts = np.array([
        [-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]
    ], dtype=np.float32)
    
    # Rotación 3D simplificada (proyección)
    rad_y = np.radians(angulo_y)
    rad_x = np.radians(angulo_x)
    
    # Matriz de rotación Y (horizontal)
    cos_y, sin_y = np.cos(rad_y), np.sin(rad_y)
    pts_rot = pts.copy()
    pts_rot[:, 0] = pts[:, 0] * cos_y  # X se acorta
    # Profundidad simulada para perspectiva
    profundidad = pts[:, 0] * sin_y * 0.3
    
    # Rotación X (vertical)
    cos_x, sin_x = np.cos(rad_x), np.sin(rad_x)
    pts_rot[:, 1] = pts_rot[:, 1] * cos_x + profundidad * sin_x
    
    # Perspectiva: objetos más lejos se ven más pequeños
    factor_persp = 1.0 / (1.0 + profundidad * 0.001)
    pts_rot[:, 0] *= factor_persp
    pts_rot[:, 1] *= factor_persp
    
    # Trasladar al centro
    pts_rot[:, 0] += cx
    pts_rot[:, 1] += cy
    
    # Añadir deformación por pliegues
    malla_pliegues = crear_malla_pliegues(nuevo_w, nuevo_h)
    for i, (x, y) in enumerate(pts_rot):
        # Muestrear pliegues en las esquinas
        u = int((i % 2) * (nuevo_w - 1))
        v = int((i // 2) * (nuevo_h - 1))
        desplazamiento = (malla_pliegues[v, u] - 0.5) * 8
        if i in [0, 3]:  # lado izquierdo
            pts_rot[i, 0] += desplazamiento
        else:  # lado derecho
            pts_rot[i, 0] -= desplazamiento
    
    # Crear imagen con el diseño deformado
    resultado = fondo.copy()
    
    # Usar transformada de perspectiva de OpenCV
    diseño_cv = cv2.cvtColor(np.array(diseño_escalado), cv2.COLOR_RGB2BGR)
    h_d, w_d = diseño_cv.shape[:2]
    
    src_pts = np.array([[0, 0], [w_d, 0], [w_d, h_d], [0, h_d]], dtype=np.float32)
    dst_pts = pts_rot.astype(np.float32)
    
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(diseño_cv, M, (fw, fh), 
                                  borderMode=cv2.BORDER_TRANSPARENT)
    
    # Máscara para blend
    mask = np.ones((h_d, w_d), dtype=np.uint8) * 255
    warped_mask = cv2.warpPerspective(mask, M, (fw, fh), 
                                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    
    # Aplicar iluminación direccional (sombras por pliegues)
    # Crear mapa de sombreado basado en pliegues
    malla_grande = cv2.resize(malla_pliegues, (fw, fh), interpolation=cv2.INTER_CUBIC)
    # Luz direccional (desde arriba-izquierda)
    grad_x = cv2.Sobel(malla_grande, cv2.CV_32F, 1, 0, ksize=5)
    grad_y = cv2.Sobel(malla_grande, cv2.CV_32F, 0, 1, ksize=5)
    # Dirección de luz
    luz_x, luz_y = -0.5, -0.7
    intensidad = 1.0 + (grad_x * luz_x + grad_y * luz_y) * 0.3
    intensidad = np.clip(intensidad, 0.5, 1.3)
    
    # Aplicar sombreado al warped
    warped_float = warped.astype(np.float32)
    for c in range(3):
        warped_float[:, :, c] *= intensidad
    warped_shaded = np.clip(warped_float, 0, 255).astype(np.uint8)
    
    # Blend con fondo
    fondo_cv = cv2.cvtColor(np.array(fondo), cv2.COLOR_RGB2BGR)
    alpha = warped_mask.astype(np.float32) / 255.0
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)  # Suavizar bordes
    alpha = np.stack([alpha]*3, axis=2)
    
    composicion = fondo_cv * (1 - alpha) + warped_shaded * alpha
    composicion = np.clip(composicion, 0, 255).astype(np.uint8)
    
    return Image.fromarray(cv2.cvtColor(composicion, cv2.COLOR_BGR2RGB))

def agregar_efectos_fotograficos(img, seed=None):
    """Agrega efectos de cámara real: viñeteo, ruido, aberración cromática, compresión."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    img = img.copy()
    w, h = img.size
    
    # 1. Viñeteo (oscurecimiento en esquinas)
    viñeteo = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(viñeteo)
    for i in range(min(w, h) // 2):
        alpha = int(255 * (1 - (i / (min(w, h) * 0.6)) ** 2 * 0.4))
        draw.ellipse([i, i, w-i, h-i], outline=alpha)
    viñeteo = viñeteo.filter(ImageFilter.GaussianBlur(radius=min(w,h)//20))
    img = Image.composite(img, Image.new('RGB', (w, h), (0,0,0)), viñeteo)
    
    # 2. Ruido de sensor (ISO simulado)
    arr = np.array(img).astype(np.float32)
    iso = random.uniform(200, 800)
    ruido_std = iso / 1000.0 * 15
    ruido = np.random.normal(0, ruido_std, arr.shape)
    arr = np.clip(arr + ruido, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    # 3. Aberración cromática ligera (desplazamiento RGB en bordes)
    if random.random() < 0.7:
        r, g, b = img.split()
        offset = random.randint(1, 3)
        r = ImageOps.expand(r, border=(offset, 0, -offset, 0), fill=0)
        b = ImageOps.expand(b, border=(-offset, 0, offset, 0), fill=0)
        r = r.crop((0, 0, w, h))
        g = g.crop((0, 0, w, h))
        b = b.crop((0, 0, w, h))
        img = Image.merge('RGB', (r, g, b))
    
    # 4. Desenfoque de movimiento ligero (mano temblorosa)
    if random.random() < 0.3:
        angulo = random.uniform(-2, 2)
        img = img.rotate(angulo, expand=False, fillcolor=(128,128,128))
        img = img.rotate(-angulo, expand=False, fillcolor=(128,128,128))
    
    # 5. Ajuste de exposición/contraste (medición de cámara)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.85, 1.15))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.9, 1.2))
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(random.uniform(0.85, 1.15))
    
    # 6. Compresión JPEG realista (calidad 75-90)
    import io
    buffer = io.BytesIO()
    calidad = random.randint(75, 90)
    img.save(buffer, format='JPEG', quality=calidad, subsampling=2)
    buffer.seek(0)
    img = Image.open(buffer).convert('RGB')
    
    return img

def main():
    print(f'Creando 10 fotos de prueba en {OUTPUT_DIR}...')
    print('=' * 60)
    
    tipos_fondo = ['interior', 'tienda', 'exterior', 'interior', 'tienda', 
                   'exterior', 'interior', 'tienda', 'exterior', 'interior']
    
    MAX_DIM = 2000  # Limitar dimensión máxima para evitar DecompressionBomb y lentitud
    
    for i, (codigo, tipo_fondo) in enumerate(zip(CODIGOS, tipos_fondo)):
        print(f'\n[{i+1}/10] {codigo} -> fondo: {tipo_fondo}')
        
        # Cargar PNG original (plantilla)
        path_original = os.path.join(INPUT_DIR, f'{codigo}.png')
        diseño = Image.open(path_original).convert('RGB')
        
        # Redimensionar si es muy grande (SBX-03-0030 tiene 13231x8861)
        if max(diseño.size) > MAX_DIM:
            diseño.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
            print(f'  Redimensionado a: {diseño.size}')
        
        # Crear fondo ambiental
        fw, fh = 1920, 1280  # Resolución foto realista
        fondo = crear_fondo_ambiental(fw, fh, tipo_fondo)
        
        # Aplicar diseño en perspectiva sobre camiseta
        seed = 1000 + i * 100  # Seed determinístico por diseño
        foto = aplicar_perspectiva_camiseta(diseño, fondo, seed=seed)
        
        # Agregar efectos fotográficos
        foto = agregar_efectos_fotograficos(foto, seed=seed + 50)
        
        # Guardar
        output_path = os.path.join(OUTPUT_DIR, f'{codigo}_foto_prueba.jpg')
        foto.save(output_path, 'JPEG', quality=85, subsampling=2)
        print(f'  Guardado: {output_path} ({os.path.getsize(output_path)} bytes)')
    
    print('\n' + '=' * 60)
    print('¡10 fotos de prueba creadas exitosamente!')
    print(f'Carpeta: {OUTPUT_DIR}')
    print('\nNOTA: Son simulaciones fotográficas programáticas.')
    print('Para evaluación real se requieren fotos físicas de camisetas impresas.')

if __name__ == '__main__':
    main()