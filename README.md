# Yacht Club Galle

A marketing website for the developing Yacht Club Galle concept, aimed at yacht owners, captains and international yacht clubs. The design uses the supplied Yacht Club Galle logo, an ivory and navy palette, editorial typography and the local WebP photography in `public/web`.

The public copy covers the destination, yacht care, international club connections and the marine experience behind the vision. Facilities and partnerships are presented as developing ambitions. The source letter, its recipient and its official request are not published.

## Run locally

Requires Node.js 20.9 or newer.

```sh
npm ci
npm run dev
```

Copy `.env.example` to `.env.local` and enter the public contact details before launch. Never enter credentials in `NEXT_PUBLIC_` settings.

## Enquiries

- `NEXT_PUBLIC_CONTACT_EMAIL` defaults to `info@dpvoffshore.lk`.
- `NEXT_PUBLIC_CONTACT_EMAIL_ALTERNATE` defaults to `info@dpvoffshore.com`. Both addresses appear on the Contact page and in the footer; visitors choose a recipient in the form.
- The form opens the visitor’s email application with their enquiry filled in. The visitor must send it there; nothing is sent or stored on a server by the website. A downloadable text copy is also available.
- `NEXT_PUBLIC_CONTACT_PHONE` optionally displays a telephone link.
- `NEXT_PUBLIC_SITE_URL` sets the absolute base URL used for social metadata.

Rebuild after changing public environment variables. The WhatsApp setting is retained for compatibility but the current homepage does not use it.

## Verify and deploy

```sh
npm run typecheck
npm run build
npm start
```

For a static export, set `STATIC_EXPORT=true` before running `npm run build`. Publish the resulting `out` folder using the repository's existing deployment workflow. The page and enquiry draft work without a backend.

## Main files

- `app/page.tsx`: the destination and marketing content.
- `app/services/page.tsx`: dedicated Services page, interactive 3D yacht and six service disciplines.
- `app/contact/page.tsx`: dedicated Contact page, direct email links and enquiry form.
- `app/globals.css`: responsive layouts, colours, typography and motion.
- `app/layout.tsx`: metadata and self-hosted Archivo font.
- `components/SiteHeader.tsx`: desktop navigation and mobile menu.
- `components/HeroSlideshow.tsx`: six-slide crossfade, pause control and reduced-motion support.
- `components/ContactSection.tsx`: enquiry form, email handoff and downloadable draft.
- `components/SiteFooter.tsx`: brand and footer navigation.
- `lib/site.ts`: public contact settings and site name.
- `public/brand/yacht-club-galle.png`: supplied logo, preserved unchanged.
- `public/web`: desktop and mobile yacht photographs.

The Services page restores the interactive 3D yacht, with part selection, inside view, camera movement and optional rotation. Its sage highlights and ivory stage match the current visual style. Choosing a service and following its enquiry link prefills the Contact page. The model and three.js load only as the explorer approaches the viewport; the homepage does not load them. Trailing-slash routes produce `services/index.html` and `contact/index.html` for static hosting.

## Assets

Archivo is self-hosted under the SIL Open Font License; see `app/fonts/LICENSE-Archivo-OFL.txt`. The supplied logo and photography retain their existing ownership.
