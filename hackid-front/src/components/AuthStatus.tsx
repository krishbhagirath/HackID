import { auth0 } from "~/lib/auth0";
import { verifyOrganizerDomain, getRoleName } from "~/lib/domain-verification";
import UserButton from "./UserButton";

export default async function AuthStatus() {
    const session = await auth0.getSession();

    if (!session?.user) {
        return <UserButton user={null} isVerified={false} role="Guest" />;
    }

    const { user } = session;
    const email = user.email || "";
    const verificationResult = verifyOrganizerDomain(email);
    const roleName = getRoleName(verificationResult);

    return (
        <UserButton
            user={{
                name: user.name,
                email: user.email,
                picture: user.picture,
            }}
            isVerified={verificationResult.isVerified}
            role={roleName}
        />
    );
}
