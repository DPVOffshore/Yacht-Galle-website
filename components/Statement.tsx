import { Motif } from "./Waves";
import { Split } from "./Split";

export default function Statement() {
  return (
    <section className="statement" aria-label="Our approach">
      <div className="wrap">
        <Motif />
        <p className="display scrub" data-scrub style={{ "--n": 7 } as React.CSSProperties}>
          <Split text="Where marine engineering meets luxury craftsmanship." />
        </p>
        <p className="sub" data-reveal="blur">Secure, transparent and reliable yacht care.</p>
      </div>
    </section>
  );
}
