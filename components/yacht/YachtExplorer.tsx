"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { SERVICES, SERVICE_ORDER, PANEL_INTRO, type ServiceId } from "@/lib/services";
import { MODEL_URL } from "@/lib/site";
import { Motif } from "@/components/Waves";
import { Split } from "@/components/Split";
import { ASK_EVENT } from "@/lib/events";
import type { YachtViewer, ViewerStatus } from "./YachtViewer";

export default function YachtExplorer() {
  const [selected, setSelected] = useState<ServiceId | null>(null);
  const [xray, setXray] = useState(false);
  const [status, setStatus] = useState<ViewerStatus>({ state: "loading", progress: null });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const tipRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLElement>(null);
  const headRef = useRef<HTMLElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const viewerRef = useRef<YachtViewer | null>(null);
  const stateRef = useRef({ selected, xray });
  stateRef.current = { selected, xray };

  /** Tapping the selected service again clears it; picking a part on the model always selects. */
  const select = useCallback((id: ServiceId | null, fromModel = false) => {
    const current = stateRef.current.selected;
    const next = id && id === current && !fromModel ? null : id;
    if (next) setXray(SERVICES[next].xray);
    setSelected(next);
  }, []);
  const selectRef = useRef(select);
  selectRef.current = select;

  const toggleXray = () => {
    const next = !xray;
    setXray(next);
    if (selected && SERVICES[selected].xray !== next) setSelected(null);
  };

  const reset = () => {
    setXray(false);
    setSelected(null);
  };

  const ask = () => {
    window.dispatchEvent(new CustomEvent<ServiceId | null>(ASK_EVENT, { detail: selected }));
  };

  // Create the viewer only when the section approaches the viewport; three.js loads on demand.
  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;
    let cancelled = false;
    const io = new IntersectionObserver(
      async ([entry]) => {
        if (!entry.isIntersecting || viewerRef.current) return;
        io.disconnect();
        try {
          const { YachtViewer } = await import("./YachtViewer");
          if (cancelled || !canvasRef.current || !tipRef.current) return;
          viewerRef.current = new YachtViewer({
            canvas: canvasRef.current,
            tip: tipRef.current,
            modelUrl: MODEL_URL,
            getLayout: () => ({
              card: cardRef.current,
              head: headRef.current,
              desktop: window.matchMedia("(min-width: 1021px)").matches,
            }),
            onPick: (id) => selectRef.current(id, true),
            onStatus: setStatus,
            getState: () => ({ id: stateRef.current.selected, xray: stateRef.current.xray }),
          });
        } catch {
          setStatus({ state: "error", message: "3D isn't available on this device. The services are listed alongside." });
        }
      },
      { rootMargin: "600px" },
    );
    io.observe(stage);
    return () => {
      cancelled = true;
      io.disconnect();
      viewerRef.current?.dispose();
      viewerRef.current = null;
    };
  }, []);

  // Push selection changes to the 3D view (skip the initial render).
  const first = useRef(true);
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    viewerRef.current?.show(selected, xray);
  }, [selected, xray]);

  // On phones the services are a swipeable row; keep the active one in view.
  useEffect(() => {
    if (!selected || !window.matchMedia("(max-width: 1020px)").matches) return;
    listRef.current
      ?.querySelector<HTMLButtonElement>(`[data-svc="${selected}"]`)
      ?.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
  }, [selected]);

  const service = selected ? SERVICES[selected] : null;

  return (
    <section className="block explore" id="services" aria-labelledby="svc-title">
      <div className={`stage${selected ? " has-selection" : ""}`} ref={stageRef}>
        <canvas
          data-reveal="canvas"
          ref={canvasRef}
          role="img"
          aria-label="Interactive 3D model of a motor yacht. Selecting a service highlights the parts it covers."
        />

        {status.state !== "ready" && (
          <div className="stage-status">
            {status.state === "loading" ? (
              <>
                <div className="bar" />
                <span>
                  Loading the 3D yacht
                  {status.progress !== null && status.progress > 0 && (
                    <span className="pct"> {Math.round(status.progress * 100)}%</span>
                  )}
                </span>
              </>
            ) : (
              <span>{status.message}</span>
            )}
          </div>
        )}

        <div className="tip" ref={tipRef} aria-hidden="true" />

        <div className="overlay">
          <div className="wrap overlay-inner">
            <header className="ov-head" ref={headRef}>
              <Motif />
              <h2 className="display split" id="svc-title" data-reveal="words">
                <Split text="Tap any part" />
                <br />
                <Split text="of the yacht." from={3} />
              </h2>
              <p className="lede" data-reveal style={{ "--d": 400 } as React.CSSProperties}>
                Every system on board, and the work we do on it. Turn the yacht, select a part, or choose a service.
              </p>
            </header>

            <aside className="ov-card" ref={cardRef} aria-label="Services" data-reveal="card">
              <ul className="svc-list" ref={listRef} aria-label="Services" data-stagger>
                {SERVICE_ORDER.map((id) => (
                  <li key={id}>
                    <button type="button" data-svc={id} aria-pressed={selected === id} onClick={() => select(id)}>
                      {SERVICES[id].name}
                    </button>
                  </li>
                ))}
              </ul>

              <div className="panel" aria-live="polite">
                <h3 key={`h-${selected}`}>{service ? service.name : PANEL_INTRO.title}</h3>
                <p key={`p-${selected}`}>{service ? service.desc : PANEL_INTRO.desc}</p>
                {service && (
                  <>
                    <ul key={`u-${selected}`}>
                      {service.items.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                    <a key={`a-${selected}`} className="btn btn-line" href="#contact" onClick={ask}>
                      Ask about this service
                    </a>
                  </>
                )}
              </div>
            </aside>

            <div className="ov-controls" data-stagger>
              <button className="btn btn-line stage-xray" type="button" aria-pressed={xray} onClick={toggleXray}>
                {xray ? "Show outside" : "See inside"}
              </button>
              <button className="btn btn-line stage-reset" type="button" onClick={reset}>
                Show whole yacht
              </button>
              <p className="stage-hint">Drag to turn the yacht. Tap a part to see the service.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
