"use client";

import { useEffect, useState, type FormEvent } from "react";
import { CONTACT } from "@/lib/site";
import { SERVICES, SERVICE_ORDER, type ServiceId } from "@/lib/services";

export default function ContactSection() {
  const [note, setNote] = useState("");
  const [draft, setDraft] = useState("");
  const [interest, setInterest] = useState("Planning a future visit");
  const [discipline, setDiscipline] = useState<ServiceId | "">("");

  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get("service");
    if (requested && SERVICE_ORDER.includes(requested as ServiceId)) {
      setInterest("Yacht care & refit");
      setDiscipline(requested as ServiceId);
    }
  }, []);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const value = (key: string) => String(data.get(key) ?? "").trim();
    const recipient = value("recipient") === CONTACT.alternateEmail ? CONTACT.alternateEmail : CONTACT.email;
    const text = [
      "Yacht Club Galle enquiry", "",
      `Name: ${value("name")}`, `Email: ${value("email")}`, `Interest: ${interest}`,
      ...(discipline && interest === "Yacht care & refit" ? [`Service: ${SERVICES[discipline].name}`] : []),
      `Yacht / club: ${value("organisation")}`, "", value("message"),
    ].join("\n");
    setDraft(text);
    window.location.href = `mailto:${recipient}?subject=${encodeURIComponent(`Yacht Club Galle — ${interest}`)}&body=${encodeURIComponent(text)}`;
    setNote(`Your email app will open with your enquiry to ${recipient}. Send it there to reach us. You can also save a copy below.`);
  };

  const save = () => {
    const url = URL.createObjectURL(new Blob([draft], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "yacht-club-galle-enquiry.txt";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  return (
    <section className="contact-section" id="contact" aria-labelledby="contact-title">
      <div className="wrap contact-layout">
        <div>
          <p className="eyebrow">A personal connection</p>
          <h2 id="contact-title">Every journey starts<br />with <em>a conversation.</em></h2>
          <p>Tell us about your yacht, your club or the journey you have in mind. Let’s explore what a connection with Galle could look like.</p>
          <div className="contact-emails"><span className="eyebrow">Write to us</span><a href={`mailto:${CONTACT.email}`}>{CONTACT.email}<span aria-hidden="true">↗</span></a><a href={`mailto:${CONTACT.alternateEmail}`}>{CONTACT.alternateEmail}<span aria-hidden="true">↗</span></a></div>
          <div className="contact-location"><span className="location-mark" aria-hidden="true">↗</span><div><strong>Galle Harbour, Sri Lanka</strong><span>06°02′ N &nbsp; 80°12′ E</span></div></div>
          {CONTACT.phone && <a className="contact-phone" href={`tel:${CONTACT.phone.replace(/\s/g, "")}`}>{CONTACT.phone}</a>}
        </div>
        <form onSubmit={submit} onChange={() => { setDraft(""); setNote(""); }}>
          <div className="form-grid">
            <div className="field"><label htmlFor="enquiry-name">Your name *</label><input id="enquiry-name" name="name" autoComplete="name" placeholder="Full name" required maxLength={150} /></div>
            <div className="field"><label htmlFor="enquiry-email">Email address *</label><input id="enquiry-email" name="email" type="email" autoComplete="email" placeholder="you@example.com" required maxLength={254} /></div>
            <div className="field"><label htmlFor="enquiry-interest">I’m interested in</label><select id="enquiry-interest" name="interest" value={interest} onChange={event => setInterest(event.target.value)}><option>Planning a future visit</option><option>Yacht care & refit</option><option>International club partnership</option><option>Marine industry collaboration</option><option>Something else</option></select></div>
            <div className="field"><label htmlFor="enquiry-organisation">Yacht or club name</label><input id="enquiry-organisation" name="organisation" placeholder="Your yacht or organisation" maxLength={200} /></div>
            {interest === "Yacht care & refit" && <div className="field full"><label htmlFor="enquiry-discipline">Service of interest</label><select id="enquiry-discipline" name="discipline" value={discipline} onChange={event => setDiscipline(event.target.value as ServiceId | "")}><option value="">General yacht care enquiry</option>{SERVICE_ORDER.map(id => <option key={id} value={id}>{SERVICES[id].name}</option>)}</select></div>}
            <div className="field full"><label htmlFor="enquiry-recipient">Send your enquiry to</label><select id="enquiry-recipient" name="recipient"><option value={CONTACT.email}>{CONTACT.email}</option><option value={CONTACT.alternateEmail}>{CONTACT.alternateEmail}</option></select></div>
            <div className="field full"><label htmlFor="enquiry-message">Tell us a little more *</label><textarea id="enquiry-message" name="message" placeholder="Your plans, requirements or ideas…" required rows={3} maxLength={4000} /></div>
          </div>
          <div className="form-bottom"><p>Your enquiry opens in your email app. Details are only shared when you send.</p><button className="button button-navy" type="submit">Make an enquiry <span aria-hidden="true">↗</span></button></div>
          <p className="form-note" role="status">{note}</p>
          {draft && <div className="enquiry-preview"><pre>{draft}</pre><button type="button" className="editorial-link" onClick={save}>Save your enquiry <span aria-hidden="true">↓</span></button></div>}
        </form>
      </div>
    </section>
  );
}
