import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import HeroSlideshow from "@/components/HeroSlideshow";
import Link from "next/link";

const disciplines = [
  { number: "01", title: "Refit & restoration", text: "A considered approach to yacht refurbishment, bringing together marine engineering and the detail of skilled local craftsmanship.", image: "04-teak-deck", alt: "The warm timber finish of a yacht’s teak deck", items: "Interiors · Finishes · Craftsmanship" },
  { number: "02", title: "Engineering & care", text: "Repair, maintenance and vessel support, shaped by international marine experience and a focus on the yacht as a whole.", image: "06-marine-engineering", alt: "Marine engine systems aboard a yacht", items: "Maintenance · Engineering · Vessel support" },
  { number: "03", title: "Hull & craft", text: "Specialist hull care, with a longer-term vision for aluminium fabrication and the construction of small craft in Galle.", image: "05-hull-care", alt: "Specialist care of a yacht’s hull", items: "Hull care · Fabrication · Small craft" },
];

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main id="main-content">
        <section className="hero" aria-labelledby="hero-title">
          <div className="wrap hero-content">
            <p className="eyebrow light"><span className="small-line" /> Galle, Sri Lanka · Indian Ocean</p>
            <h1 id="hero-title">A new perspective<br />on <em>life at sea.</em></h1>
            <div className="hero-bottom">
              <p>A new chapter in yachting at Galle.<br />For owners with a spirit of discovery.<br />For clubs with a world of connections.</p>
              <a className="button button-light" href="#experience">Discover the vision <span aria-hidden="true">↗</span></a>
            </div>
          </div>
          <HeroSlideshow />
        </section>
        <div className="coordinates-strip wrap"><span>Rooted in Galle. Looking to the world.</span><span>06°02′ N &nbsp; 80°12′ E <span aria-hidden="true">✧</span> Sri Lanka</span></div>
        <section className="section intro wrap" id="experience" aria-labelledby="intro-title">
          <div className="section-side"><p className="eyebrow">01 / The Yacht Club Galle vision</p><span className="compass" aria-hidden="true">✳</span></div>
          <div><h2 id="intro-title">A remarkable setting.<br />A more <em>considered welcome.</em></h2>
            <div className="intro-copy"><p>Some destinations become part of your story. We see Galle as one of them: a place to pause, reconnect and look towards the next horizon.</p><p>Yacht Club Galle is a developing vision for an international yachting community in Sri Lanka. Bringing together yacht care, marine expertise and connections across borders, our ambition is to make Galle part of a richer journey.</p></div>
            <a className="editorial-link" href="#destination">A closer look at Galle <span aria-hidden="true">↗</span></a>
          </div>
        </section>
        <section className="destination" id="destination" aria-labelledby="destination-title">
          <div className="destination-photo"><picture><source media="(max-width:760px)" srcSet="/web/02-galle-arrival-mobile.webp" /><img src="/web/02-galle-arrival.webp" alt="A yacht arriving in the coastal setting of Galle" loading="lazy" /></picture><span className="photo-note">A different rhythm. A new horizon.</span></div>
          <div className="destination-copy"><p className="eyebrow">02 / The destination</p><h2 id="destination-title">Set your course<br />for <em>Galle.</em></h2><p>On Sri Lanka’s southern coast, Galle offers a compelling setting for a new yachting destination. Our vision starts at the harbour and looks out to the wider Indian Ocean.</p><p>Whether you are planning a passage, exploring a future visit or opening a conversation for your club, this is an invitation to discover what comes next.</p><div className="destination-details"><div><span>THE SETTING</span><strong>Galle Harbour</strong></div><div><span>THE OUTLOOK</span><strong>International by nature</strong></div></div><a className="editorial-link" href="/contact/">Begin a conversation <span aria-hidden="true">↗</span></a></div>
        </section>
        <section className="section wrap" id="yacht-care" aria-labelledby="care-title">
          <div className="section-heading"><div><p className="eyebrow">03 / Care beyond the ordinary</p><h2 id="care-title">For the yacht.<br /><em>For the journey.</em></h2></div><p>Exceptional journeys begin with confidence in your yacht. Our service vision connects international marine experience with Sri Lankan technical skill and craftsmanship.</p></div>
          <div className="care-grid">{disciplines.map((item) => <article className="care-card" key={item.number}><div className="care-image"><picture><source media="(max-width:760px)" srcSet={`/web/${item.image}-mobile.webp`} /><img src={`/web/${item.image}.webp`} alt={item.alt} loading="lazy" /></picture><span>{item.number}</span></div><p className="card-kicker">{item.items}</p><h3>{item.title}</h3><p>{item.text}</p><a className="editorial-link" href="/services/">Explore our services <span aria-hidden="true">↗</span></a></article>)}</div>
          <p className="care-note">The Galle facility and service offering are in development. Discuss your requirements with us to explore the possibilities.</p>
        </section>
        <section className="club-section" id="club-connections" aria-labelledby="club-title">
          <div className="wrap club-layout"><div><p className="eyebrow light">04 / A world of connections</p><h2 id="club-title">Shared horizons.<br /><em>Lasting connections.</em></h2><p>Great clubs open up the world to their members. We welcome conversations with yacht clubs in the UAE, Europe and beyond that share our ambition to introduce their communities to Galle.</p><a className="button button-light" href="/contact/">Explore a club partnership <span aria-hidden="true">↗</span></a></div><div className="club-card"><span className="club-card-label">AN INVITATION TO CONNECT</span><div className="route"><span>Galle</span><i aria-hidden="true" /><span>The world</span></div><ul><li><span>01</span> International club relationships</li><li><span>02</span> Future visits & member introductions</li><li><span>03</span> A shared vision for yachting in Galle</li></ul><p>For club committees, fleet organisers<br />and international yachting communities.</p></div></div>
        </section>
        <section className="section wrap heritage" aria-labelledby="heritage-title"><div className="heritage-image"><picture><source media="(max-width:760px)" srcSet="/web/03-tropical-harbour-mobile.webp" /><img src="/web/03-tropical-harbour.webp" alt="Yachts at a palm-lined tropical harbour" loading="lazy" /></picture><span className="image-tag">Local knowledge. International perspective.</span></div><div><p className="eyebrow">05 / The experience behind the vision</p><h2 id="heritage-title">Marine expertise.<br /><em>Human connection.</em></h2><p>The vision brings together DPV Offshore & Marine Services in Sri Lanka and its sister company in the UAE, combining international marine services experience with local technical expertise.</p><p>With a background spanning ship supply, spares, marine engineering and vessel support, the ambition is to build a place where careful workmanship and long-term relationships belong together.</p><div className="heritage-signature"><span>Yacht Club Galle</span><small>A new chapter on the Indian Ocean.</small></div></div></section>
        <section className="journey-cta"><div className="wrap journey-cta-inner"><div><p className="eyebrow light">Your next chapter</p><h2>Every journey starts<br />with <em>a conversation.</em></h2></div><Link className="button button-light" href="/contact/">Make an enquiry <span aria-hidden="true">↗</span></Link></div></section>
      </main>
      <SiteFooter />
    </>
  );
}
