import { auth0 } from "~/lib/auth0";
import { verifyOrganizerDomain, getRoleName } from "~/lib/domain-verification";
import UserButton from "./UserButton";

/**
 * Server Component that fetches user session and renders UserButton
 * This keeps the auth logic on the server while providing a clean client UI
 */
export default async function AuthStatus() {
    const session = await auth0.getSession();

    let user = null;
    let isVerified = false;
    let roleName = "Guest";

    if (session?.user) {
        user = {
            name: session.user.name as string | undefined,
            email: session.user.email as string | undefined,
            picture: session.user.picture as string | undefined,
        };

        // Verify domain
        if (user.email) {
            const verification = verifyOrganizerDomain(user.email);
            isVerified = verification.isVerified;
            roleName = getRoleName(verification);
        }
    }

    return (
        <UserButton
            user={user}
            isVerified={isVerified}
            roleName={roleName}
        />
    );
}
