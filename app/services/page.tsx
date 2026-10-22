import type { Metadata } from "next";
import Link from "next/link";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import YachtExplorer from "@/components/yacht/YachtExplorer";
import { SERVICES, SERVICE_ORDER } from "@/lib/services";

export const metadata: Metadata = {
  title: "Yacht Care & Services | Yacht Club Galle",
  description: "Explore yacht refit, hull care, engineering, electrical systems and interiors with our interactive 3D yacht. Discover the Yacht Club Galle service vision.",
};

export default function ServicesPage() {
  return (
    <>
      <SiteHeader />
      <main id="main-content">
        <section className="page-intro wrap" aria-labelledby="services-title">
          <div><p className="eyebrow">Yacht Club Galle / Services</p><h1 id="services-title">Every detail.<br /><em>Every passage.</em></h1></div>
          <div className="page-intro-copy"><p>Care for every part of your yacht, considered as one. Explore the systems that make each journey possible, and the expertise behind our yacht care vision.</p><a className="editorial-link" href="#services">Explore the yacht <span aria-hidden="true">↓</span></a></div>
        </section>
        <YachtExplorer />
        <section className="section wrap service-disciplines" aria-labelledby="disciplines-title">
          <div className="section-heading"><div><p className="eyebrow">The service collection</p><h2 id="disciplines-title">Complete care.<br /><em>Considered craftsmanship.</em></h2></div><p>From beneath the waterline to the spaces you live in, discover six disciplines at the heart of our service vision.</p></div>
          <div className="discipline-grid">
            {SERVICE_ORDER.map((id, index) => <article key={id} id={`discipline-${id}`}><span className="discipline-number">0{index + 1}</span><h3>{SERVICES[id].name}</h3><p>{SERVICES[id].desc}</p><ul>{SERVICES[id].items.map(item => <li key={item}>{item}</li>)}</ul><Link className="editorial-link" href={`/contact/?service=${id}`}>Discuss your requirements <span aria-hidden="true">↗</span></Link></article>)}
          </div>
          <p className="care-note">The Galle facility and service offering are in development. Contact us to discuss availability, your yacht’s requirements and the scope of a future project.</p>
        </section>
        <section className="journey-cta"><div className="wrap journey-cta-inner"><div><p className="eyebrow light">Care starts with understanding</p><h2>Your yacht.<br /><em>Our next conversation.</em></h2></div><Link className="button button-light" href="/contact/">Talk to us <span aria-hidden="true">↗</span></Link></div></section>
      </main>
      <SiteFooter />
    </>
  );
}
