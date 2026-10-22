"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const links = [
  { href: "/#experience", label: "The experience" },
  { href: "/#destination", label: "Destination Galle" },
  { href: "/services/", label: "Services" },
  { href: "/#club-connections", label: "Club connections" },
];

export default function SiteHeader() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  return (
    <>
      <a href="#main-content" className="skip-link">Skip to content</a>
      <header className="site-head" id="top">
        <div className="wrap head-row">
          <Link className="brand" href="/" aria-label="Yacht Club Galle, home" onClick={() => setOpen(false)}>
            <Image src="/brand/yacht-club-galle.png" alt="Yacht Club Galle" width={1536} height={1024} sizes="150px" priority />
          </Link>
          <nav className="desktop-nav" aria-label="Main">
            {links.map(link => <Link key={link.href} href={link.href} aria-current={pathname === link.href ? "page" : undefined}>{link.label}</Link>)}
          </nav>
          <Link className="header-enquiry" href="/contact/" aria-current={pathname === "/contact/" ? "page" : undefined}>Contact us <span aria-hidden="true">↗</span></Link>
          <button className="menu-toggle" type="button" aria-expanded={open} aria-controls="mobile-navigation" onClick={() => setOpen(!open)} aria-label={open ? "Close menu" : "Open menu"}>{open ? "Close −" : "Menu +"}</button>
        </div>
        <nav className="mobile-nav" id="mobile-navigation" aria-label="Mobile" hidden={!open}>
          {links.map(link => <Link key={link.href} href={link.href} onClick={() => setOpen(false)}>{link.label}</Link>)}
          <Link href="/contact/" onClick={() => setOpen(false)}>Contact us ↗</Link>
        </nav>
      </header>
    </>
  );
}
