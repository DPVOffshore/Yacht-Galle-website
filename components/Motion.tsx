"use client";

import { useEffect } from "react";

/**
 * Page-wide motion: reveals [data-reveal] elements as they enter the viewport, drives scroll-linked
 * CSS variables (hero parallax, statement scrub), hides the header while scrolling down, and adds
 * magnetic buttons and tilting cards for fine pointers. Renders nothing.
 */
export default function Motion() {
  useEffect(() => {
    const root = document.documentElement;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      root.classList.remove("js-motion");
      return;
    }

    // Stagger index for children of [data-stagger].
    document.querySelectorAll<HTMLElement>("[data-stagger]").forEach((el) => {
      Array.from(el.children).forEach((c, i) => (c as HTMLElement).style.setProperty("--i", String(i)));
    });

    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.12 },
    );
    const observeAll = () =>
      document.querySelectorAll("[data-reveal]:not(.in), [data-stagger]:not(.in)").forEach((el) => io.observe(el));
    observeAll();
    // Content that mounts later (explorer panel) still gets revealed.
    const mo = new MutationObserver(observeAll);
    mo.observe(document.body, { childList: true, subtree: true });

    // Scroll-linked values.
    const hero = document.querySelector<HTMLElement>(".hero");
    const scrubs = Array.from(document.querySelectorAll<HTMLElement>("[data-scrub]"));
    const header = document.querySelector<HTMLElement>(".site-head");
    let lastY = window.scrollY;
    let ticking = false;
    const update = () => {
      ticking = false;
      const y = window.scrollY;
      const vh = window.innerHeight;
      if (hero) {
        const p = Math.min(1, Math.max(0, y / hero.offsetHeight));
        hero.style.setProperty("--hp", p.toFixed(4));
      }
      for (const el of scrubs) {
        const r = el.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (vh * 0.9 - r.top) / (vh * 0.9 - vh * 0.35)));
        el.style.setProperty("--p", p.toFixed(4));
      }
      if (header) {
        const down = y > lastY + 4;
        const up = y < lastY - 4;
        if (down && y > 480) header.classList.add("tucked");
        else if (up || y < 480) header.classList.remove("tucked");
      }
      lastY = y;
    };
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);

    // Magnetic buttons and tilting cards, mouse only.
    const fine = window.matchMedia("(pointer: fine)").matches;
    let magnet: HTMLElement | null = null;
    let tilt: HTMLElement | null = null;
    const release = (el: HTMLElement | null, props: string[]) => el && props.forEach((p) => el.style.removeProperty(p));
    const onMove = (e: PointerEvent) => {
      const t = e.target as Element | null;
      const btn = t?.closest<HTMLElement>(".btn") ?? null;
      if (btn !== magnet) {
        release(magnet, ["--mx", "--my"]);
        magnet = btn;
      }
      if (btn) {
        const r = btn.getBoundingClientRect();
        btn.style.setProperty("--mx", `${((e.clientX - r.left) / r.width - 0.5) * 12}px`);
        btn.style.setProperty("--my", `${((e.clientY - r.top) / r.height - 0.5) * 10}px`);
      }
      const card = t?.closest<HTMLElement>(".trio article, .steps li") ?? null;
      if (card !== tilt) {
        release(tilt, ["--rx", "--ry", "--gx", "--gy"]);
        tilt = card;
      }
      if (card) {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width;
        const yy = (e.clientY - r.top) / r.height;
        card.style.setProperty("--ry", `${(x - 0.5) * 8}deg`);
        card.style.setProperty("--rx", `${(0.5 - yy) * 8}deg`);
        card.style.setProperty("--gx", `${x * 100}%`);
        card.style.setProperty("--gy", `${yy * 100}%`);
      }
    };
    if (fine) document.addEventListener("pointermove", onMove, { passive: true });

    return () => {
      io.disconnect();
      mo.disconnect();
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      document.removeEventListener("pointermove", onMove);
    };
  }, []);

  return null;
}
