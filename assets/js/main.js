(() => {
	const scene = document.querySelector("[data-parallax-scene]");

	if (!scene) {
		return;
	}

	const layers = [...scene.querySelectorAll("[data-parallax-speed]")];
	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
	let ticking = false;

	const setParallax = () => {
		if (reduceMotion.matches) {
			layers.forEach((layer) => {
				layer.style.transform = "";
			});
			return;
		}

		const sceneRect = scene.getBoundingClientRect();
		const progress = Math.min(Math.max((0 - sceneRect.top) / sceneRect.height, 0), 1);
		const travel = Math.min(Math.max(sceneRect.height * 0.08, 80), 180);

		layers.forEach((layer) => {
			const speed = Number(layer.dataset.parallaxSpeed) || 1;
			const y = (1 - speed) * travel * progress;

			layer.style.transform = `translate3d(0, ${y}px, 0)`;
		});
	};

	const requestParallax = () => {
		if (ticking) {
			return;
		}

		ticking = true;
		window.requestAnimationFrame(() => {
			setParallax();
			ticking = false;
		});
	};

	setParallax();
	window.addEventListener("scroll", requestParallax, { passive: true });
	window.addEventListener("resize", requestParallax);

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", setParallax);
	} else {
		reduceMotion.addListener(setParallax);
	}
})();

(() => {
	const cards = new Set();
	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
	let ticking = false;

	const getNumberVar = (element, name, fallback) => {
		const value = getComputedStyle(element).getPropertyValue(name).trim();
		const parsed = Number.parseFloat(value);

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const getParallaxRange = (card) => {
		const rangeVar = card.dataset.spriteCard === "cad"
			? "--cad-card-parallax-range"
			: card.dataset.spriteCard === "projects"
				? "--projects-card-parallax-range"
				: "--art-card-parallax-range";

		return getNumberVar(card, rangeVar, 70);
	};

	const getParallaxLayers = (card) => [...card.querySelectorAll("[data-card-parallax-layer]")];

	const clearCardParallax = (card) => {
		getParallaxLayers(card).forEach((layer) => {
			layer.style.removeProperty("--sprite-parallax-y");
		});
	};

	const setCardParallax = (card) => {
		if (reduceMotion.matches) {
			clearCardParallax(card);
			return;
		}

		const rect = card.getBoundingClientRect();
		const viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

		if (viewportHeight <= 0) {
			return;
		}

		const viewportCenter = viewportHeight / 2;
		const cardCenter = rect.top + (rect.height / 2);
		const progress = Math.max(Math.min((viewportCenter - cardCenter) / viewportHeight, 1), -1);
		const range = getParallaxRange(card);

		getParallaxLayers(card).forEach((layer) => {
			const strength = Number.parseFloat(layer.dataset.spriteParallaxStrength) || 0;
			const y = progress * range * strength;

			layer.style.setProperty("--sprite-parallax-y", `${y.toFixed(2)}px`);
		});
	};

	const setAllParallax = () => {
		cards.forEach((card) => setCardParallax(card));
	};

	const requestParallax = () => {
		if (ticking) {
			return;
		}

		ticking = true;
		window.requestAnimationFrame(() => {
			setAllParallax();
			ticking = false;
		});
	};

	window.helloTeacherSpriteParallax = {
		register(card) {
			cards.add(card);
			requestParallax();
		},
		refresh: requestParallax,
	};

	window.addEventListener("scroll", requestParallax, { passive: true });
	window.addEventListener("resize", requestParallax);

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", setAllParallax);
	} else {
		reduceMotion.addListener(setAllParallax);
	}
})();

(() => {
	const cadCards = [...document.querySelectorAll("[data-sprite-card='cad']")];

	if (!cadCards.length) {
		return;
	}

	const layerOrderTopToBottom = [
		"cad_front_colordodge",
		"cad_left_structure2",
		"cad_left_structure1",
		"cad_top_structure",
		"cad_desk",
		"cad_title_colordodge",
		"cad_title_shell",
		"cad_title_add",
		"cad_title",
		"cad_engine_mask_add",
		"cad_engine_front_left",
		"cad_engine_front_right",
		"cad_beam_add2",
		"cad_beam_colordodge",
		"cad_beam_add",
		"cad_beam_color",
		"cad_engine_center_left",
		"cad_engine_center_right",
		"cad_engine_back_left",
		"cad_engine_back_right",
		"cad_back3",
		"cad_back2",
		"cad_back1",
	];
	const layerOrderBottomToTop = [...layerOrderTopToBottom].reverse();
	const topIndexByLayer = new Map(layerOrderTopToBottom.map((name, index) => [name, index]));
	const hiddenAtRest = new Set([
		"cad_beam_add2",
		"cad_beam_colordodge",
		"cad_beam_add",
		"cad_beam_color",
		"cad_front_colordodge",
		"cad_title_colordodge",
		"cad_title_add",
		"cad_engine_mask_add",
	]);
	const backMoveLayers = new Set([
		"cad_back3",
		"cad_back2",
		"cad_back1",
	]);
	const frontMoveLayers = new Set([
		"cad_left_structure2",
		"cad_left_structure1",
		"cad_top_structure",
		"cad_desk",
	]);
	const engineCenterLayers = new Set([
		"cad_engine_center_left",
		"cad_engine_center_right",
	]);
	const frontParallaxLayers = new Set([
		"cad_front_colordodge",
		"cad_left_structure2",
		"cad_left_structure1",
		"cad_top_structure",
		"cad_desk",
	]);
	const backParallaxLayers = new Set([
		"cad_back3",
		"cad_back2",
		"cad_back1",
	]);
	const titleParallaxLayers = new Set([
		"cad_title_colordodge",
		"cad_title_shell",
		"cad_title_add",
		"cad_title",
	]);
	const strongHoverFlickerLayers = new Set([
		"cad_beam_add2",
		"cad_beam_add",
	]);
	const softHoverFlickerLayers = new Set([
		"cad_engine_mask_add",
		"cad_title_colordodge",
		"cad_front_colordodge",
	]);
	const extraRestOffsets = new Map([
		["cad_engine_center_left", "calc(var(--cad-rest-left-x) - 20px)"],
		["cad_engine_center_right", "calc(var(--cad-rest-right-x) + 20px)"],
	]);
	const rightRestLayers = new Set([
		"cad_desk",
		"cad_back1",
		"cad_top_structure",
	]);
	const leftRestLayers = new Set([
		"cad_back3",
		"cad_back2",
	]);
	const blendModes = new Map([
		["cad_front_colordodge", "color-dodge"],
		["cad_title_colordodge", "color-dodge"],
		["cad_title_add", "plus-lighter"],
		["cad_engine_mask_add", "plus-lighter"],
		["cad_beam_add2", "plus-lighter"],
		["cad_beam_colordodge", "color-dodge"],
		["cad_beam_add", "plus-lighter"],
		["cad_beam_color", "color"],
	]);
	const maskTargets = new Map([
		["cad_front_colordodge", ["cad_left_structure2", "cad_left_structure1", "cad_top_structure", "cad_desk"]],
		["cad_engine_mask_add", ["cad_engine_front_left", "cad_engine_front_right"]],
		["cad_beam_add", ["cad_beam_color"]],
	]);
	const manifestUrl = "/assets/images/site/sprite-crop-manifest.json";
	const assetBase = "/assets/images/site/cad/";
	const leaveTimers = new WeakMap();

	const getNumberVar = (element, name, fallback) => {
		const value = getComputedStyle(element).getPropertyValue(name).trim();
		const parsed = Number.parseFloat(value);

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const cssLengthList = (items) => items.join(", ");
	const cssUrlList = (items) => items.map((item) => `url("${assetBase}${item}.png")`).join(", ");

	const getRestSide = (layerName) => {
		if (layerName.includes("right") || rightRestLayers.has(layerName)) {
			return "right";
		}

		if (layerName.includes("left") || leftRestLayers.has(layerName)) {
			return "left";
		}

		return "center";
	};

	const getMoveGroup = (layerName) => {
		if (backMoveLayers.has(layerName)) {
			return "back";
		}

		if (frontMoveLayers.has(layerName)) {
			return "front";
		}

		if (engineCenterLayers.has(layerName)) {
			return "center";
		}

		if (layerName.startsWith("cad_engine_")) {
			return "engine";
		}

		return "none";
	};

	const getCadParallaxStrength = (card, layerName) => {
		if (frontParallaxLayers.has(layerName)) {
			return getNumberVar(card, "--cad-parallax-front-strength", 0.22);
		}

		if (titleParallaxLayers.has(layerName)) {
			return getNumberVar(card, "--cad-parallax-title-strength", 0.55);
		}

		if (layerName.startsWith("cad_engine_") || layerName.startsWith("cad_beam_")) {
			return getNumberVar(card, "--cad-parallax-engine-strength", 0.68);
		}

		if (backParallaxLayers.has(layerName)) {
			return getNumberVar(card, "--cad-parallax-back-strength", 0.85);
		}

		return getNumberVar(card, "--cad-parallax-fallback-strength", 0.4);
	};

	const setMask = (sprite, layerName, effectBox, spritesByName) => {
		const targets = maskTargets.get(layerName);

		if (!targets) {
			return;
		}

		const validTargets = targets
			.map((targetName) => spritesByName.get(targetName))
			.filter(Boolean);

		if (!validTargets.length) {
			return;
		}

		sprite.classList.add("is-masked");
		sprite.style.setProperty("--sprite-mask-image", cssUrlList(validTargets.map((target) => target.file.replace(/\.png$/i, ""))));
		sprite.style.setProperty("--sprite-mask-position", cssLengthList(validTargets.map((target) => {
			const box = target.cropBox;
			return `calc(${box.left - effectBox.left} * var(--cad-unit)) calc(${box.top - effectBox.top} * var(--cad-unit))`;
		})));
		sprite.style.setProperty("--sprite-mask-size", cssLengthList(validTargets.map((target) => {
			const box = target.cropBox;
			return `calc(${box.width} * var(--cad-unit)) calc(${box.height} * var(--cad-unit))`;
		})));
	};

	const setSpriteMovement = (sprite, layerName) => {
		const moveGroup = getMoveGroup(layerName);

		if (moveGroup === "none") {
			sprite.style.setProperty("--sprite-move-in-delay", "0ms");
			sprite.style.setProperty("--sprite-move-out-delay", "0ms");
			return;
		}

		sprite.style.setProperty("--sprite-move-in-delay", `var(--cad-${moveGroup}-move-delay)`);
		sprite.style.setProperty("--sprite-move-out-delay", `var(--cad-${moveGroup}-move-out-delay)`);

		if (engineCenterLayers.has(layerName)) {
			sprite.style.setProperty("--sprite-move-duration", "var(--cad-engine-center-move-duration)");
		}
	};

	const setSpriteTiming = (card, sprite, layerName) => {
		const effectDelay = getNumberVar(card, "--cad-effect-delay", 1860);
		const effectFadeDuration = getNumberVar(card, "--cad-effect-fade-duration", 520);

		if (!hiddenAtRest.has(layerName)) {
			sprite.style.setProperty("--sprite-in-delay", "0ms");
			sprite.style.setProperty("--sprite-out-delay", "0ms");
			return;
		}

		sprite.classList.add("is-hover-only");
		sprite.classList.add("is-flicker-in");
		if (strongHoverFlickerLayers.has(layerName)) {
			sprite.classList.add("is-strong-hover-flicker");
		}
		if (softHoverFlickerLayers.has(layerName)) {
			sprite.classList.add("is-soft-hover-flicker");
		}
		sprite.style.setProperty("--sprite-rest-opacity", "0");
		sprite.style.setProperty("--sprite-hover-opacity", "1");
		sprite.style.setProperty("--sprite-in-delay", `${effectDelay}ms`);
		sprite.style.setProperty("--sprite-out-delay", "0ms");
		sprite.style.setProperty("--sprite-fade-duration", `${effectFadeDuration}ms`);
		sprite.style.setProperty("--sprite-loop-delay", `${effectDelay + effectFadeDuration}ms`);
	};

	const bindCadCardState = (card) => {
		if (card.dataset.cadStateBound === "true") {
			return;
		}

		const hitbox = card.querySelector("[data-card-hitbox]") || card;
		const enter = () => {
			const timer = leaveTimers.get(card);

			if (timer) {
				window.clearTimeout(timer);
			}
			card.classList.remove("is-leaving");
			card.classList.add("is-hovered");
		};
		const leave = () => {
			if (card.matches(":focus-within")) {
				return;
			}

			if (!card.classList.contains("is-hovered")) {
				return;
			}

			const leaveWindow = getNumberVar(card, "--cad-leave-animation-window", 620);
			const existingTimer = leaveTimers.get(card);

			if (existingTimer) {
				window.clearTimeout(existingTimer);
			}
			card.classList.remove("is-hovered");
			card.classList.add("is-leaving");
			leaveTimers.set(card, window.setTimeout(() => {
				card.classList.remove("is-leaving");
				leaveTimers.delete(card);
			}, leaveWindow));
		};

		hitbox.addEventListener("pointerenter", enter);
		hitbox.addEventListener("pointerleave", leave);
		card.addEventListener("focusin", enter);
		card.addEventListener("focusout", (event) => {
			if (!card.contains(event.relatedTarget)) {
				leave();
			}
		});
		card.dataset.cadStateBound = "true";
	};

	const buildCadCard = (card, sprites) => {
		const scene = card.querySelector("[data-cad-card-scene]");

		if (!scene) {
			return;
		}

		const sourceX = getNumberVar(card, "--cad-source-x", 0);
		const sourceY = getNumberVar(card, "--cad-source-y", 3702);
		const spritesByName = new Map(sprites.map((sprite) => [sprite.file.replace(/\.png$/i, ""), sprite]));
		const missingLayers = layerOrderTopToBottom.filter((name) => !spritesByName.has(name));
		const extraLayers = [...spritesByName.keys()].filter((name) => !topIndexByLayer.has(name));

		if (missingLayers.length || extraLayers.length) {
			console.warn("CAD card layer mismatch", { missingLayers, extraLayers });
		}

		const fragment = document.createDocumentFragment();

		layerOrderBottomToTop.forEach((layerName, bottomIndex) => {
			const spriteData = spritesByName.get(layerName);

			if (!spriteData) {
				return;
			}

			const box = spriteData.cropBox;
			const sprite = document.createElement("span");
			const parallax = document.createElement("span");
			const image = document.createElement("img");
			const restSide = getRestSide(layerName);

			sprite.className = "cad-sprite-card__sprite";
			sprite.dataset.cadLayer = layerName;
			parallax.className = "cad-sprite-card__parallax";
			parallax.dataset.cardParallaxLayer = layerName;
			parallax.dataset.spriteParallaxStrength = getCadParallaxStrength(card, layerName).toFixed(3);
			image.className = "cad-sprite-card__sprite-image";
			image.src = `${assetBase}${spriteData.file}`;
			image.alt = "";
			image.decoding = "async";
			image.loading = "lazy";
			sprite.setAttribute("aria-hidden", "true");
			sprite.style.setProperty("--sprite-left", box.left - sourceX);
			sprite.style.setProperty("--sprite-top", box.top - sourceY);
			sprite.style.setProperty("--sprite-width", box.width);
			sprite.style.setProperty("--sprite-height", box.height);
			sprite.style.setProperty("--sprite-z", bottomIndex + 1);

			if (extraRestOffsets.has(layerName)) {
				sprite.style.setProperty("--sprite-rest-x", extraRestOffsets.get(layerName));
			} else if (restSide === "left") {
				sprite.style.setProperty("--sprite-rest-x", "var(--cad-rest-left-x)");
			} else if (restSide === "right") {
				sprite.style.setProperty("--sprite-rest-x", "var(--cad-rest-right-x)");
			}

			if (blendModes.has(layerName)) {
				sprite.style.setProperty("--sprite-blend", blendModes.get(layerName));
			}

			setMask(parallax, layerName, box, spritesByName);
			setSpriteMovement(sprite, layerName);
			setSpriteTiming(card, sprite, layerName);
			parallax.append(image);
			sprite.append(parallax);
			fragment.append(sprite);
		});

		scene.replaceChildren(fragment);
		bindCadCardState(card);
		window.helloTeacherSpriteParallax?.register(card);
		card.dataset.spriteCardReady = "true";
	};

	fetch(manifestUrl)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Could not load ${manifestUrl}`);
			}

			return response.json();
		})
		.then((manifest) => {
			const cadSprites = manifest?.folders?.cad?.sprites || [];

			cadCards.forEach((card) => buildCadCard(card, cadSprites));
		})
		.catch((error) => {
			console.warn("CAD card sprites were not loaded", error);
		});
})();

(() => {
	const journalCards = [...document.querySelectorAll("[data-sprite-card='journal']")];

	if (!journalCards.length) {
		return;
	}

	const layerOrderTopToBottom = [
		"journal_add",
		"journal_overlay",
		"journal_grass_detail",
		"journal_rocks",
		"journal_character",
		"journal_flowers",
		"journal_waterfall",
		"journal_title",
		"journal_leaffront",
		"journal_tree",
		"journal_leafback2",
		"journal_leafback1",
		"journal_grass",
		"journal_book",
		"journal_splotches",
	];
	const layerOrderBottomToTop = [...layerOrderTopToBottom].reverse();
	const topIndexByLayer = new Map(layerOrderTopToBottom.map((name, index) => [name, index]));
	const hiddenAtRest = new Set([
		"journal_add",
		"journal_overlay",
	]);
	const lockedMotionLayers = new Set([
		"journal_book",
		"journal_grass",
		"journal_waterfall",
		"journal_flowers",
		"journal_grass_detail",
	]);
	const blendModes = new Map([
		["journal_add", "plus-lighter"],
		["journal_overlay", "overlay"],
	]);
	const lateMotionLayers = new Set([
		"journal_rocks",
		"journal_splotches",
		"journal_title",
	]);
	const regularMaskTargets = layerOrderTopToBottom.filter((name) => (
		!hiddenAtRest.has(name)
		&& !lockedMotionLayers.has(name)
		&& !lateMotionLayers.has(name)
	));
	const maskTargetGroups = [
		{ timingLayer: "journal_character", targets: regularMaskTargets },
		{ timingLayer: "journal_book", targets: [...lockedMotionLayers] },
		{ timingLayer: "journal_rocks", targets: ["journal_rocks"] },
		{ timingLayer: "journal_splotches", targets: ["journal_splotches"] },
		{ timingLayer: "journal_title", targets: ["journal_title"] },
	];
	const manifestUrl = "/assets/images/site/sprite-crop-manifest.json";
	const assetBase = "/assets/images/site/journal/";

	const getNumberVar = (element, name, fallback) => {
		const value = getComputedStyle(element).getPropertyValue(name).trim();
		const parsed = Number.parseFloat(value);

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const cssLengthList = (items) => items.join(", ");
	const cssUrlList = (items) => items.map((item) => `url("${assetBase}${item}.png")`).join(", ");

	const setMask = (sprite, targets, effectBox, spritesByName) => {
		const validTargets = targets
			.map((targetName) => spritesByName.get(targetName))
			.filter(Boolean);

		if (!validTargets.length) {
			return;
		}

		sprite.classList.add("is-masked");
		sprite.style.setProperty("--sprite-mask-image", cssUrlList(validTargets.map((target) => target.file.replace(/\.png$/i, ""))));
		sprite.style.setProperty("--sprite-mask-position", cssLengthList(validTargets.map((target) => {
			const box = target.cropBox;
			return `calc(${box.left - effectBox.left} * var(--journal-unit)) calc(${box.top - effectBox.top} * var(--journal-unit))`;
		})));
		sprite.style.setProperty("--sprite-mask-size", cssLengthList(validTargets.map((target) => {
			const box = target.cropBox;
			return `calc(${box.width} * var(--journal-unit)) calc(${box.height} * var(--journal-unit))`;
		})));
	};

	const getMoveDelayVar = (layerName, direction) => {
		const suffix = direction === "in" ? "move-delay" : "move-out-delay";

		if (layerName === "journal_title") {
			return `--journal-title-${suffix}`;
		}

		if (layerName === "journal_splotches") {
			return `--journal-splotches-${suffix}`;
		}

		if (layerName === "journal_rocks") {
			return `--journal-rocks-${suffix}`;
		}

		if (lockedMotionLayers.has(layerName)) {
			return direction === "in"
				? "--journal-locked-move-delay"
				: "--journal-regular-move-out-delay";
		}

		return direction === "in"
			? "--journal-regular-move-delay"
			: "--journal-regular-move-out-delay";
	};

	const setSpriteTiming = (sprite, layerName, timingLayerName = layerName) => {
		sprite.style.setProperty("--sprite-move-in-delay", `var(${getMoveDelayVar(timingLayerName, "in")})`);
		sprite.style.setProperty("--sprite-move-out-delay", `var(${getMoveDelayVar(timingLayerName, "out")})`);
		sprite.style.setProperty("--sprite-fade-in-delay", hiddenAtRest.has(layerName) ? "var(--journal-effect-fade-in-delay)" : `var(${getMoveDelayVar(timingLayerName, "in")})`);
		sprite.style.setProperty("--sprite-fade-out-delay", hiddenAtRest.has(layerName) ? "var(--journal-effect-fade-out-delay)" : `var(${getMoveDelayVar(timingLayerName, "out")})`);
		sprite.style.setProperty("--sprite-fade-duration", "var(--journal-fade-duration)");

		if (lockedMotionLayers.has(timingLayerName)) {
			sprite.style.setProperty("--sprite-move-duration", "var(--journal-locked-move-duration)");
			return;
		}

		if (lateMotionLayers.has(timingLayerName)) {
			sprite.style.setProperty("--sprite-move-duration", "var(--journal-late-move-duration)");
			return;
		}

		sprite.style.setProperty("--sprite-move-duration", "var(--journal-move-duration)");
	};

	const bindJournalCardState = (card) => {
		if (card.dataset.journalStateBound === "true") {
			return;
		}

		const hitbox = card.querySelector("[data-card-hitbox]") || card;
		const enter = () => {
			card.classList.add("is-hovered");
		};
		const leave = () => {
			if (card.matches(":focus-within")) {
				return;
			}

			card.classList.remove("is-hovered");
		};

		hitbox.addEventListener("pointerenter", enter);
		hitbox.addEventListener("pointerleave", leave);
		card.addEventListener("focusin", enter);
		card.addEventListener("focusout", (event) => {
			if (!card.contains(event.relatedTarget)) {
				leave();
			}
		});
		card.dataset.journalStateBound = "true";
	};

	const buildJournalCard = (card, sprites) => {
		const scene = card.querySelector("[data-journal-card-scene]");

		if (!scene) {
			return;
		}

		const sourceX = getNumberVar(card, "--journal-source-x", 0);
		const sourceY = getNumberVar(card, "--journal-source-y", 5151);
		const spritesByName = new Map(sprites.map((sprite) => [sprite.file.replace(/\.png$/i, ""), sprite]));
		const missingLayers = layerOrderTopToBottom.filter((name) => !spritesByName.has(name));
		const extraLayers = [...spritesByName.keys()].filter((name) => !topIndexByLayer.has(name));

		if (missingLayers.length || extraLayers.length) {
			console.warn("Journal card layer mismatch", { missingLayers, extraLayers });
		}

		const fragment = document.createDocumentFragment();

		const createSpriteElement = (layerName, spriteData, bottomIndex, timingLayerName = layerName, maskTargets = null) => {
			const box = spriteData.cropBox;
			const sprite = document.createElement("span");
			const image = document.createElement("img");

			sprite.className = "journal-sprite-card__sprite";
			sprite.dataset.journalLayer = layerName;
			if (timingLayerName !== layerName) {
				sprite.dataset.journalTimingLayer = timingLayerName;
			}
			image.className = "journal-sprite-card__sprite-image";
			image.src = `${assetBase}${spriteData.file}`;
			image.alt = "";
			image.decoding = "async";
			image.loading = "lazy";
			sprite.setAttribute("aria-hidden", "true");
			sprite.style.setProperty("--sprite-left", box.left - sourceX);
			sprite.style.setProperty("--sprite-top", box.top - sourceY);
			sprite.style.setProperty("--sprite-width", box.width);
			sprite.style.setProperty("--sprite-height", box.height);
			sprite.style.setProperty("--sprite-z", bottomIndex + 1);

			if (hiddenAtRest.has(layerName)) {
				sprite.style.setProperty("--sprite-rest-opacity", "0");
				sprite.style.setProperty("--sprite-hover-opacity", "1");
			}

			if (blendModes.has(layerName)) {
				sprite.style.setProperty("--sprite-blend", blendModes.get(layerName));
			}

			if (maskTargets) {
				setMask(sprite, maskTargets, box, spritesByName);
			}

			setSpriteTiming(sprite, layerName, timingLayerName);
			sprite.append(image);
			return sprite;
		};

		layerOrderBottomToTop.forEach((layerName, bottomIndex) => {
			const spriteData = spritesByName.get(layerName);

			if (!spriteData) {
				return;
			}

			if (blendModes.has(layerName)) {
				maskTargetGroups.forEach((group) => {
					fragment.append(createSpriteElement(layerName, spriteData, bottomIndex, group.timingLayer, group.targets));
				});
				return;
			}

			fragment.append(createSpriteElement(layerName, spriteData, bottomIndex));
		});

		scene.replaceChildren(fragment);
		bindJournalCardState(card);
		card.dataset.spriteCardReady = "true";
	};

	fetch(manifestUrl)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Could not load ${manifestUrl}`);
			}

			return response.json();
		})
		.then((manifest) => {
			const journalSprites = manifest?.folders?.journal?.sprites || [];

			journalCards.forEach((card) => buildJournalCard(card, journalSprites));
		})
		.catch((error) => {
			console.warn("Journal card sprites were not loaded", error);
		});
})();

(() => {
	const projectsCards = [...document.querySelectorAll("[data-sprite-card='projects']")];

	if (!projectsCards.length) {
		return;
	}

	const layerOrderTopToBottom = [
		"projects_o_colordodge",
		"projects_p_colordodge",
		"projects_j_colordodge",
		"projects_t_colordodge",
		"projects_s_outline",
		"projects_t_outline",
		"projects_c_outline",
		"projects_e_outline",
		"projects_j_outline",
		"projects_o_outline",
		"projects_r_outline",
		"projects_p_outline",
		"projects_s_hardmix",
		"projects_j_hardmix",
		"projects_p_hardmix",
		"projects_s",
		"projects_t",
		"projects_c",
		"projects_e",
		"projects_j",
		"projects_o",
		"projects_r",
		"projects_p",
		"projects_board",
		"projects_blueprint_glow_colordodge",
		"projects_blueprint_jimbo_colordodge",
		"projects_blueprint",
		"projects_metal",
		"projects_ruler",
		"projects_pencil",
		"projects_triangle",
		"projects_eraser",
	];
	const layerOrderBottomToTop = [...layerOrderTopToBottom].reverse();
	const topIndexByLayer = new Map(layerOrderTopToBottom.map((name, index) => [name, index]));
	const letterLayers = new Set([
		"projects_p",
		"projects_r",
		"projects_o",
		"projects_j",
		"projects_e",
		"projects_c",
		"projects_t",
		"projects_s",
	]);
	const lockedMotionTargets = new Map([
		["projects_p_outline", "projects_p"],
		["projects_r_outline", "projects_r"],
		["projects_o_outline", "projects_o"],
		["projects_j_outline", "projects_j"],
		["projects_e_outline", "projects_e"],
		["projects_c_outline", "projects_c"],
		["projects_t_outline", "projects_t"],
		["projects_s_outline", "projects_s"],
		["projects_p_colordodge", "projects_p"],
		["projects_o_colordodge", "projects_o"],
		["projects_j_colordodge", "projects_j"],
		["projects_t_colordodge", "projects_t"],
		["projects_p_hardmix", "projects_p"],
		["projects_j_hardmix", "projects_j"],
		["projects_s_hardmix", "projects_s"],
		["projects_blueprint_glow_colordodge", "projects_blueprint"],
		["projects_blueprint_jimbo_colordodge", "projects_blueprint"],
	]);
	const nonTitleMotionGroups = new Map([
		["projects_board", "board"],
		["projects_blueprint", "blueprint"],
		["projects_metal", "metal"],
		["projects_ruler", "ruler"],
		["projects_pencil", "pencil"],
		["projects_triangle", "triangle"],
		["projects_eraser", "eraser"],
	]);
	const hiddenAtRest = new Set(layerOrderTopToBottom.filter((name) => (
		name.includes("_colordodge") || name.includes("_hardmix")
	)));
	const blendMaskTargets = new Map([...lockedMotionTargets]
		.filter(([layerName]) => hiddenAtRest.has(layerName))
		.map(([layerName, targetName]) => [layerName, [targetName]]));
	const blendModes = new Map([
		...layerOrderTopToBottom
			.filter((name) => name.includes("_colordodge"))
			.map((name) => [name, "color-dodge"]),
		// CSS does not support Photoshop's exact "hard mix"; hard-light is the closest native blend fallback.
		...layerOrderTopToBottom
			.filter((name) => name.includes("_hardmix"))
			.map((name) => [name, "hard-light"]),
	]);
	const manifestUrl = "/assets/images/site/sprite-crop-manifest.json";
	const assetBase = "/assets/images/site/projects/";
	const leaveTimers = new WeakMap();

	const getNumberVar = (element, name, fallback) => {
		const value = getComputedStyle(element).getPropertyValue(name).trim();
		const parsed = Number.parseFloat(value);

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const getLetterPart = (layerName) => {
		const match = layerName.match(/^projects_([a-z])(?:_(outline|colordodge|hardmix))?$/);

		if (!match) {
			return null;
		}

		return {
			letter: match[1],
			variant: match[2] || "base",
		};
	};

	const usesFullCanvasCoordinates = (spriteData) => {
		const original = spriteData.original || {};

		return original.width === 2560 && original.height === 7130;
	};

	const projectsCalc = (...terms) => `calc((${terms.filter(Boolean).join(" + ")}) * var(--projects-unit))`;
	const cssLengthList = (items) => items.join(", ");
	const cssUrlList = (items) => items.map((item) => `url("${assetBase}${item}.png")`).join(", ");

	const getPositionTerm = (spriteData, layerName, axis, sourceOffset) => {
		const box = spriteData.cropBox;
		const letterPart = getLetterPart(layerName);
		const coordinate = axis === "x" ? box.left : box.top;

		if (letterPart && letterPart.variant !== "colordodge") {
			const baseVar = `var(--projects-${letterPart.letter}-${axis})`;
			const variantVar = letterPart.variant === "base"
				? "0"
				: `var(--projects-${letterPart.letter}-${letterPart.variant}-${axis})`;

			return projectsCalc(`var(--projects-title-${axis})`, baseVar, variantVar, coordinate);
		}

		if (letterPart && letterPart.variant === "colordodge") {
			return projectsCalc(
				`var(--projects-title-${axis})`,
				`var(--projects-${letterPart.letter}-colordodge-${axis})`,
				coordinate - (usesFullCanvasCoordinates(spriteData) ? sourceOffset : 0),
			);
		}

		const layerDialName = layerName.replace(/^projects_/, "").replaceAll("_", "-");
		const layerDial = `var(--projects-${layerDialName}-${axis}, 0)`;
		const adjustedCoordinate = coordinate - (usesFullCanvasCoordinates(spriteData) ? sourceOffset : 0);

		return projectsCalc(layerDial, adjustedCoordinate);
	};

	const setMask = (maskElement, layerName, spriteData, spritesByName, sourceX, sourceY) => {
		const targets = blendMaskTargets.get(layerName);

		if (!targets) {
			return;
		}

		const validTargets = targets
			.map((targetName) => ({
				name: targetName,
				data: spritesByName.get(targetName),
			}))
			.filter((target) => target.data);

		if (!validTargets.length) {
			return;
		}

		const effectLeft = getPositionTerm(spriteData, layerName, "x", sourceX);
		const effectTop = getPositionTerm(spriteData, layerName, "y", sourceY);

		maskElement.classList.add("is-masked");
		maskElement.style.setProperty("--sprite-mask-image", cssUrlList(validTargets.map((target) => target.data.file.replace(/\.png$/i, ""))));
		maskElement.style.setProperty("--sprite-mask-position", cssLengthList(validTargets.map((target) => {
			const targetLeft = getPositionTerm(target.data, target.name, "x", sourceX);
			const targetTop = getPositionTerm(target.data, target.name, "y", sourceY);

			return `calc(${targetLeft} - ${effectLeft}) calc(${targetTop} - ${effectTop})`;
		})));
		maskElement.style.setProperty("--sprite-mask-size", cssLengthList(validTargets.map((target) => {
			const box = target.data.cropBox;

			return `calc(${box.width} * var(--projects-unit)) calc(${box.height} * var(--projects-unit))`;
		})));
	};

	const getProjectsParallaxStrength = (card, layerName) => {
		const motionTarget = lockedMotionTargets.get(layerName) || layerName;

		if (letterLayers.has(motionTarget)) {
			return getNumberVar(card, "--projects-parallax-title-strength", 0.72);
		}

		if (motionTarget.startsWith("projects_blueprint")) {
			return getNumberVar(card, "--projects-parallax-blueprint-strength", 0.62);
		}

		if (motionTarget === "projects_board" || motionTarget === "projects_metal") {
			return getNumberVar(card, "--projects-parallax-board-strength", 0.42);
		}

		if (
			motionTarget === "projects_ruler" ||
			motionTarget === "projects_pencil" ||
			motionTarget === "projects_triangle" ||
			motionTarget === "projects_eraser"
		) {
			return getNumberVar(card, "--projects-parallax-tool-strength", 0.84);
		}

		return getNumberVar(card, "--projects-parallax-fallback-strength", 0.55);
	};

	const setSpriteTiming = (card, sprite, layerName) => {
		const motionTarget = lockedMotionTargets.get(layerName) || layerName;
		const targetTopIndex = topIndexByLayer.get(motionTarget) ?? topIndexByLayer.get(layerName) ?? 0;
		const isTitleMotion = letterLayers.has(motionTarget);
		const nonTitleMotionGroup = nonTitleMotionGroups.get(motionTarget);
		const hasNonTitleMotion = Boolean(nonTitleMotionGroup);
		const staggerMs = getNumberVar(card, "--projects-stagger-ms", 18);
		const nonTitleLeadMs = getNumberVar(card, "--projects-nontitle-lead-ms", 80);
		const baseDuration = getNumberVar(card, "--projects-move-base-duration", 1120);
		const durationSpread = getNumberVar(card, "--projects-move-duration-spread", 360);
		const moveDuration = baseDuration + ((targetTopIndex * 31) % durationSpread);
		const inDelay = (layerOrderTopToBottom.length - 1 - targetTopIndex) * staggerMs;
		const outDelay = targetTopIndex * staggerMs;
		const moveInDelay = hasNonTitleMotion ? Math.max(0, inDelay - nonTitleLeadMs) : inDelay;
		const moveOutDelay = hasNonTitleMotion ? outDelay + nonTitleLeadMs : outDelay;
		const hasMotion = isTitleMotion || hasNonTitleMotion;

		sprite.style.setProperty("--sprite-move-duration", `${moveDuration}ms`);

		if (isTitleMotion) {
			sprite.style.setProperty("--sprite-rest-x", "var(--projects-title-rest-x)");
			sprite.style.setProperty("--sprite-rest-y", "0px");
			sprite.style.setProperty("--sprite-hover-x", "0px");
			sprite.style.setProperty("--sprite-hover-y", "0px");
			sprite.style.setProperty("--sprite-move-in-delay", `${moveInDelay}ms`);
			sprite.style.setProperty("--sprite-move-out-delay", `${moveOutDelay}ms`);
		} else if (hasNonTitleMotion) {
			sprite.style.setProperty("--sprite-rest-x", `calc(var(--projects-${nonTitleMotionGroup}-hover-shift-x) + var(--projects-rest-offset-x))`);
			sprite.style.setProperty("--sprite-rest-y", `calc(var(--projects-${nonTitleMotionGroup}-hover-shift-y) + var(--projects-rest-offset-y))`);
			sprite.style.setProperty("--sprite-hover-x", `var(--projects-${nonTitleMotionGroup}-hover-shift-x)`);
			sprite.style.setProperty("--sprite-hover-y", `var(--projects-${nonTitleMotionGroup}-hover-shift-y)`);
			sprite.style.setProperty("--sprite-move-in-delay", `${moveInDelay}ms`);
			sprite.style.setProperty("--sprite-move-out-delay", `${moveOutDelay}ms`);
		} else {
			sprite.style.setProperty("--sprite-move-in-delay", "0ms");
			sprite.style.setProperty("--sprite-move-out-delay", "0ms");
		}

		if (hiddenAtRest.has(layerName)) {
			sprite.classList.add("is-hover-only", "is-flicker-in");
			sprite.style.setProperty("--sprite-rest-opacity", "0");
			sprite.style.setProperty("--sprite-hover-opacity", "1");
			sprite.style.setProperty("--sprite-fade-in-delay", hasMotion
				? "calc(var(--sprite-move-in-delay) + var(--projects-effect-delay))"
				: "var(--projects-effect-delay)");
			sprite.style.setProperty("--sprite-fade-out-delay", "0ms");
			sprite.style.setProperty("--sprite-fade-duration", "var(--projects-effect-fade-duration)");
			return;
		}

		sprite.style.setProperty("--sprite-fade-in-delay", hasMotion ? "var(--sprite-move-in-delay)" : "0ms");
		sprite.style.setProperty("--sprite-fade-out-delay", hasMotion ? "var(--sprite-move-out-delay)" : "0ms");
		sprite.style.setProperty("--sprite-fade-duration", "var(--projects-effect-fade-duration)");
	};

	const bindProjectsCardState = (card) => {
		if (card.dataset.projectsStateBound === "true") {
			return;
		}

		const hitbox = card.querySelector("[data-card-hitbox]") || card;
		const enter = () => {
			const timer = leaveTimers.get(card);

			if (timer) {
				window.clearTimeout(timer);
			}

			card.classList.remove("is-leaving");
			card.classList.add("is-hovered");
		};
		const leave = () => {
			if (card.matches(":focus-within")) {
				return;
			}

			if (!card.classList.contains("is-hovered")) {
				return;
			}

			const leaveWindow = getNumberVar(card, "--projects-leave-animation-window", 2000);
			const existingTimer = leaveTimers.get(card);

			if (existingTimer) {
				window.clearTimeout(existingTimer);
			}

			card.classList.remove("is-hovered");
			card.classList.add("is-leaving");
			leaveTimers.set(card, window.setTimeout(() => {
				card.classList.remove("is-leaving");
				leaveTimers.delete(card);
			}, leaveWindow));
		};

		hitbox.addEventListener("pointerenter", enter);
		hitbox.addEventListener("pointerleave", leave);
		card.addEventListener("focusin", enter);
		card.addEventListener("focusout", (event) => {
			if (!card.contains(event.relatedTarget)) {
				leave();
			}
		});
		card.dataset.projectsStateBound = "true";
	};

	const buildProjectsCard = (card, sprites) => {
		const scene = card.querySelector("[data-projects-card-scene]");

		if (!scene) {
			return;
		}

		const sourceX = getNumberVar(card, "--projects-source-x", 0);
		const sourceY = getNumberVar(card, "--projects-source-y", 1800);
		const spritesByName = new Map(sprites.map((sprite) => [sprite.file.replace(/\.png$/i, ""), sprite]));
		const missingLayers = layerOrderTopToBottom.filter((name) => !spritesByName.has(name));
		const extraLayers = [...spritesByName.keys()].filter((name) => !topIndexByLayer.has(name));

		if (missingLayers.length || extraLayers.length) {
			console.warn("Projects card layer mismatch", { missingLayers, extraLayers });
		}

		const fragment = document.createDocumentFragment();

		layerOrderBottomToTop.forEach((layerName, bottomIndex) => {
			const spriteData = spritesByName.get(layerName);

			if (!spriteData) {
				return;
			}

			const box = spriteData.cropBox;
			const sprite = document.createElement("span");
			const parallax = document.createElement("span");
			const image = document.createElement("img");

			sprite.className = "projects-sprite-card__sprite";
			sprite.dataset.projectsLayer = layerName;
			parallax.className = "projects-sprite-card__parallax";
			parallax.dataset.cardParallaxLayer = layerName;
			parallax.dataset.spriteParallaxStrength = getProjectsParallaxStrength(card, layerName).toFixed(3);
			image.className = "projects-sprite-card__sprite-image";
			image.src = `${assetBase}${spriteData.file}`;
			image.alt = "";
			image.decoding = "async";
			image.loading = "lazy";
			sprite.setAttribute("aria-hidden", "true");
			sprite.style.setProperty("--sprite-left", getPositionTerm(spriteData, layerName, "x", sourceX));
			sprite.style.setProperty("--sprite-top", getPositionTerm(spriteData, layerName, "y", sourceY));
			sprite.style.setProperty("--sprite-width", box.width);
			sprite.style.setProperty("--sprite-height", box.height);
			sprite.style.setProperty("--sprite-z", bottomIndex + 1);

			if (blendModes.has(layerName)) {
				sprite.style.setProperty("--sprite-blend", blendModes.get(layerName));
			}

			setMask(parallax, layerName, spriteData, spritesByName, sourceX, sourceY);
			setSpriteTiming(card, sprite, layerName);
			parallax.append(image);
			sprite.append(parallax);
			fragment.append(sprite);
		});

		scene.replaceChildren(fragment);
		bindProjectsCardState(card);
		window.helloTeacherSpriteParallax?.register(card);
		card.dataset.spriteCardReady = "true";
	};

	fetch(manifestUrl)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Could not load ${manifestUrl}`);
			}

			return response.json();
		})
		.then((manifest) => {
			const projectsSprites = manifest?.folders?.projects?.sprites || [];

			projectsCards.forEach((card) => buildProjectsCard(card, projectsSprites));
		})
		.catch((error) => {
			console.warn("Projects card sprites were not loaded", error);
		});
})();

(() => {
	const artCards = [...document.querySelectorAll("[data-sprite-card='art']")];

	if (!artCards.length) {
		return;
	}

	const layerOrderTopToBottom = [
		"art_sun_overlay",
		"art_sun",
		"art_star5",
		"art_triangle10",
		"art_triangle9",
		"art_triangle8",
		"art_star4",
		"art_colordodge",
		"art_bluewave",
		"art_pencil",
		"art_ipad",
		"art_pinkwave",
		"art_star3",
		"art_star2",
		"art_star1",
		"art_triangle7",
		"art_triangle6",
		"art_triangle5",
		"art_triangle4",
		"art_triangle3",
		"art_triangle2",
		"art_triangle1",
		"art_hull",
		"art_a",
		"art_r",
		"art_t",
		"art_character",
		"art_pic4",
		"art_pic3",
		"art_pic2",
		"art_waves",
		"art_pic",
		"art_moon_overlay",
		"art_moon",
		"art_splotches",
	];
	const layerOrderBottomToTop = [...layerOrderTopToBottom].reverse();
	const topIndexByLayer = new Map(layerOrderTopToBottom.map((name, index) => [name, index]));
	const lockedMotionTargets = new Map([
		["art_sun_overlay", "art_sun"],
		["art_colordodge", "art_bluewave"],
		["art_ipad", "art_bluewave"],
		["art_pencil", "art_bluewave"],
		["art_moon_overlay", "art_moon"],
		["art_splotches", "art_moon"],
	]);
	const lockedParallaxTargets = new Map([
		...lockedMotionTargets,
		["art_a", "art_r"],
		["art_t", "art_r"],
	]);
	const blendModes = new Map([
		["art_sun_overlay", "overlay"],
		["art_moon_overlay", "overlay"],
		["art_colordodge", "color-dodge"],
	]);
	const hiddenAtRest = new Set([
		"art_sun_overlay",
		"art_moon_overlay",
		"art_colordodge",
		"art_splotches",
	]);
	const triangleRestRotations = new Map([
		["art_triangle1", "-11deg"],
		["art_triangle2", "14deg"],
		["art_triangle3", "-8deg"],
		["art_triangle4", "18deg"],
		["art_triangle5", "-15deg"],
		["art_triangle6", "9deg"],
		["art_triangle7", "-12deg"],
	]);
	const restYByTopIndex = [
		"-9px", "6px", "12px", "-5px", "8px", "-11px", "5px", "10px", "-7px",
		"4px", "11px", "-10px", "7px", "-6px", "9px", "-9px", "12px", "-4px",
		"6px", "-8px", "5px", "13px", "-12px", "4px", "8px", "-6px", "10px",
		"-8px", "3px", "12px", "-4px", "7px", "-10px", "5px", "9px",
	];
	const leftHugFloatLayers = new Set([
		"art_star5",
		"art_triangle10",
		"art_triangle9",
		"art_star3",
		"art_triangle3",
	]);
	const floatConfigs = new Map([
		["art_sun_overlay", { kind: "bob", yPeriod: 3100, yPhase: 0, yScale: 1 }],
		["art_sun", { kind: "bob", yPeriod: 3100, yPhase: 0, yScale: 1 }],
		["art_star1", { kind: "star", xPeriod: 2380, yPeriod: 3170, xPhase: 180, yPhase: 930, xScale: 0.82, yScale: 1 }],
		["art_star2", { kind: "star", xPeriod: 2910, yPeriod: 2510, xPhase: 640, yPhase: 130, xScale: 0.72, yScale: 0.78 }],
		["art_star3", { kind: "star", xPeriod: 2640, yPeriod: 3490, xPhase: 1180, yPhase: 410, xScale: 0.96, yScale: 0.66 }],
		["art_star4", { kind: "star", xPeriod: 3370, yPeriod: 2860, xPhase: 300, yPhase: 1520, xScale: 0.68, yScale: 0.94 }],
		["art_star5", { kind: "star", xPeriod: 3740, yPeriod: 3090, xPhase: 1430, yPhase: 780, xScale: 1, yScale: 0.7 }],
		["art_triangle8", { kind: "triangle", xPeriod: 6200, yPeriod: 7600, xPhase: 400, yPhase: 2100, xScale: 1, yScale: 0.68 }],
		["art_triangle9", { kind: "triangle", xPeriod: 7100, yPeriod: 6400, xPhase: 1800, yPhase: 900, xScale: 0.78, yScale: 1 }],
		["art_triangle10", { kind: "triangle", xPeriod: 8400, yPeriod: 6900, xPhase: 2700, yPhase: 3100, xScale: 0.9, yScale: 0.82 }],
		["art_triangle7", { kind: "triangleJitter", xPeriod: 980, yPeriod: 1280, xPhase: 80, yPhase: 410, xScale: 0.82, yScale: 1 }],
		["art_triangle6", { kind: "triangleJitter", xPeriod: 1180, yPeriod: 920, xPhase: 260, yPhase: 110, xScale: 1, yScale: 0.72 }],
		["art_triangle5", { kind: "triangleJitter", xPeriod: 870, yPeriod: 1390, xPhase: 430, yPhase: 720, xScale: 0.7, yScale: 0.94 }],
		["art_triangle4", { kind: "triangleJitter", xPeriod: 1320, yPeriod: 1020, xPhase: 690, yPhase: 250, xScale: 0.92, yScale: 0.76 }],
		["art_triangle3", { kind: "triangleJitter", xPeriod: 1060, yPeriod: 1210, xPhase: 120, yPhase: 840, xScale: 1, yScale: 0.7 }],
		["art_triangle2", { kind: "triangleJitter", xPeriod: 940, yPeriod: 1120, xPhase: 530, yPhase: 190, xScale: 0.78, yScale: 1 }],
		["art_triangle1", { kind: "triangleJitter", xPeriod: 1240, yPeriod: 960, xPhase: 310, yPhase: 580, xScale: 0.86, yScale: 0.82 }],
		["art_a", { kind: "letter", delay: 0 }],
		["art_r", { kind: "letter", delay: 170 }],
		["art_t", { kind: "letter", delay: 340 }],
		["art_moon_overlay", { kind: "bob", yPeriod: 3700, yPhase: 540, yScale: 0.86 }],
		["art_moon", { kind: "bob", yPeriod: 3700, yPhase: 540, yScale: 0.86 }],
	]);
	const manifestUrl = "/assets/images/site/sprite-crop-manifest.json";
	const assetBase = "/assets/images/site/art/";
	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
	const activeFloatCards = new Map();
	let floatFrame = 0;

	const getNumberVar = (element, name, fallback) => {
		const value = getComputedStyle(element).getPropertyValue(name).trim();
		const parsed = Number.parseFloat(value);

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const asPercent = (value) => `${value.toFixed(4)}%`;

	const getArtParallaxStrength = (card, layerName) => {
		const parallaxTarget = lockedParallaxTargets.get(layerName) || layerName;

		const topIndex = topIndexByLayer.get(parallaxTarget) ?? topIndexByLayer.get(layerName) ?? 0;
		const maxIndex = layerOrderTopToBottom.length - 1;
		const minStrength = getNumberVar(card, "--art-card-parallax-min-strength", 0.18);
		const maxStrength = getNumberVar(card, "--art-card-parallax-max-strength", 1);

		return minStrength + (topIndex / maxIndex) * (maxStrength - minStrength);
	};

	const setSpriteTiming = (card, sprite, layerName) => {
		const motionTarget = lockedMotionTargets.get(layerName) || layerName;
		const topIndex = topIndexByLayer.get(motionTarget) ?? topIndexByLayer.get(layerName) ?? 0;
		const staggerMs = getNumberVar(card, "--art-stagger-ms", 14);
		const moveBaseDuration = getNumberVar(card, "--art-move-base-duration", 1100);
		const moveDurationSpread = getNumberVar(card, "--art-move-duration-spread", 420);
		const hiddenFadeDuration = getNumberVar(card, "--art-hidden-fade-duration", 440);
		const regularFadeDuration = getNumberVar(card, "--art-regular-fade-duration", 360);
		const splotchesMoveDuration = getNumberVar(card, "--art-splotches-move-duration", 1300);
		const splotchesFadeRatio = getNumberVar(card, "--art-splotches-fade-ratio", 0.25);
		const inDelay = (layerOrderTopToBottom.length - 1 - topIndex) * staggerMs;
		const outDelay = topIndex * staggerMs;
		const moveDuration = layerName === "art_splotches"
			? splotchesMoveDuration
			: moveBaseDuration + ((topIndex * 29) % moveDurationSpread);
		const fadeDuration = layerName === "art_splotches"
			? Math.round(moveDuration * splotchesFadeRatio)
			: hiddenAtRest.has(layerName)
				? hiddenFadeDuration
				: regularFadeDuration;

		sprite.style.setProperty("--sprite-rest-y", restYByTopIndex[topIndex] || "0px");
		sprite.style.setProperty("--sprite-in-delay", `${inDelay}ms`);
		sprite.style.setProperty("--sprite-out-delay", `${outDelay}ms`);
		sprite.style.setProperty("--sprite-move-duration", `${moveDuration}ms`);
		sprite.style.setProperty("--sprite-fade-duration", `${fadeDuration}ms`);
	};

	const getFloatingSprites = (card) => [...card.querySelectorAll("[data-art-float]")];

	const applyFloatFrame = (card, sprites, time) => {
		const starAmplitude = getNumberVar(card, "--art-star-jitter-amplitude", 5);
		const triangleJitterAmplitude = getNumberVar(card, "--art-triangle-jitter-amplitude", 2.5);
		const triangleAmplitude = getNumberVar(card, "--art-triangle-drift-amplitude", 10);
		const letterAmplitude = getNumberVar(card, "--art-letter-sway-amplitude", 5);
		const letterPeriod = getNumberVar(card, "--art-letter-sway-period", 2600);
		const letterMotionDuration = getNumberVar(card, "--art-letter-sway-motion-duration", 1900);
		const bobAmplitude = getNumberVar(card, "--art-sun-moon-bob-amplitude", 5);

		sprites.forEach((sprite) => {
			const layerName = sprite.dataset.artLayer;
			const config = floatConfigs.get(layerName);
			const image = sprite.querySelector(".art-sprite-card__sprite-image");
			let x = 0;
			let y = 0;

			if (!config || !image) {
				return;
			}

			if (config.kind === "letter") {
				const cycleTime = time % letterPeriod;
				const activeTime = cycleTime - config.delay;
				const duration = Math.min(letterMotionDuration, letterPeriod - config.delay);

				if (activeTime >= 0 && activeTime <= duration) {
					const progress = activeTime / duration;

					x = ((1 - Math.cos(progress * Math.PI * 2)) / 2) * letterAmplitude;
				}
			} else if (config.kind === "bob") {
				y = Math.sin(((time + config.yPhase) / config.yPeriod) * Math.PI * 2) * bobAmplitude * (config.yScale || 1);
			} else {
				const amplitude = config.kind === "triangle"
					? triangleAmplitude
					: config.kind === "triangleJitter"
						? triangleJitterAmplitude
						: starAmplitude;
				const xWave = Math.sin(((time + config.xPhase) / config.xPeriod) * Math.PI * 2);

				x = xWave * amplitude * (config.xScale || 1);
				y = Math.sin(((time + config.yPhase) / config.yPeriod) * Math.PI * 2) * amplitude * (config.yScale || 1);

				if (leftHugFloatLayers.has(layerName)) {
					x = -((xWave + 1) / 2) * amplitude * (config.xScale || 1);
				}
			}

			image.style.setProperty("--sprite-float-x", `${x.toFixed(2)}px`);
			image.style.setProperty("--sprite-float-y", `${y.toFixed(2)}px`);
		});
	};

	const isArtCardActive = (card) => card.classList.contains("is-hovered") || card.matches(":focus-within");

	const runFloatLoop = (time) => {
		activeFloatCards.forEach((state, card) => {
			if (isArtCardActive(card)) {
				applyFloatFrame(card, state.sprites, time - state.startTime);
				return;
			}

			state.sprites.forEach((sprite) => {
				const image = sprite.querySelector(".art-sprite-card__sprite-image");

				if (image) {
					image.style.removeProperty("--sprite-float-x");
					image.style.removeProperty("--sprite-float-y");
				}
			});
			activeFloatCards.delete(card);
		});

		floatFrame = activeFloatCards.size ? window.requestAnimationFrame(runFloatLoop) : 0;
	};

	const startFloatLoop = () => {
		if (!floatFrame) {
			floatFrame = window.requestAnimationFrame(runFloatLoop);
		}
	};

	const setFloatActive = (card, active) => {
		const sprites = getFloatingSprites(card);

		if (!sprites.length || reduceMotion.matches) {
			return;
		}

		if (active) {
			if (!activeFloatCards.has(card)) {
				activeFloatCards.set(card, {
					sprites,
					startTime: performance.now(),
				});
			}
			startFloatLoop();
			return;
		}

		sprites.forEach((sprite) => {
			const image = sprite.querySelector(".art-sprite-card__sprite-image");

			if (image) {
				image.style.removeProperty("--sprite-float-x");
				image.style.removeProperty("--sprite-float-y");
			}
		});
		activeFloatCards.delete(card);
	};

	const syncFloatActiveState = (card) => {
		setFloatActive(card, isArtCardActive(card));
	};

	const setupFloatingMotion = (card) => {
		if (card.dataset.artFloatingReady === "true") {
			return;
		}

		const hitbox = card.querySelector("[data-card-hitbox]") || card;
		const enter = () => {
			card.classList.add("is-hovered");
			window.requestAnimationFrame(() => syncFloatActiveState(card));
		};
		const leave = () => {
			if (card.matches(":focus-within")) {
				return;
			}

			card.classList.remove("is-hovered");
			window.requestAnimationFrame(() => syncFloatActiveState(card));
		};

		card.dataset.artFloatingReady = "true";
		hitbox.addEventListener("pointerenter", enter);
		hitbox.addEventListener("pointerleave", leave);
		card.addEventListener("focusin", enter);
		card.addEventListener("focusout", (event) => {
			if (!card.contains(event.relatedTarget)) {
				leave();
			}
		});
	};

	const buildArtCard = (card, sprites) => {
		const scene = card.querySelector("[data-art-card-scene]");

		if (!scene) {
			return;
		}

		const sourceWidth = getNumberVar(card, "--art-source-width", 2560);
		const sourceHeight = getNumberVar(card, "--art-source-height", 1800);
		const sourceX = getNumberVar(card, "--art-source-x", 0);
		const sourceY = getNumberVar(card, "--art-source-y", 2200);
		const spritesByName = new Map(sprites.map((sprite) => [sprite.file.replace(/\.png$/i, ""), sprite]));
		const missingLayers = layerOrderTopToBottom.filter((name) => !spritesByName.has(name));
		const extraLayers = [...spritesByName.keys()].filter((name) => !topIndexByLayer.has(name));

		if (missingLayers.length || extraLayers.length) {
			console.warn("Art card layer mismatch", { missingLayers, extraLayers });
		}

		const fragment = document.createDocumentFragment();

		layerOrderBottomToTop.forEach((layerName, bottomIndex) => {
			const spriteData = spritesByName.get(layerName);

			if (!spriteData) {
				return;
			}

			const box = spriteData.cropBox;
			const sprite = document.createElement("span");
			const parallax = document.createElement("span");
			const image = document.createElement("img");

			sprite.className = "art-sprite-card__sprite";
			sprite.dataset.artLayer = layerName;
			parallax.className = "art-sprite-card__parallax";
			parallax.dataset.cardParallaxLayer = layerName;
			parallax.dataset.spriteParallaxStrength = getArtParallaxStrength(card, layerName).toFixed(3);
			image.className = "art-sprite-card__sprite-image";
			image.src = `${assetBase}${spriteData.file}`;
			image.alt = "";
			image.decoding = "async";
			image.loading = "lazy";
			sprite.setAttribute("aria-hidden", "true");
			sprite.style.setProperty("--sprite-left", asPercent(((box.left - sourceX) / sourceWidth) * 100));
			sprite.style.setProperty("--sprite-top", asPercent(((box.top - sourceY) / sourceHeight) * 100));
			sprite.style.setProperty("--sprite-width", asPercent((box.width / sourceWidth) * 100));
			sprite.style.setProperty("--sprite-z", bottomIndex + 1);
			sprite.style.setProperty("--sprite-rest-rotate", triangleRestRotations.get(layerName) || "0deg");
			sprite.style.setProperty("--sprite-rest-scale", layerName === "art_splotches" ? "0.05" : "1");

			if (hiddenAtRest.has(layerName)) {
				sprite.style.setProperty("--sprite-rest-opacity", "0");
				sprite.style.setProperty("--sprite-hover-opacity", "1");
			}

			if (blendModes.has(layerName)) {
				sprite.style.setProperty("--sprite-blend", blendModes.get(layerName));
			}

			if (floatConfigs.has(layerName)) {
				sprite.dataset.artFloat = floatConfigs.get(layerName).kind;
			}

			setSpriteTiming(card, sprite, layerName);
			parallax.append(image);
			sprite.append(parallax);
			fragment.append(sprite);
		});

		scene.replaceChildren(fragment);
		card.dataset.spriteCardReady = "true";
		setupFloatingMotion(card);
		window.helloTeacherSpriteParallax?.register(card);
	};

	fetch(manifestUrl)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Could not load ${manifestUrl}`);
			}

			return response.json();
		})
		.then((manifest) => {
			const artSprites = manifest?.folders?.art?.sprites || [];

			artCards.forEach((card) => buildArtCard(card, artSprites));
		})
		.catch((error) => {
			console.warn("Art card sprites were not loaded", error);
		});

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			activeFloatCards.forEach((state) => {
				state.sprites.forEach((sprite) => {
					const image = sprite.querySelector(".art-sprite-card__sprite-image");

					if (image) {
						image.style.removeProperty("--sprite-float-x");
						image.style.removeProperty("--sprite-float-y");
					}
				});
			});
			activeFloatCards.clear();
		});
	}
})();
