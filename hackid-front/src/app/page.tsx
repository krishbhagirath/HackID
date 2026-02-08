import { auth0 } from "~/lib/auth0";
import HomeContent from "~/components/HomeContent";

export default async function Home() {
  const session = await auth0.getSession();

  const user = session?.user ? {
    name: session.user.name,
    email: session.user.email,
    picture: session.user.picture,
  } : null;

  return <HomeContent user={user} />;
}
