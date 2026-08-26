(() => {
	const gallery = document.querySelector("[data-art-gallery]");
	const homeLink = document.querySelector("[data-art-home-link]");

	if (!gallery) {
		return;
	}

	const ARTWORKS = Array.isArray(window.HELLOTEACHER_ARTWORK_MANIFEST)
		? window.HELLOTEACHER_ARTWORK_MANIFEST
		: [];

	const THUMB_ROOT = "/assets/images/art/thumbs/";
	const FULL_ROOT = "/assets/images/art/artworks/";
	const DESCRIPTION_SRC = "/assets/data/art-descriptions.json";
	const DRAG_THRESHOLD = 7;
	const INERTIA_MIN_SPEED = 0.018;
	const INERTIA_FRICTION = 0.86;
	const INERTIA_RELEASE_DAMPING = 0.42;
	const INERTIA_MAX_VELOCITY = 1.05;
	const PARALLAX_LAYER_BOOST = 0.82;
	const PARALLAX_SCROLL_SCALE = 0.24;
	const TILT_MAX_DEGREES = 18;
	const LAYOUT_SEED = 0xA7172026;
	const LAYOUT_EDGE_PAD_RATIO = 0.035;
	const LAYOUT_EDGE_PAD_MIN = 30;
	const LAYOUT_EDGE_PAD_MAX = 70;
	const LAYOUT_COLUMN_GAP_RATIO = 0.031;
	const LAYOUT_COLUMN_GAP_MIN = 16;
	const LAYOUT_COLUMN_GAP_MAX = 52;
	const LAYOUT_HORIZONTAL_OVERLAP_RATIO = 0.27;
	const LAYOUT_HORIZONTAL_OVERLAP_MOBILE_RATIO = 0.14;
	const LAYOUT_HORIZONTAL_OVERLAP_MAX = 120;
	const LAYOUT_EDGE_OVERLAP_RATIO = 0.16;
	const LAYOUT_EDGE_OVERLAP_MOBILE_RATIO = 0.08;
	const LAYOUT_ROW_CLEARANCE_RATIO = 0.17;
	const LAYOUT_ROW_CLEARANCE_MIN = 64;
	const LAYOUT_ROW_CLEARANCE_MAX = 205;
	const LAYOUT_TOP_PAD_RATIO = 0.26;
	const LAYOUT_TOP_PAD_MIN = 150;
	const LAYOUT_TOP_PAD_MAX = 280;
	const LAYOUT_BOTTOM_PAD_RATIO = 0.18;
	const LAYOUT_BOTTOM_PAD_MIN = 80;
	const LAYOUT_BOTTOM_PAD_MAX = 220;
	const LAYOUT_MIN_VIEWPORT_HEIGHTS = 2.45;
	const LAYOUT_JITTER_X_MAX = 34;
	const LAYOUT_JITTER_Y_MAX = 42;
	const LAYOUT_ROW_STAGGER_X_MAX = 118;
	const LAYOUT_ROW_STAGGER_Y_MAX = 54;
	const LAYOUT_ITEM_SCATTER_X_MAX = 72;
	const LAYOUT_ITEM_SCATTER_Y_MAX = 62;
	const DRIFT_VIEWPORT_MARGIN_RATIO = 0.66;
	const DRIFT_MIN_DURATION = 10;
	const DRIFT_MAX_DURATION = 18;
	const DRIFT_X_MAX = 14;
	const DRIFT_Y_MAX = 18;
	const DRIFT_ROTATE_MAX = 0.7;
	const DRIFT_START_DELAY_MAX = 1.8;
	const DRIFT_SETTLE_MS = 360;
	const RELAYOUT_WIDTH_THRESHOLD = 12;
	const VISIBLE_YEAR_LAYER_COUNT = 4;
	const DEPTH_ATTRIBUTE_LAYER_COUNT = 6;
	const DEPTH_IMAGE_LAYER_COUNT = 1;
	const COLOR_SCROLL_SAMPLE_STEP = 18;
	const DEPTH_PARALLAX_SCROLL_SCALE = 0.62;
	const YEAR_TRANSITION_MS = 940;
	const YEAR_ACTIVE_SCALE = 1;
	const YEAR_BACK_SCALE = 0.12;
	const YEAR_BACK_SCALE_POWER = 0.72;
	const YEAR_FUTURE_SCALE = 2.18;
	const YEAR_FUTURE_SCALE_STEP = 0.18;
	const YEAR_DEPTH_Y_MAX = 54;
	const YEAR_FUTURE_Y = -36;
	const GRADIENT_STOPS = [
		{ position: 0, hex: "#81F5FC" },
		{ position: 0.5, hex: "#DB63C2" },
		{ position: 1, hex: "#3935AB" },
	];
	const DEPTH_TINT_SATURATION = 0.68;
	const DEPTH_FRONT_LIGHTNESS = 0.12;
	const DEPTH_BACK_LIGHTNESS = 0.6;
	const DEPTH_TOP_LIGHTNESS_OFFSET = 0.25;
	const DEPTH_BOTTOM_LIGHTNESS_OFFSET = -0.08;
	const DEPTH_BOTTOM_BACK_LIGHTNESS_OFFSET = -0.16;
	const DEPTH_BOTTOM_BACK_DARKEN_START = 0.56;
	const DEPTH_BOTTOM_BACK_DARKEN_POWER = 1.35;
	const DEPTH_FRONT_PARALLAX = 0.26;
	const DEPTH_BACK_PARALLAX = 0.045;
	const DEPTH_IMAGE_FRONT_OPACITY = 0.4;
	const DEPTH_IMAGE_BACK_OPACITY = 0.2;
	const VIEWER_SIDE_LAYOUT_MIN_WIDTH = 760;
	const VIEWER_DESCRIPTION_MIN_WIDTH = 260;
	const VIEWER_DESCRIPTION_MAX_WIDTH = 380;
	const VIEWER_DESCRIPTION_STACK_MIN_HEIGHT = 124;
	const VIEWER_DESCRIPTION_STACK_MAX_HEIGHT = 190;

	const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
	const lerp = (from, to, progress) => from + ((to - from) * progress);
	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

	const hashString = (value) => {
		let hash = 2166136261;

		for (let index = 0; index < value.length; index += 1) {
			hash ^= value.charCodeAt(index);
			hash = Math.imul(hash, 16777619);
		}

		return hash >>> 0;
	};

	const seededRandom = (seed) => {
		let state = seed >>> 0;

		return () => {
			state += 0x6D2B79F5;
			let result = state;
			result = Math.imul(result ^ (result >>> 15), result | 1);
			result ^= result + Math.imul(result ^ (result >>> 7), result | 61);

			return ((result ^ (result >>> 14)) >>> 0) / 4294967296;
		};
	};

	const shuffleWithSeed = (items, seed) => {
		const shuffled = [...items];
		const random = seededRandom(seed);

		for (let index = shuffled.length - 1; index > 0; index -= 1) {
			const swapIndex = Math.floor(random() * (index + 1));
			[shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
		}

		return shuffled;
	};

	const hexToRgb = (hex) => {
		const normalized = hex.replace("#", "");
		const value = Number.parseInt(normalized, 16);

		return {
			r: (value >> 16) & 255,
			g: (value >> 8) & 255,
			b: value & 255,
		};
	};

	const rgbToHsl = ({ r, g, b }) => {
		const red = r / 255;
		const green = g / 255;
		const blue = b / 255;
		const max = Math.max(red, green, blue);
		const min = Math.min(red, green, blue);
		const lightness = (max + min) / 2;

		if (max === min) {
			return { h: 0, s: 0, l: lightness };
		}

		const delta = max - min;
		const saturation = lightness > 0.5
			? delta / (2 - max - min)
			: delta / (max + min);
		let hue;

		if (max === red) {
			hue = ((green - blue) / delta) + (green < blue ? 6 : 0);
		} else if (max === green) {
			hue = ((blue - red) / delta) + 2;
		} else {
			hue = ((red - green) / delta) + 4;
		}

		return {
			h: hue * 60,
			s: saturation,
			l: lightness,
		};
	};

	const gradientStops = GRADIENT_STOPS.map((stop) => ({
		...stop,
		rgb: hexToRgb(stop.hex),
	}));

	const sampleGradient = (progress) => {
		const clamped = clamp(progress, 0, 1);
		let first = gradientStops[0];
		let second = gradientStops[gradientStops.length - 1];

		for (let index = 0; index < gradientStops.length - 1; index += 1) {
			if (clamped >= gradientStops[index].position && clamped <= gradientStops[index + 1].position) {
				first = gradientStops[index];
				second = gradientStops[index + 1];
				break;
			}
		}

		const span = Math.max(second.position - first.position, 0.0001);
		const localProgress = (clamped - first.position) / span;

		return rgbToHsl({
			r: lerp(first.rgb.r, second.rgb.r, localProgress),
			g: lerp(first.rgb.g, second.rgb.g, localProgress),
			b: lerp(first.rgb.b, second.rgb.b, localProgress),
		});
	};

	const titleFromFile = (file) => file
		.replace(/\.[^.]+$/, "")
		.replace(/[-_]+/g, " ")
		.replace(/\b\w/g, (letter) => letter.toUpperCase());

	const getViewport = () => ({
		width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
		height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
	});

	const getFieldHeight = () => Math.max(currentLayoutHeight || 0, window.innerHeight || 0, 1);

	const getMetrics = () => ({
		fieldHeight: getFieldHeight(),
		scrollY: window.scrollY,
		width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
		height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
	});

	const getColumns = (viewportWidth) => {
		if (viewportWidth < 560) {
			return 2;
		}

		if (viewportWidth < 1100) {
			return 3;
		}

		if (viewportWidth < 1700) {
			return 4;
		}

		return 5;
	};

	const getCardWidth = (artwork, viewportWidth) => {
		const random = seededRandom(hashString(`${artwork.key}-size`));
		const aspect = artwork.width / artwork.height;
		const minWidth = viewportWidth < 520 ? 150 : viewportWidth < 850 ? 220 : 270;
		const maxWidth = viewportWidth < 520 ? 230 : viewportWidth < 850 ? 340 : viewportWidth < 1240 ? 430 : 520;
		let width = lerp(minWidth, maxWidth, 0.35 + (random() * 0.65));

		if (aspect > 1.8) {
			width *= 1.18;
		} else if (aspect < 0.82) {
			width *= 0.9;
		}

		return Math.round(clamp(width, minWidth, maxWidth + 70));
	};

	const getLayoutMetrics = (viewport) => {
		const isSmall = viewport.width < 520;

		return {
			edgePad: clamp(
				viewport.width * LAYOUT_EDGE_PAD_RATIO,
				isSmall ? 28 : LAYOUT_EDGE_PAD_MIN,
				isSmall ? 52 : LAYOUT_EDGE_PAD_MAX
			),
			columnGap: clamp(
				viewport.width * LAYOUT_COLUMN_GAP_RATIO,
				isSmall ? 10 : LAYOUT_COLUMN_GAP_MIN,
				isSmall ? 26 : LAYOUT_COLUMN_GAP_MAX
			),
			rowClearance: clamp(
				viewport.height * (isSmall ? 0.16 : LAYOUT_ROW_CLEARANCE_RATIO),
				isSmall ? 46 : LAYOUT_ROW_CLEARANCE_MIN,
				isSmall ? 108 : LAYOUT_ROW_CLEARANCE_MAX
			),
			topPad: clamp(
				viewport.height * (isSmall ? 0.24 : LAYOUT_TOP_PAD_RATIO),
				isSmall ? 132 : LAYOUT_TOP_PAD_MIN,
				isSmall ? 190 : LAYOUT_TOP_PAD_MAX
			),
			bottomPad: clamp(
				viewport.height * LAYOUT_BOTTOM_PAD_RATIO,
				LAYOUT_BOTTOM_PAD_MIN,
				LAYOUT_BOTTOM_PAD_MAX
			),
		};
	};

	const constrainLayoutPosition = (state, x, y, metrics, galleryHeight) => {
		const viewport = getViewport();
		const overlapRatio = viewport.width < 520
			? LAYOUT_EDGE_OVERLAP_MOBILE_RATIO
			: LAYOUT_EDGE_OVERLAP_RATIO;
		const minX = -state.cardWidth * overlapRatio;
		const maxX = Math.max(minX, viewport.width - (state.cardWidth * (1 - overlapRatio)));
		const maxY = Math.max(metrics.topPad, galleryHeight - state.cardHeight - metrics.bottomPad * 0.45);

		return {
			x: clamp(x, minX, maxX),
			y: clamp(y, metrics.topPad * 0.5, maxY),
		};
	};

	const getFullArtworkSrc = (artwork) => {
		const yearSegment = artwork.year ? `${artwork.year}/` : "";
		const file = artwork.fullFile || artwork.file;

		if (artwork.hasFull === false) {
			return `${THUMB_ROOT}${artwork.year}/${artwork.file}`;
		}

		return `${FULL_ROOT}${yearSegment}${file}`;
	};

	const getPreviewArtworkSrc = (artwork) => (
		artwork.hasThumb === false
			? getFullArtworkSrc(artwork)
			: `${THUMB_ROOT}${artwork.year}/${artwork.file}`
	);

	const normalizedArtworks = ARTWORKS
		.map((artwork) => {
			const id = artwork.file.replace(/\.[^.]+$/, "");
			const title = artwork.title || titleFromFile(artwork.file);

			return {
				...artwork,
				id,
				key: `${artwork.year}:${id}`,
				title,
				fullSrc: getFullArtworkSrc(artwork),
				thumbSrc: `${THUMB_ROOT}${artwork.year}/${artwork.file}`,
				previewSrc: getPreviewArtworkSrc(artwork),
			};
		})
		.sort((first, second) => {
			if (first.year === second.year) {
				return first.id.localeCompare(second.id);
			}

			return Number.parseInt(second.year, 10) - Number.parseInt(first.year, 10);
		});

	const createYearGroups = () => {
		const groups = new Map();

		normalizedArtworks.forEach((artwork) => {
			if (!groups.has(artwork.year)) {
				groups.set(artwork.year, []);
			}

			groups.get(artwork.year).push(artwork);
		});

		return [...groups.entries()]
			.sort((first, second) => Number.parseInt(second[0], 10) - Number.parseInt(first[0], 10))
			.map(([year, artworks]) => ({
				year,
				artworks,
				layer: null,
				title: null,
				titleHint: null,
				states: [],
				topLayerRank: artworks.length - 1,
				depthSlot: 0,
				layoutHeight: 0,
			}));
	};

	const yearGroups = createYearGroups();

	if (yearGroups.length === 0) {
		return;
	}

	const initialYearIndex = 0;
	let activeYearIndex = initialYearIndex;
	let states = [];
	let activeDrag = null;
	let resizeQueued = false;
	let lastLayoutWidth = 0;
	let lastLayoutColumns = 0;
	let currentLayoutHeight = 0;
	let galleryPageTop = 0;
	let activeTilt = null;
	let tiltQueued = false;
	let activeFoilTilt = null;
	let foilTiltQueued = false;
	let viewerState = null;
	let artworkDescriptions = {};
	let activeDescriptionGlint = null;
	let descriptionGlintQueued = false;
	let renderQueued = false;
	let pendingFullRender = false;
	let pendingDepthRender = false;
	let lastColorScrollY = null;
	let lastColorHeight = null;
	let isYearTransitioning = false;
	let yearTransitionTimer = null;
	let yearTransitionFrame = null;
	let transitionFromIndex = null;
	let transitionToIndex = null;

	window.HELLOTEACHER_ARTWORKS = normalizedArtworks;
	window.HELLOTEACHER_ACTIVE_ART_YEAR = yearGroups[activeYearIndex].year;

	const waitForImageReady = (image) => {
		const timeout = new Promise((resolve) => {
			window.setTimeout(resolve, 160);
		});

		if (typeof image.decode === "function") {
			return Promise.race([
				image.decode().catch(() => {}),
				timeout,
			]);
		}

		if (image.complete) {
			return Promise.resolve();
		}

		return Promise.race([
			new Promise((resolve) => {
				image.addEventListener("load", resolve, { once: true });
				image.addEventListener("error", resolve, { once: true });
			}),
			timeout,
		]);
	};

	const viewer = document.createElement("div");
	viewer.className = "art-viewer";
	viewer.setAttribute("aria-hidden", "true");
	viewer.setAttribute("data-art-viewer", "");

	const viewerImage = document.createElement("img");
	viewerImage.className = "art-viewer__image";
	viewerImage.alt = "";
	viewerImage.decoding = "async";
	viewerImage.draggable = false;
	viewer.append(viewerImage);

	const viewerDescription = document.createElement("aside");
	viewerDescription.className = "art-viewer__description";
	viewerDescription.setAttribute("aria-label", "Artwork description");

	const viewerDescriptionTitle = document.createElement("h2");
	viewerDescriptionTitle.className = "art-viewer__description-title";

	const viewerDescriptionMeta = document.createElement("p");
	viewerDescriptionMeta.className = "art-viewer__description-meta";

	const viewerDescriptionBody = document.createElement("p");
	viewerDescriptionBody.className = "art-viewer__description-body";

	viewerDescription.append(viewerDescriptionTitle, viewerDescriptionMeta, viewerDescriptionBody);
	viewer.append(viewerDescription);
	document.body.append(viewer);

	const loadArtworkDescriptions = () => {
		if (typeof window.fetch !== "function") {
			return;
		}

		window.fetch(DESCRIPTION_SRC, { cache: "no-store" })
			.then((response) => {
				if (!response.ok) {
					throw new Error(`Description request failed: ${response.status}`);
				}

				return response.json();
			})
			.then((data) => {
				artworkDescriptions = data?.artworks && typeof data.artworks === "object"
					? data.artworks
					: {};

				if (viewerState) {
					renderViewerDescription(viewerState.source.artwork);
				}
			})
			.catch(() => {
				artworkDescriptions = {};
			});
	};

	const getArtworkDescription = (artwork) => {
		const entry = artworkDescriptions[artwork.key]
			|| artworkDescriptions[artwork.id]
			|| artworkDescriptions[artwork.file]
			|| {};

		return {
			title: entry.title || artwork.title,
			year: entry.year || artwork.year || "",
			medium: entry.medium || "",
			description: typeof entry.description === "string" ? entry.description : "",
		};
	};

	const renderViewerDescription = (artwork) => {
		const entry = getArtworkDescription(artwork);
		const meta = [entry.year, entry.medium].filter(Boolean).join(" / ");

		viewerDescriptionTitle.textContent = entry.title;
		viewerDescriptionMeta.textContent = meta;
		viewerDescriptionMeta.hidden = meta.length === 0;
		viewerDescriptionBody.textContent = entry.description;
	};

	const positionViewerDescription = (target) => {
		viewerDescription.dataset.layout = target.description.layout;
		viewerDescription.style.width = `${target.description.width}px`;
		viewerDescription.style.maxHeight = `${target.description.maxHeight}px`;
		viewerDescription.style.setProperty("--description-x", `${target.description.left}px`);
		viewerDescription.style.setProperty("--description-y", `${target.description.top}px`);
	};

	const ensureImageLoaded = (state) => {
		if (state.image.dataset.loaded === "true") {
			return;
		}

		state.image.dataset.loaded = "true";
		state.image.src = state.artwork.previewSrc;
		state.imageWrap.style.setProperty("--artwork-mask-image", `url("${state.artwork.previewSrc}")`);
	};

	const releaseImageMask = (state) => {
		state.imageWrap.style.setProperty("--artwork-mask-image", "none");
		state.image.removeAttribute("src");
		state.image.dataset.loaded = "false";
	};

	const measureParallaxContext = () => {
		const viewport = getViewport();
		const scrollCenter = viewport.height * 0.5;
		const galleryProgress = clamp((window.scrollY + scrollCenter - galleryPageTop) / Math.max(currentLayoutHeight, 1), 0, 1);
		const scrollTravel = currentLayoutHeight * PARALLAX_SCROLL_SCALE;
		const depthScrollTravel = viewport.height * DEPTH_PARALLAX_SCROLL_SCALE;

		return {
			galleryProgress,
			scrollTravel,
			depthScrollTravel,
		};
	};

	const calculateParallaxY = (context, effectiveParallax) => (
		-context.scrollTravel * context.galleryProgress * effectiveParallax
	);

	const calculateDepthParallaxY = (context, effectiveParallax) => (
		-context.depthScrollTravel * context.galleryProgress * effectiveParallax
	);

	const getDepthProgress = (depthSlot) => (
		clamp(depthSlot / Math.max(DEPTH_ATTRIBUTE_LAYER_COUNT - 1, 1), 0, 1)
	);

	const getLayerAttributes = (depthSlot) => {
		if (depthSlot < 0) {
			const futureDepth = Math.min(Math.abs(depthSlot), 4);

			return {
				depthProgress: 0,
				scale: YEAR_FUTURE_SCALE + ((futureDepth - 1) * YEAR_FUTURE_SCALE_STEP),
				opacity: 0,
				y: YEAR_FUTURE_Y * futureDepth,
				parallax: 0,
				zIndex: 140 + futureDepth,
			};
		}

		const depthProgress = getDepthProgress(depthSlot);

		return {
			depthProgress,
			scale: lerp(YEAR_ACTIVE_SCALE, YEAR_BACK_SCALE, Math.pow(depthProgress, YEAR_BACK_SCALE_POWER)),
			opacity: lerp(1, 0.88, depthProgress),
			y: lerp(0, YEAR_DEPTH_Y_MAX, depthProgress),
			parallax: lerp(DEPTH_FRONT_PARALLAX, DEPTH_BACK_PARALLAX, depthProgress),
			zIndex: 120 - depthSlot,
		};
	};

	const updateZoomOrigin = () => {
		const viewport = getViewport();
		const originY = clamp(
			window.scrollY + (viewport.height * 0.52) - galleryPageTop,
			0,
			Math.max(currentLayoutHeight, viewport.height)
		);

		gallery.style.setProperty("--art-zoom-origin-y", `${originY.toFixed(2)}px`);
	};

	const updateLayerColors = (metrics, colorScrollY = metrics.scrollY) => {
		const sampleProgress = clamp((colorScrollY + (metrics.height * 0.5)) / metrics.fieldHeight, 0, 1);
		const gradient = sampleGradient(sampleProgress);
		const saturation = clamp(gradient.s * DEPTH_TINT_SATURATION, 0, 1);
		const pageLightnessOffset = lerp(DEPTH_TOP_LIGHTNESS_OFFSET, DEPTH_BOTTOM_LIGHTNESS_OFFSET, sampleProgress);
		const bottomBackProgress = Math.pow(
			clamp((sampleProgress - DEPTH_BOTTOM_BACK_DARKEN_START) / (1 - DEPTH_BOTTOM_BACK_DARKEN_START), 0, 1),
			DEPTH_BOTTOM_BACK_DARKEN_POWER
		);

		yearGroups.forEach((group) => {
			if (!group.isVisible) {
				return;
			}

			const depthSlot = Math.max(group.depthSlot, 0);
			const depthProgress = getDepthProgress(depthSlot);
			const layerLightness = lerp(DEPTH_FRONT_LIGHTNESS, DEPTH_BACK_LIGHTNESS, depthProgress);
			const backOnlyOffset = DEPTH_BOTTOM_BACK_LIGHTNESS_OFFSET * bottomBackProgress * depthProgress;
			const lightness = clamp(layerLightness + pageLightnessOffset + backOnlyOffset, 0, 1);

			group.layer.style.color = `hsl(${gradient.h.toFixed(1)} ${Math.round(saturation * 100)}% ${Math.round(lightness * 100)}%)`;
			group.layer.style.setProperty("--year-depth-image-opacity", lerp(DEPTH_IMAGE_FRONT_OPACITY, DEPTH_IMAGE_BACK_OPACITY, depthProgress).toFixed(3));
		});
	};

	const getActiveGroup = () => yearGroups[activeYearIndex];
	const getActiveStates = () => getActiveGroup()?.states || [];

	const renderArtwork = (state, parallaxContext, includeGeometry = false, useCardParallax = true) => {
		state.parallaxY = useCardParallax
			? calculateParallaxY(parallaxContext, state.effectiveParallax)
			: 0;
		state.card.style.setProperty("--artwork-parallax-y", `${state.parallaxY.toFixed(2)}px`);

		if (!includeGeometry) {
			return;
		}

		state.card.style.setProperty("--artwork-x", `${state.x.toFixed(2)}px`);
		state.card.style.setProperty("--artwork-y", `${state.y.toFixed(2)}px`);
		state.card.style.setProperty("--artwork-z", state.zIndex);
		state.card.style.setProperty("--artwork-width", `${state.cardWidth}px`);
		state.card.style.setProperty("--artwork-aspect", (state.cardWidth / state.cardHeight).toFixed(5));
	};

	const clearDriftSettle = (state) => {
		if (state.driftSettleTimer) {
			window.clearTimeout(state.driftSettleTimer);
			state.driftSettleTimer = null;
		}

		if (!state.driftWrap) {
			return;
		}

		state.driftWrap.style.animation = "";
		state.driftWrap.style.transition = "";
		state.driftWrap.style.transform = "";
	};

	const settleDriftToNeutral = (state) => {
		if (!state.driftWrap || !state.isDriftActive) {
			return;
		}

		const currentTransform = window.getComputedStyle(state.driftWrap).transform;

		state.isDriftActive = false;
		state.card.classList.remove("is-drift-active");

		if (!currentTransform || currentTransform === "none") {
			clearDriftSettle(state);
			return;
		}

		if (state.driftSettleTimer) {
			window.clearTimeout(state.driftSettleTimer);
		}

		state.driftWrap.style.animation = "none";
		state.driftWrap.style.transition = "none";
		state.driftWrap.style.transform = currentTransform;
		state.driftWrap.getBoundingClientRect();
		state.driftWrap.style.transition = `transform ${DRIFT_SETTLE_MS}ms cubic-bezier(0.16, 0.92, 0.18, 1)`;
		state.driftWrap.style.transform = "translate3d(0, 0, 0) rotate(0deg)";
		state.driftSettleTimer = window.setTimeout(() => clearDriftSettle(state), DRIFT_SETTLE_MS + 80);
	};

	const settleActiveDriftToNeutral = () => {
		getActiveStates().forEach(settleDriftToNeutral);
	};

	const setDriftActive = (state, isActive) => {
		const shouldBeActive = isActive
			&& state.isActive
			&& !viewerState
			&& !isYearTransitioning
			&& !reduceMotion.matches;

		if (state.isDriftActive === shouldBeActive) {
			return;
		}

		if (shouldBeActive) {
			clearDriftSettle(state);
		}

		state.isDriftActive = shouldBeActive;
		state.card.classList.toggle("is-drift-active", shouldBeActive);
	};

	const updateDriftActivation = (metrics) => {
		const activeStates = getActiveStates();

		if (reduceMotion.matches || viewerState || isYearTransitioning) {
			activeStates.forEach((state) => setDriftActive(state, false));
			return;
		}

		const viewportTop = metrics.scrollY - galleryPageTop;
		const margin = metrics.height * DRIFT_VIEWPORT_MARGIN_RATIO;
		const activationTop = viewportTop - margin;
		const activationBottom = viewportTop + metrics.height + margin;

		activeStates.forEach((state) => {
			const visualTop = state.y + state.parallaxY;
			const visualBottom = visualTop + state.cardHeight;
			const shouldDrift = visualBottom >= activationTop && visualTop <= activationBottom;

			setDriftActive(state, shouldDrift);
		});
	};

	const renderAll = ({ includeGeometry = false, includeDepthGeometry = false } = {}) => {
		const metrics = getMetrics();
		const colorScrollY = Math.round(metrics.scrollY / COLOR_SCROLL_SAMPLE_STEP) * COLOR_SCROLL_SAMPLE_STEP;
		const shouldUpdateColor = colorScrollY !== lastColorScrollY
			|| metrics.fieldHeight !== lastColorHeight;
		const parallaxContext = measureParallaxContext();

		if (includeGeometry) {
			updateZoomOrigin();
		}

		if (shouldUpdateColor) {
			updateLayerColors(metrics, colorScrollY);
			lastColorScrollY = colorScrollY;
			lastColorHeight = metrics.fieldHeight;
		}

		yearGroups.forEach((group) => {
			if (!group.isVisible) {
				return;
			}

			const isActiveGroup = group.depthSlot === 0;
			const layerParallaxY = isActiveGroup
				? 0
				: calculateDepthParallaxY(parallaxContext, group.layerParallax || 0);
			group.layer.style.setProperty("--year-scroll-y", `${layerParallaxY.toFixed(2)}px`);
			const shouldRenderGeometry = includeGeometry && (isActiveGroup || includeDepthGeometry);

			if (!shouldRenderGeometry && !isActiveGroup) {
				return;
			}

			group.states.forEach((state) => {
				renderArtwork(state, parallaxContext, shouldRenderGeometry, isActiveGroup);
			});
		});

		updateDriftActivation(metrics);
	};

	const renderOne = (state) => {
		const parallaxContext = measureParallaxContext();
		renderArtwork(state, parallaxContext, true);
	};

	const renderActiveLayerGeometry = () => {
		const parallaxContext = measureParallaxContext();

		getActiveStates().forEach((state) => {
			renderArtwork(state, parallaxContext, true);
		});
	};

	const requestRender = ({ includeGeometry = false, includeDepthGeometry = false } = {}) => {
		pendingFullRender = pendingFullRender || includeGeometry;
		pendingDepthRender = pendingDepthRender || includeDepthGeometry;

		if (renderQueued) {
			return;
		}

		renderQueued = true;
		window.requestAnimationFrame(() => {
			renderQueued = false;
			const shouldIncludeGeometry = pendingFullRender;
			const shouldIncludeDepthGeometry = pendingDepthRender;
			pendingFullRender = false;
			pendingDepthRender = false;
			renderAll({
				includeGeometry: shouldIncludeGeometry,
				includeDepthGeometry: shouldIncludeDepthGeometry,
			});
		});
	};

	const handleScroll = () => {
		if (isYearTransitioning) {
			return;
		}

		requestRender();
	};

	const updateLayering = ({ preserveVisualPosition = false } = {}) => {
		const activeStates = getActiveStates();
		const parallaxContext = preserveVisualPosition ? measureParallaxContext() : null;
		const visualYByState = preserveVisualPosition
			? new Map(activeStates.map((state) => [
				state,
				state.y + calculateParallaxY(parallaxContext, state.effectiveParallax),
			]))
			: null;
		const layerSorted = [...activeStates].sort((first, second) => {
			if (first.layerRank === second.layerRank) {
				return first.artwork.id.localeCompare(second.artwork.id);
			}

			return first.layerRank - second.layerRank;
		});
		const maxIndex = Math.max(layerSorted.length - 1, 1);

		layerSorted.forEach((state, index) => {
			state.zIndex = 20 + index;
			state.layerIndex = index;
			state.effectiveParallax = state.baseParallax + ((index / maxIndex) * PARALLAX_LAYER_BOOST);

			if (preserveVisualPosition) {
				state.parallaxY = calculateParallaxY(parallaxContext, state.effectiveParallax);
				state.y = visualYByState.get(state) - state.parallaxY;
			}
		});
	};

	const bringToFront = (state, options = {}) => {
		state.yearGroup.topLayerRank += 1;
		state.layerRank = state.yearGroup.topLayerRank;
		updateLayering(options);
		renderActiveLayerGeometry();
	};

	const isLayerVisibleAtIndex = (groupIndex) => {
		const depthSlot = groupIndex - activeYearIndex;
		const isTransitionParticipant = isYearTransitioning
			&& (groupIndex === transitionFromIndex || groupIndex === transitionToIndex);

		return (depthSlot >= 0 && depthSlot < VISIBLE_YEAR_LAYER_COUNT) || isTransitionParticipant;
	};

	const applyGalleryHeight = () => {
		const viewport = getViewport();
		let galleryHeight = viewport.height * LAYOUT_MIN_VIEWPORT_HEIGHTS;

		yearGroups.forEach((group, groupIndex) => {
			if (!isLayerVisibleAtIndex(groupIndex)) {
				return;
			}

			galleryHeight = Math.max(galleryHeight, group.layoutHeight || 0);
		});

		currentLayoutHeight = galleryHeight;
		gallery.style.setProperty("--art-gallery-height", `${Math.ceil(galleryHeight)}px`);
		galleryPageTop = gallery.getBoundingClientRect().top + window.scrollY;
	};

	const updateYearLabel = () => {
		const activeGroup = getActiveGroup();
		const year = activeGroup.year;

		window.HELLOTEACHER_ACTIVE_ART_YEAR = year;
		document.body.dataset.artYear = year;
		gallery.setAttribute("aria-label", `${year} draggable artwork gallery`);

		yearGroups.forEach((group) => {
			const isActiveTitle = group === activeGroup;

			if (group.title) {
				group.title.tabIndex = isActiveTitle ? 0 : -1;
				group.title.setAttribute("aria-hidden", isActiveTitle ? "false" : "true");
			}

			if (group.titleHint) {
				group.titleHint.hidden = !(isActiveTitle && activeYearIndex === initialYearIndex);
			}
		});
	};

	const updateYearLayers = ({ updateLabel = true } = {}) => {
		applyGalleryHeight();

		yearGroups.forEach((group, groupIndex) => {
			const depthSlot = groupIndex - activeYearIndex;
			const attributes = getLayerAttributes(depthSlot);
			const isActive = depthSlot === 0;
			const isTransitionParticipant = isYearTransitioning
				&& (groupIndex === transitionFromIndex || groupIndex === transitionToIndex);
			const isVisible = isLayerVisibleAtIndex(groupIndex);
			const shouldLoadImages = isVisible
				&& (
					(depthSlot >= 0 && depthSlot <= DEPTH_IMAGE_LAYER_COUNT)
					|| isActive
					|| isTransitionParticipant
				);

			group.depthSlot = depthSlot;
			group.isVisible = isVisible;
			group.layerParallax = attributes.parallax;
			group.layer.dataset.depthSlot = String(depthSlot);
			group.layer.classList.toggle("is-current-year", isActive);
			group.layer.classList.toggle("is-before-current", depthSlot < 0);
			group.layer.classList.toggle("is-depth-year", depthSlot > 0);
			group.layer.classList.toggle("is-year-transition-participant", isTransitionParticipant);
			group.layer.classList.toggle("is-hidden-year", !isVisible);
			group.layer.style.zIndex = String(attributes.zIndex);
			group.layer.style.setProperty("--year-scale", attributes.scale.toFixed(4));
			group.layer.style.setProperty("--year-depth-opacity", attributes.opacity.toFixed(3));
			group.layer.style.setProperty("--year-depth-y", `${attributes.y.toFixed(2)}px`);
			group.layer.style.setProperty("--year-scroll-y", "0px");

			group.states.forEach((state) => {
				state.depthSlot = depthSlot;
				state.isActive = isActive;

				if (!isActive) {
					state.effectiveParallax = attributes.parallax;
					setDriftActive(state, false);
				}

				state.card.disabled = !isActive;
				state.card.tabIndex = isActive ? 0 : -1;
				state.card.setAttribute("aria-hidden", isActive ? "false" : "true");
				state.card.classList.toggle("is-current-year", isActive);
				state.card.classList.toggle("is-depth-placeholder", !shouldLoadImages);

				if (shouldLoadImages) {
					ensureImageLoaded(state);
				} else {
					releaseImageMask(state);
				}
			});
		});

		if (updateLabel) {
			updateYearLabel();
		}

		updateLayering();
		lastColorScrollY = null;
		renderAll({ includeGeometry: true, includeDepthGeometry: true });
	};

	const calculateYearLayout = (group, viewport, metrics) => {
		const availableWidth = Math.max(1, viewport.width - (metrics.edgePad * 2));
		const shuffled = shuffleWithSeed(group.states, hashString(`${LAYOUT_SEED}-${group.year}`));
		const layoutItems = shuffled.map((state) => {
			const aspect = state.artwork.width / state.artwork.height;
			const width = Math.min(getCardWidth(state.artwork, viewport.width), availableWidth);
			const height = width / aspect;
			const overlapRatio = viewport.width < 520
				? LAYOUT_HORIZONTAL_OVERLAP_MOBILE_RATIO
				: LAYOUT_HORIZONTAL_OVERLAP_RATIO;
			const overlap = Math.min(width * overlapRatio, LAYOUT_HORIZONTAL_OVERLAP_MAX);
			const advanceWidth = Math.max(width - overlap + metrics.columnGap, width * 0.58);

			return {
				state,
				width,
				height,
				advanceWidth,
				offsetX: 0,
				random: seededRandom(hashString(`${LAYOUT_SEED}-${group.year}-${state.artwork.id}-layout`)),
				placementRandom: seededRandom(hashString(`${LAYOUT_SEED}-${group.year}-${state.artwork.id}-placement`)),
			};
		});
		const layoutRows = [];
		let currentRow = [];
		let currentRowAdvance = 0;
		let currentRowVisualWidth = 0;

		const commitRow = () => {
			if (currentRow.length === 0) {
				return;
			}

			layoutRows.push({
				index: layoutRows.length,
				items: currentRow,
				width: currentRowVisualWidth,
				height: Math.max(...currentRow.map((item) => item.height)),
			});
			currentRow = [];
			currentRowAdvance = 0;
			currentRowVisualWidth = 0;
		};

		layoutItems.forEach((item) => {
			let offsetX = currentRow.length === 0 ? 0 : currentRowAdvance;
			let nextVisualWidth = offsetX + item.width;

			if (currentRow.length > 0 && nextVisualWidth > availableWidth) {
				commitRow();
				offsetX = 0;
				nextVisualWidth = item.width;
			}

			item.offsetX = offsetX;
			currentRow.push(item);
			currentRowVisualWidth = Math.max(currentRowVisualWidth, nextVisualWidth);
			currentRowAdvance = offsetX + item.advanceWidth;
		});

		commitRow();

		let cursorY = metrics.topPad;

		layoutRows.forEach((row) => {
			row.top = cursorY;
			cursorY += row.height + metrics.rowClearance;
		});

		const galleryHeight = Math.max(
			viewport.height * LAYOUT_MIN_VIEWPORT_HEIGHTS,
			cursorY + metrics.bottomPad + LAYOUT_ROW_STAGGER_Y_MAX + LAYOUT_ITEM_SCATTER_Y_MAX
		);

		layoutRows.forEach((row) => {
			const rowRandom = seededRandom(hashString(`${LAYOUT_SEED}-${group.year}-row-${row.index}`));
			const rowSlack = Math.max(0, availableWidth - row.width);
			const rowAlignment = rowRandom();
			const rowLeft = metrics.edgePad + (rowSlack * rowAlignment);
			const rowStaggerXLimit = Math.min(
				LAYOUT_ROW_STAGGER_X_MAX,
				(rowSlack * 0.22) + (metrics.edgePad * 0.82)
			);
			const rowStaggerYLimit = Math.min(LAYOUT_ROW_STAGGER_Y_MAX, metrics.rowClearance * 0.62);
			const rowStaggerX = (rowRandom() - 0.5) * 2 * rowStaggerXLimit;
			const rowStaggerY = (rowRandom() - 0.5) * 2 * rowStaggerYLimit;

			row.items.forEach((item) => {
				const { state, width, height, random, placementRandom } = item;
				const xJitterLimit = Math.min(LAYOUT_JITTER_X_MAX, rowSlack * 0.5, width * 0.1);
				const yJitterLimit = Math.min(LAYOUT_JITTER_Y_MAX, metrics.rowClearance * 0.24);
				const xScatterLimit = Math.min(LAYOUT_ITEM_SCATTER_X_MAX, (width * 0.24) + metrics.columnGap);
				const yScatterLimit = Math.min(LAYOUT_ITEM_SCATTER_Y_MAX, (metrics.rowClearance * 0.58) + (height * 0.08));
				const jitterX = (random() - 0.5) * 2 * xJitterLimit;
				const jitterY = (random() - 0.5) * 2 * yJitterLimit;
				const scatterX = (placementRandom() - 0.5) * 2 * xScatterLimit;
				const scatterY = (placementRandom() - 0.5) * 2 * yScatterLimit;
				const targetX = rowLeft + rowStaggerX + item.offsetX + jitterX + scatterX;
				const targetY = row.top + rowStaggerY + ((row.height - height) * 0.5) + jitterY + scatterY;

				state.cardWidth = width;
				state.cardHeight = height;

				if (!state.hasCustomPosition) {
					const constrained = constrainLayoutPosition(state, targetX, targetY, metrics, galleryHeight);
					state.x = constrained.x;
					state.y = constrained.y;
				}
			});
		});

		return galleryHeight;
	};

	const calculateLayout = () => {
		const viewport = getViewport();
		const layoutColumns = getColumns(viewport.width);
		const metrics = getLayoutMetrics(viewport);

		yearGroups.forEach((group) => {
			group.layoutHeight = calculateYearLayout(group, viewport, metrics);
		});

		lastLayoutWidth = viewport.width;
		lastLayoutColumns = layoutColumns;
		updateYearLayers();
	};

	const requestLayout = () => {
		syncOpenViewerLayout();

		const viewport = getViewport();
		const columns = getColumns(viewport.width);
		const shouldRelayout = lastLayoutWidth === 0
			|| columns !== lastLayoutColumns
			|| Math.abs(viewport.width - lastLayoutWidth) > RELAYOUT_WIDTH_THRESHOLD;

		if (!shouldRelayout) {
			requestRender();
			return;
		}

		if (resizeQueued) {
			return;
		}

		resizeQueued = true;
		window.requestAnimationFrame(() => {
			resizeQueued = false;
			const latestViewport = getViewport();
			const latestColumns = getColumns(latestViewport.width);
			const stillNeedsRelayout = lastLayoutWidth === 0
				|| latestColumns !== lastLayoutColumns
				|| Math.abs(latestViewport.width - lastLayoutWidth) > RELAYOUT_WIDTH_THRESHOLD;

			if (stillNeedsRelayout) {
				calculateLayout();
			} else {
				requestRender();
			}
		});
	};

	const cancelInertia = (state) => {
		if (state.inertiaFrame) {
			window.cancelAnimationFrame(state.inertiaFrame);
			state.inertiaFrame = null;
			state.card.classList.remove("is-settling");
		}
	};

	const cancelActiveMotion = () => {
		states.forEach((state) => {
			cancelInertia(state);
			resetTilt(state);
			state.card.classList.remove("is-pressed", "is-dragging");
		});
		activeDrag = null;
	};

	const resetTilt = (state) => {
		if (!state) {
			return;
		}

		if (activeTilt?.state === state) {
			activeTilt = null;
		}

		state.card.classList.remove("is-tilting");
		state.card.style.setProperty("--tilt-x", "0deg");
		state.card.style.setProperty("--tilt-y", "0deg");
		state.card.style.setProperty("--glint-x", "50%");
		state.card.style.setProperty("--glint-y", "50%");
		state.card.style.setProperty("--glint-angle", "135deg");
		state.card.style.setProperty("--glint-opacity", "0");
		state.card.style.setProperty("--glint-shadow-opacity", "0");
	};

	const resetDescriptionGlint = () => {
		activeDescriptionGlint = null;
		viewerDescription.style.setProperty("--description-glint-x", "50%");
		viewerDescription.style.setProperty("--description-glint-y", "50%");
		viewerDescription.style.setProperty("--description-glint-angle", "135deg");
		viewerDescription.style.setProperty("--description-glint-opacity", "0");
	};

	const resetFoilTilt = (target) => {
		if (!target) {
			return;
		}

		target.element.style.setProperty(`--${target.prefix}-tilt-x`, "0deg");
		target.element.style.setProperty(`--${target.prefix}-tilt-y`, "0deg");
		target.element.style.setProperty(`--${target.prefix}-glint-x`, "50%");
		target.element.style.setProperty(`--${target.prefix}-glint-y`, "50%");
		target.element.style.setProperty(`--${target.prefix}-glint-angle`, "135deg");
		target.element.style.setProperty(`--${target.prefix}-glint-opacity`, "0");

		if (activeFoilTilt?.element === target.element) {
			activeFoilTilt = null;
		}
	};

	const updateFoilTilt = () => {
		foilTiltQueued = false;

		if (!activeFoilTilt || viewerState || reduceMotion.matches) {
			resetFoilTilt(activeFoilTilt);
			return;
		}

		const rect = activeFoilTilt.element.getBoundingClientRect();

		if (rect.width <= 0 || rect.height <= 0) {
			return;
		}

		const x = clamp((activeFoilTilt.clientX - rect.left) / rect.width, 0, 1);
		const y = clamp((activeFoilTilt.clientY - rect.top) / rect.height, 0, 1);
		const offsetX = x - 0.5;
		const offsetY = y - 0.5;
		const tiltX = -offsetY * activeFoilTilt.tiltXMax;
		const tiltY = offsetX * activeFoilTilt.tiltYMax;
		const edgeEnergy = clamp(Math.hypot(offsetX, offsetY) * 1.9, 0, 1);
		const glintAngle = 122 + (offsetX * 64) - (offsetY * 38);
		const glintOpacity = lerp(activeFoilTilt.glintMin, activeFoilTilt.glintMax, edgeEnergy);

		activeFoilTilt.element.style.setProperty(`--${activeFoilTilt.prefix}-tilt-x`, `${tiltX.toFixed(2)}deg`);
		activeFoilTilt.element.style.setProperty(`--${activeFoilTilt.prefix}-tilt-y`, `${tiltY.toFixed(2)}deg`);
		activeFoilTilt.element.style.setProperty(`--${activeFoilTilt.prefix}-glint-x`, `${(x * 100).toFixed(2)}%`);
		activeFoilTilt.element.style.setProperty(`--${activeFoilTilt.prefix}-glint-y`, `${(y * 100).toFixed(2)}%`);
		activeFoilTilt.element.style.setProperty(`--${activeFoilTilt.prefix}-glint-angle`, `${glintAngle.toFixed(2)}deg`);
		activeFoilTilt.element.style.setProperty(`--${activeFoilTilt.prefix}-glint-opacity`, glintOpacity.toFixed(3));
	};

	const requestFoilTilt = (target, event) => {
		if (!target || event.pointerType === "touch" || viewerState || reduceMotion.matches) {
			return;
		}

		activeFoilTilt = {
			...target,
			clientX: event.clientX,
			clientY: event.clientY,
		};

		if (foilTiltQueued) {
			return;
		}

		foilTiltQueued = true;
		window.requestAnimationFrame(updateFoilTilt);
	};

	const updateDescriptionGlint = () => {
		descriptionGlintQueued = false;

		if (!activeDescriptionGlint || !viewerState || reduceMotion.matches) {
			resetDescriptionGlint();
			return;
		}

		const rect = viewerDescription.getBoundingClientRect();

		if (rect.width <= 0 || rect.height <= 0) {
			return;
		}

		const x = clamp((activeDescriptionGlint.clientX - rect.left) / rect.width, 0, 1);
		const y = clamp((activeDescriptionGlint.clientY - rect.top) / rect.height, 0, 1);
		const offsetX = x - 0.5;
		const offsetY = y - 0.5;
		const edgeEnergy = clamp(Math.hypot(offsetX, offsetY) * 1.65, 0, 1);
		const glintAngle = 128 + (offsetX * 42) - (offsetY * 24);
		const glintOpacity = lerp(0.04, 0.18, edgeEnergy);

		viewerDescription.style.setProperty("--description-glint-x", `${(x * 100).toFixed(2)}%`);
		viewerDescription.style.setProperty("--description-glint-y", `${(y * 100).toFixed(2)}%`);
		viewerDescription.style.setProperty("--description-glint-angle", `${glintAngle.toFixed(2)}deg`);
		viewerDescription.style.setProperty("--description-glint-opacity", glintOpacity.toFixed(3));
	};

	const requestDescriptionGlint = (event) => {
		if (event.pointerType === "touch" || reduceMotion.matches) {
			return;
		}

		activeDescriptionGlint = {
			clientX: event.clientX,
			clientY: event.clientY,
		};

		if (descriptionGlintQueued) {
			return;
		}

		descriptionGlintQueued = true;
		window.requestAnimationFrame(updateDescriptionGlint);
	};

	const applyTilt = () => {
		tiltQueued = false;

		if (!activeTilt) {
			return;
		}

		const { state, clientX, clientY } = activeTilt;

		if (!state.isActive || viewerState || reduceMotion.matches || activeDrag?.state === state || isYearTransitioning) {
			resetTilt(state);
			return;
		}

		const rect = state.imageWrap.getBoundingClientRect();

		if (rect.width <= 0 || rect.height <= 0) {
			return;
		}

		const x = clamp((clientX - rect.left) / rect.width, 0, 1);
		const y = clamp((clientY - rect.top) / rect.height, 0, 1);
		const offsetX = x - 0.5;
		const offsetY = y - 0.5;
		const tiltX = -offsetY * TILT_MAX_DEGREES;
		const tiltY = offsetX * TILT_MAX_DEGREES;
		const edgeEnergy = clamp(Math.hypot(offsetX, offsetY) * 1.85, 0, 1);
		const glintOpacity = lerp(0.28, 0.78, edgeEnergy);
		const glintShadowOpacity = glintOpacity * 0.32;
		const glintAngle = 125 + (offsetX * 58) - (offsetY * 34);

		state.card.classList.add("is-tilting");
		state.card.style.setProperty("--tilt-x", `${tiltX.toFixed(2)}deg`);
		state.card.style.setProperty("--tilt-y", `${tiltY.toFixed(2)}deg`);
		state.card.style.setProperty("--glint-x", `${(x * 100).toFixed(2)}%`);
		state.card.style.setProperty("--glint-y", `${(y * 100).toFixed(2)}%`);
		state.card.style.setProperty("--glint-angle", `${glintAngle.toFixed(2)}deg`);
		state.card.style.setProperty("--glint-opacity", glintOpacity.toFixed(3));
		state.card.style.setProperty("--glint-shadow-opacity", glintShadowOpacity.toFixed(3));
	};

	const requestTilt = (state, event) => {
		if (!state.isActive || event.pointerType === "touch" || viewerState || reduceMotion.matches || isYearTransitioning) {
			return;
		}

		activeTilt = {
			state,
			clientX: event.clientX,
			clientY: event.clientY,
		};

		if (tiltQueued) {
			return;
		}

		tiltQueued = true;
		window.requestAnimationFrame(applyTilt);
	};

	const startInertia = (state, velocityX, velocityY) => {
		let vx = clamp(velocityX * INERTIA_RELEASE_DAMPING, -INERTIA_MAX_VELOCITY, INERTIA_MAX_VELOCITY);
		let vy = clamp(velocityY * INERTIA_RELEASE_DAMPING, -INERTIA_MAX_VELOCITY, INERTIA_MAX_VELOCITY);

		if (Math.hypot(vx, vy) <= INERTIA_MIN_SPEED) {
			renderOne(state);
			return;
		}

		let lastTime = performance.now();
		state.card.classList.add("is-settling");

		const step = (now) => {
			const delta = Math.min(now - lastTime, 32);
			lastTime = now;

			state.x += vx * delta;
			state.y += vy * delta;
			renderOne(state);

			const friction = Math.pow(INERTIA_FRICTION, delta / 16.67);
			vx *= friction;
			vy *= friction;

			if (Math.hypot(vx, vy) > INERTIA_MIN_SPEED) {
				state.inertiaFrame = window.requestAnimationFrame(step);
				return;
			}

			state.inertiaFrame = null;
			state.card.classList.remove("is-settling");
		};

		state.inertiaFrame = window.requestAnimationFrame(step);
	};

	const measureViewerTarget = (artwork) => {
		const viewport = getViewport();
		const margin = Math.min(50, viewport.width * 0.14, viewport.height * 0.14);
		const gap = clamp(viewport.width * 0.024, 18, 30);
		const maxWidth = Math.max(1, viewport.width - (margin * 2));
		const maxHeight = Math.max(1, viewport.height - (margin * 2));
		const artworkAspect = artwork.width / artwork.height;
		const viewportAspect = viewport.width / viewport.height;
		const canUseSideLayout = viewport.width >= VIEWER_SIDE_LAYOUT_MIN_WIDTH && artworkAspect < viewportAspect;

		if (canUseSideLayout) {
			const descriptionWidth = clamp(viewport.width * 0.27, VIEWER_DESCRIPTION_MIN_WIDTH, VIEWER_DESCRIPTION_MAX_WIDTH);
			const maxImageWidth = Math.max(1, maxWidth - descriptionWidth - gap);
			const scale = Math.min(maxImageWidth / artwork.width, maxHeight / artwork.height);
			const width = artwork.width * scale;
			const height = artwork.height * scale;
			const totalWidth = width + gap + descriptionWidth;
			const left = (viewport.width - totalWidth) / 2;
			const top = (viewport.height - height) / 2;

			return {
				width,
				height,
				left,
				top,
				description: {
					layout: "side",
					width: descriptionWidth,
					maxHeight: height,
					left: left + width + gap,
					top,
				},
			};
		}

		const descriptionMaxHeight = Math.min(
			clamp(viewport.height * 0.22, VIEWER_DESCRIPTION_STACK_MIN_HEIGHT, VIEWER_DESCRIPTION_STACK_MAX_HEIGHT),
			Math.max(100, maxHeight * 0.34)
		);
		const maxImageHeight = Math.max(1, maxHeight - gap - descriptionMaxHeight);
		const scale = Math.min(maxWidth / artwork.width, maxImageHeight / artwork.height);
		const width = artwork.width * scale;
		const height = artwork.height * scale;
		const totalHeight = height + gap + descriptionMaxHeight;
		const left = (viewport.width - width) / 2;
		const top = (viewport.height - totalHeight) / 2;
		const descriptionWidth = Math.min(maxWidth, Math.max(width, Math.min(420, maxWidth)));

		return {
			width,
			height,
			left,
			top,
			description: {
				layout: "stack",
				width: descriptionWidth,
				maxHeight: descriptionMaxHeight,
				left: (viewport.width - descriptionWidth) / 2,
				top: top + height + gap,
			},
		};
	};

	const finishCloseViewer = () => {
		if (!viewerState) {
			return;
		}

		viewerState.source.card.classList.remove("is-viewer-source");
		viewerState = null;
		viewer.classList.remove("is-active");
		viewer.setAttribute("aria-hidden", "true");
		viewerImage.removeAttribute("src");
		viewerImage.alt = "";
		viewerDescriptionTitle.textContent = "";
		viewerDescriptionMeta.textContent = "";
		viewerDescriptionBody.textContent = "";
		viewerDescription.removeAttribute("data-layout");
		resetDescriptionGlint();
		document.body.classList.remove("is-art-viewer-open");
	};

	const closeViewer = () => {
		if (!viewerState || viewerState.isClosing) {
			return;
		}

		const source = viewerState.source;
		const sourceRect = source.image.getBoundingClientRect();
		viewerState.isClosing = true;
		viewer.classList.remove("is-open");
		resetDescriptionGlint();
		viewerImage.style.width = `${sourceRect.width}px`;
		viewerImage.style.height = `${sourceRect.height}px`;
		viewerImage.style.transform = `translate3d(${sourceRect.left}px, ${sourceRect.top}px, 0)`;
		window.setTimeout(finishCloseViewer, 460);
	};

	const syncOpenViewerLayout = () => {
		if (!viewerState || viewerState.isClosing) {
			return;
		}

		const target = measureViewerTarget(viewerState.source.artwork);
		viewerImage.style.width = `${target.width}px`;
		viewerImage.style.height = `${target.height}px`;
		viewerImage.style.transform = `translate3d(${target.left}px, ${target.top}px, 0) rotate(0deg)`;
		positionViewerDescription(target);
	};

	const activateViewer = (state) => {
		if (viewerState?.source !== state || viewerState.isClosing) {
			return;
		}

		viewer.classList.add("is-active");
		viewer.setAttribute("aria-hidden", "false");
		document.body.classList.add("is-art-viewer-open");
		state.card.classList.add("is-viewer-source");
		viewerImage.getBoundingClientRect();

		window.requestAnimationFrame(() => {
			if (viewerState?.source !== state || viewerState.isClosing) {
				return;
			}

			viewer.classList.add("is-open");
			syncOpenViewerLayout();
		});
	};

	const openViewer = (state) => {
		if (viewerState || !state.isActive || isYearTransitioning) {
			return;
		}

		resetTilt(state);
		ensureImageLoaded(state);

		const sourceRect = state.image.getBoundingClientRect();
		const target = measureViewerTarget(state.artwork);
		viewerState = { source: state, isClosing: false };
		renderViewerDescription(state.artwork);
		positionViewerDescription(target);
		resetDescriptionGlint();
		viewerImage.src = state.image.currentSrc || state.image.src || state.artwork.previewSrc;
		viewerImage.alt = state.artwork.title;
		viewerImage.style.width = `${sourceRect.width}px`;
		viewerImage.style.height = `${sourceRect.height}px`;
		viewerImage.style.transform = `translate3d(${sourceRect.left}px, ${sourceRect.top}px, 0)`;
		waitForImageReady(viewerImage).then(() => activateViewer(state));

		const fullImage = new Image();
		fullImage.decoding = "async";
		fullImage.onload = () => {
			if (viewerState?.source === state && !viewerState.isClosing) {
				viewerImage.src = state.artwork.fullSrc;
			}
		};
		fullImage.src = state.artwork.fullSrc;
	};

	const handlePointerDown = (event, state) => {
		if (!state.isActive || viewerState || event.button !== 0 || isYearTransitioning) {
			return;
		}

		cancelInertia(state);
		state.card.setPointerCapture(event.pointerId);
		state.card.classList.add("is-pressed");
		activeDrag = {
			state,
			pointerId: event.pointerId,
			startClientX: event.clientX,
			startClientY: event.clientY,
			startX: state.x,
			startY: state.y,
			lastClientX: event.clientX,
			lastClientY: event.clientY,
			lastTime: performance.now(),
			velocityX: 0,
			velocityY: 0,
			isDragging: false,
		};
		event.preventDefault();
	};

	const handlePointerMove = (event) => {
		if (!activeDrag || event.pointerId !== activeDrag.pointerId) {
			return;
		}

		const state = activeDrag.state;
		const moveX = event.clientX - activeDrag.startClientX;
		const moveY = event.clientY - activeDrag.startClientY;

		if (!activeDrag.isDragging && Math.hypot(moveX, moveY) > DRAG_THRESHOLD) {
			activeDrag.isDragging = true;
			state.hasCustomPosition = true;
			state.card.classList.add("is-dragging");
			resetTilt(state);
			bringToFront(state, { preserveVisualPosition: true });
			activeDrag.startY = state.y;
		}

		if (!activeDrag.isDragging) {
			return;
		}

		const now = performance.now();
		const delta = Math.max(now - activeDrag.lastTime, 1);

		state.x = activeDrag.startX + moveX;
		state.y = activeDrag.startY + moveY;
		renderOne(state);
		activeDrag.velocityX = (event.clientX - activeDrag.lastClientX) / delta;
		activeDrag.velocityY = (event.clientY - activeDrag.lastClientY) / delta;
		activeDrag.lastClientX = event.clientX;
		activeDrag.lastClientY = event.clientY;
		activeDrag.lastTime = now;
		event.preventDefault();
	};

	const endPointerInteraction = (event) => {
		if (!activeDrag || event.pointerId !== activeDrag.pointerId) {
			return;
		}

		const drag = activeDrag;
		const state = drag.state;
		activeDrag = null;

		if (state.card.hasPointerCapture(event.pointerId)) {
			state.card.releasePointerCapture(event.pointerId);
		}

		state.card.classList.remove("is-pressed", "is-dragging");

		if (drag.isDragging) {
			startInertia(state, drag.velocityX, drag.velocityY);
			return;
		}

		openViewer(state);
	};

	const cancelPointerInteraction = (event) => {
		if (!activeDrag || event.pointerId !== activeDrag.pointerId) {
			return;
		}

		const state = activeDrag.state;
		activeDrag = null;

		if (state.card.hasPointerCapture(event.pointerId)) {
			state.card.releasePointerCapture(event.pointerId);
		}

		state.card.classList.remove("is-pressed", "is-dragging");
	};

	const goToYearIndex = (nextIndex) => {
		const clampedIndex = clamp(nextIndex, 0, yearGroups.length - 1);

		if (clampedIndex === activeYearIndex || viewerState || activeDrag || isYearTransitioning) {
			return;
		}

		cancelActiveMotion();
		settleActiveDriftToNeutral();

		if (yearTransitionTimer) {
			window.clearTimeout(yearTransitionTimer);
			yearTransitionTimer = null;
		}

		if (yearTransitionFrame) {
			window.cancelAnimationFrame(yearTransitionFrame);
			yearTransitionFrame = null;
		}

		if (reduceMotion.matches) {
			activeYearIndex = clampedIndex;
			transitionFromIndex = null;
			transitionToIndex = null;
			updateYearLayers();
			return;
		}

		transitionFromIndex = activeYearIndex;
		transitionToIndex = clampedIndex;
		isYearTransitioning = true;
		document.body.classList.add("is-art-year-transitioning");
		updateYearLayers({ updateLabel: false });
		gallery.offsetHeight;

		yearTransitionFrame = window.requestAnimationFrame(() => {
			yearTransitionFrame = null;

			if (!isYearTransitioning || transitionToIndex !== clampedIndex) {
				return;
			}

			activeYearIndex = clampedIndex;
			updateYearLayers();
		});

		yearTransitionTimer = window.setTimeout(() => {
			isYearTransitioning = false;
			document.body.classList.remove("is-art-year-transitioning");
			transitionFromIndex = null;
			transitionToIndex = null;
			yearTransitionTimer = null;
			updateYearLayers();
		}, YEAR_TRANSITION_MS);
	};

	const handleYearKeydown = (event) => {
		if (event.metaKey || event.ctrlKey || event.altKey || viewerState) {
			return;
		}

		const key = event.key.toLowerCase();

		if (key === "e") {
			event.preventDefault();
			goToYearIndex(activeYearIndex + 1);
		} else if (key === "q") {
			event.preventDefault();
			goToYearIndex(activeYearIndex - 1);
		}
	};

	const createArtworkCard = (group, artwork, index) => {
		const random = seededRandom(hashString(artwork.key));
		const driftRandom = seededRandom(hashString(`${artwork.key}-drift`));
		const card = document.createElement("button");
		card.className = "artwork-card is-depth-placeholder";
		card.type = "button";
		card.setAttribute("aria-label", `Expand ${artwork.title}`);
		card.dataset.artworkId = artwork.id;
		card.dataset.year = artwork.year;
		const driftDuration = lerp(DRIFT_MIN_DURATION, DRIFT_MAX_DURATION, driftRandom());
		const driftX = lerp(4, DRIFT_X_MAX, driftRandom());
		const driftY = lerp(5, DRIFT_Y_MAX, driftRandom());
		const driftRotate = lerp(0.18, DRIFT_ROTATE_MAX, driftRandom());
		card.style.setProperty("--artwork-drift-x", `${driftX.toFixed(2)}px`);
		card.style.setProperty("--artwork-drift-y", `${(-driftY * 0.65).toFixed(2)}px`);
		card.style.setProperty("--artwork-drift-x-alt", `${(-driftX * 0.82).toFixed(2)}px`);
		card.style.setProperty("--artwork-drift-y-alt", `${driftY.toFixed(2)}px`);
		card.style.setProperty("--artwork-drift-rotate", `${driftRotate.toFixed(3)}deg`);
		card.style.setProperty("--artwork-drift-rotate-alt", `${(-driftRotate).toFixed(3)}deg`);
		card.style.setProperty("--artwork-drift-duration", `${driftDuration.toFixed(2)}s`);
		card.style.setProperty("--artwork-drift-delay", `${(driftRandom() * DRIFT_START_DELAY_MAX).toFixed(2)}s`);

		const driftWrap = document.createElement("span");
		driftWrap.className = "artwork-card__drift";
		driftWrap.setAttribute("aria-hidden", "true");

		const imageWrap = document.createElement("span");
		imageWrap.className = "artwork-card__image-wrap";

		const image = document.createElement("img");
		image.className = "artwork-card__image";
		image.alt = "";
		image.width = artwork.width;
		image.height = artwork.height;
		image.decoding = "async";
		image.loading = "lazy";
		image.draggable = false;
		image.addEventListener("error", () => {
			if (image.src !== artwork.fullSrc) {
				image.src = artwork.fullSrc;
			}
		}, { once: true });

		imageWrap.append(image);
		driftWrap.append(imageWrap);
		card.append(driftWrap);
		group.layer.append(card);

		const state = {
			artwork,
			yearGroup: group,
			card,
			driftWrap,
			imageWrap,
			image,
			x: 0,
			y: 0,
			parallaxY: 0,
			zIndex: 20 + index,
			layerIndex: index,
			layerRank: index,
			depthSlot: 0,
			isActive: false,
			isDriftActive: false,
			baseParallax: lerp(0.34, 0.56, random()),
			effectiveParallax: 0.34,
			cardWidth: 220,
			cardHeight: 260,
			hasCustomPosition: false,
			inertiaFrame: null,
			driftSettleTimer: null,
		};

		card.addEventListener("pointerdown", (event) => handlePointerDown(event, state));
		card.addEventListener("pointerenter", (event) => requestTilt(state, event));
		card.addEventListener("pointermove", (event) => requestTilt(state, event));
		card.addEventListener("pointerleave", () => resetTilt(state));
		card.addEventListener("keydown", (event) => {
			if (event.key !== "Enter" && event.key !== " ") {
				return;
			}

			event.preventDefault();
			openViewer(state);
		});

		return state;
	};

	const createYearTitle = (group) => {
		const slot = document.createElement("div");
		slot.className = "art-year-title-slot";

		const title = document.createElement("div");
		title.className = "art-year-title";
		title.dataset.year = group.year;
		title.tabIndex = -1;
		title.setAttribute("role", "status");
		title.setAttribute("aria-live", "polite");
		title.setAttribute("aria-hidden", "true");

		const surface = document.createElement("span");
		surface.className = "art-year-title__surface";

		const text = document.createElement("span");
		text.className = "art-year-title__text";
		text.dataset.text = group.year;
		text.textContent = group.year;

		const hint = document.createElement("span");
		hint.className = "art-year-title__hint";
		hint.hidden = true;
		hint.textContent = "Q/E to move forward/backward in time";

		surface.append(text, hint);
		title.append(surface);
		slot.append(title);

		group.title = title;
		group.titleHint = hint;

		return slot;
	};

	const createYearLayer = (group, index) => {
		const layer = document.createElement("section");
		layer.className = "art-year-layer";
		layer.dataset.year = group.year;
		layer.setAttribute("aria-label", `${group.year} artworks`);
		layer.style.zIndex = String(120 - index);
		group.layer = layer;
		gallery.append(layer);
		layer.append(createYearTitle(group));
		group.states = group.artworks.map((artwork, artworkIndex) => createArtworkCard(group, artwork, artworkIndex));
		states.push(...group.states);
	};

	yearGroups.forEach(createYearLayer);

	const attachFoilTiltHandlers = (target) => {
		target.element.addEventListener("pointermove", (event) => requestFoilTilt(target, event));
		target.element.addEventListener("pointerleave", () => resetFoilTilt(target));
		target.element.addEventListener("focusout", () => resetFoilTilt(target));
	};

	const homeFoilTarget = homeLink
		? { element: homeLink, prefix: "home", tiltXMax: 14, tiltYMax: 18, glintMin: 0.28, glintMax: 0.88 }
		: null;

	if (homeFoilTarget) {
		attachFoilTiltHandlers(homeFoilTarget);
	}

	yearGroups.forEach((group) => {
		if (!group.title) {
			return;
		}

		attachFoilTiltHandlers({
			element: group.title,
			prefix: "year",
			tiltXMax: 12,
			tiltYMax: 16,
			glintMin: 0.22,
			glintMax: 0.76,
		});
	});

	window.HELLOTEACHER_ART_YEARS = {
		goFuture: () => goToYearIndex(activeYearIndex - 1),
		goPast: () => goToYearIndex(activeYearIndex + 1),
		getCurrentYear: () => getActiveGroup().year,
	};

	window.addEventListener("pointermove", handlePointerMove, { passive: false });
	window.addEventListener("pointerup", endPointerInteraction);
	window.addEventListener("pointercancel", cancelPointerInteraction);
	window.addEventListener("keydown", handleYearKeydown);
	window.addEventListener("scroll", handleScroll, { passive: true });
	window.addEventListener("resize", requestLayout);

	viewer.addEventListener("click", (event) => {
		if (event.target === viewer) {
			closeViewer();
		}
	});
	viewerImage.addEventListener("click", (event) => {
		event.stopPropagation();
	});
	viewerDescription.addEventListener("pointermove", requestDescriptionGlint);
	viewerDescription.addEventListener("pointerleave", resetDescriptionGlint);
	document.addEventListener("keydown", (event) => {
		if (event.key === "Escape") {
			closeViewer();
		}
	});

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			renderAll({ includeGeometry: true, includeDepthGeometry: true });
		});
	} else {
		reduceMotion.addListener(() => {
			renderAll({ includeGeometry: true, includeDepthGeometry: true });
		});
	}

	loadArtworkDescriptions();
	calculateLayout();
	renderAll({ includeGeometry: true, includeDepthGeometry: true });
})();
