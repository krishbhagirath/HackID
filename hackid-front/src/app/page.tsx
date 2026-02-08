import { auth0 } from "~/lib/auth0";
import HomeContent from "~/components/HomeContent";

export default async function Home() {
  const session = await auth0.getSession();

  const user = session?.user ? {
    name: session.user.name,
    email: session.user.email,
    picture: session.user.picture,
  } : null;

  // Get organization from user's app_metadata (set in Auth0 Dashboard)
  const orgId = (session?.user as any)?.app_metadata?.organization ||
    (session?.user as any)?.organization ||
    null;

  return <HomeContent user={user} orgId={orgId} />;
}
