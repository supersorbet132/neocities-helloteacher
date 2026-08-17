(() => {
	const gallery = document.querySelector("[data-art-gallery]");
	const homeLink = document.querySelector("[data-art-home-link]");

	if (!gallery) {
		return;
	}

	const ARTWORKS = [
		{ file: "ark.jpg", year: "2025", width: 2732, height: 2048 },
		{ file: "bananasplit.png", year: "2025", width: 2793, height: 2732 },
		{ file: "black.jpg", year: "2025", width: 2426, height: 2048 },
		{ file: "blackhole.jpg", year: "2026", width: 1326, height: 1768 },
		{ file: "cosmicdress.jpg", year: "2025", width: 1536, height: 2048 },
		{ file: "dog.jpg", year: "2026", width: 4096, height: 1714 },
		{ file: "green.jpg", year: "2025", width: 1536, height: 2048 },
		{ file: "hornet.jpg", year: "2025", width: 1579, height: 2049 },
		{ file: "kimiacity.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimiaclouds.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimiacomets.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimiadescent.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimialog.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimiaruins.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimiasunrise.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "kimiasword.jpg", year: "2026", width: 1536, height: 2048 },
		{ file: "pillars.jpg", year: "2025", width: 4877, height: 2048 },
		{ file: "providence.jpg", year: "2025", width: 3851, height: 2539 },
		{ file: "ruinedrobot.jpg", year: "2025", width: 2048, height: 2732 },
		{ file: "solyn.jpg", year: "2025", width: 6095, height: 3833 },
		{ file: "soma.jpg", year: "2025", width: 2048, height: 2732 },
		{ file: "twins.jpg", year: "2025", width: 2048, height: 2732 },
	];

	const THUMB_ROOT = "/assets/images/art/thumbs/";
	const FULL_ROOT = "/assets/images/art/artworks/";
	const DESCRIPTION_SRC = "/assets/data/art-descriptions.json";
	const DRAG_THRESHOLD = 7;
	const INERTIA_MIN_SPEED = 0.018;
	const INERTIA_FRICTION = 0.86;
	const INERTIA_RELEASE_DAMPING = 0.42;
	const INERTIA_MAX_VELOCITY = 1.05;
	const PARALLAX_LAYER_BOOST = 1.7;
	const PARALLAX_SCROLL_SCALE = 0.52;
	const TILT_MAX_DEGREES = 18;
	const LAYOUT_EDGE_PAD_RATIO = 0.035;
	const LAYOUT_EDGE_PAD_MIN = 30;
	const LAYOUT_EDGE_PAD_MAX = 70;
	const LAYOUT_COLUMN_GAP_RATIO = 0.025;
	const LAYOUT_COLUMN_GAP_MIN = 12;
	const LAYOUT_COLUMN_GAP_MAX = 38;
	const LAYOUT_HORIZONTAL_OVERLAP_RATIO = 0.31;
	const LAYOUT_HORIZONTAL_OVERLAP_MOBILE_RATIO = 0.17;
	const LAYOUT_HORIZONTAL_OVERLAP_MAX = 142;
	const LAYOUT_ROW_CLEARANCE_RATIO = 0.15;
	const LAYOUT_ROW_CLEARANCE_MIN = 52;
	const LAYOUT_ROW_CLEARANCE_MAX = 170;
	const LAYOUT_TOP_PAD_RATIO = 0.2;
	const LAYOUT_TOP_PAD_MIN = 82;
	const LAYOUT_TOP_PAD_MAX = 220;
	const LAYOUT_BOTTOM_PAD_RATIO = 0.48;
	const LAYOUT_BOTTOM_PAD_MIN = 180;
	const LAYOUT_BOTTOM_PAD_MAX = 560;
	const LAYOUT_JITTER_X_MAX = 30;
	const LAYOUT_JITTER_Y_MAX = 34;
	const RELAYOUT_WIDTH_THRESHOLD = 12;
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

	const titleFromFile = (file) => file
		.replace(/\.[^.]+$/, "")
		.replace(/[-_]+/g, " ")
		.replace(/\b\w/g, (letter) => letter.toUpperCase());

	const getViewport = () => ({
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
		const random = seededRandom(hashString(`${artwork.id}-size`));
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
				viewport.height * (isSmall ? 0.18 : LAYOUT_TOP_PAD_RATIO),
				isSmall ? 76 : LAYOUT_TOP_PAD_MIN,
				isSmall ? 138 : LAYOUT_TOP_PAD_MAX
			),
			bottomPad: clamp(
				viewport.height * LAYOUT_BOTTOM_PAD_RATIO,
				LAYOUT_BOTTOM_PAD_MIN,
				LAYOUT_BOTTOM_PAD_MAX
			),
		};
	};

	const constrainLayoutPosition = (state, x, y, metrics, galleryHeight) => {
		const maxX = Math.max(metrics.edgePad, getViewport().width - state.cardWidth - metrics.edgePad);
		const maxY = Math.max(metrics.topPad, galleryHeight - state.cardHeight - metrics.bottomPad * 0.45);

		return {
			x: clamp(x, metrics.edgePad, maxX),
			y: clamp(y, metrics.topPad * 0.5, maxY),
		};
	};

	const getFullArtworkSrc = (artwork) => {
		const yearSegment = artwork.year ? `${artwork.year}/` : "";

		return `${FULL_ROOT}${yearSegment}${artwork.file}`;
	};

	const normalizedArtworks = ARTWORKS
		.map((artwork) => {
			const id = artwork.file.replace(/\.[^.]+$/, "");
			const title = artwork.title || titleFromFile(artwork.file);

			return {
				...artwork,
				id,
				title,
				fullSrc: getFullArtworkSrc(artwork),
				thumbSrc: `${THUMB_ROOT}${artwork.file}`,
			};
		})
		.sort((first, second) => first.id.localeCompare(second.id));

	let states = [];
	let activeDrag = null;
	let topLayerRank = normalizedArtworks.length - 1;
	let parallaxQueued = false;
	let resizeQueued = false;
	let lastLayoutWidth = 0;
	let lastLayoutColumns = 0;
	let activeTilt = null;
	let tiltQueued = false;
	let viewerState = null;
	let artworkDescriptions = {};
	let activeDescriptionGlint = null;
	let descriptionGlintQueued = false;
	let activeHomeTilt = null;
	let homeTiltQueued = false;

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
		const entry = artworkDescriptions[artwork.id] || artworkDescriptions[artwork.file] || {};

		return {
			title: entry.title || artwork.title,
			year: entry.year || "",
			medium: entry.medium || "",
			description: entry.description || `Placeholder note for ${artwork.title}. Add this artwork's final description in assets/data/art-descriptions.json.`,
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

	const renderArtwork = (state) => {
		state.card.style.setProperty("--artwork-x", `${state.x.toFixed(2)}px`);
		state.card.style.setProperty("--artwork-y", `${state.y.toFixed(2)}px`);
		state.card.style.setProperty("--artwork-parallax-y", `${state.parallaxY.toFixed(2)}px`);
		state.card.style.setProperty("--artwork-z", state.zIndex);
		state.card.style.setProperty("--artwork-width", `${state.cardWidth}px`);
	};

	const measureParallaxContext = () => {
		const galleryRect = gallery.getBoundingClientRect();
		const viewport = getViewport();
		const scrollCenter = viewport.height * 0.5;
		const galleryProgress = clamp((scrollCenter - galleryRect.top) / Math.max(galleryRect.height, 1), 0, 1);
		const scrollTravel = galleryRect.height * PARALLAX_SCROLL_SCALE;

		return {
			galleryProgress,
			scrollTravel,
		};
	};

	const calculateParallaxY = (context, effectiveParallax) => (
		-context.scrollTravel * context.galleryProgress * effectiveParallax
	);

	const updateLayering = ({ preserveVisualPosition = false } = {}) => {
		const visualYByState = preserveVisualPosition
			? new Map(states.map((state) => [state, state.y + state.parallaxY]))
			: null;
		const parallaxContext = preserveVisualPosition ? measureParallaxContext() : null;
		const layerSorted = [...states].sort((first, second) => {
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

			renderArtwork(state);
		});
	};

	const bringToFront = (state, options = {}) => {
		topLayerRank += 1;
		state.layerRank = topLayerRank;
		updateLayering(options);
	};

	const updateParallax = () => {
		parallaxQueued = false;
		const parallaxContext = measureParallaxContext();

		states.forEach((state) => {
			state.parallaxY = calculateParallaxY(parallaxContext, state.effectiveParallax);
			renderArtwork(state);
		});
	};

	const requestParallax = () => {
		if (parallaxQueued) {
			return;
		}

		parallaxQueued = true;
		window.requestAnimationFrame(updateParallax);
	};

	const calculateLayout = () => {
		const viewport = getViewport();
		const layoutColumns = getColumns(viewport.width);
		const metrics = getLayoutMetrics(viewport);
		const availableWidth = Math.max(1, viewport.width - (metrics.edgePad * 2));
		const shuffled = shuffleWithSeed(states, 0xA7172026);
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
				random: seededRandom(hashString(`${state.artwork.id}-layout`)),
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
			viewport.height * 3.47,
			cursorY + metrics.bottomPad
		);

		lastLayoutWidth = viewport.width;
		lastLayoutColumns = layoutColumns;
		gallery.style.setProperty("--art-gallery-height", `${Math.ceil(galleryHeight)}px`);

		layoutRows.forEach((row) => {
			const rowLeft = metrics.edgePad + Math.max(0, (availableWidth - row.width) / 2);
			const rowSlack = Math.max(0, availableWidth - row.width);

			row.items.forEach((item) => {
				const { state, width, height, random } = item;
				const xJitterLimit = Math.min(LAYOUT_JITTER_X_MAX, rowSlack * 0.42, width * 0.08);
				const yJitterLimit = Math.min(LAYOUT_JITTER_Y_MAX, metrics.rowClearance * 0.18);
				const jitterX = (random() - 0.5) * 2 * xJitterLimit;
				const jitterY = (random() - 0.5) * 2 * yJitterLimit;
				const targetX = rowLeft + item.offsetX + jitterX;
				const targetY = row.top + ((row.height - height) * 0.5) + jitterY;

				state.cardWidth = width;
				state.cardHeight = height;

				if (!state.hasCustomPosition) {
					const constrained = constrainLayoutPosition(state, targetX, targetY, metrics, galleryHeight);
					state.x = constrained.x;
					state.y = constrained.y;
				}

				renderArtwork(state);
			});
		});

		updateLayering();
		requestParallax();
	};

	const requestLayout = () => {
		syncOpenViewerLayout();

		const viewport = getViewport();
		const columns = getColumns(viewport.width);
		const shouldRelayout = lastLayoutWidth === 0
			|| columns !== lastLayoutColumns
			|| Math.abs(viewport.width - lastLayoutWidth) > RELAYOUT_WIDTH_THRESHOLD;

		if (!shouldRelayout) {
			requestParallax();
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
				requestParallax();
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

	const resetHomeTilt = () => {
		if (!homeLink) {
			return;
		}

		activeHomeTilt = null;
		homeLink.style.setProperty("--home-tilt-x", "0deg");
		homeLink.style.setProperty("--home-tilt-y", "0deg");
		homeLink.style.setProperty("--home-glint-x", "50%");
		homeLink.style.setProperty("--home-glint-y", "50%");
		homeLink.style.setProperty("--home-glint-angle", "135deg");
		homeLink.style.setProperty("--home-glint-opacity", "0");
	};

	const updateHomeTilt = () => {
		homeTiltQueued = false;

		if (!homeLink || !activeHomeTilt || viewerState || reduceMotion.matches) {
			resetHomeTilt();
			return;
		}

		const rect = homeLink.getBoundingClientRect();

		if (rect.width <= 0 || rect.height <= 0) {
			return;
		}

		const x = clamp((activeHomeTilt.clientX - rect.left) / rect.width, 0, 1);
		const y = clamp((activeHomeTilt.clientY - rect.top) / rect.height, 0, 1);
		const offsetX = x - 0.5;
		const offsetY = y - 0.5;
		const tiltX = -offsetY * 14;
		const tiltY = offsetX * 18;
		const edgeEnergy = clamp(Math.hypot(offsetX, offsetY) * 1.9, 0, 1);
		const glintAngle = 122 + (offsetX * 64) - (offsetY * 38);
		const glintOpacity = lerp(0.28, 0.88, edgeEnergy);

		homeLink.style.setProperty("--home-tilt-x", `${tiltX.toFixed(2)}deg`);
		homeLink.style.setProperty("--home-tilt-y", `${tiltY.toFixed(2)}deg`);
		homeLink.style.setProperty("--home-glint-x", `${(x * 100).toFixed(2)}%`);
		homeLink.style.setProperty("--home-glint-y", `${(y * 100).toFixed(2)}%`);
		homeLink.style.setProperty("--home-glint-angle", `${glintAngle.toFixed(2)}deg`);
		homeLink.style.setProperty("--home-glint-opacity", glintOpacity.toFixed(3));
	};

	const requestHomeTilt = (event) => {
		if (!homeLink || event.pointerType === "touch" || viewerState || reduceMotion.matches) {
			return;
		}

		activeHomeTilt = {
			clientX: event.clientX,
			clientY: event.clientY,
		};

		if (homeTiltQueued) {
			return;
		}

		homeTiltQueued = true;
		window.requestAnimationFrame(updateHomeTilt);
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

		if (viewerState || reduceMotion.matches || activeDrag?.state === state) {
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
		if (event.pointerType === "touch" || viewerState || reduceMotion.matches) {
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
			renderArtwork(state);
			return;
		}

		let lastTime = performance.now();
		state.card.classList.add("is-settling");

		const step = (now) => {
			const delta = Math.min(now - lastTime, 32);
			lastTime = now;

			let nextX = state.x + (vx * delta);
			let nextY = state.y + (vy * delta);

			state.x = nextX;
			state.y = nextY;

			const friction = Math.pow(INERTIA_FRICTION, delta / 16.67);
			vx *= friction;
			vy *= friction;
			renderArtwork(state);

			if (Math.hypot(vx, vy) > INERTIA_MIN_SPEED) {
				state.inertiaFrame = window.requestAnimationFrame(step);
				return;
			}

			renderArtwork(state);
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
		if (viewerState) {
			return;
		}

		resetTilt(state);
		const sourceRect = state.image.getBoundingClientRect();
		const target = measureViewerTarget(state.artwork);
		viewerState = { source: state, isClosing: false };
		renderViewerDescription(state.artwork);
		positionViewerDescription(target);
		resetDescriptionGlint();
		viewerImage.src = state.image.currentSrc || state.image.src || state.artwork.thumbSrc;
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
		if (viewerState || event.button !== 0) {
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
		activeDrag.velocityX = (event.clientX - activeDrag.lastClientX) / delta;
		activeDrag.velocityY = (event.clientY - activeDrag.lastClientY) / delta;
		activeDrag.lastClientX = event.clientX;
		activeDrag.lastClientY = event.clientY;
		activeDrag.lastTime = now;
		renderArtwork(state);
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

	const createArtworkCard = (artwork, index) => {
		const random = seededRandom(hashString(artwork.id));
		const card = document.createElement("button");
		card.className = "artwork-card";
		card.type = "button";
		card.setAttribute("aria-label", `Expand ${artwork.title}`);
		card.dataset.artworkId = artwork.id;

		const imageWrap = document.createElement("span");
		imageWrap.className = "artwork-card__image-wrap";
		imageWrap.setAttribute("aria-hidden", "true");
		imageWrap.style.setProperty("--artwork-mask-image", `url("${artwork.thumbSrc}")`);

		const image = document.createElement("img");
		image.className = "artwork-card__image";
		image.src = artwork.thumbSrc;
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
		card.append(imageWrap);
		gallery.append(card);

		const state = {
			artwork,
			card,
			imageWrap,
			image,
			x: 0,
			y: 0,
			parallaxY: 0,
			zIndex: 20 + index,
			layerIndex: index,
			layerRank: index,
			baseParallax: lerp(0.52, 0.78, random()),
			effectiveParallax: 0.52,
			cardWidth: 220,
			cardHeight: 260,
			hasCustomPosition: false,
			inertiaFrame: null,
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

	states = normalizedArtworks.map(createArtworkCard);

	window.addEventListener("pointermove", handlePointerMove, { passive: false });
	window.addEventListener("pointerup", endPointerInteraction);
	window.addEventListener("pointercancel", cancelPointerInteraction);
	window.addEventListener("scroll", requestParallax, { passive: true });
	window.addEventListener("resize", requestLayout);
	viewer.addEventListener("click", (event) => {
		if (event.target === viewer) {
			closeViewer();
		}
	});
	viewerImage.addEventListener("click", (event) => {
		event.stopPropagation();
	});
	viewerDescription.addEventListener("pointerenter", requestDescriptionGlint);
	viewerDescription.addEventListener("pointermove", requestDescriptionGlint);
	viewerDescription.addEventListener("pointerleave", resetDescriptionGlint);
	if (homeLink) {
		homeLink.addEventListener("pointerenter", requestHomeTilt);
		homeLink.addEventListener("pointermove", requestHomeTilt);
		homeLink.addEventListener("pointerleave", resetHomeTilt);
	}
	window.addEventListener("keydown", (event) => {
		if (event.key === "Escape") {
			closeViewer();
		}
	});
	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			states.forEach(resetTilt);
			resetHomeTilt();
			requestParallax();
		});
	} else {
		reduceMotion.addListener(() => {
			states.forEach(resetTilt);
			resetHomeTilt();
			requestParallax();
		});
	}

	loadArtworkDescriptions();
	calculateLayout();
})();
