# DPV Offshore: yacht refit and repair at Galle Port

Website for **DPV Offshore Marine Services (Pvt) Ltd**. The centrepiece is an interactive 3D yacht: visitors turn it, tap a part and see the service that covers it. They can also look inside at the engine room, electrical systems and cabins.

Built with **Next.js 16** (App Router), **React 19**, **TypeScript** and **three.js**.

---

## Quick start

Requirements: **Node.js 20.9 or newer** (Node 22 recommended, see `.nvmrc`).

```bash
npm install
cp .env.example .env.local     # then fill in your contact details
npm run dev                    # http://localhost:3000
```

Production build:

```bash
npm run build
npm start
```

| Script                | What it does                                                     |
| --------------------- | ---------------------------------------------------------------- |
| `npm run dev`         | Development server with hot reload                               |
| `npm run build`       | Production build                                                 |
| `npm start`           | Serve the production build                                       |
| `npm run typecheck`   | TypeScript check without building                                |
| `npm run model:build` | Rebuild the detailed 3D model from the original (needs Python 3) |

---

## Before you launch

1. **Contact details.** Set these in `.env.local`, or in your hosting dashboard:
   - `NEXT_PUBLIC_CONTACT_PHONE`: shown on the page, e.g. `+94 77 123 4567`
   - `NEXT_PUBLIC_CONTACT_WHATSAPP`: digits only with country code, e.g. `94771234567`
   - `NEXT_PUBLIC_CONTACT_EMAIL`: where survey requests are sent
   - `NEXT_PUBLIC_SITE_URL`: your live domain, used for social share images

   Until the phone number and email are set, the page shows "to be added" and the send buttons explain that they aren't connected yet.

2. **Check the claims.** The four "How a job runs" steps (in `components/Process.tsx`) describe commitments such as photo progress updates and a sea-trial report. Confirm that the Sri Lanka team works this way.

3. **Form delivery.** The survey form opens the visitor's email app or WhatsApp with the request filled in. No server is needed. To receive requests directly instead, add a Next.js route handler (`app/api/survey/route.ts`) that sends email through a provider such as Resend or Postmark, and point the form at it.

---

## Project structure

```
app/
  layout.tsx              Fonts, metadata, viewport
  page.tsx                Page composition
  globals.css             All styles (white base, DPV blue and red accents)
  fonts/                  Archivo variable font (self-hosted) and its OFL licence
  icon.png, apple-icon.png, opengraph-image.png

components/
  SiteHeader.tsx          Sticky header with logo and navigation
  Hero.tsx                Headline, calls to action, wave line marking Galle
  yacht/
    YachtExplorer.tsx     Full-bleed 3D section: heading, service card, controls (client)
    YachtViewer.ts        three.js viewer: loading, inside view, highlighting, picking, camera
  Statement.tsx           Brand statement
  Audiences.tsx           "Built for the yachts that call at Galle"
  Process.tsx             "How a job runs"
  ContactSection.tsx      Survey request form (client)
  SiteFooter.tsx
  Waves.tsx               Double-wave motif from the logo

lib/
  services.ts             The six services: copy, 3D part mapping, camera views, hover labels
  site.ts                 Contact settings, company name, model URL, wave paths
  events.ts               Event linking "Ask about this service" to the form

public/
  models/dpv-luxury-yacht-detailed.glb   The 3D model served to visitors
  brand/                                 Original logos (colours unchanged)

scripts/model/
  build_detailed_model.py  Builds the detailed model from the original
  geom.py                  Geometry library (rounded boxes, lathes, swept tubes, lofts)
  source/dpv-luxury-yacht.glb   Original model (input)
  requirements.txt

docs/brochure/             Original DPV brochure (reference only, not served)
```

---

## The 3D explorer

### How it works

- `YachtExplorer.tsx` renders the overlays in React and creates a `YachtViewer` when the section scrolls near the viewport. three.js is loaded on demand, so it doesn't slow the first page load.
- `YachtViewer.ts` loads `/models/dpv-luxury-yacht-detailed.glb` and shows loading progress.
  - **Selecting a service** fades the rest of the yacht to pale and moves the camera to that service's view.
  - **The inside view** turns the hull see-through and outlines it in blue.
  - **Tapping a part** selects its service. On a computer, hovering over a part shows its name.
- **Colour when selected.** The new detailed parts keep their true colours (red valve covers, copper heat exchangers). Parts from the original model that have no colour of their own, such as the white hull, turn DPV blue.
- **Camera framing.** The camera uses a view offset so the yacht stays centred in the open space beside the floating service card.

### Changing services or camera views

Everything is in `lib/services.ts`:

- `parts`: exact node names from the original model
- `prefixes`: name prefixes of the added parts (`eng_`, `elec_`, `nav_`, `int_`, `hull_str_`, `hw_`)
- `xray`: whether the service opens the inside view
- `cam`: camera position and target, in metres (bow is +x, starboard is +z, up is +y)
- `PART_LABELS`: hover names, matched by the longest prefix

### Rebuilding the detailed model

The detailed model is generated from the original by a Python script. Every added part is fitted to the measured hull shape and checked to sit inside it.

```bash
pip install -r scripts/model/requirements.txt
npm run model:build        # writes public/models/dpv-luxury-yacht-detailed.glb
```

The script adds the following, and prints any parts that would poke through the hull:

- **Engine room:** twin V12 diesels, gearboxes, shafts, exhaust and mufflers, and fuel tanks shaped to the hull.
- **Electrical:** generator, batteries, switchboard, inverters, cable trays and lights.
- **Navigation:** helm displays, radar, satcom and antennas.
- **Interior:** cabins, bulkheads with doors, stairs, galley and tables.
- **Hardware:** swim ladder, anchor and chain.
- **Propeller fix:** it seats the propellers on their pod drives and makes them counter-rotate.

If you replace the original with a more accurate hull model from the builder, keep the node names used in `lib/services.ts`, or update them. Then rerun the script.

### Model size

The detailed model is about 7.8 MB. It is cached for a day (see `next.config.ts`) and only loads when the visitor reaches the 3D section. To shrink it by roughly 70–80%, you can compress it with [glTF Transform](https://gltf-transform.dev):

```bash
npx @gltf-transform/cli optimize public/models/dpv-luxury-yacht-detailed.glb public/models/dpv-luxury-yacht-detailed.glb --compress meshopt
```

If you do, register the decoder in `YachtViewer.ts`:

```ts
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);
```

Test the result in the browser before deploying.

---

## Design

- **Colours:** white base (`#FFFFFF`), text `#1D2935` and `#5B6773`. DPV blue `#195C8F` is used for headlines, buttons and highlights, and DPV red `#BA2127` for small accents only. The logo is used in its original colours.
- **Type:** Archivo. Headlines use the expanded width at light weight, and body text uses the normal width.
- **Motif:** the double wave from the logo, used in the hero with a red marker for Galle, above section headings and along the footer.
- **Motion:** the hero waves draw in once, and the camera glides between views. Both respect the visitor's reduced-motion setting.

---

## Deployment

**Vercel:** import the repository, set the environment variables, and deploy. No extra configuration is needed.

**Any Node host:** run `npm ci && npm run build && npm start`, with the port set by the `PORT` variable.

---

## Credits and licences

- Archivo typeface © The Archivo Project Authors, SIL Open Font License 1.1 (`app/fonts/LICENSE-Archivo-OFL.txt`).
- three.js, MIT licence.
- DPV logos and brochure © DPV Offshore Marine Services.
