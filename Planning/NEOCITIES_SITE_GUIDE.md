# A practical roadmap for `helloteacher.neocities.org`

This plan is designed for a first website that will eventually become an expressive personal blog, design portfolio, art gallery, and CAD showcase. The recommended starting stack is deliberately small:

- **HTML** describes the content.
- **CSS** controls layout, appearance, and most animation.
- **JavaScript** adds behavior and richer interaction.
- **Neocities** publishes the finished static files.

You do not need React, a database, or a build system yet. Plain files are the quickest way to learn what the browser is actually doing, and they leave plenty of room for unusual visual design.

## 1. What you have now

The downloaded archive contains:

- `index.html` — the homepage visitors receive at `/`.
- `style.css` — the shared visual rules.
- `not_found.html` — Neocities' custom 404 page.
- `robots.txt` — instructions for cooperative search-engine and AI crawlers.
- `neocities.png` — the default hosting badge.

This is a sound blank slate. The existing HTML already includes the mobile viewport setting and connects to the stylesheet.

One important note: `robots.txt` does not make anything private. Every uploaded file should be treated as public. The current file allows normal search indexing and blocks only the crawler names that are uncommented.

## 2. The recommended site map

Start with five destinations. More sections can appear after these work well.

| Page | Purpose | Suggested URL |
| --- | --- | --- |
| Home | Introduction, newest post, and selected work | `/` |
| Work | Filterable index of art, design, and CAD projects | `/work/` |
| Project | One case study with images, process, and credits | `/work/project-name/` |
| Journal | Reverse-chronological list of posts | `/journal/` |
| About | Short biography, interests, tools, and contact links | `/about/` |

Useful later additions are `/now/`, `/links/`, `/sketchbook/`, and `/colophon/`. Resist creating empty categories just because they might be useful someday; let real content earn each new section.

The homepage should be a doorway, not an archive. A good first version contains a short introduction, three featured projects, the latest two journal entries, and one clear way to contact you.

## 3. Folder structure

Use lowercase names, hyphens instead of spaces, and descriptive filenames. A tidy first version looks like this:

```text
site/
├── index.html
├── not_found.html
├── robots.txt
├── about/
│   └── index.html
├── work/
│   ├── index.html
│   ├── lamp-concept/
│   │   └── index.html
│   └── robot-arm/
│       └── index.html
├── journal/
│   ├── index.html
│   └── 2026/
│       └── first-post/
│           └── index.html
└── assets/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    ├── images/
    │   ├── site/
    │   │   └── neocities.png
    │   └── work/
    │       ├── lamp-concept/
    │       └── robot-arm/
    ├── models/
    │   └── robot-arm.glb
    ├── fonts/
    └── icons/
```

Putting an `index.html` inside a folder gives clean URLs such as `/about/` and `/work/robot-arm/`. Keep media for each project in its own folder; `final-2-newest.png` becomes surprisingly mysterious six months later.

Begin with one CSS file and one JavaScript file. Split them only when navigation becomes genuinely difficult. A reasonable later CSS split is `base.css`, `layout.css`, `components.css`, and page-specific files.

## 4. The reusable page shell

Every page should use roughly the same semantic skeleton. The words and page-specific content change; the header, navigation, and footer stay consistent.

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="A concise description of this page.">
    <title>Page name — Hello Teacher</title>
    <link rel="stylesheet" href="/assets/css/style.css">
    <script src="/assets/js/main.js" defer></script>
  </head>
  <body>
    <a class="skip-link" href="#content">Skip to content</a>

    <header class="site-header">
      <a class="site-name" href="/">Hello Teacher</a>
      <nav aria-label="Primary navigation">
        <a href="/work/">Work</a>
        <a href="/journal/">Journal</a>
        <a href="/about/">About</a>
      </nav>
    </header>

    <main id="content">
      <h1>One clear page heading</h1>
      <!-- The page's unique content goes here. -->
    </main>

    <footer>
      <p>Made by hand. Hosted by Neocities.</p>
    </footer>
  </body>
</html>
```

Copying the small navigation between a handful of pages is acceptable at first. When keeping it synchronized becomes annoying, that is the right time to adopt a static-site generator. Do not use JavaScript to inject the only navigation: the page should remain usable if a script fails.

Use root-relative links such as `/assets/images/site/logo.svg`. They behave consistently on every nested page when served by Neocities. For local previewing, run a tiny web server rather than double-clicking the HTML file:

```sh
cd site
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## 5. A small design system before elaborate pages

Define a limited visual vocabulary in CSS first. These variables make later experimentation much less destructive:

```css
:root {
  --color-bg: #f5f1e8;
  --color-text: #171717;
  --color-accent: #db4a2b;
  --color-surface: #ffffff;
  --space-1: 0.5rem;
  --space-2: 1rem;
  --space-3: 2rem;
  --radius: 0.75rem;
  --page-width: 72rem;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: system-ui, sans-serif;
  line-height: 1.6;
}

img,
video,
canvas {
  display: block;
  max-width: 100%;
}

main,
.site-header,
footer {
  width: min(100% - 2rem, var(--page-width));
  margin-inline: auto;
}
```

Choose type, color, spacing, card style, link style, and mobile behavior before polishing animated details. Build mobile-first: begin with a single column, then add columns inside `@media (min-width: 48rem)` rules when there is room.

## 6. Portfolio and project pages

Each work card should be a real link with a thumbnail, title, category, and year. A project page can use this order:

1. Title, one-sentence summary, year, and role.
2. Strong hero image or a lightweight poster image for a 3D model.
3. The goal or prompt.
4. Process: sketches, iterations, CAD screenshots, failed directions.
5. Outcome and what you learned.
6. Tools, materials, collaborators, and credits.
7. Previous/next project links.

The process is usually more memorable than a grid of finished images. Write useful `alt` text for images that communicate information; use `alt=""` for genuinely decorative imagery.

For responsive portfolio images, export WebP or AVIF when practical, keep the original high-resolution master outside the website folder, and upload a web-sized copy. Use `loading="lazy"` below the first screen:

```html
<img
  src="/assets/images/work/robot-arm/detail.webp"
  alt="Close view of the arm's three-joint linkage"
  width="1200"
  height="800"
  loading="lazy"
>
```

The `width` and `height` prevent the page from jumping while the image downloads.

## 7. A blog without a database

Neocities cannot run WordPress, PHP, Node.js, or a database on its servers. A blog is therefore a collection of HTML pages.

For the first several posts:

1. Copy a good post template into `/journal/YYYY/post-title/index.html`.
2. Change its title, description, date, and article body.
3. Add a card or link to the top of `/journal/index.html`.
4. Add the newest post to the homepage if desired.
5. Upload the new files.

Use a real `<time>` element:

```html
<article>
  <header>
    <h1>Making the first prototype</h1>
    <p><time datetime="2026-06-22">June 22, 2026</time></p>
  </header>
  <p>Post content…</p>
</article>
```

Once you have about ten posts—or once copying templates stops being fun—move to a static-site generator such as Eleventy, Astro, Hugo, or Jekyll. It will turn Markdown posts and shared templates into ordinary HTML before upload. Neocities itself lists static-site generators as a supported workflow. **Eleventy** is a good eventual fit for this project because it is small, flexible, and does not require turning the site into a JavaScript application.

Later blog improvements can include an `rss.xml` feed, tag pages, previous/next links, and an archive grouped by year. They are useful, but none is required to publish the first post.

## 8. An interaction ladder

Add interaction in layers, testing keyboard and touch use at every stage.

### Layer 1: CSS states

Start with `:hover`, `:focus-visible`, transitions, transforms, and color changes. Anything available on hover must also be understandable without hover, because phones do not have a cursor.

```css
.project-card {
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.project-card:hover,
.project-card:focus-within {
  transform: translateY(-0.25rem);
}
```

### Layer 2: CSS animation

Use keyframes for decorative loops and page-entry motion. Animate `transform` and `opacity` when possible; they are generally smoother than continually changing layout properties.

Always respect reduced-motion preferences:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Layer 3: Small JavaScript behaviors

Good first scripts are a theme switch, gallery lightbox, work-category filters, expandable process notes, and elements that reveal as they enter the viewport. JavaScript should usually add or remove CSS classes; CSS remains responsible for appearance.

Build each interaction as a small independent component. If the script is removed, visitors should still be able to read the content and follow links.

### Layer 4: Canvas, WebGL, and 3D

Reserve canvas/WebGL for a feature that benefits from it, such as an interactive CAD viewer or a playful homepage scene. Load heavy code only on the pages that use it. A continuously running full-window effect can make an otherwise small art site unpleasant on phones.

For CAD work:

- Export a web preview as optimized `.glb` or `.gltf`; Neocities currently permits both, as well as `.obj` and `.dae`.
- Use a still poster image first and load the viewer after a click or when it approaches the viewport.
- Reduce polygon count and texture sizes in a copy of the model; keep the archival master untouched.
- Test a locally hosted viewer library or an iframe-based specialist viewer before committing to it.
- Host source files that use unsupported formats—such as STEP or STL, which are not on the current free-account allowlist—on an appropriate repository or model-sharing service and link to them.

Web Components such as `<model-viewer>` or a library such as Three.js can provide orbit controls and lighting, but add them only after the image-based case study is complete. The project page should still tell its story if 3D fails to load.

## 9. Features that need an outside service

Because the site has no server-side code, these require a third party or a simple alternative:

| Desired feature | Practical first solution |
| --- | --- |
| Contact | Visible email link (`mailto:`) or social/profile links |
| Comments | Link to a discussion elsewhere; add a hosted comment widget only if truly wanted |
| Guestbook | Use a guestbook service and link/embed it |
| Mailing list | Hosted newsletter signup form |
| Large video | Embed from a video host rather than uploading it |
| Large CAD downloads | Link to GitHub Releases or a model repository |
| Analytics | Neocities stats or a privacy-conscious external service |
| Search | A generated index/client-side search later; navigation and tags first |

Never place a secret API key in HTML or JavaScript. Visitors can inspect every client-side file.

## 10. Performance and accessibility guardrails

Treat these as part of the design rather than cleanup:

- The site must work at narrow phone widths without horizontal scrolling.
- Use one `<h1>` that names each page, followed by properly nested headings.
- Make every control reachable and understandable with a keyboard.
- Maintain visible focus styles and sufficient text contrast.
- Do not rely on color, sound, hover, or animation alone to communicate meaning.
- Avoid autoplaying audio. Give animation, sound, and 3D clear controls.
- Compress images and provide poster images for video and 3D.
- Lazy-load media below the fold, but not the main page image.
- Test with JavaScript disabled occasionally; the essential content and links should remain.
- Check the 404 page, broken links, image alt text, page titles, and descriptions before releases.

A useful initial performance budget is roughly 200 KB per gallery thumbnail and 500 KB for a large hero image. Models vary, but smaller is always kinder; make loading explicit when a model is several megabytes.

## 11. Publishing workflow

Keep one complete local copy as the source of truth. Edit and preview locally, then upload the changed files through the Neocities dashboard. Preserve the same folder structure online.

When manual uploads become tedious, the official Neocities command-line tool can push a whole directory and skip unchanged files. Put only publishable files inside `site/`; notes, original artwork, and source CAD should live beside it, not inside it.

Also keep the project in Git. Git is a versioned undo system: it lets you experiment boldly and recover earlier working versions. A simple rhythm is one commit after each working feature or finished page. Do not automate deployment until manual publishing feels understandable.

If a change appears missing online, try a hard refresh; browsers commonly cache CSS and JavaScript.

## 12. Recommended roadmap

There is no deadline implied here. Each phase should leave behind a usable website.

### Phase 0 — Establish a safe workspace

- Unzip the Neocities download into a local `site/` folder.
- Keep original art and CAD masters in separate non-published folders.
- Initialize Git and make a snapshot of the untouched starter.
- Learn to run the local preview server and use the browser inspector.

**Done when:** the same starter page works locally and online.

### Phase 1 — Content and navigation

- Write one sentence describing who the site is for and what it contains.
- Select three real projects and one short first post.
- Create the five-page map above and working navigation.
- Update the homepage title, description, visible introduction, and 404 page.

**Done when:** every navigation link goes somewhere useful, even if the styling is plain.

### Phase 2 — Visual foundation

- Choose a small color palette, type system, spacing scale, and page width.
- Create the shared header, footer, buttons, cards, and image treatment.
- Make the layout responsive from phone to desktop.
- Add visible focus styles and the reduced-motion rule.

**Done when:** all core pages feel related and remain readable at 320 px wide.

### Phase 3 — The first complete portfolio project

- Build one detailed project page using the case-study order above.
- Export and compress its images.
- Add its card to Work and Home.
- Test image loading, alt text, and previous/next navigation.

**Done when:** one project is good enough to send directly to another person.

### Phase 4 — Journal workflow

- Make a reusable post template.
- Publish the first post and add it to the Journal index.
- Write down the publishing checklist so the next post is routine.
- Add RSS only after posting itself feels easy.

**Done when:** a second post could be published without redesigning the site.

### Phase 5 — Purposeful interaction

- Add one CSS-based card or navigation animation.
- Add one small JavaScript component, such as filters or a lightbox.
- Test keyboard, touch, reduced-motion, and script-failure behavior.
- Keep an interaction only if it improves the experience or expresses the site's character.

**Done when:** the feature feels intentional and does not obscure the work.

### Phase 6 — CAD and richer media

- Optimize one model to GLB and create a still poster.
- Add a click-to-load 3D viewer on one project page.
- Test performance on a phone and a slower connection.
- Link externally to source downloads when their format is not supported.

**Done when:** the page is useful before the viewer loads and delightful after it does.

### Phase 7 — Automate only the repetition

- Consider Eleventy when shared navigation and post indexes become repetitive.
- Generate HTML locally and upload only the output folder.
- Adopt the Neocities CLI after the generated folder is predictable.
- Add automated link or HTML checks if the site grows large.

**Done when:** publishing is faster without making creative changes harder.

## 13. What to learn, in order

Do not try to “learn all of HTML” before building. Learn the next concept while using it.

1. HTML document structure, headings, paragraphs, links, images, lists, and semantic regions.
2. File paths and how pages link to assets and one another.
3. CSS selectors, the box model, colors, type, spacing, Flexbox, and Grid.
4. Responsive design, media queries, focus states, and reduced motion.
5. JavaScript values, functions, events, DOM selection, and class toggling.
6. More advanced animation, asynchronous loading, and 3D only as projects require them.
7. Static-site generation after you understand the HTML it produces.

Good references are the [Neocities tutorials page](https://neocities.org/tutorials) and MDN's structured [Learn Web Development](https://developer.mozilla.org/en-US/docs/Learn_web_development). Prefer MDN when looking up what an HTML element, CSS property, or browser API actually does.

## 14. Neocities constraints to design around

As checked on June 22, 2026:

- Neocities is static hosting: HTML, CSS, and browser-side JavaScript work; server-side PHP, Node.js, and databases do not.
- The free plan lists **1 GB storage** and **200 GB bandwidth**.
- Free sites have a restricted file-type allowlist and hotlink protection.
- Supported web assets currently include HTML, CSS, JavaScript, common image/font formats, PDF, Markdown, and several web-friendly 3D formats.
- The official CLI can upload a whole directory and skip unchanged files.
- Custom domains, unrestricted file types, and some other capabilities are supporter features.

Current primary sources: [plan comparison](https://neocities.org/supporter), [allowed file types](https://neocities.org/site_files/allowed_types), [hotlinking policy](https://neocities.org/site_files/hotlinking), [official CLI](https://neocities.org/cli), and [tutorials](https://neocities.org/tutorials).

## 15. The first concrete session

For the very next work session, do only this:

1. Create the folder structure through `about/`, `work/`, `journal/`, and `assets/`.
2. Move the shared CSS and badge into `assets/` and update their paths.
3. Replace the tutorial homepage with your name/site title, a two-sentence introduction, and the three navigation links.
4. Make plain but valid About, Work, and Journal pages from the shared shell.
5. Preview at phone and desktop widths, then upload.

That first version will not be the final aesthetic. It will be something more valuable: a complete, understandable skeleton that you can safely make strange.
