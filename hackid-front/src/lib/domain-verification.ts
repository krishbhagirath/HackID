/**
 * Domain-Based Verification for Organizers
 * 
 * This utility checks if a user's email belongs to a known organization.
 * Only users from approved domains can access organizer features.
 */

// Approved email domains for organizers
const APPROVED_DOMAINS: string[] = [
    // MLH (Major League Hacking)
    "mlh.io",
    "majorleaguehacking.com",

    // Universities (Add your target universities here)
    ".edu",           // All US educational institutions
    ".edu.ca",        // Canadian educational institutions
    ".ac.uk",         // UK academic institutions
    ".edu.au",        // Australian educational institutions
    "uwaterloo.ca",   // University of Waterloo
    "utoronto.ca",    // University of Toronto
    "mcmaster.ca",    // McMaster University
    "uoft.ca",        // University of Toronto alternate
    "mit.edu",
    "stanford.edu",
    "berkeley.edu",
    "harvard.edu",
    "princeton.edu",
    "cmu.edu",

    // Major Tech Companies (Hackathon Sponsors)
    "google.com",
    "microsoft.com",
    "amazon.com",
    "meta.com",
    "apple.com",
    "netflix.com",
    "github.com",
    "stripe.com",
    "shopify.com",
    "mongodb.com",
    "twilio.com",
    "digitalocean.com",
    "vercel.com",
    "cloudflare.com",
    "auth0.com",

    // Hackathon Organizations
    "devpost.com",
    "hackerearth.com",
    "hackclub.com",
];

export type VerificationResult = {
    isVerified: boolean;
    domain: string | null;
    matchedPattern: string | null;
    organizationType: "mlh" | "university" | "company" | null;
};

/**
 * Extract domain from email address
 */
export function extractDomain(email: string): string | null {
    if (!email || !email.includes("@")) {
        return null;
    }
    return email.split("@")[1]?.toLowerCase() || null;
}

/**
 * Determine the organization type based on the matched domain
 */
function getOrganizationType(matchedPattern: string): "mlh" | "university" | "company" {
    // MLH domains
    if (matchedPattern.includes("mlh") || matchedPattern.includes("majorleaguehacking")) {
        return "mlh";
    }

    // Educational domains
    if (
        matchedPattern.includes(".edu") ||
        matchedPattern.includes(".ac.") ||
        matchedPattern.endsWith(".ca") && !matchedPattern.includes(".")
    ) {
        return "university";
    }

    return "company";
}

/**
 * Check if an email domain matches any approved pattern
 */
export function verifyOrganizerDomain(email: string): VerificationResult {
    const domain = extractDomain(email);

    if (!domain) {
        return {
            isVerified: false,
            domain: null,
            matchedPattern: null,
            organizationType: null,
        };
    }

    for (const pattern of APPROVED_DOMAINS) {
        // Exact match
        if (domain === pattern) {
            return {
                isVerified: true,
                domain,
                matchedPattern: pattern,
                organizationType: getOrganizationType(pattern),
            };
        }

        // Suffix match (e.g., ".edu" matches "student@harvard.edu")
        if (pattern.startsWith(".") && domain.endsWith(pattern)) {
            return {
                isVerified: true,
                domain,
                matchedPattern: pattern,
                organizationType: getOrganizationType(pattern),
            };
        }
    }

    return {
        isVerified: false,
        domain,
        matchedPattern: null,
        organizationType: null,
    };
}

/**
 * Get a user-friendly role name based on verification result
 */
export function getRoleName(result: VerificationResult): string {
    if (!result.isVerified) {
        return "Guest";
    }

    switch (result.organizationType) {
        case "mlh":
            return "MLH Staff";
        case "university":
            return "University Organizer";
        case "company":
            return "Sponsor";
        default:
            return "Verified Organizer";
    }
}
