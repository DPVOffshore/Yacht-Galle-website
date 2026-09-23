import { Motif } from "./Waves";
import { Split } from "./Split";

const STEPS = [
  { title: "Survey on board", body: "We inspect the yacht and agree the scope of work with the owner or captain." },
  { title: "Written quote", body: "An itemised quote and timeline, approved by you before any work begins." },
  { title: "Work with updates", body: "Regular progress updates with photos, so you always know where the job stands." },
  { title: "Sea trial and handover", body: "We test the work under way and hand over a report of everything we did." },
];

export default function Process() {
  return (
    <section className="block" id="process" aria-labelledby="process-title">
      <div className="wrap">
        <div className="head-pair">
          <div>
            <Motif />
            <h2 className="display split" id="process-title" data-reveal="words">
              <Split text="How a job runs." />
            </h2>
          </div>
          <p className="lede" data-reveal style={{ "--d": 300 } as React.CSSProperties}>Transparency at every stage, from the first survey to the sea trial.</p>
        </div>
        <ol className="steps" data-stagger>
          {STEPS.map((s) => (
            <li key={s.title}>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
