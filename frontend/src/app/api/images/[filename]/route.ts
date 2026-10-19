import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const resolvedParams = await params;
    
    // Path traversal safety
    const rawFilename = resolvedParams.filename;
    const filename = path.basename(rawFilename);

    if (!filename) {
      return new NextResponse('Filename is required', { status: 400 });
    }

    // Allowlist de extensiones: NO servir archivos arbitrarios de data/
    const EXT_PERMITIDAS = /\.(jpe?g|png|webp|gif|svg)$/i;
    if (!EXT_PERMITIDAS.test(filename)) {
      return new NextResponse('Extensión no permitida', { status: 403 });
    }

    // Candidate directories to look for images
    const candidateDirs = [
      path.join(process.cwd(), 'public', 'images'),
      path.join(process.cwd(), 'public'),
      path.join(process.cwd(), 'src', 'assets', 'images'),
      path.join(process.cwd(), '..', 'data', 'images_normalized'),
    ];

    let foundPath: string | null = null;

    for (const dir of candidateDirs) {
      const candidatePath = path.join(dir, filename);
      if (fs.existsSync(candidatePath)) {
        foundPath = candidatePath;
        break;
      }
      // Check .jpg fallback if name lacks extension
      const parsed = path.parse(filename);
      const fallbackPath = path.join(dir, `${parsed.name}.jpg`);
      if (fs.existsSync(fallbackPath)) {
        foundPath = fallbackPath;
        break;
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

    const stat = fs.statSync(foundPath);
    const fileStream = fs.createReadStream(foundPath);
    
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
