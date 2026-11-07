/**
 * Public contact settings, matching the contact details on www.dpvoffshore.lk.
 * Environment variables can override the phone and email addresses (see README).
 * Optional WhatsApp details remain hidden when empty.
 */
export const CONTACT = {
  /** 24/7 operations line, shown on the page */
  phone: process.env.NEXT_PUBLIC_CONTACT_PHONE?.trim() || "+94 11 26 82 692",
  /** Digits only, with country code, e.g. "94771234567" */
  whatsapp: process.env.NEXT_PUBLIC_CONTACT_WHATSAPP ?? "",
  email: process.env.NEXT_PUBLIC_CONTACT_EMAIL?.trim() || "info@dpvoffshore.lk",
  alternateEmail: process.env.NEXT_PUBLIC_CONTACT_EMAIL_ALTERNATE?.trim() || "info@dpvoffshore.com",
  location: "Galle Port, Galle, Sri Lanka",
  headOffice: {
    company: "DPV Offshore & Marine Services (Pvt) Ltd",
    address: ["No. 59/2, Norris Canal Road", "Colombo 10, Sri Lanka"],
  },
  linkedin: "https://www.linkedin.com/company/102757900/",
};

export const COMPANY = {
  name: "Yacht Club Galle",
  short: "Yacht Club Galle",
  city: "Galle, Sri Lanka",
};

/** The detailed 3D model served from /public. Rebuild it with `npm run model:build`. */
export const MODEL_URL = "/models/dpv-luxury-yacht-detailed.glb";

/** Double-wave motif echoing the waves in the logo: a large version (hero, footer) and a small section marker. */
export const WAVE_PATHS = {
  large: [
    "M0 14 C 50 5, 100 5, 150 14 S 250 23, 300 14 S 400 5, 450 14 S 550 23, 600 14 S 700 5, 750 14 S 850 23, 900 14 S 1000 5, 1050 14 S 1150 23, 1200 14",
    "M0 28 C 50 19, 100 19, 150 28 S 250 37, 300 28 S 400 19, 450 28 S 550 37, 600 28 S 700 19, 750 28 S 850 37, 900 28 S 1000 19, 1050 28 S 1150 37, 1200 28",
  ],
  small: [
    "M0 8 C 6 3, 12 3, 18 8 S 30 13, 36 8 S 48 3, 54 8 S 66 13, 72 8",
    "M0 17 C 6 12, 12 12, 18 17 S 30 22, 36 17 S 48 12, 54 17 S 66 22, 72 17",
  ],
};
