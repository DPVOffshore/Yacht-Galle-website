import { WAVE_PATHS } from "@/lib/site";

/** Small double-wave marker above section headings, echoing the waves in the logo. */
export function Motif() {
  return (
    <svg className="motif" viewBox="0 0 72 22" aria-hidden="true" data-reveal="draw">
      {WAVE_PATHS.small.map((d) => (
        <path key={d} d={d} pathLength={1} />
      ))}
    </svg>
  );
}

/** Full-width double wave. In the hero it draws in once and marks Galle in DPV red. */
export function Waves({ marker }: { marker?: string }) {
  return (
    <div className="waves" aria-hidden="true">
      <svg viewBox="0 0 1200 42" preserveAspectRatio="none">
        {WAVE_PATHS.large.map((d) => (
          <path key={d} d={d} pathLength={1} />
        ))}
      </svg>
      {marker && (
        <>
          <span className="dot" />
          <span className="dot-label">{marker}</span>
        </>
      )}
    </div>
  );
}
