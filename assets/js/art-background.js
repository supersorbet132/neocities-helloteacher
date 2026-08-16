(() => {
	const field = document.querySelector("[data-art-depth-field]");
	const surface = document.querySelector(".art-page__surface");

	if (!field || !surface) {
		return;
	}

	const LAYER_COUNT = 6;
	const RECT_COUNTS = [24, 30, 38, 48, 60, 72];
	const GRADIENT_STOPS = [
		{ position: 0, hex: "#81F5FC" },
		{ position: 0.5, hex: "#DB63C2" },
		{ position: 1, hex: "#3935AB" },
	];
	const RECT_TINT_SATURATION = 0.68;
	const RECT_FRONT_LIGHTNESS = 0.12;
	const RECT_BACK_LIGHTNESS = 0.42;
	const RECT_TOP_LIGHTNESS_OFFSET = 0.25;
	const RECT_BOTTOM_LIGHTNESS_OFFSET = -0.08;
	const RECT_BOTTOM_BACK_LIGHTNESS_OFFSET = -0.16;
	const RECT_BOTTOM_BACK_DARKEN_START = 0.56;
	const RECT_BOTTOM_BACK_DARKEN_POWER = 1.35;
	const RECT_FRONT_SIZE_SCALE = 0.77;
	const RECT_BACK_SIZE_SCALE = 1.12;
	const RECT_FRONT_PARALLAX = 0.2;
	const RECT_BACK_PARALLAX = -0.5;
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

	let layers = [];
	let rects = [];
	let frame = null;
	let lastTime = 0;
	let lastColorScrollY = null;
	let layoutQueued = false;
	let lastBuildWidth = 0;

	const getFieldHeight = () => Math.max(surface.offsetHeight, window.innerHeight || 0, 1);

	const getMetrics = () => ({
		fieldHeight: getFieldHeight(),
		scrollY: window.scrollY,
		width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
		height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
	});

	const updateLayerColors = (metrics) => {
		const sampleProgress = clamp((metrics.scrollY + (metrics.height * 0.5)) / metrics.fieldHeight, 0, 1);
		const gradient = sampleGradient(sampleProgress);
		const saturation = clamp(gradient.s * RECT_TINT_SATURATION, 0, 1);
		const pageLightnessOffset = lerp(RECT_TOP_LIGHTNESS_OFFSET, RECT_BOTTOM_LIGHTNESS_OFFSET, sampleProgress);
		const bottomBackProgress = Math.pow(
			clamp((sampleProgress - RECT_BOTTOM_BACK_DARKEN_START) / (1 - RECT_BOTTOM_BACK_DARKEN_START), 0, 1),
			RECT_BOTTOM_BACK_DARKEN_POWER,
		);

		layers.forEach((state) => {
			const layerLightness = lerp(RECT_FRONT_LIGHTNESS, RECT_BACK_LIGHTNESS, state.depth);
			const backOnlyOffset = RECT_BOTTOM_BACK_LIGHTNESS_OFFSET * bottomBackProgress * state.depth;
			const lightness = clamp(layerLightness + pageLightnessOffset + backOnlyOffset, 0, 1);
			state.element.style.color = `hsl(${gradient.h.toFixed(1)} ${Math.round(saturation * 100)}% ${Math.round(lightness * 100)}%)`;
		});
	};

	const renderRect = (state, now, metrics) => {
		const elapsed = reduceMotion.matches ? 0 : now / 1000;
		const travel = metrics.width + state.width + 160;
		const drift = ((elapsed * state.speed) + state.phase) % travel;
		const x = state.x + (state.direction * drift);
		const wrappedX = state.direction > 0
			? ((x + state.width + 80) % travel) - state.width - 80
			: metrics.width - (((-x + state.width + 80) % travel) - 80);
		const parallaxY = -metrics.scrollY * state.parallax;
		const y = state.y + parallaxY;

		state.element.style.setProperty("--rect-x", `${wrappedX.toFixed(2)}px`);
		state.element.style.setProperty("--rect-y", `${y.toFixed(2)}px`);
	};

	const render = (now) => {
		lastTime = now;
		const metrics = getMetrics();
		const shouldUpdateColor = metrics.scrollY !== lastColorScrollY;

		if (shouldUpdateColor) {
			updateLayerColors(metrics);
			lastColorScrollY = metrics.scrollY;
		}

		rects.forEach((state) => renderRect(state, now, metrics));

		if (!reduceMotion.matches) {
			frame = window.requestAnimationFrame(render);
		} else {
			frame = null;
		}
	};

	const start = () => {
		if (frame || reduceMotion.matches) {
			renderRectsOnce();
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

	const build = () => {
		layoutQueued = false;
		stop();
		field.replaceChildren();
		layers = [];
		rects = [];
		lastColorScrollY = null;

		const viewportWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
		const fieldHeight = getFieldHeight();
		const maxFrontWidth = Math.min(viewportWidth * 0.31, 373);

		lastBuildWidth = viewportWidth;

		for (let layerIndex = 0; layerIndex < LAYER_COUNT; layerIndex += 1) {
			const depth = layerIndex / (LAYER_COUNT - 1);
			const frontness = 1 - depth;
			const layer = document.createElement("span");
			layer.className = "art-depth-layer";
			layer.style.zIndex = String(LAYER_COUNT - layerIndex);
			field.append(layer);
			layers.push({ element: layer, depth });

			for (let rectIndex = 0; rectIndex < RECT_COUNTS[layerIndex]; rectIndex += 1) {
				const random = seededRandom(hashString(`art-depth-${layerIndex}-${rectIndex}`));
				const rect = document.createElement("span");
				rect.className = "art-depth-rect";
				layer.append(rect);

				const baseWidth = lerp(maxFrontWidth, 52, depth) * lerp(RECT_FRONT_SIZE_SCALE, RECT_BACK_SIZE_SCALE, depth);
				const width = baseWidth * lerp(0.72, 1.3, random());
				const height = width * lerp(1, 1.82, random());

				rect.style.setProperty("--rect-w", `${width.toFixed(2)}px`);
				rect.style.setProperty("--rect-h", `${height.toFixed(2)}px`);
				rect.style.setProperty("--rect-opacity", "1");

				rects.push({
					element: rect,
					depth,
					width,
					height,
					x: lerp(-width, viewportWidth, random()),
					y: lerp(-height * 0.5, fieldHeight - (height * 0.5), random()),
					phase: random() * (viewportWidth + width + 160),
					speed: lerp(2, 11, frontness) * lerp(0.65, 1.35, random()),
					direction: 1,
					parallax: lerp(RECT_FRONT_PARALLAX, RECT_BACK_PARALLAX, depth),
				});
			}
		}

		renderRectsOnce();
		start();
	};

	const renderRectsOnce = () => {
		const metrics = getMetrics();

		updateLayerColors(metrics);
		rects.forEach((state) => renderRect(state, performance.now(), metrics));
		lastColorScrollY = metrics.scrollY;
	};

	const requestBuild = () => {
		const viewportWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
		const shouldRebuild = lastBuildWidth === 0
			|| Math.abs(viewportWidth - lastBuildWidth) > REBUILD_WIDTH_THRESHOLD;

		if (!shouldRebuild) {
			renderRectsOnce();
			return;
		}

		if (layoutQueued) {
			return;
		}

		layoutQueued = true;
		window.requestAnimationFrame(build);
	};

	window.addEventListener("scroll", () => {
		if (reduceMotion.matches) {
			renderRectsOnce();
		}
	}, { passive: true });
	window.addEventListener("resize", requestBuild);

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			if (reduceMotion.matches) {
				stop();
				renderRectsOnce();
			} else {
				start();
			}
		});
	} else {
		reduceMotion.addListener(() => {
			if (reduceMotion.matches) {
				stop();
				renderRectsOnce();
			} else {
				start();
			}
		});
	}

	window.requestAnimationFrame(build);
})();
