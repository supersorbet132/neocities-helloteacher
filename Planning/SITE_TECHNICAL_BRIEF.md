# HELLOTEACHER technical brief

Purpose: a condensed reference for explaining how this portfolio site works, what technical ideas it uses, and what knowledge would be required to build or maintain it.


## 1. Architecture in one paragraph

This is a static Neocities site. Each page is an HTML file served directly by the browser. The shared stylesheet, `kombucha.css`, contains nearly all visual design, layout, responsive behavior, and CSS animation. The JavaScript files in `assets/js/` add behavior: parallax, sprite-card setup, gallery layout, modals, project readers, WebGL background effects, a Three.js CAD model viewer, and journal parsing. There is no server, database, user login, or build system. The browser downloads files and runs the JavaScript locally.

## 2. Main file map

- `index.html`: homepage and directory to the rest of the site.
- `kombucha.css`: shared visual system for all pages.
- `assets/js/main.js`: homepage parallax, homepage cards, shared sprite-card behavior, touch hover replacement.
- `assets/js/shader-background.js`: WebGL animated gradient/wave background.
- `art/index.html`: art gallery shell.
- `assets/js/art-manifest.js`: artwork manifest data.
- `assets/js/art-gallery.js`: dynamic art gallery layout, viewer, dragging, tilt, year navigation.
- `projects/index.html`: project tabs and project reader markup.
- `assets/js/projects.js`: project interactions, FLIP-like transitions, comic viewer, BEET zoom viewer, poker iframe mounting.
- `cad/index.html`: CAD page shell, import map for Three.js, modal viewer markup.
- `assets/js/cad-display.js`: CAD display sprite setup and modal open/close events.
- `assets/js/cad-model-viewer.js`: lazy-loaded Three.js model viewer.
- `assets/js/cad-archive.js`: CAD archive/filter behavior.
- `journal/index.html`: journal page shell.
- `assets/js/journal.js`: journal text parser and reader modal.
- `assets/data/journal-entries.txt`: journal source content.
- `assets/data/art-descriptions.json`: art description data.
- `assets/models/Phone_holder_assembled.glb`: 3D CAD model.
- `games/poker/`: browser game build currently intended to be embedded in a project reader.

## 3. HTML knowledge used

HTML provides the site skeleton.

Important concepts:

- `<!doctype html>`, `<html>`, `<head>`, `<body>`: base document structure.
- `<meta name="viewport">`: tells mobile browsers to size the page to the device width.
- `<link rel="stylesheet">`: connects the CSS file.
- `<script defer>`: loads JavaScript after HTML parsing without blocking the initial page structure.
- `<main>`, `<section>`, `<nav>`, `<footer>`, `<article>`: semantic page regions.
- `<button>` for interactive controls instead of clickable `<div>` elements.
- `<dialog>`-style modal patterns, or dialog-like components, for art/project/CAD readers.
- `aria-label`, `aria-hidden`, `aria-expanded`, `aria-controls`: accessibility metadata.
- Empty `alt=""` on decorative images so screen readers can skip them.
- `data-*` attributes such as `data-gradient-shader`, `data-parallax-scene`, and `data-project-tab`: hooks that JavaScript can query without relying only on visual class names.


## 4. CSS knowledge used

CSS is the main engine of the site's art direction.

Core CSS ideas:

- Cascade and specificity: later or more specific rules override earlier rules.
- CSS custom properties: variables such as `--home-unit`, `--sprite-left`, and `--poker-parallax-x` act like tuning dials.
- `position: relative` on a stage plus `position: absolute` on child sprites: lets images be placed precisely inside a controlled composition.
- `aspect-ratio`: preserves designed proportions for scenes, cards, artwork, and viewers.
- `transform`: moves, scales, and rotates visual elements without changing document layout.
- `translate3d(...)`: encourages compositor-friendly movement for many animated layers.
- `opacity`: fades elements in and out cheaply.
- `transition`: animates between two visual states, such as rest and hover.
- `@keyframes`: defines repeating animation cycles.
- `mix-blend-mode`: lets layers visually blend with what is behind them, such as screen, multiply, color-dodge, or hard-light style effects.
- `mask-image` and `-webkit-mask-image`: clip an image to the alpha shape of another image or gradient.
- `clip-path`: cuts an element into a custom shape or animates a visible region.
- `filter`: creates effects like blur, contrast, brightness, or drop shadow, though it can be more expensive than transforms.
- `will-change`: hints that an element will animate, useful in moderation.
- `@media`: changes layout based on viewport size, aspect ratio, input type, or motion preference.
- `@supports`: provides fallbacks when newer CSS features are unavailable.
- `container-type: size` plus `cqw`/`cqh`: lets child elements size themselves relative to their own container.
- `clamp(min, preferred, max)`: keeps sizes responsive without becoming extreme.
- `svh`/`dvh`: newer viewport-height units that behave better around mobile browser address bars than old `vh`.

## 5. Aspect ratios and positioning

The site often uses a source-canvas approach. A visual scene is treated as if it was designed at a known pixel size, then CSS scales positions proportionally.

Example idea:

```css
--home-source-width: 2560;
--home-unit: calc(100vw / var(--home-source-width));
```

If a design was composed at 2560px wide, then `1 * var(--home-unit)` equals one source pixel scaled to the current viewport width. This lets many sprite coordinates scale together.

For project tabs, the site also uses container-relative units:

```css
container-type: size;
width: 10cqw;
```

`1cqw` means 1 percent of the container's width. This is useful when the art inside a card should respond to the card size, not the full browser window.

Important tradeoff:

- This technique is strong for preserving a designed composition.
- It still needs separate responsive rules for unusual phones, tablets, browser zoom levels, and very wide or narrow screens.


## 6. Transformations and animation

Most motion is based on `transform` and `opacity`.

Why that matters:

- Animating `top`, `left`, `width`, or `height` can trigger layout recalculation.
- Animating `transform` and `opacity` is usually cheaper because browsers can often handle it on the compositor.
- This is why many sprites can hover, drift, scale, or parallax without completely reflowing the page.

Examples of transform-based effects:

- Hover states: sprites move from rest positions to active positions.
- Parallax: layers shift at different speeds.
- Floating loops: sprites bob or drift using `requestAnimationFrame` plus CSS variables.
- Project transitions: temporary visual layers move with `translate3d`.
- Gallery motion: artworks translate, tilt, and settle with inertia.

Performance caveat:

- "Transform is cheap" does not mean unlimited.
- Hundreds of large transparent PNG/WebP layers can still cost memory, image decoding time, paint time, and GPU compositing resources.
- The size of the image and number of animated layers matter as much as the CSS property being animated.

## 7. JavaScript knowledge used

JavaScript provides behavior and state.

Core JS/browser concepts:

- `document.querySelector(...)` and `querySelectorAll(...)`: find HTML elements.
- `classList.add/remove/toggle`: change visual state by changing classes.
- `dataset`: read `data-*` attributes from HTML.
- `addEventListener`: respond to clicks, pointer movement, keyboard input, resize, scroll, and visibility changes.
- Pointer events: unified mouse, stylus, and touch-ish input handling.
- Touch-specific logic: detects coarse pointer devices and substitutes hover with scroll-centered focus states.
- `requestAnimationFrame`: schedules animation work in sync with the browser's paint cycle.
- `matchMedia`: detects reduced motion, touch capability, and desktop pointer conditions.
- `IntersectionObserver`: detects when elements are near or inside the viewport, useful for lazy loading and deferring work.
- `fetch`: loads JSON/text files such as manifests and journal entries.
- `CustomEvent`: lets one script announce a state change to another script.
- `getBoundingClientRect`: measures element position and size on screen.
- `ResizeObserver`: responds when a rendered element changes size.
- `Promise` and `async/await`: manage loading steps such as dynamic imports or images.
- `iframe`: embeds the poker browser build inside the projects page.


## 8. Homepage systems

The homepage has three major layers:

1. Static HTML structure.
2. CSS-staged artwork and sprite cards.
3. JavaScript-controlled parallax and shader animation.

Important systems:

- Background canvas: the `<canvas data-gradient-shader>` element is used by WebGL.
- Layered artwork: images have `data-parallax-speed` values so each layer scrolls differently.
- Directory cards: each page link is represented by a sprite-card composition.
- Sprite manifests: JavaScript loads crop data, creates sprite layers, and sets CSS variables for positions.
- Touch behavior: on touch devices, the centered card can activate a hover-like state because real hover does not exist.

## 9. Art gallery systems

The art page is a small client-side gallery app.

Knowledge involved:

- Manifest-driven rendering: artwork data is stored in JavaScript/JSON-like structures instead of hard-coded entirely in HTML.
- Year grouping: artworks are grouped and navigated by year.
- Responsive layout calculation: JavaScript calculates card positions based on viewport size and artwork aspect ratios.
- Deterministic randomness: seeded shuffle/jitter makes the layout feel organic while remaining repeatable.
- Lazy image loading: preview images load first, full images load when needed.
- Pointer interaction: artworks can tilt, drag, or respond to hover/pointer movement.
- Inertia: after dragging, motion can continue briefly and slow down.
- Modal/lightbox viewer: clicking an artwork opens a larger view with descriptions.


## 10. Projects page systems

The projects page is one of the most technically dense parts of the site.

Major pieces:

- Project tabs: large interactive entries for comic, BEET, and poker.
- Project reader: a modal-like expanded view for a selected project.
- FLIP-like transitions: the script measures the project tab, creates a temporary visual flyer/snapshot, and animates it into the reader.
- Comic reader: chapter/page navigation for sequential images.
- BEET viewer: image zooming, panning, thumbnails, and preview switching.
- Poker embed: an iframe is mounted only when the poker project opens.
- Deferred images: some images are loaded later to reduce initial page cost.
- Input handling: hover, pointer movement, touch scroll, keyboard, and close actions all update reader state.

FLIP explanation:

```text
First: measure where the element starts.
Last: measure where it should end.
Invert: temporarily transform it so it visually appears to still be at the start.
Play: animate the transform away so it lands in the final state.
```


Poker caveat:

- The original game was Python/Pygame.
- Static websites cannot run ordinary Python scripts directly in the browser.
- The browser version depends on a compatible build output.
- Neocities free hosting blocks some unsupported file types, so the embedded game may need a different host, a simplified JavaScript rewrite, a video demo, or an itch.io link.


## 11. CAD page systems

The CAD page combines a sprite-based visual interface with a lazy-loaded 3D viewer.

Knowledge involved:

- Import maps: map the name `three` to CDN-hosted Three.js module URLs.
- Dynamic imports: load Three.js, `GLTFLoader`, and `OrbitControls` only when needed.
- `.glb` model format: a binary 3D asset format that can contain geometry, materials, and scene data.
- Three.js scene: contains objects, lights, camera, and renderer.
- Camera: defines what part of the 3D world is visible.
- Renderer: draws the scene onto a canvas using WebGL.
- OrbitControls: lets the user rotate, pan, or zoom the model.
- Resize handling: updates renderer size and camera aspect ratio when the viewer changes size.
- Pixel-ratio cap: limits rendering resolution on high-DPI screens to avoid excess GPU cost.
- Visibility handling: stops rendering when the viewer is closed or the document is hidden.


## 12. WebGL and shader background

WebGL is a browser API for drawing through the GPU. It is lower-level than normal CSS or Canvas 2D.

Core concepts:

- Canvas: the drawing surface in the page.
- WebGL context: the API object used to send drawing commands to the GPU.
- Vertex shader: positions geometry. In this site, the geometry is basically a full-screen triangle/quad.
- Fragment shader: decides the color of each pixel.
- Uniforms: values passed from JavaScript into the shader, such as time, scroll position, resolution, speed, and strength.
- Textures: image-like GPU memory. This site uses textures not only for pictures, but also to store simulation state.
- Framebuffers: offscreen render targets. The shader can draw into a texture, then use that texture in the next frame.
- Ping-pong simulation: two textures alternate between read and write targets so the animation can evolve over time.
- FPS cap: the background targets a limited frame rate rather than running at maximum speed.
- Resolution scale: the shader renders smaller than the actual screen, then scales up visually.

Why this is used:

- CSS gradients are easy but limited.
- WebGL allows fluid, procedural, time-based effects.
- The result can look more organic and less template-like.

Why it is potentially expensive:

- It runs continuously while visible.
- It uses GPU memory and per-frame GPU work.
- Larger canvas resolution means many more pixels to shade.

Optimization choices:

- Use `powerPreference: "low-power"`.
- Disable antialiasing, depth, and stencil buffers.
- Cap device pixel ratio.
- Render at a reduced resolution.
- Cap FPS.
- Stop when `document.hidden`.
- Disable for `prefers-reduced-motion`.
- Hide the canvas if WebGL fails.


## 13. Performance concepts

Performance is about total browser cost, not just one technique.

Main costs:

- HTML parse cost: usually low here.
- CSS parse and style calculation: moderate because the stylesheet is large.
- Layout: calculating where elements go.
- Paint: drawing pixels, shadows, filters, masks, and images.
- Compositing: combining layers, especially transformed/transparent elements.
- Image decode: converting compressed images like WebP or PNG into pixels.
- GPU memory: storing canvases, textures, large images, and composited layers.
- JavaScript main-thread work: layout measurement, event handling, calculations.

Optimizations already used:

- Prefer `transform` and `opacity`.
- Use `requestAnimationFrame` for visual updates.
- Use passive listeners for scroll/pointer cases where possible.
- Use WebP for many art assets.
- Use `loading="lazy"` and `decoding="async"` on many images.
- Lazy-load or defer heavier systems.
- Use `IntersectionObserver` for deferred image behavior.
- Cap WebGL resolution and frame rate.
- Cap Three.js renderer pixel ratio.
- Stop animation loops when not needed.
- Support `prefers-reduced-motion`.

Risks to watch:

- Too many animated sprites at once can still lag.
- Large transparent images are costly even if much of the visible area is empty.
- Blend modes, filters, masks, and shadows can trigger extra paint/compositing work.
- Mobile Safari and older browsers can behave differently from desktop Chrome.
- Aspect-ratio-specific art direction can break on unusual screens without targeted responsive rules.

## 14. Responsive design knowledge

Responsive design means the site adapts to different widths, heights, aspect ratios, browsers, and input types.

Concepts used or relevant:

- Fluid widths: use percentages, viewport units, and `clamp()`.
- Breakpoints: use `@media` to change layout at certain widths/aspect ratios.
- Aspect-ratio queries: handle very wide or very tall screens.
- Touch queries: `(hover: none) and (pointer: coarse)` helps detect phone/tablet-style input.
- Desktop pointer queries: `(hover: hover) and (pointer: fine)` helps detect mouse/trackpad behavior.
- Safe viewport units: `svh` and `dvh` reduce mobile address-bar issues.
- Minimum hit targets: buttons/links need enough physical size on touch screens.
- Avoid hover-only information: touch devices need tap, focus, scroll, or explicit controls.

## 15. Accessibility knowledge

Accessibility matters even for an art site.

Useful concepts:

- Semantic landmarks: `<main>`, `<nav>`, `<section>`, `<footer>`.
- Keyboard access: buttons should be reachable and usable by keyboard.
- Focus management: when a modal opens, focus should move into it; when it closes, focus should return.
- Escape-to-close: common modal behavior.
- `aria-expanded` and `aria-controls`: tell assistive tech what a button opens.
- `aria-hidden`: hides purely decorative visual layers.
- Alt text: meaningful images need descriptions; decorative images should use `alt=""`.
- Reduced motion: users who request less motion should not receive intense animation.
- Color contrast: text should remain readable over complex backgrounds.


## 16. Why `kombucha.css` is over 8000 lines

The CSS file is large because the site is not a generic page layout. It is an art-directed interactive site.

The file includes:

- Global variables and colors.
- Shared base layout rules.
- Homepage artwork staging.
- Homepage sprite-card systems.
- CAD page layout and display styling.
- Projects page tab art, project reader, comic reader, BEET viewer, and poker frame.
- Journal page layout.
- Art gallery layout, viewer, depth effects, and animation.
- Dozens of keyframe animations.
- Many custom properties used as tuning dials.
- Responsive overrides.
- Browser-support fallbacks.
- Reduced-motion rules.

Why this happened:

- Each page has a distinct visual system.
- Many sprites have hand-tuned positions.
- A lot of rules encode art direction rather than reusable business UI.
- The CSS has grown as one shared file instead of being split into page-specific files.


## 17. Static hosting and Neocities constraints

Neocities serves static files.

That means it is good for:

- HTML.
- CSS.
- JavaScript.
- Images.
- Fonts.
- Audio/video.
- JSON/text files.
- Some model files, depending on file type and plan support.

It is not the same as a backend server.

Static hosting does not directly run:

- Python scripts.
- Pygame applications.
- Databases.
- Server-side authentication.
- Backend API logic.

This is why the poker game is difficult. A desktop Python/Pygame game must be converted into a browser-compatible format, rewritten in web tech, or hosted somewhere designed for games.

High-confidence topics:

- The site is static and file-based.
- HTML provides semantic structure and data hooks.
- CSS controls the majority of layout, art direction, and animation.
- JavaScript coordinates interactivity and browser APIs.
- The site uses transform/opacity animations for performance.
- The layout uses aspect-ratio stages and CSS variables for art-directed scaling.
- The homepage uses parallax layers and a WebGL shader canvas.
- The CAD page uses Three.js to load a `.glb` model.
- The project reader uses FLIP-like transitions.
- The art gallery is data-driven and dynamically rendered.
- Neocities cannot directly run ordinary Python/Pygame files.
- Cross-device responsive behavior is one of the active learning areas.


Question: Why did you use plain HTML/CSS/JS instead of React?

Answer:

> Because Neocities is static hosting and the site is mostly content, visuals, and client-side interaction. Plain files keep deployment simple and helped me learn what the browser is doing directly. If the site grew into a larger app, I would consider a framework or static-site generator.

Question: Why is the CSS file so large?

Answer:

> The CSS contains the art direction: sprite positioning, animation timing, page-specific layouts, responsive overrides, and reduced-motion fallbacks. It is large because the site is highly custom. I would eventually split it into smaller page-specific files for maintainability.

Question: How does the site handle performance?

Answer:

> Most animation uses transform and opacity. Heavier systems are deferred or lazy-loaded, WebGL runs at reduced resolution and capped FPS, images are often WebP/lazy-loaded, and motion can be reduced for users who prefer reduced motion.

Question: What is WebGL doing here?

Answer:

> WebGL renders the animated background shader. JavaScript passes time, scroll, and size values into GPU shaders, and the shader computes the visual effect pixel by pixel.

Question: What is Three.js doing here?

Answer:

> Three.js powers the CAD model viewer. It handles the scene, camera, renderer, model loading, lighting, and orbit controls so I do not have to write raw WebGL model rendering from scratch.

Question: What would you improve next?

Answer:

> I would improve responsive robustness, split the CSS into maintainable sections, test across more browsers/devices, create fallbacks for the poker project, and continue tightening accessibility.

## 20. Fast glossary

- Static site: a site made of files served as-is, without server-side code.
- DOM: the browser's live tree representation of HTML.
- CSS variable: a reusable CSS value written like `--name`.
- Viewport: the visible browser area.
- Aspect ratio: width divided by height.
- Compositor: browser layer system that can animate some visual changes efficiently.
- Reflow/layout: browser recalculation of element positions and sizes.
- Paint: drawing pixels for elements.
- Transform: CSS movement/scale/rotation that usually avoids layout recalculation.
- Parallax: depth illusion where layers move at different rates.
- Shader: small GPU program that calculates vertex positions or pixel colors.
- WebGL: browser API for GPU rendering.
- Three.js: JavaScript library that simplifies 3D WebGL work.
- GLB: binary 3D model file format.
- FLIP: First, Last, Invert, Play animation technique.
- iframe: an embedded page inside another page.
- Lazy loading: delaying work or assets until needed.
- Progressive enhancement: adding advanced effects when supported while preserving basic functionality.
- Reduced motion: user setting indicating that heavy animation should be minimized.
