import { Motif } from "./Waves";
import { Split } from "./Split";

const AUDIENCES = [
  {
    title: "Yachts in transit",
    body: "Galle is where most yachts clear into Sri Lanka and prepare for an Indian Ocean crossing. We inspect and repair while you clear in, provision and wait for weather.",
  },
  {
    title: "Maldives fleet and superyachts",
    body: "A short passage from the Maldives, Galle is a closer option than sending vessels to Thailand or Indonesia for maintenance. We schedule around your charter calendar and work with your yacht agent.",
  },
  {
    title: "Sri Lankan owners and charter operators",
    body: "Scheduled maintenance, pre-season checks and repairs for private yachts and charter boats working the south and west coasts.",
  },
];

export default function Audiences() {
  return (
    <section className="block" id="galle" aria-labelledby="galle-title">
      <div className="wrap">
        <div className="head-pair">
          <div>
            <Motif />
            <h2 className="display split" id="galle-title" data-reveal="words">
              <Split text="Built for the yachts that call at Galle." />
            </h2>
          </div>
          <p className="lede" data-reveal style={{ "--d": 300 } as React.CSSProperties}>
            Galle is Sri Lanka&apos;s port for visiting pleasure yachts. Until now, owners have had to look elsewhere for
            serious repair work.
          </p>
        </div>
        <div className="trio" data-stagger>
          {AUDIENCES.map((a) => (
            <article key={a.title}>
              <h3>{a.title}</h3>
              <p>{a.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
