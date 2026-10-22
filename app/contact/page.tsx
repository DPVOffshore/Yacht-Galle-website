import type { Metadata } from "next";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import ContactSection from "@/components/ContactSection";

export const metadata: Metadata = {
  title: "Contact & Enquiries | Yacht Club Galle",
  description: "Contact Yacht Club Galle about yacht care, a future visit or an international club partnership. Reach us at info@dpvoffshore.lk or info@dpvoffshore.com.",
};

export default function ContactPage() {
  return (
    <>
      <SiteHeader />
      <main id="main-content">
        <section className="page-intro wrap" aria-labelledby="contact-page-title"><div><p className="eyebrow">Yacht Club Galle / Contact</p><h1 id="contact-page-title">Let’s chart<br /><em>what comes next.</em></h1></div><p className="page-intro-copy">A yacht to care for. A new destination to discover. A club connection to explore. Share your plans with us.</p></section>
        <ContactSection />
        <div className="wrap contact-closing"><p>For yacht owners, captains and international clubs.</p><span>Galle, Sri Lanka · Connected to the world.</span></div>
      </main>
      <SiteFooter />
    </>
  );
}
