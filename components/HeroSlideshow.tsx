"use client";

import { useEffect, useState } from "react";

const slides = [
  { file: "01-yacht-at-anchor", label: "At anchor" },
  { file: "02-galle-arrival", label: "Arrival in Galle" },
  { file: "03-tropical-harbour", label: "Tropical harbour" },
  { file: "04-teak-deck", label: "Teak & interiors" },
  { file: "05-hull-care", label: "Hull care" },
  { file: "06-marine-engineering", label: "Marine engineering" },
];

export default function HeroSlideshow() {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(true);
  const [visible, setVisible] = useState(true);
  const [focused, setFocused] = useState(false);
  const [loaded, setLoaded] = useState<number[]>([]);

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updateMotion = () => setReducedMotion(preference.matches);
    const updateVisibility = () => setVisible(!document.hidden);
    updateMotion();
    updateVisibility();
    preference.addEventListener("change", updateMotion);
    document.addEventListener("visibilitychange", updateVisibility);
    return () => {
      preference.removeEventListener("change", updateMotion);
      document.removeEventListener("visibilitychange", updateVisibility);
    };
  }, []);

  const playing = !paused && !reducedMotion && visible && !focused;
  useEffect(() => {
    const next = (active + 1) % slides.length;
    if (!playing || !loaded.includes(next)) return;
    const timer = window.setTimeout(() => setActive(next), 6500);
    return () => window.clearTimeout(timer);
  }, [active, playing, loaded]);

  return (
    <>
      <div className="hero-media" aria-hidden="true" data-playing={playing}>
        {slides.map((slide, index) => (
          <picture key={slide.file} className={`hero-slide${active === index ? " is-active" : ""}`}>
            <source media="(max-width: 760px)" srcSet={`/web/${slide.file}-mobile.webp`} />
            {/* Art-directed local WebP files also work with the static export. */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`/web/${slide.file}.webp`}
              alt=""
              fetchPriority={index === 0 ? "high" : "low"}
              decoding="async"
              onLoad={() => setLoaded((previous) => previous.includes(index) ? previous : [...previous, index])}
            />
          </picture>
        ))}
      </div>
      <div className="wrap hero-gallery">
        <div
          className="hero-gallery-bar"
          role="group"
          aria-label="Hero image slideshow"
          onFocusCapture={() => setFocused(true)}
          onBlurCapture={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) setFocused(false);
          }}
        >
          <p className="hero-caption" aria-live={playing ? "off" : "polite"} aria-atomic="true">
            <span className="hero-slide-count">0{active + 1} / 0{slides.length}</span>
            {slides[active].label}
          </p>
          <div className="hero-gallery-controls">
            <div className="hero-slide-selectors" role="group" aria-label="Choose an image">
              {slides.map((slide, index) => (
                <button
                  key={slide.file}
                  type="button"
                  className="hero-slide-selector"
                  aria-label={`Show image ${index + 1}: ${slide.label}`}
                  aria-pressed={active === index}
                  onClick={() => { setActive(index); setPaused(true); }}
                />
              ))}
            </div>
            {!reducedMotion && (
              <button
                type="button"
                className="hero-playback"
                aria-label={paused ? "Play slideshow" : "Pause slideshow"}
                onClick={() => setPaused(!paused)}
              >
                <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
                  {paused ? <path d="M4 2 12 7 4 12Z" fill="currentColor" /> : <path d="M4 2v10M10 2v10" stroke="currentColor" strokeWidth="2" />}
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
