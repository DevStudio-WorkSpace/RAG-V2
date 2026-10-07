"""
Crea 10 fotos de prueba simples para Tarea 1.
Versión optimizada: usa OpenCV para leer/redimensionar rápido, luego PIL para efectos.
"""
import os
import sys
import random
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CODIGOS = [
    'SBX-03-0001', 'SBX-03-0005', 'SBX-03-0010', 'SBX-03-0015', 'SBX-03-0020',
    'SBX-03-0025', 'SBX-03-0030', 'SBX-03-0035', 'SBX-03-0040', 'SBX-03-0008'
]

INPUT_DIR = 'data/demo_sublitex/png_publicados'
OUTPUT_DIR = 'data/demo_sublitex/fotos_prueba_tarea1'

os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_DIM = 1500

def leer_y_redimensionar(path, max_dim=MAX_DIM):
    """Lee con OpenCV (rápido, ignora DecompressionBomb) y redimensiona."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"No se pudo leer {path}")
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def crear_fondo_simple(w, h, tipo, seed):
    """Fondo simple y rápido usando gradientes numpy."""
    random.seed(seed)
    np.random.seed(seed)
    
    y_grad = np.linspace(0, 1, h).reshape(-1, 1)
    x_grad = np.linspace(0, 1, w).reshape(1, -1)
    
    if tipo == 'interior':
        # Pared con luz lateral
        base = 180 + 40 * y_grad
        luz = 30 * np.exp(-((x_grad - 0.2) / 0.4)**2)
        r = np.clip(base + luz, 120, 230)
        g = np.clip(base + luz - 5, 115, 225)
        b = np.clip(base + luz - 10, 110, 220)
    elif tipo == 'tienda':
        # Tienda neutra con focos
        base = 200 + 20 * y_grad
        r = g = b = base
        for fx, fy in [(0.2,0.15),(0.5,0.15),(0.8,0.15),(0.2,0.4),(0.5,0.4),(0.8,0.4),(0.2,0.65),(0.5,0.65),(0.8,0.65)]:
            dist2 = (x_grad - fx)**2 + (y_grad - fy)**2
            spot = 20 * np.exp(-dist2 * 50)
            r = np.clip(r + spot, 0, 255)
            g = np.clip(g + spot, 0, 255)
            b = np.clip(b + spot - 5, 0, 255)
    else:  # exterior
        # Cielo + suelo
        cielo = y_grad < 0.6
        r = np.where(cielo, 160 + 60*(1-y_grad/0.6), 60 + 40*((y_grad-0.6)/0.4))
        g = np.where(cielo, 180 + 50*(1-y_grad/0.6), 100 + 40*((y_grad-0.6)/0.4))
        b = np.where(cielo, 220 + 30*(1-y_grad/0.6), 60 + 30*((y_grad-0.6)/0.4))
    
    img = np.stack([r, g, b], axis=2).astype(np.uint8)
    return Image.fromarray(img)

def aplicar_perspectiva_simple(diseño_pil, fondo_pil, seed):
    """Perspectiva simplificada y rápida."""
    random.seed(seed)
    np.random.seed(seed)
    
    diseño = cv2.cvtColor(np.array(diseño_pil), cv2.COLOR_RGB2BGR)
    fondo = cv2.cvtColor(np.array(fondo_pil), cv2.COLOR_RGB2BGR)
    
    fw, fh = fondo_pil.size
    dh, dw = diseño.shape[:2]
    
    # Área de camiseta (40-50% del ancho)
    escala = random.uniform(0.38, 0.45)
    nuevo_w = int(fw * escala)
    if nuevo_w <= 0: nuevo_w = 1
    nuevo_h = max(1, int(dh * nuevo_w / dw))
    diseño_esc = cv2.resize(diseño, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)
    
    # Centro con variación
    cx = fw // 2 + random.randint(-fw//12, fw//12)
    cy = fh // 2 + random.randint(-fh//12, fh//12)
    
    # Perspectiva: trapezoide simulando rotación 3D
    ang_y = random.uniform(-10, 10)
    factor = 1.0 + np.sin(np.radians(abs(ang_y))) * 0.15
    
    hw, hh = nuevo_w // 2, nuevo_h // 2
    if ang_y > 0:
        # Rotado a la derecha: lado izq más cerca (más grande)
        src = np.float32([[0,0], [nuevo_w,0], [nuevo_w,nuevo_h], [0,nuevo_h]])
        dst = np.float32([
            [cx - hw*factor, cy - hh],
            [cx + hw, cy - hh],
            [cx + hw, cy + hh],
            [cx - hw*factor, cy + hh]
        ])
    else:
        # Rotado a la izquierda: lado der más cerca
        src = np.float32([[0,0], [nuevo_w,0], [nuevo_w,nuevo_h], [0,nuevo_h]])
        dst = np.float32([
            [cx - hw, cy - hh],
            [cx + hw*factor, cy - hh],
            [cx + hw*factor, cy + hh],
            [cx - hw, cy + hh]
        ])
    
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(diseño_esc, M, (fw, fh), 
                                  borderMode=cv2.BORDER_TRANSPARENT)
    
    # Máscara
    mask = np.ones((nuevo_h, nuevo_w), dtype=np.uint8) * 255
    warped_mask = cv2.warpPerspective(mask, M, (fw, fh), 
                                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    warped_mask = cv2.GaussianBlur(warped_mask, (7, 7), 0)
    
    # Sombreado simple (luz desde arriba-izquierda)
    grad_y = np.linspace(1.0, 0.7, fh).reshape(-1, 1)
    grad_x = np.linspace(1.0, 0.85, fw).reshape(1, -1)
    shade = np.clip(grad_y * grad_x, 0.6, 1.0)
    shade = np.stack([shade]*3, axis=2)
    
    warped_f = warped.astype(np.float32) * shade
    warped_f = np.clip(warped_f, 0, 255).astype(np.uint8)
    
    # Blend
    alpha = (warped_mask.astype(np.float32) / 255.0)[:, :, np.newaxis]
    resultado = fondo.astype(np.float32) * (1 - alpha) + warped_f * alpha
    resultado = np.clip(resultado, 0, 255).astype(np.uint8)
    
    return Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))

def efectos_foto_simple(img_pil, seed):
    """Efectos fotográficos rápidos."""
    random.seed(seed)
    np.random.seed(seed)
    
    img = img_pil.copy()
    w, h = img.size
    
    # Viñeteo rápido
    viñeteo = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(viñeteo)
    for i in range(0, min(w, h)//2, 4):
        alpha = int(255 * (1 - (i / (min(w, h) * 0.55)) ** 2 * 0.35))
        draw.ellipse([i, i, w-i, h-i], outline=alpha)
    viñeteo = viñeteo.filter(ImageFilter.GaussianBlur(radius=max(w,h)//15))
    img = Image.composite(img, Image.new('RGB', (w, h), (20,20,20)), viñeteo)
    
    # Ruido + JPEG
    arr = np.array(img).astype(np.float32)
    ruido = np.random.normal(0, random.uniform(3, 8), arr.shape)
    arr = np.clip(arr + ruido, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    # JPEG
    import io
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=random.randint(78, 88), subsampling=2)
    buf.seek(0)
    img = Image.open(buf).convert('RGB')
    
    # Exposición/contraste ligero
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.9, 1.1))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.95, 1.15))
    
    return img

def main():
    print(f'Creando 10 fotos de prueba en {OUTPUT_DIR}...')
    print('=' * 60)
    
    tipos_fondo = ['interior', 'tienda', 'exterior', 'interior', 'tienda', 
                   'exterior', 'interior', 'tienda', 'exterior', 'interior']
    
    for i, (codigo, tipo_fondo) in enumerate(zip(CODIGOS, tipos_fondo)):
        print(f'\n[{i+1}/10] {codigo} -> fondo: {tipo_fondo}')
        
        # Leer y redimensionar con OpenCV (evita DecompressionBomb)
        path_original = os.path.join(INPUT_DIR, f'{codigo}.png')
        diseño_arr = leer_y_redimensionar(path_original)
        diseño_pil = Image.fromarray(diseño_arr)
        print(f'  Diseño: {diseño_pil.size}')
        
        # Fondo
        fw, fh = 1600, 1067  # 3:2 ratio, resolución foto
        seed = 2000 + i * 100
        fondo = crear_fondo_simple(fw, fh, tipo_fondo, seed)
        
        # Perspectiva
        foto = aplicar_perspectiva_simple(diseño_pil, fondo, seed)
        
        # Efectos foto
        foto = efectos_foto_simple(foto, seed + 50)
        
        # Guardar
        output_path = os.path.join(OUTPUT_DIR, f'{codigo}_foto_prueba.jpg')
        foto.save(output_path, 'JPEG', quality=85, subsampling=2)
        size_kb = os.path.getsize(output_path) // 1024
        print(f'  Guardado: {output_path} ({size_kb} KB)')
    
    print('\n' + '=' * 60)
    print('¡10 fotos de prueba creadas!')
    print(f'Carpeta: {OUTPUT_DIR}')

if __name__ == '__main__':
    main()