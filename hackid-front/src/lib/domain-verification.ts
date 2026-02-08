/**
 * Domain Verification Utility
 * Validates organizer domains for hackathon access
 */

// Approved exact domains
const APPROVED_DOMAINS = [
    // MLH
    "mlh.io",
    "majorleaguehacking.com",

    // Tech Companies
    "microsoft.com",
    "github.com",
    "shopify.com",
    "amazon.com",
    "google.com",
    "stripe.com",
    "vercel.com",
    "meta.com",
    "apple.com",

    // Hackathon Platforms
    "devpost.com",
    "hackerearth.com",
];

// Canadian University Domains
const CANADIAN_UNIVERSITIES = [
    "mcmaster.ca",
    "uwaterloo.ca",
    "utoronto.ca",
    "yorku.ca",
    "ubc.ca",
    "ualberta.ca",
    "queensu.ca",
    "uottawa.ca",
    "mcgill.ca",
    "dal.ca",
    "carleton.ca",
    "wlu.ca",
    "torontomu.ca",
    "uwo.ca",
    "sfu.ca",
    "usask.ca",
    "umanitoba.ca",
    "mun.ca",
];

// Educational domain suffixes
const EDU_SUFFIXES = [
    ".edu",      // US Universities
    ".edu.ca",   // Canadian (some)
    ".ac.uk",    // UK
    ".edu.au",   // Australia
    ".ac.jp",    // Japan
    ".edu.sg",   // Singapore
];

export type OrganizationType = "MLH" | "UNIVERSITY" | "COMPANY" | "HACKATHON_PLATFORM" | "UNKNOWN";

export interface VerificationResult {
    isVerified: boolean;
    domain: string;
    organizationType: OrganizationType;
}

/**
 * Verify if an email belongs to an approved organizer domain
 */
export function verifyOrganizerDomain(email: string): VerificationResult {
    const domain = email.split("@")[1]?.toLowerCase() || "";

    // Check MLH
    if (domain === "mlh.io" || domain === "majorleaguehacking.com") {
        return { isVerified: true, domain, organizationType: "MLH" };
    }

    // Check hackathon platforms
    if (domain === "devpost.com" || domain === "hackerearth.com") {
        return { isVerified: true, domain, organizationType: "HACKATHON_PLATFORM" };
    }

    // Check exact approved domains (companies)
    if (APPROVED_DOMAINS.includes(domain)) {
        return { isVerified: true, domain, organizationType: "COMPANY" };
    }

    // Check Canadian universities (including subdomains like macid.mcmaster.ca)
    for (const uni of CANADIAN_UNIVERSITIES) {
        if (domain === uni || domain.endsWith("." + uni)) {
            return { isVerified: true, domain, organizationType: "UNIVERSITY" };
        }
    }

    // Check educational suffixes
    for (const suffix of EDU_SUFFIXES) {
        if (domain.endsWith(suffix)) {
            return { isVerified: true, domain, organizationType: "UNIVERSITY" };
        }
    }

    return { isVerified: false, domain, organizationType: "UNKNOWN" };
}

/**
 * Get a user-friendly role name based on verification result
 */
export function getRoleName(result: VerificationResult): string {
    switch (result.organizationType) {
        case "MLH":
            return "MLH Staff";
        case "UNIVERSITY":
            return "University Organizer";
        case "COMPANY":
            return "Sponsor";
        case "HACKATHON_PLATFORM":
            return "Platform Partner";
        default:
            return "Guest";
    }
}
