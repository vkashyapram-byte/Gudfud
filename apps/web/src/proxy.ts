import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/admin')) {
    const token = request.cookies.get(process.env.ADMIN_COOKIE_NAME || 'admin_session_token')?.value;

    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
    
    // Strict Next.js middleware verification happens here
    // For this MVP, we only ensure the cookie is present.
    // Further cryptographic verification would occur in the backend API calls.
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/admin/:path*'],
};
