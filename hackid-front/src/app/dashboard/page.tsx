import { redirect } from "next/navigation";
import { auth0 } from "~/lib/auth0";
import { verifyOrganizerDomain, getRoleName } from "~/lib/domain-verification";
import HeaderServer from "~/components/HeaderServer";

export default async function DashboardPage() {
    const session = await auth0.getSession();

    if (!session?.user) {
        redirect("/auth/login?returnTo=/dashboard");
    }

    const email = session.user.email as string | undefined;
    const verification = email ? verifyOrganizerDomain(email) : null;

    if (!verification?.isVerified) {
        // User is authenticated but not from an approved domain
        return (
            <div className="min-h-screen">
                <HeaderServer />
                <main className="max-w-[1400px] mx-auto p-6">
                    <div className="brutal-border bg-zinc-900 brutal-shadow p-12 text-center">
                        <span className="material-icons text-8xl text-brutal-red mb-6">block</span>
                        <h1 className="font-display text-4xl md:text-5xl uppercase mb-4">Access Denied</h1>
                        <p className="text-lg opacity-70 max-w-xl mx-auto mb-6">
                            Your email domain <strong className="text-brutal-red">{verification?.domain || 'unknown'}</strong> is not recognized as an approved organizer domain.
                        </p>
                        <div className="brutal-border bg-zinc-800 p-6 text-left max-w-md mx-auto mb-8">
                            <h3 className="font-bold uppercase text-sm mb-3 text-brutal-green">Approved Domains Include:</h3>
                            <ul className="text-xs space-y-1 opacity-70">
                                <li>• MLH Staff (mlh.io, majorleaguehacking.com)</li>
                                <li>• Universities (.edu, .edu.ca, .ac.uk)</li>
                                <li>• Major Tech Companies (google.com, github.com, etc.)</li>
                                <li>• Hackathon Platforms (devpost.com, hackerearth.com)</li>
                            </ul>
                        </div>
                        <div className="flex gap-4 justify-center">
                            <a
                                href="/"
                                className="brutal-border px-6 py-3 bg-zinc-800 font-bold text-sm uppercase hover:bg-zinc-700 transition-colors"
                            >
                                Go Home
                            </a>
                            <a
                                href="/auth/logout"
                                className="brutal-border px-6 py-3 bg-brutal-red text-white font-bold text-sm uppercase hover:bg-red-700 transition-colors"
                            >
                                Logout
                            </a>
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    // Verified organizer dashboard
    const roleName = getRoleName(verification);
    const userName = session.user.name || email;

    return (
        <div className="min-h-screen">
            <HeaderServer />
            <main className="max-w-[1400px] mx-auto p-6">
                {/* Welcome Section */}
                <div className="mb-12">
                    <div className="flex items-center gap-4 mb-4">
                        <span className="material-icons text-brutal-green text-4xl">verified</span>
                        <div>
                            <h1 className="font-display text-4xl md:text-5xl uppercase leading-none">
                                Organizer Dashboard
                            </h1>
                            <p className="text-sm opacity-70 uppercase">
                                Welcome back, <strong className="text-primary">{userName}</strong>
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-4 mt-6">
                        <div className="brutal-border bg-zinc-900 px-4 py-2">
                            <span className="text-xs uppercase font-bold opacity-50">Role:</span>
                            <span className="text-xs uppercase font-bold text-brutal-green ml-2">{roleName}</span>
                        </div>
                        <div className="brutal-border bg-zinc-900 px-4 py-2">
                            <span className="text-xs uppercase font-bold opacity-50">Domain:</span>
                            <span className="text-xs uppercase font-bold text-primary ml-2">{verification.domain}</span>
                        </div>
                        <div className="brutal-border bg-zinc-900 px-4 py-2">
                            <span className="text-xs uppercase font-bold opacity-50">Type:</span>
                            <span className="text-xs uppercase font-bold ml-2">{verification.organizationType}</span>
                        </div>
                    </div>
                </div>

                {/* Dashboard Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Card: Run Scan */}
                    <div className="brutal-border bg-zinc-900 brutal-shadow-hover p-6">
                        <span className="material-icons text-primary text-4xl mb-4">radar</span>
                        <h3 className="font-display text-xl uppercase mb-2">Run Plagiarism Scan</h3>
                        <p className="text-sm opacity-70 mb-4">
                            Analyze hackathon submissions for potential plagiarism or recycled projects.
                        </p>
                        <a
                            href="/"
                            className="block text-center brutal-border px-4 py-2 bg-primary text-black font-bold text-sm uppercase hover:bg-yellow-400 transition-colors"
                        >
                            Start Scan
                        </a>
                    </div>

                    {/* Card: View Reports */}
                    <div className="brutal-border bg-zinc-900 brutal-shadow-hover p-6">
                        <span className="material-icons text-brutal-green text-4xl mb-4">assessment</span>
                        <h3 className="font-display text-xl uppercase mb-2">View Reports</h3>
                        <p className="text-sm opacity-70 mb-4">
                            Access historical scan results and detailed plagiarism reports.
                        </p>
                        <button
                            className="w-full brutal-border px-4 py-2 bg-zinc-800 font-bold text-sm uppercase hover:bg-zinc-700 transition-colors opacity-50 cursor-not-allowed"
                            disabled
                        >
                            Coming Soon
                        </button>
                    </div>

                    {/* Card: Manage Events */}
                    <div className="brutal-border bg-zinc-900 brutal-shadow-hover p-6">
                        <span className="material-icons text-blue-400 text-4xl mb-4">event</span>
                        <h3 className="font-display text-xl uppercase mb-2">Manage Events</h3>
                        <p className="text-sm opacity-70 mb-4">
                            Configure hackathon events and submission scraping settings.
                        </p>
                        <button
                            className="w-full brutal-border px-4 py-2 bg-zinc-800 font-bold text-sm uppercase hover:bg-zinc-700 transition-colors opacity-50 cursor-not-allowed"
                            disabled
                        >
                            Coming Soon
                        </button>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="mt-12">
                    <h2 className="font-display text-2xl uppercase mb-6">Recent Activity</h2>
                    <div className="brutal-border bg-zinc-900 p-6">
                        <div className="flex items-center justify-center py-12 opacity-50">
                            <span className="material-icons text-4xl mr-4">history</span>
                            <span className="font-bold uppercase">No recent activity</span>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
