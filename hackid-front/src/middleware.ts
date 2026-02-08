import type { NextRequest } from "next/server";
import { auth0 } from "~/lib/auth0";

// Routes that require authentication
const PROTECTED_ROUTES = ["/dashboard", "/organizer", "/admin"];

export async function middleware(request: NextRequest) {
    // Let Auth0 handle its authentication routes
    const authResponse = await auth0.middleware(request);

    // Check if this is a protected route
    const pathname = request.nextUrl.pathname;
    const isProtectedRoute = PROTECTED_ROUTES.some((route) =>
        pathname.startsWith(route)
    );

    if (isProtectedRoute) {
        const session = await auth0.getSession(request);

        if (!session) {
            // Redirect to login with return URL
            const loginUrl = new URL("/auth/login", request.url);
            loginUrl.searchParams.set("returnTo", pathname);
            return Response.redirect(loginUrl);
        }
    }

    return authResponse;
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico, sitemap.xml, robots.txt (metadata files)
         * - Static assets (images, fonts, etc.)
         */
        "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|woff|woff2)$).*)",
    ],
};
