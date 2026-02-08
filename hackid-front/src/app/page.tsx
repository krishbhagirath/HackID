import { auth0 } from "~/lib/auth0";
import HomeContent from "~/components/HomeContent";

export default async function Home() {
  const session = await auth0.getSession();

  const user = session?.user ? {
    name: session.user.name,
    email: session.user.email,
    picture: session.user.picture,
  } : null;

  // Get user's email for filtering their hackathons
  const userEmail = session?.user?.email ?? null;

  console.log('[Home Page] Auth0 session user:', session?.user);
  console.log('[Home Page] Extracted userEmail:', userEmail);

  return <HomeContent user={user} userEmail={userEmail} />;
}
