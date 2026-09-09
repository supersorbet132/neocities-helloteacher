(() => {
	const display = document.querySelector("[data-cad-display]");

	if (!display) {
		return;
	}

	const scene = display.querySelector("[data-cad-display-scene]");
	const modelPreview = display.querySelector("[data-cad-model-preview]");
	const modelPreviewImage = display.querySelector("[data-cad-model-preview-image]");
	const expandedWindow = document.querySelector("[data-cad-display-window]");
	const featuredModelViewer = expandedWindow?.querySelector("[data-cad-model-viewer]");
	const viewerTitle = expandedWindow?.querySelector("[data-cad-viewer-title]");
	const viewerKicker = expandedWindow?.querySelector("[data-cad-viewer-kicker]");
	const viewerStatus = expandedWindow?.querySelector("[data-cad-viewer-status]");
	const viewerCopy = expandedWindow?.querySelector("[data-cad-viewer-copy]");
	const viewerCloseButtons = expandedWindow?.querySelectorAll("[data-cad-display-window-close]") || [];
	const featuredModelTitle = featuredModelViewer?.dataset.cadModelTitle || "Phone Holder Assembly";
	const featuredViewerCopy = viewerCopy?.textContent || "";
	const touchHoverQuery = window.matchMedia("(hover: none) and (pointer: coarse)");

	if (!scene) {
		return;
	}

	if (modelPreviewImage?.dataset.cadModelPreviewFallback) {
		modelPreviewImage.addEventListener("error", () => {
			if (modelPreviewImage.dataset.cadModelPreviewFallbackApplied === "true") {
				return;
			}

			modelPreviewImage.dataset.cadModelPreviewFallbackApplied = "true";
			modelPreviewImage.src = modelPreviewImage.dataset.cadModelPreviewFallback;
		});
	}

	const baseLayerOrderBottomToTop = [
		"cad_display_beam",
		"cad_display_colordodge",
		"cad_display_rails",
	];
	const manifestUrls = [
		"/assets/images/cad/sprites/sprite-crop-manifest-2026-09-03-new-batch.json?v=20260904-layout2",
		"/assets/images/cad/sprites/sprite-crop-manifest.json?v=20260904-layout2",
	];
	const assetBase = "/assets/images/cad/sprites/";
	const imageExtensionRe = /\.[^.]+$/;
	const sideLayerRe = /^cad_display_(left|right)(\d+)$/;
	const hoverTimers = new WeakMap();
	let lockedScrollY = 0;
	let lastFocusWasPointer = false;
	let touchHoverFrame = 0;
	let activeViewerDetail = {
		action: "featured",
		hasModel: true,
		model: featuredModelTitle,
	};

	const getNumberVar = (element, name, fallback) => {
		const value = getComputedStyle(element).getPropertyValue(name).trim();
		const parsed = Number.parseFloat(value);

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const asPercent = (value) => `${value.toFixed(4)}%`;
	const toLayerName = (fileName) => fileName.replace(imageExtensionRe, "");
	const toAssetFile = (fileName) => `${toLayerName(fileName)}.webp`;
	const cssUrl = (fileName) => `url("${assetBase}${toAssetFile(fileName)}")`;
	const toLayerSlug = (layerName) => layerName.replace(/^cad_display_/, "cad-display-").replaceAll("_", "-");

	const getLayerOrder = (spritesByName) => {
		const sideLayers = [...spritesByName.keys()]
			.map((layerName) => {
				const match = layerName.match(sideLayerRe);

				if (!match) {
					return null;
				}

				return {
					layerName,
					side: match[1],
					layerNumber: Number.parseInt(match[2], 10),
				};
			})
			.filter(Boolean)
			.sort((a, b) => a.layerNumber - b.layerNumber || a.side.localeCompare(b.side));
		const legacySideLayers = ["cad_display_left", "cad_display_right"].filter((layerName) => spritesByName.has(layerName));

		return [
			...baseLayerOrderBottomToTop,
			...(sideLayers.length ? sideLayers.map((layer) => layer.layerName) : legacySideLayers),
		];
	};

	const setMask = (layer, layerName, spriteBox, spritesByName) => {
		if (layerName !== "cad_display_colordodge") {
			return;
		}

		const maskSprite = spritesByName.get("cad_display_beam");

		if (!maskSprite) {
			return;
		}

		const maskBox = maskSprite.cropBox;

		layer.classList.add("is-masked");
		layer.style.setProperty("--cad-display-mask-image", cssUrl(maskSprite.file));
		layer.style.setProperty("--cad-display-mask-position", `calc(${maskBox.left - spriteBox.left} * var(--cad-display-unit)) calc(${maskBox.top - spriteBox.top} * var(--cad-display-unit))`);
		layer.style.setProperty("--cad-display-mask-size", `calc(${maskBox.width} * var(--cad-display-unit)) calc(${maskBox.height} * var(--cad-display-unit))`);
	};

	const buildDisplay = (sprites) => {
		const sourceWidth = getNumberVar(display, "--cad-display-source-width", 2560);
		const sourceX = getNumberVar(display, "--cad-display-source-x", 0);
		const sourceY = getNumberVar(display, "--cad-display-source-y", 573);
		const sourceHeight = getNumberVar(display, "--cad-display-source-height", 1259);
		const spritesByName = new Map(sprites.map((sprite) => [toLayerName(sprite.file), sprite]));
		const layerOrderBottomToTop = getLayerOrder(spritesByName);
		const missingLayers = baseLayerOrderBottomToTop.filter((layerName) => !spritesByName.has(layerName));

		if (missingLayers.length) {
			console.warn("CAD display layer mismatch", { missingLayers });
		}

		const fragment = document.createDocumentFragment();
		let modelPreviewAdded = false;

		layerOrderBottomToTop.forEach((layerName, index) => {
			const spriteData = spritesByName.get(layerName);

			if (!spriteData) {
				return;
			}

			const box = spriteData.cropBox;
			const layerSlug = toLayerSlug(layerName);
			const isSideLayer = sideLayerRe.test(layerName);
			const layer = document.createElement("span");
			const image = document.createElement("img");

			layer.className = `cad-display__layer cad-display__layer--${layerName}`;
			layer.dataset.cadDisplayLayer = layerName;
			layer.style.setProperty("--cad-layer-left", asPercent(((box.left - sourceX) / sourceWidth) * 100));
			layer.style.setProperty("--cad-layer-top", asPercent(((box.top - sourceY) / sourceHeight) * 100));
			layer.style.setProperty("--cad-layer-width", asPercent((box.width / sourceWidth) * 100));
			layer.style.setProperty("--cad-layer-height", asPercent((box.height / sourceHeight) * 100));
			layer.style.setProperty("--cad-layer-z", index + 1);
			layer.style.setProperty("--cad-layer-nudge-x", isSideLayer ? `var(--${layerSlug}-x, 0px)` : "0px");
			layer.style.setProperty("--cad-layer-nudge-y", isSideLayer ? `var(--${layerSlug}-y, 0px)` : "0px");
			layer.setAttribute("aria-hidden", "true");

			image.className = "cad-display__image";
			image.src = `${assetBase}${toAssetFile(spriteData.file)}`;
			image.alt = "";
			image.width = box.width;
			image.height = box.height;
			image.decoding = "async";
			image.draggable = false;

			setMask(layer, layerName, box, spritesByName);
			layer.append(image);
			fragment.append(layer);

			if (layerName === "cad_display_colordodge" && modelPreview) {
				fragment.append(modelPreview);
				modelPreviewAdded = true;
			}
		});

		if (modelPreview && !modelPreviewAdded) {
			fragment.append(modelPreview);
		}

		scene.replaceChildren(fragment);
		display.dataset.cadDisplayReady = "true";
	};

	const setHover = (active) => {
		const timer = hoverTimers.get(display);

		if (timer) {
			window.clearTimeout(timer);
			hoverTimers.delete(display);
		}

		if (active) {
			display.classList.remove("is-leaving");
			display.classList.add("is-hovered");
			return;
		}

		if (!display.classList.contains("is-hovered")) {
			return;
		}

		display.classList.remove("is-hovered");
		display.classList.add("is-leaving");
		hoverTimers.set(display, window.setTimeout(() => {
			display.classList.remove("is-leaving");
			hoverTimers.delete(display);
		}, getNumberVar(display, "--cad-display-leave-animation-window", 960)));
	};

	const isWindowOpen = () => expandedWindow?.classList.contains("is-window-open") || false;

	const isDisplayInTouchBand = () => {
		const viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

		if (viewportHeight <= 0 || isWindowOpen()) {
			return false;
		}

		const rect = display.getBoundingClientRect();
		const displayCenter = rect.top + (rect.height * 0.5);
		const bandTop = viewportHeight / 6;
		const bandBottom = viewportHeight * (5 / 6);

		return rect.bottom > 0
			&& rect.top < viewportHeight
			&& displayCenter >= bandTop
			&& displayCenter <= bandBottom;
	};

	const updateTouchHover = () => {
		touchHoverFrame = 0;

		if (!touchHoverQuery.matches) {
			return;
		}

		setHover(isDisplayInTouchBand());
	};

	const requestTouchHoverUpdate = () => {
		if (!touchHoverFrame) {
			touchHoverFrame = window.requestAnimationFrame(updateTouchHover);
		}
	};

	const handleTouchHoverModeChange = () => {
		if (touchHoverQuery.matches) {
			requestTouchHoverUpdate();
			return;
		}

		setHover(false);
	};

	const setViewerContent = (detail = {}) => {
		const action = detail.action || "featured";

		activeViewerDetail = {
			action,
			copy: typeof detail.copy === "string" ? detail.copy : action === "featured" ? featuredViewerCopy : "",
			hasModel: detail.hasModel === true || action === "featured" || !detail.action,
			model: detail.model || featuredModelTitle,
		};

		const modelName = activeViewerDetail.model;
		const modelLabel = modelName.replace(/\s+/g, " ").trim();
		const viewerMode = "Model Viewer";

		if (viewerTitle) {
			viewerTitle.textContent = modelLabel;
		}

		if (viewerKicker) {
			viewerKicker.textContent = action === "featured"
				? "Active File / Featured"
				: `Active File / ${viewerMode}`;
		}

		if (viewerStatus) {
			viewerStatus.textContent = action === "featured"
				? "Viewer Standby"
				: `${viewerMode} Standby`;
		}

		if (viewerCopy) {
			viewerCopy.textContent = activeViewerDetail.copy;
		}
	};

	const setWindowOpen = (open) => {
		if (!expandedWindow) {
			return;
		}

		const wasOpen = expandedWindow.classList.contains("is-window-open");

		if (open) {
			lockedScrollY = window.scrollY || window.pageYOffset || 0;
			document.body.style.setProperty("--cad-scroll-lock-y", `${lockedScrollY}px`);
		}

		display.classList.toggle("is-clamped", open);
		display.setAttribute("aria-expanded", String(open));
		display.setAttribute("aria-pressed", String(open));
		expandedWindow.classList.toggle("is-window-open", open);
		expandedWindow.setAttribute("aria-hidden", String(!open));
		document.documentElement.classList.toggle("is-cad-viewer-open", open);
		document.body.classList.toggle("is-cad-viewer-open", open);

		if (wasOpen !== open) {
			document.dispatchEvent(new CustomEvent(open ? "cad:viewer-opened" : "cad:viewer-closed", {
				detail: activeViewerDetail,
			}));
		}

		if (!open) {
			document.body.style.removeProperty("--cad-scroll-lock-y");
			window.scrollTo(0, lockedScrollY);
		}
	};

	display.addEventListener("pointerdown", () => {
		lastFocusWasPointer = true;
	});
	display.addEventListener("keydown", () => {
		lastFocusWasPointer = false;
	});
	display.addEventListener("pointerenter", () => {
		if (!touchHoverQuery.matches) {
			setHover(true);
		}
	});
	display.addEventListener("pointerleave", () => {
		if (!touchHoverQuery.matches) {
			setHover(false);
		}
	});
	display.addEventListener("focus", () => {
		if (!lastFocusWasPointer || display.matches(":focus-visible")) {
			setHover(true);
		}
	});
	display.addEventListener("blur", () => {
		lastFocusWasPointer = false;
		setHover(false);
	});
	display.addEventListener("click", () => {
		setViewerContent({
			action: "featured",
			model: "Phone Holder Assembly",
		});
		setWindowOpen(true);
	});
	document.addEventListener("cad:open-viewer", (event) => {
		setViewerContent({
			...(event.detail || {}),
			hasModel: false,
		});
		setWindowOpen(true);
	});
	viewerCloseButtons.forEach((button) => {
		button.addEventListener("click", () => setWindowOpen(false));
	});
	expandedWindow?.addEventListener("click", (event) => {
		if (event.target.closest("[data-cad-display-window-content]")) {
			return;
		}

		event.preventDefault();
		event.stopPropagation();
		setWindowOpen(false);
	});
	document.addEventListener("keydown", (event) => {
		if (event.key === "Escape" && isWindowOpen()) {
			setWindowOpen(false);
			display.focus();
		}
	});
	document.addEventListener("cad:viewer-closed", () => {
		window.setTimeout(requestTouchHoverUpdate, 0);
	});
	window.addEventListener("scroll", requestTouchHoverUpdate, { passive: true });
	window.addEventListener("resize", requestTouchHoverUpdate);
	window.addEventListener("orientationchange", requestTouchHoverUpdate);

	if (typeof touchHoverQuery.addEventListener === "function") {
		touchHoverQuery.addEventListener("change", handleTouchHoverModeChange);
	} else {
		touchHoverQuery.addListener(handleTouchHoverModeChange);
	}

	const loadManifest = () => manifestUrls.reduce((promise, manifestUrl) => promise.catch(() => fetch(manifestUrl)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Could not load ${manifestUrl}`);
			}

			return response.json();
		})), Promise.reject())
		.catch((error) => {
			throw new Error(`Could not load a CAD display manifest: ${error.message}`);
		});

	loadManifest()
		.then((manifest) => {
			buildDisplay(manifest?.sprites || []);
			requestTouchHoverUpdate();
		})
		.catch((error) => {
			console.warn("CAD display sprites were not loaded", error);
		});

	requestTouchHoverUpdate();
})();
