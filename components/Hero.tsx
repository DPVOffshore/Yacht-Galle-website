import { Waves } from "./Waves";
import { Split } from "./Split";
import { asset } from "@/lib/site";

export default function Hero() {
  return (
    <section className="hero">
      <video className="hero-video" autoPlay muted loop playsInline preload="auto" aria-hidden="true">
        <source src={asset("/video/hero.mp4")} type="video/mp4" />
      </video>
      <div className="wrap">
        <h1 className="display split" data-reveal="words">
          <Split text="Yacht refit and repair" /> <br className="br-lg" />
          <Split text="at Galle Port." from={4} />
        </h1>
        <div className="hero-grid">
          <div>
            <p className="lede" data-reveal style={{ "--d": 700 } as React.CSSProperties}>
              Hull, engine, electrical, navigation and interior work for yachts calling at Galle, carried out by one
              accountable team.
            </p>
            <div className="hero-actions" data-stagger style={{ "--d": 900 } as React.CSSProperties}>
              <a className="btn btn-blue" href="#contact">Request a survey</a>
              <a className="textlink" href="#services">Explore the yacht</a>
            </div>
          </div>
          <p className="coords" data-reveal="right" style={{ "--d": 1100 } as React.CSSProperties}>
            <strong>Galle Harbour, Sri Lanka</strong>
            06°02′N 80°12′E
          </p>
        </div>
        <Waves marker="Galle" />
      </div>
    </section>
  );
}
