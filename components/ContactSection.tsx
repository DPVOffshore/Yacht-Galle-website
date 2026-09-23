"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { SERVICES, SERVICE_ORDER, type ServiceId } from "@/lib/services";
import { CONTACT } from "@/lib/site";
import { ASK_EVENT } from "@/lib/events";
import { Motif } from "./Waves";
import { Split } from "./Split";

const LOCATIONS = ["Berthed at Galle Port", "Arriving at Galle soon", "Elsewhere in Sri Lanka", "In the Maldives", "Other"];

export default function ContactSection() {
  const [service, setService] = useState<ServiceId | "">("");
  const [note, setNote] = useState("");
  const nameRef = useRef<HTMLInputElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);

  // "Ask about this service" in the 3D explorer preselects the service and focuses the form.
  useEffect(() => {
    const onAsk = (e: Event) => {
      setService((e as CustomEvent<ServiceId | null>).detail ?? "");
      window.setTimeout(() => nameRef.current?.focus({ preventScroll: true }), 600);
    };
    window.addEventListener(ASK_EVENT, onAsk);
    return () => window.removeEventListener(ASK_EVENT, onAsk);
  }, []);

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const submitter = (e.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null;
    const via = submitter?.dataset.via ?? "email";
    const data = new FormData(e.currentTarget);
    const get = (k: string) => String(data.get(k) ?? "").trim();

    const name = get("name");
    const email = get("email");
    if (!name) {
      setNote("Add your name so we know who to reply to.");
      nameRef.current?.focus();
      return;
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setNote("Add a valid email address so we can reply.");
      emailRef.current?.focus();
      return;
    }

    const svc = service ? SERVICES[service].name : "Not sure yet";
    const body = [
      `Name: ${name}`,
      `Email: ${email}`,
      `Phone or WhatsApp: ${get("phone") || "-"}`,
      `Yacht: ${get("yacht") || "-"}`,
      `Length overall: ${get("length") ? `${get("length")} m` : "-"}`,
      `Location: ${get("where")}`,
      `Service: ${svc}`,
      "",
      get("message"),
    ].join("\n");

    if (via === "whatsapp") {
      if (!CONTACT.whatsapp) {
        setNote("WhatsApp isn't connected yet. Please use email, or call the number above.");
        return;
      }
      window.open(`https://wa.me/${CONTACT.whatsapp}?text=${encodeURIComponent(`Survey request\n\n${body}`)}`, "_blank", "noopener");
      setNote("WhatsApp opened with your request. Send it there to reach us.");
    } else {
      if (!CONTACT.email) {
        setNote("Email isn't connected yet. Please try WhatsApp, or call the number above.");
        return;
      }
      const subject = `Survey request: ${get("yacht") || name}`;
      window.location.href = `mailto:${CONTACT.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      setNote("Your email app opened with the request. Send it there to reach us.");
    }
  };

  return (
    <section className="block" id="contact" aria-labelledby="contact-title">
      <div className="wrap contact">
        <div>
          <Motif />
          <h2 className="display split" id="contact-title" data-reveal="words">
            <Split text="Tell us about" />
            <br />
            <Split text="your yacht." from={3} />
          </h2>
          <p className="lede" style={{ marginTop: 28, "--d": 400 } as React.CSSProperties} data-reveal>
            Send the details and we&apos;ll reply with next steps and a proposed time to come aboard.
          </p>
          <dl className="details" data-stagger>
            <div>
              <dt>Phone and WhatsApp</dt>
              {CONTACT.phone ? (
                <dd>
                  <a href={`tel:${CONTACT.phone.replace(/\s/g, "")}`} style={{ textDecoration: "none" }}>{CONTACT.phone}</a>
                </dd>
              ) : (
                <dd className="todo">Number to be added</dd>
              )}
            </div>
            <div>
              <dt>Email</dt>
              {CONTACT.email ? (
                <dd>
                  <a href={`mailto:${CONTACT.email}`} style={{ textDecoration: "none" }}>{CONTACT.email}</a>
                </dd>
              ) : (
                <dd className="todo">Email to be added</dd>
              )}
            </div>
            <div>
              <dt>Location</dt>
              <dd>{CONTACT.location}</dd>
            </div>
          </dl>
        </div>

        <form onSubmit={onSubmit} noValidate data-stagger>
          <div className="field">
            <label htmlFor="f-name">Your name</label>
            <input id="f-name" name="name" autoComplete="name" required ref={nameRef} />
          </div>
          <div className="field">
            <label htmlFor="f-email">Email</label>
            <input id="f-email" name="email" type="email" autoComplete="email" required ref={emailRef} />
          </div>
          <div className="field">
            <label htmlFor="f-phone">Phone or WhatsApp</label>
            <input id="f-phone" name="phone" type="tel" autoComplete="tel" />
          </div>
          <div className="field">
            <label htmlFor="f-yacht">Yacht name</label>
            <input id="f-yacht" name="yacht" />
          </div>
          <div className="field">
            <label htmlFor="f-length">Length overall (metres)</label>
            <input id="f-length" name="length" inputMode="decimal" />
          </div>
          <div className="field">
            <label htmlFor="f-where">Where is the yacht?</label>
            <select id="f-where" name="where" defaultValue={LOCATIONS[0]}>
              {LOCATIONS.map((l) => (
                <option key={l}>{l}</option>
              ))}
            </select>
          </div>
          <div className="field full">
            <label htmlFor="f-svc">Service needed</label>
            <select id="f-svc" name="service" value={service} onChange={(e) => setService(e.target.value as ServiceId | "")}>
              <option value="">Not sure yet</option>
              {SERVICE_ORDER.map((id) => (
                <option key={id} value={id}>
                  {SERVICES[id].name}
                </option>
              ))}
            </select>
          </div>
          <div className="field full">
            <label htmlFor="f-msg">What needs doing?</label>
            <textarea id="f-msg" name="message" placeholder="Describe the issue, and any dates we should work around." />
          </div>
          <div className="form-actions">
            <button className="btn btn-blue" type="submit" data-via="email">Send by email</button>
            <button className="btn btn-line" type="submit" data-via="whatsapp">Send on WhatsApp</button>
          </div>
          <p className="form-note" role="status">{note}</p>
        </form>
      </div>
    </section>
  );
}
