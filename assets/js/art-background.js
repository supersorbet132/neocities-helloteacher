(() => {
	const field = document.querySelector("[data-art-depth-field]");
	const surface = document.querySelector(".art-page__surface");

	if (!field || !surface) {
		return;
	}

	const ACTIVE_ART_YEAR = window.HELLOTEACHER_ACTIVE_ART_YEAR || "2026";
	const ARTWORKS = Array.isArray(window.HELLOTEACHER_ARTWORKS)
		? window.HELLOTEACHER_ARTWORKS
		: [];
	const DEPTH_ATTRIBUTE_LAYER_COUNT = 6;
	const DEPTH_IMAGE_LAYER_COUNT = 2;
	const DEPTH_LAYOUT_SEED = 0xD3A72026;
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
	const DEPTH_FRONT_SIZE_SCALE = 0.77;
	const DEPTH_BACK_SIZE_SCALE = 1.12;
	const DEPTH_FRONT_PARALLAX = 0.2;
	const DEPTH_BACK_PARALLAX = -0.5;
	const DEPTH_FRONT_WIDTH_RATIO = 0.31;
	const DEPTH_FRONT_WIDTH_MAX = 373;
	const DEPTH_BACK_WIDTH = 52;
	const DEPTH_WIDTH_RANDOM_MIN = 0.72;
	const DEPTH_WIDTH_RANDOM_MAX = 1.3;
	const DEPTH_DRIFT_FRONT_SPEED = 11;
	const DEPTH_DRIFT_BACK_SPEED = 2;
	const DEPTH_DRIFT_RANDOM_MIN = 0.65;
	const DEPTH_DRIFT_RANDOM_MAX = 1.35;
	const DEPTH_DRIFT_WRAP_PAD = 80;
	const DEPTH_IMAGE_FRONT_BRIGHTNESS = 0.46;
	const DEPTH_IMAGE_BACK_BRIGHTNESS = 1.18;
	const DEPTH_IMAGE_FRONT_OPACITY = 0.78;
	const DEPTH_IMAGE_BACK_OPACITY = 0.52;
	const DEPTH_IMAGE_CONTRAST = 1.08;
	const DEPTH_TINT_FRONT_OPACITY = 0.82;
	const DEPTH_TINT_BACK_OPACITY = 0.54;
	const DEPTH_VALUE_FRONT_OPACITY = 0.48;
	const DEPTH_VALUE_BACK_OPACITY = 0.12;
	const DEPTH_EDGE_PAD_RATIO = 0.035;
	const DEPTH_EDGE_PAD_MIN = 30;
	const DEPTH_EDGE_PAD_MAX = 70;
	const DEPTH_COLUMN_GAP_RATIO = 0.034;
	const DEPTH_COLUMN_GAP_MIN = 18;
	const DEPTH_COLUMN_GAP_MAX = 56;
	const DEPTH_HORIZONTAL_OVERLAP_RATIO = 0.24;
	const DEPTH_HORIZONTAL_OVERLAP_MOBILE_RATIO = 0.13;
	const DEPTH_HORIZONTAL_OVERLAP_MAX = 104;
	const DEPTH_ROW_CLEARANCE_RATIO = 0.19;
	const DEPTH_ROW_CLEARANCE_MIN = 72;
	const DEPTH_ROW_CLEARANCE_MAX = 225;
	const DEPTH_TOP_PAD_RATIO = 0.2;
	const DEPTH_TOP_PAD_MIN = 82;
	const DEPTH_TOP_PAD_MAX = 220;
	const DEPTH_BOTTOM_PAD_RATIO = 0.48;
	const DEPTH_BOTTOM_PAD_MIN = 180;
	const DEPTH_BOTTOM_PAD_MAX = 560;
	const DEPTH_JITTER_X_MAX = 36;
	const DEPTH_JITTER_Y_MAX = 44;
	const DEPTH_ROW_STAGGER_X_MAX = 130;
	const DEPTH_ROW_STAGGER_Y_MAX = 92;
	const DEPTH_ITEM_SCATTER_X_FRONT = 22;
	const DEPTH_ITEM_SCATTER_X_BACK = 84;
	const DEPTH_ITEM_SCATTER_Y_FRONT = 48;
	const DEPTH_ITEM_SCATTER_Y_BACK = 190;
	const DEPTH_LAYER_Y_OFFSET_RATIO = 0.018;
	const REBUILD_WIDTH_THRESHOLD = 12;

	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
	const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
	const lerp = (from, to, progress) => from + ((to - from) * progress);

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

	let layers = [];
	let depthArtworks = [];
	let frame = null;
	let lastColorScrollY = null;
	let layoutQueued = false;
	let lastBuildWidth = 0;

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

	const getFieldHeight = () => Math.max(surface.offsetHeight, window.innerHeight || 0, 1);

	const getMetrics = () => ({
		fieldHeight: getFieldHeight(),
		scrollY: window.scrollY,
		width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
		height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
	});

	const getLayoutMetrics = (metrics) => {
		const isSmall = metrics.width < 520;

		return {
			edgePad: clamp(
				metrics.width * DEPTH_EDGE_PAD_RATIO,
				isSmall ? 28 : DEPTH_EDGE_PAD_MIN,
				isSmall ? 52 : DEPTH_EDGE_PAD_MAX
			),
			columnGap: clamp(
				metrics.width * DEPTH_COLUMN_GAP_RATIO,
				isSmall ? 10 : DEPTH_COLUMN_GAP_MIN,
				isSmall ? 26 : DEPTH_COLUMN_GAP_MAX
			),
			rowClearance: clamp(
				metrics.height * (isSmall ? 0.16 : DEPTH_ROW_CLEARANCE_RATIO),
				isSmall ? 46 : DEPTH_ROW_CLEARANCE_MIN,
				isSmall ? 108 : DEPTH_ROW_CLEARANCE_MAX
			),
			topPad: clamp(
				metrics.height * (isSmall ? 0.18 : DEPTH_TOP_PAD_RATIO),
				isSmall ? 76 : DEPTH_TOP_PAD_MIN,
				isSmall ? 138 : DEPTH_TOP_PAD_MAX
			),
			bottomPad: clamp(
				metrics.height * DEPTH_BOTTOM_PAD_RATIO,
				DEPTH_BOTTOM_PAD_MIN,
				DEPTH_BOTTOM_PAD_MAX
			),
		};
	};

	const getOlderYearGroups = () => {
		const activeYearNumber = Number.parseInt(ACTIVE_ART_YEAR, 10);
		const groups = new Map();

		ARTWORKS.forEach((artwork) => {
			const yearNumber = Number.parseInt(artwork.year, 10);

			if (!Number.isFinite(yearNumber) || yearNumber >= activeYearNumber) {
				return;
			}

			if (!groups.has(yearNumber)) {
				groups.set(yearNumber, []);
			}

			groups.get(yearNumber).push(artwork);
		});

		return [...groups.entries()]
			.sort((first, second) => second[0] - first[0])
			.map(([year, artworks]) => ({
				year: String(year),
				artworks: artworks.sort((first, second) => first.id.localeCompare(second.id)),
			}));
	};

	const getDepthForLayer = (layerIndex) => (
		clamp(layerIndex / Math.max(DEPTH_ATTRIBUTE_LAYER_COUNT - 1, 1), 0, 1)
	);

	const getDepthArtworkWidth = (artwork, depth, viewportWidth, random) => {
		const maxFrontWidth = Math.min(viewportWidth * DEPTH_FRONT_WIDTH_RATIO, DEPTH_FRONT_WIDTH_MAX);
		const baseWidth = lerp(maxFrontWidth, DEPTH_BACK_WIDTH, depth)
			* lerp(DEPTH_FRONT_SIZE_SCALE, DEPTH_BACK_SIZE_SCALE, depth);
		const width = baseWidth * lerp(DEPTH_WIDTH_RANDOM_MIN, DEPTH_WIDTH_RANDOM_MAX, random());
		const aspect = artwork.width / artwork.height;

		return {
			width,
			height: width / aspect,
		};
	};

	const constrainLayerPosition = (item, x, y, layoutMetrics, metrics) => {
		const maxX = Math.max(layoutMetrics.edgePad, metrics.width - item.width - layoutMetrics.edgePad);
		const maxY = Math.max(layoutMetrics.topPad, metrics.fieldHeight - item.height - layoutMetrics.bottomPad * 0.45);

		return {
			x: clamp(x, layoutMetrics.edgePad, maxX),
			y: clamp(y, layoutMetrics.topPad * 0.5, maxY),
		};
	};

	const layoutYearArtworks = (yearGroup, layerIndex, metrics) => {
		const depth = getDepthForLayer(layerIndex);
		const layoutMetrics = getLayoutMetrics(metrics);
		const availableWidth = Math.max(1, metrics.width - (layoutMetrics.edgePad * 2));
		const layoutItems = yearGroup.artworks.map((artwork) => {
			const random = seededRandom(hashString(`art-depth-${yearGroup.year}-${artwork.id}`));
			const placementRandom = seededRandom(hashString(`art-depth-placement-${DEPTH_LAYOUT_SEED}-${yearGroup.year}-${artwork.id}`));
			const size = getDepthArtworkWidth(artwork, depth, metrics.width, random);
			const width = Math.min(size.width, availableWidth);
			const height = width / (artwork.width / artwork.height);
			const overlapRatio = metrics.width < 520
				? DEPTH_HORIZONTAL_OVERLAP_MOBILE_RATIO
				: DEPTH_HORIZONTAL_OVERLAP_RATIO;
			const overlap = Math.min(width * overlapRatio, DEPTH_HORIZONTAL_OVERLAP_MAX);
			const advanceWidth = Math.max(width - overlap + layoutMetrics.columnGap, width * 0.58);

			return {
				artwork,
				width,
				height,
				advanceWidth,
				offsetX: 0,
				random,
				placementRandom,
			};
		});
		const rows = [];
		let currentRow = [];
		let currentRowAdvance = 0;
		let currentRowVisualWidth = 0;

		const commitRow = () => {
			if (currentRow.length === 0) {
				return;
			}

			rows.push({
				index: rows.length,
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

		let cursorY = layoutMetrics.topPad;

		rows.forEach((row) => {
			row.top = cursorY;
			cursorY += row.height + layoutMetrics.rowClearance;
		});

		return rows.flatMap((row) => {
			const rowRandom = seededRandom(hashString(`art-depth-row-${DEPTH_LAYOUT_SEED}-${yearGroup.year}-${layerIndex}-${row.index}`));
			const rowLeft = layoutMetrics.edgePad + Math.max(0, (availableWidth - row.width) / 2);
			const rowSlack = Math.max(0, availableWidth - row.width);
			const depthScatter = Math.pow(depth, 0.72);
			const rowStaggerXLimit = Math.min(
				DEPTH_ROW_STAGGER_X_MAX,
				(rowSlack * 0.5) + (layoutMetrics.edgePad * 0.8)
			);
			const rowStaggerYLimit = Math.min(DEPTH_ROW_STAGGER_Y_MAX, layoutMetrics.rowClearance * 0.74);
			const rowStaggerX = (rowRandom() - 0.5) * 2 * rowStaggerXLimit * lerp(0.35, 1, depthScatter);
			const rowStaggerY = (rowRandom() - 0.5) * 2 * rowStaggerYLimit * lerp(0.25, 1, depthScatter);
			const layerYShift = metrics.height * DEPTH_LAYER_Y_OFFSET_RATIO * layerIndex;

			return row.items.map((item) => {
				const xJitterLimit = Math.min(DEPTH_JITTER_X_MAX, rowSlack * 0.42, item.width * 0.08);
				const yJitterLimit = Math.min(DEPTH_JITTER_Y_MAX, layoutMetrics.rowClearance * 0.24);
				const xScatterLimit = Math.min(
					lerp(DEPTH_ITEM_SCATTER_X_FRONT, DEPTH_ITEM_SCATTER_X_BACK, depthScatter),
					(item.width * 0.42) + layoutMetrics.columnGap
				);
				const yScatterLimit = Math.min(
					lerp(DEPTH_ITEM_SCATTER_Y_FRONT, DEPTH_ITEM_SCATTER_Y_BACK, depthScatter),
					(layoutMetrics.rowClearance * 1.12) + (item.height * 0.16)
				);
				const jitterX = (item.random() - 0.5) * 2 * xJitterLimit;
				const jitterY = (item.random() - 0.5) * 2 * yJitterLimit;
				const scatterX = (item.placementRandom() - 0.5) * 2 * xScatterLimit;
				const scatterY = (item.placementRandom() - 0.5) * 2 * yScatterLimit;
				const position = constrainLayerPosition(
					item,
					rowLeft + rowStaggerX + item.offsetX + jitterX + scatterX,
					row.top + layerYShift + rowStaggerY + ((row.height - item.height) * 0.5) + jitterY + scatterY,
					layoutMetrics,
					metrics
				);

				return {
					...item,
					depth,
					x: position.x,
					y: position.y,
				};
			});
		});
	};

	const updateLayerColors = (metrics) => {
		const sampleProgress = clamp((metrics.scrollY + (metrics.height * 0.5)) / metrics.fieldHeight, 0, 1);
		const gradient = sampleGradient(sampleProgress);
		const saturation = clamp(gradient.s * DEPTH_TINT_SATURATION, 0, 1);
		const pageLightnessOffset = lerp(DEPTH_TOP_LIGHTNESS_OFFSET, DEPTH_BOTTOM_LIGHTNESS_OFFSET, sampleProgress);
		const bottomBackProgress = Math.pow(
			clamp((sampleProgress - DEPTH_BOTTOM_BACK_DARKEN_START) / (1 - DEPTH_BOTTOM_BACK_DARKEN_START), 0, 1),
			DEPTH_BOTTOM_BACK_DARKEN_POWER
		);

		layers.forEach((state) => {
			const layerLightness = lerp(DEPTH_FRONT_LIGHTNESS, DEPTH_BACK_LIGHTNESS, state.depth);
			const backOnlyOffset = DEPTH_BOTTOM_BACK_LIGHTNESS_OFFSET * bottomBackProgress * state.depth;
			const lightness = clamp(layerLightness + pageLightnessOffset + backOnlyOffset, 0, 1);

			state.element.style.color = `hsl(${gradient.h.toFixed(1)} ${Math.round(saturation * 100)}% ${Math.round(lightness * 100)}%)`;
			state.element.style.setProperty("--depth-brightness", lerp(DEPTH_IMAGE_FRONT_BRIGHTNESS, DEPTH_IMAGE_BACK_BRIGHTNESS, state.depth).toFixed(3));
			state.element.style.setProperty("--depth-image-opacity", lerp(DEPTH_IMAGE_FRONT_OPACITY, DEPTH_IMAGE_BACK_OPACITY, state.depth).toFixed(3));
			state.element.style.setProperty("--depth-contrast", DEPTH_IMAGE_CONTRAST.toFixed(3));
			state.element.style.setProperty("--depth-tint-opacity", lerp(DEPTH_TINT_FRONT_OPACITY, DEPTH_TINT_BACK_OPACITY, state.depth).toFixed(3));
			state.element.style.setProperty("--depth-value-opacity", lerp(DEPTH_VALUE_FRONT_OPACITY, DEPTH_VALUE_BACK_OPACITY, state.depth).toFixed(3));
		});
	};

	const renderDepthArtwork = (state, now, metrics) => {
		const elapsed = reduceMotion.matches ? 0 : now / 1000;
		const travel = metrics.width + state.width + (DEPTH_DRIFT_WRAP_PAD * 2);
		const drift = ((elapsed * state.speed) + state.phase) % travel;
		const x = state.x + (state.direction * drift);
		const wrappedX = state.direction > 0
			? ((x + state.width + DEPTH_DRIFT_WRAP_PAD) % travel) - state.width - DEPTH_DRIFT_WRAP_PAD
			: metrics.width - (((-x + state.width + DEPTH_DRIFT_WRAP_PAD) % travel) - DEPTH_DRIFT_WRAP_PAD);
		const parallaxY = -metrics.scrollY * state.parallax;
		const y = state.y + parallaxY;

		state.element.style.setProperty("--depth-x", `${wrappedX.toFixed(2)}px`);
		state.element.style.setProperty("--depth-y", `${y.toFixed(2)}px`);
	};

	const render = (now) => {
		const metrics = getMetrics();
		const shouldUpdateColor = metrics.scrollY !== lastColorScrollY;

		if (shouldUpdateColor) {
			updateLayerColors(metrics);
			lastColorScrollY = metrics.scrollY;
		}

		depthArtworks.forEach((state) => renderDepthArtwork(state, now, metrics));

		if (!reduceMotion.matches) {
			frame = window.requestAnimationFrame(render);
		} else {
			frame = null;
		}
	};

	const start = () => {
		if (frame || reduceMotion.matches) {
			renderDepthOnce();
			return;
		}

		frame = window.requestAnimationFrame(render);
	};

	const stop = () => {
		if (!frame) {
			return;
		}

		window.cancelAnimationFrame(frame);
		frame = null;
	};

	const createDepthArtworkElement = (item, layer, yearGroup, layerIndex) => {
		const element = document.createElement("span");
		const shouldRenderImage = layerIndex < DEPTH_IMAGE_LAYER_COUNT;

		element.className = shouldRenderImage
			? "art-depth-artwork"
			: "art-depth-artwork is-depth-placeholder";
		element.style.setProperty("--depth-w", `${item.width.toFixed(2)}px`);
		element.style.setProperty("--depth-aspect", (item.width / item.height).toFixed(5));
		element.dataset.year = yearGroup.year;
		element.dataset.artworkId = item.artwork.id;

		if (shouldRenderImage) {
			const image = document.createElement("img");
			image.className = "art-depth-artwork__image";
			image.src = item.artwork.previewSrc || item.artwork.fullSrc;
			image.alt = "";
			image.decoding = "async";
			image.loading = "lazy";
			image.draggable = false;
			image.addEventListener("error", () => {
				element.hidden = true;
			}, { once: true });

			element.append(image);
		}

		layer.append(element);

		const frontness = 1 - item.depth;
		const random = seededRandom(hashString(`art-depth-motion-${yearGroup.year}-${item.artwork.id}`));

		return {
			element,
			depth: item.depth,
			width: item.width,
			height: item.height,
			x: item.x,
			y: item.y,
			phase: random() * (getMetrics().width + item.width + (DEPTH_DRIFT_WRAP_PAD * 2)),
			speed: lerp(DEPTH_DRIFT_BACK_SPEED, DEPTH_DRIFT_FRONT_SPEED, frontness)
				* lerp(DEPTH_DRIFT_RANDOM_MIN, DEPTH_DRIFT_RANDOM_MAX, random()),
			direction: 1,
			parallax: lerp(DEPTH_FRONT_PARALLAX, DEPTH_BACK_PARALLAX, item.depth),
			layerIndex,
		};
	};

	const build = () => {
		layoutQueued = false;
		stop();
		field.replaceChildren();
		layers = [];
		depthArtworks = [];
		lastColorScrollY = null;

		const metrics = getMetrics();
		const yearGroups = getOlderYearGroups();

		lastBuildWidth = metrics.width;

		yearGroups.forEach((yearGroup, layerIndex) => {
			const depth = getDepthForLayer(layerIndex);
			const layer = document.createElement("span");
			layer.className = "art-depth-layer";
			layer.dataset.year = yearGroup.year;
			layer.style.zIndex = String(100 - layerIndex);
			field.append(layer);
			layers.push({ element: layer, depth });

			layoutYearArtworks(yearGroup, layerIndex, metrics)
				.forEach((item) => {
					depthArtworks.push(createDepthArtworkElement(item, layer, yearGroup, layerIndex));
				});
		});

		renderDepthOnce();
		start();
	};

	const renderDepthOnce = () => {
		const metrics = getMetrics();

		updateLayerColors(metrics);
		depthArtworks.forEach((state) => renderDepthArtwork(state, performance.now(), metrics));
		lastColorScrollY = metrics.scrollY;
	};

	const requestBuild = () => {
		const viewportWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
		const shouldRebuild = lastBuildWidth === 0
			|| Math.abs(viewportWidth - lastBuildWidth) > REBUILD_WIDTH_THRESHOLD;

		if (!shouldRebuild) {
			renderDepthOnce();
			return;
		}

		if (layoutQueued) {
			return;
		}

		layoutQueued = true;
		window.requestAnimationFrame(build);
	};

	window.HELLOTEACHER_ART_DEPTH = {
		rebuild: requestBuild,
	};

	window.addEventListener("scroll", () => {
		if (reduceMotion.matches) {
			renderDepthOnce();
		}
	}, { passive: true });
	window.addEventListener("resize", requestBuild);

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			if (reduceMotion.matches) {
				stop();
				renderDepthOnce();
			} else {
				start();
			}
		});
	} else {
		reduceMotion.addListener(() => {
			if (reduceMotion.matches) {
				stop();
				renderDepthOnce();
			} else {
				start();
			}
		});
	}

	window.requestAnimationFrame(build);
})();
