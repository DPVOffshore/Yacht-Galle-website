import Image from "next/image";
import Link from "next/link";
import { CONTACT } from "@/lib/site";

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="wrap footer-main">
        <Link className="footer-brand" href="/" aria-label="Yacht Club Galle, home"><Image src="/brand/yacht-club-galle.png" alt="Yacht Club Galle" width={1536} height={1024} sizes="210px" /></Link>
        <p>A new perspective on life at sea.<br /><span>Galle · Sri Lanka · Indian Ocean</span></p>
        <div className="footer-contacts"><Link className="editorial-link" href="/contact/">Begin a conversation <span aria-hidden="true">↗</span></Link><a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a><a href={`mailto:${CONTACT.alternateEmail}`}>{CONTACT.alternateEmail}</a></div>
      </div>
      <div className="wrap footer-bottom"><p>© {new Date().getFullYear()} Yacht Club Galle</p><p>A vision by DPV Offshore & Marine Services</p><div className="footer-pages"><Link href="/services/">Services</Link><Link href="/contact/">Contact</Link><Link href="/#club-connections">For international yacht clubs ↗</Link></div></div>
    </footer>
  );
}
