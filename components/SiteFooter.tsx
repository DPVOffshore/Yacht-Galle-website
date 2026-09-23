import Image from "next/image";
import { COMPANY, asset } from "@/lib/site";
import { Waves } from "./Waves";

export default function SiteFooter() {
  return (
    <footer>
      <div className="wrap" data-reveal="draw">
        <Waves />
      </div>
      <div className="wrap foot" data-stagger>
        <Image src={asset("/brand/dpv-logo-horizontal.png")} alt={COMPANY.name} width={2000} height={650} sizes="140px" />
        <p>
          {COMPANY.name}, {COMPANY.city}. © {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
