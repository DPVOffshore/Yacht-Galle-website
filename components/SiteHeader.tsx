"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { COMPANY, asset } from "@/lib/site";

export default function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`site-head${scrolled ? " scrolled" : ""}`} id="top">
      <div className="wrap head-row">
        <a className="brand" href="#top" aria-label={`${COMPANY.short}, home`}>
          <Image src={asset("/brand/dpv-logo-horizontal.png")} alt={COMPANY.name} width={2000} height={650} priority sizes="160px" />
        </a>
        <nav className="nav" aria-label="Main">
          <a className="navlink" href="#services">Services</a>
          <a className="navlink" href="#galle">Why Galle</a>
          <a className="navlink" href="#process">How we work</a>
          <a className="btn btn-blue" href="#contact">Request a survey</a>
        </nav>
      </div>
    </header>
  );
}
