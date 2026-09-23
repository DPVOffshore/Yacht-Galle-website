import SiteHeader from "@/components/SiteHeader";
import Hero from "@/components/Hero";
import YachtExplorer from "@/components/yacht/YachtExplorer";
import Statement from "@/components/Statement";
import Audiences from "@/components/Audiences";
import Process from "@/components/Process";
import ContactSection from "@/components/ContactSection";
import SiteFooter from "@/components/SiteFooter";
import Motion from "@/components/Motion";

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main>
        <Hero />
        <YachtExplorer />
        <Statement />
        <Audiences />
        <Process />
        <ContactSection />
      </main>
      <SiteFooter />
      <Motion />
    </>
  );
}
