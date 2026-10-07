"""
Regenera solo las 3 fotos que fallaron (SBX-03-0010, SBX-03-0025, SBX-03-0040).
"""
import os
import sys
import random
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CODIGOS_FALLIDOS = ['SBX-03-0010', 'SBX-03-0025', 'SBX-03-0040']
TIPOS_FONDO = ['exterior', 'exterior', 'exterior']

INPUT_DIR = 'data/demo_sublitex/png_publicados'
OUTPUT_DIR = 'data/demo_sublitex/fotos_prueba_tarea1'

MAX_DIM = 1500

def leer_y_redimensionar(path, max_dim=MAX_DIM):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"No se pudo leer {path}")
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def crear_fondo_exterior(w, h, seed):
    random.seed(seed)
    np.random.seed(seed)
    y_grad = np.linspace(0, 1, h).reshape(-1, 1)
    x_grad = np.linspace(0, 1, w).reshape(1, -1)
    cielo = y_grad < 0.6
    r = np.where(cielo, 160 + 60*(1-y_grad/0.6), 60 + 40*((y_grad-0.6)/0.4))
    g = np.where(cielo, 180 + 50*(1-y_grad/0.6), 100 + 40*((y_grad-0.6)/0.4))
    b = np.where(cielo, 220 + 30*(1-y_grad/0.6), 60 + 30*((y_grad-0.6)/0.4))
    # Nubes sutiles
    noise = np.random.normal(0, 1, (h//4, w//4))
    noise = cv2.resize(noise.astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    nubes = np.clip(noise * 15, -30, 30)
    r = np.clip(r + nubes, 0, 255)
    g = np.clip(g + nubes, 0, 255)
    b = np.clip(b + nubes, 0, 255)
    img = np.stack([r, g, b], axis=2).astype(np.uint8)
    return Image.fromarray(img)

def aplicar_perspectiva_robusta(diseño_pil, fondo_pil, seed):
    random.seed(seed)
    np.random.seed(seed)
    
    diseño = cv2.cvtColor(np.array(diseño_pil), cv2.COLOR_RGB2BGR)
    fondo = cv2.cvtColor(np.array(fondo_pil), cv2.COLOR_RGB2BGR)
    
    fw, fh = fondo_pil.size
    dh, dw = diseño.shape[:2]
    
    # Escala conservadora
    escala = random.uniform(0.35, 0.42)
    nuevo_w = int(fw * escala)
    if nuevo_w <= 1: nuevo_w = 1
    nuevo_h = max(1, int(dh * nuevo_w / dw))
    diseño_esc = cv2.resize(diseño, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)
    
    # Centro
    cx = fw // 2 + random.randint(-fw//15, fw//15)
    cy = fh // 2 + random.randint(-fh//15, fh//15)
    
    # Perspectiva trapezoidal simple
    ang_y = random.uniform(-8, 8)
    factor = 1.0 + abs(np.sin(np.radians(ang_y))) * 0.12
    
    hw, hh = nuevo_w // 2, nuevo_h // 2
    if ang_y >= 0:
        src = np.float32([[0,0], [nuevo_w,0], [nuevo_w,nuevo_h], [0,nuevo_h]])
        dst = np.float32([
            [cx - hw*factor, cy - hh],
            [cx + hw, cy - hh],
            [cx + hw, cy + hh],
            [cx - hw*factor, cy + hh]
        ])
    else:
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
    
    # Máscara con feather
    mask = np.ones((nuevo_h, nuevo_w), dtype=np.uint8) * 255
    warped_mask = cv2.warpPerspective(mask, M, (fw, fh), 
                                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    warped_mask = cv2.GaussianBlur(warped_mask, (9, 9), 0)
    
    # Sombreado
    grad_y = np.linspace(1.0, 0.75, fh).reshape(-1, 1)
    grad_x = np.linspace(1.0, 0.9, fw).reshape(1, -1)
    shade = np.clip(grad_y * grad_x, 0.65, 1.0)
    shade = np.stack([shade]*3, axis=2)
    
    warped_f = warped.astype(np.float32) * shade
    warped_f = np.clip(warped_f, 0, 255).astype(np.uint8)
    
    # Blend
    alpha = (warped_mask.astype(np.float32) / 255.0)[:, :, np.newaxis]
    resultado = fondo.astype(np.float32) * (1 - alpha) + warped_f * alpha
    resultado = np.clip(resultado, 0, 255).astype(np.uint8)
    
    return Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))

def efectos_foto(img_pil, seed):
    random.seed(seed)
    np.random.seed(seed)
    
    img = img_pil.copy()
    w, h = img.size
    
    # Viñeteo
    viñeteo = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(viñeteo)
    for i in range(0, min(w, h)//2, 4):
        alpha = int(255 * (1 - (i / (min(w, h) * 0.5)) ** 2 * 0.3))
        draw.ellipse([i, i, w-i, h-i], outline=alpha)
    viñeteo = viñeteo.filter(ImageFilter.GaussianBlur(radius=max(w,h)//12))
    img = Image.composite(img, Image.new('RGB', (w, h), (25,25,25)), viñeteo)
    
    # Ruido
    arr = np.array(img).astype(np.float32)
    ruido = np.random.normal(0, random.uniform(4, 10), arr.shape)
    arr = np.clip(arr + ruido, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    # JPEG
    import io
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=random.randint(80, 90), subsampling=2)
    buf.seek(0)
    img = Image.open(buf).convert('RGB')
    
    # Exposición/contraste
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.92, 1.08))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.98, 1.12))
    
    return img

def main():
    print('Regenerando 3 fotos fallidas...')
    print('=' * 60)
    
    for i, codigo in enumerate(CODIGOS_FALLIDOS):
        tipo_fondo = TIPOS_FONDO[i]
        print(f'\n[{i+1}/3] {codigo} -> fondo: {tipo_fondo}')
        
        path_original = os.path.join(INPUT_DIR, f'{codigo}.png')
        diseño_arr = leer_y_redimensionar(path_original)
        diseño_pil = Image.fromarray(diseño_arr)
        print(f'  Diseño: {diseño_pil.size}')
        
        fw, fh = 1600, 1067
        seed = 3000 + i * 100
        fondo = crear_fondo_exterior(fw, fh, seed)
        
        foto = aplicar_perspectiva_robusta(diseño_pil, fondo, seed)
        
        # Verificar que la foto no esté vacía
        arr_check = np.array(foto)
        if arr_check.std() < 5:
            print(f'  ADVERTENCIA: imagen casi vacía, reintentando con seed diferente')
            seed += 999
            fondo = crear_fondo_exterior(fw, fh, seed)
            foto = aplicar_perspectiva_robusta(diseño_pil, fondo, seed)
        
        foto = efectos_foto(foto, seed + 50)
        
        output_path = os.path.join(OUTPUT_DIR, f'{codigo}_foto_prueba.jpg')
        foto.save(output_path, 'JPEG', quality=85, subsampling=2)
        size_kb = os.path.getsize(output_path) // 1024
        print(f'  Guardado: {output_path} ({size_kb} KB)')
    
    print('\n' + '=' * 60)
    print('¡3 fotos regeneradas!')

if __name__ == '__main__':
    main()