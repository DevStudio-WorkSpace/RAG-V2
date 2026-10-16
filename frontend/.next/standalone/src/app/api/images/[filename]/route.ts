import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const resolvedParams = await params;
    
    // Handle URL decoding and basename safety
    const rawFilename = resolvedParams.filename;
    const decodedFilename = decodeURIComponent(rawFilename).trim();
    const filename = path.basename(decodedFilename);

    if (!filename) {
      return new NextResponse('Filename is required', { status: 400 });
    }

    // Candidate directories to search for real catalog images
    const candidateDirs = [
      path.join(process.cwd(), '..', 'data', 'imagenes_normalized'),
      path.join(process.cwd(), '..', 'data', 'demo_sublitex', 'png_publicados'),
      path.join(process.cwd(), '..', 'data', 'demo_sublitex', 'fotos_prueba_tarea1'),
      path.join(process.cwd(), '..', 'data'),
      path.join(process.cwd(), '..', 'evaluation', 'test_images'),
      path.join(process.cwd(), '..', 'evaluation', 'consultas_hito2'),
      path.join(process.cwd(), 'public', 'images'),
      path.join(process.cwd(), 'public'),
      path.join(process.cwd(), 'src', 'assets', 'images'),
      path.join(process.cwd(), 'data', 'imagenes_normalized'),
    ];

    let foundPath: string | null = null;
    const lowerFilename = filename.toLowerCase();
    const parsed = path.parse(filename);
    const lowerBaseWithoutExt = parsed.name.toLowerCase();

    for (const dir of candidateDirs) {
      if (!fs.existsSync(/*turbopackIgnore: true*/ dir)) continue;

      // 1. Exact match
      const candidatePath = path.join(dir, filename);
      if (fs.existsSync(/*turbopackIgnore: true*/ candidatePath)) {
        foundPath = candidatePath;
        break;
      }

      // 2. Fallbacks with common extensions
      for (const ext of ['.jpg', '.png', '.jpeg', '.webp']) {
        const extPath = path.join(dir, `${parsed.name}${ext}`);
        if (fs.existsSync(/*turbopackIgnore: true*/ extPath)) {
          foundPath = extPath;
          break;
        }
      }
      if (foundPath) break;

      // 3. Robust case, accent, and separator-insensitive directory search
      try {
        const files = fs.readdirSync(/*turbopackIgnore: true*/ dir);
        const cleanQuery = lowerFilename
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .replace(/[^a-z0-9]/g, '');

        const cleanBaseQuery = lowerBaseWithoutExt
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .replace(/[^a-z0-9]/g, '');

        const match = files.find((f) => {
          const fLower = f.toLowerCase();
          if (fLower === lowerFilename) return true;

          const fParsed = path.parse(f);
          if (fParsed.name.toLowerCase() === lowerBaseWithoutExt) return true;

          const cleanF = fLower
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]/g, '');

          const cleanFBase = fParsed.name
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]/g, '');

          return (
            cleanF === cleanQuery ||
            cleanFBase === cleanBaseQuery ||
            (cleanQuery.length > 5 && cleanF.includes(cleanQuery)) ||
            (cleanBaseQuery.length > 5 && cleanFBase.includes(cleanBaseQuery))
          );
        });

        if (match) {
          foundPath = path.join(dir, match);
          break;
        }
      } catch {
        // ignore directory read errors
      }
    }

    if (!foundPath) {
      return new NextResponse('Image not found', { status: 404 });
    }

    let contentType = 'image/jpeg';
    const lowerName = foundPath.toLowerCase();
    if (lowerName.endsWith('.png')) contentType = 'image/png';
    else if (lowerName.endsWith('.webp')) contentType = 'image/webp';
    else if (lowerName.endsWith('.gif')) contentType = 'image/gif';
    else if (lowerName.endsWith('.svg')) contentType = 'image/svg+xml';

    const stat = fs.statSync(/*turbopackIgnore: true*/ foundPath);
    const fileStream = fs.createReadStream(/*turbopackIgnore: true*/ foundPath);
    
    const webStream = new ReadableStream({
      start(controller) {
        fileStream.on('data', (chunk: Buffer | string) => controller.enqueue(typeof chunk === 'string' ? Buffer.from(chunk) : chunk));
        fileStream.on('end', () => controller.close());
        fileStream.on('error', (err) => controller.error(err));
      },
      cancel() {
        fileStream.destroy();
      },
    });

    return new NextResponse(webStream, {
      headers: {
        'Content-Type': contentType,
        'Content-Length': stat.size.toString(),
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  } catch (error) {
    console.error('Error serving image:', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
