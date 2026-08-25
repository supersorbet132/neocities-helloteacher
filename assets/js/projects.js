(() => {
	const stack = document.querySelector("[data-project-rail]");
	const tabs = [...document.querySelectorAll("[data-project-tab]")];
	const panels = [...document.querySelectorAll("[data-project-panel]")];
	const reader = document.querySelector("[data-project-reader]");
	const readerHeader = document.querySelector("[data-project-reader-header]");
	const readerTitle = document.querySelector("[data-project-reader-title]");
	const readerPanels = [...document.querySelectorAll("[data-project-reader-panel]")];
	const readerSwitches = [...document.querySelectorAll("[data-project-reader-switch]")];
	const closeButtons = [...document.querySelectorAll("[data-project-close]")];
	const pokerGameFrame = document.querySelector("[data-project-game-frame]");
	const projectsHero = document.querySelector(".projects-hero");
	const projectsTitleCard = document.querySelector(".projects-title-card[data-sprite-card='projects']");

	if (!stack || !tabs.length) {
		return;
	}

	const visiblePanels = new Map();
	const tabHoverReadyClass = "is-project-tabs-hover-ready";
	const scrollHeldHoverClass = "is-scroll-held-hover";
	const comicCloudDriftClass = "is-comic-cloud-drifting";
	const comicParallaxActiveClass = "is-comic-parallax-active";
	const pokerParallaxActiveClass = "is-poker-parallax-active";
	const readerOriginHiddenClass = "is-project-reader-origin-hidden";
	const scrollIdleHoverDelay = 220;
	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
	const tabParallaxCache = new WeakMap();
	let lastTrigger = null;
	let hoverReadyTimer = 0;
	let tabParallaxFrame = 0;
	let pendingParallaxTab = null;
	let scrollHeldHoverTab = null;
	let pointerClientX = 0;
	let pointerClientY = 0;
	let hasPointerPosition = false;
	let titleAnimationNearViewport = true;
	let readerTransitionToken = 0;
	let activeReaderFlyer = null;

	const isReaderOpen = () => Boolean(reader && !reader.hidden);

	const setTabHoverReady = (ready) => {
		document.body.classList.toggle(tabHoverReadyClass, ready && !isReaderOpen());
	};

	const isComicTab = (tab) => tab?.classList.contains("project-bar--comic");
	const isPokerTab = (tab) => tab?.classList.contains("project-bar--poker");
	const getProjectTab = (id) => tabs.find((tab) => tab.dataset.projectTab === id);

	const getComicCloudLayers = (tab) => [...(tab?.querySelectorAll(".project-comic-tab__layer--cloud") || [])];

	const getNumberVar = (element, name, fallback) => {
		const parsed = Number.parseFloat(getComputedStyle(element).getPropertyValue(name));

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const getTabParallaxConfig = (tab) => {
		if (isComicTab(tab)) {
			return {
				activeClass: comicParallaxActiveClass,
				artSelector: ".project-comic-tab",
				defaultRangeX: 16,
				defaultRangeY: 9,
				depthVar: "--comic-parallax-depth",
				layerSelector: ".project-comic-tab__layer",
				rangeXVar: "--comic-parallax-range-x",
				rangeYVar: "--comic-parallax-range-y",
				xVar: "--comic-parallax-x",
				yVar: "--comic-parallax-y",
			};
		}

		if (isPokerTab(tab)) {
			return {
				activeClass: pokerParallaxActiveClass,
				artSelector: ".project-poker-tab",
				defaultRangeX: 16,
				defaultRangeY: 9,
				depthVar: "--poker-parallax-depth",
				layerSelector: ".project-poker-tab__stage, .project-poker-tab__layer--title-cards, .project-poker-tab__layer[class*='project-poker-tab__layer--bg-'], .project-poker-tab__layer--title-word, .project-poker-tab__layer--letter",
				rangeXVar: "--poker-parallax-range-x",
				rangeYVar: "--poker-parallax-range-y",
				xVar: "--poker-parallax-x",
				yVar: "--poker-parallax-y",
			};
		}

		return null;
	};

	const getTabParallaxData = (tab) => {
		const config = getTabParallaxConfig(tab);

		if (!config) {
			return null;
		}

		const cached = tabParallaxCache.get(tab);

		if (cached) {
			return cached;
		}

		const art = tab.querySelector(config.artSelector);

		if (!art) {
			return null;
		}

		const layers = [...tab.querySelectorAll(config.layerSelector)].map((layer) => ({
			layer,
			depth: getNumberVar(layer, config.depthVar, 0),
		}));
		const data = { art, config, layers };
		tabParallaxCache.set(tab, data);

		return data;
	};

	const startComicCloudDrift = (tab) => {
		if (!isComicTab(tab) || tab.classList.contains(comicCloudDriftClass)) {
			return;
		}

		getComicCloudLayers(tab).forEach((cloud) => {
			cloud.style.transform = "";
		});
		tab.classList.add(comicCloudDriftClass);
	};

	const stopComicCloudDrift = (tab) => {
		if (!isComicTab(tab) || !tab.classList.contains(comicCloudDriftClass)) {
			return;
		}

		const clouds = getComicCloudLayers(tab);

		clouds.forEach((cloud) => {
			const transform = getComputedStyle(cloud).transform;
			cloud.style.transform = transform && transform !== "none" ? transform : "translate3d(0, 0, 0)";
		});

		tab.classList.remove(comicCloudDriftClass);

		window.requestAnimationFrame(() => {
			clouds.forEach((cloud) => {
				cloud.style.transform = "";
			});
		});
	};

	const shouldRunTabParallax = (tab) => {
		if (!getTabParallaxConfig(tab) || isReaderOpen() || reduceMotion.matches) {
			return false;
		}

		return tab.classList.contains(scrollHeldHoverClass)
			|| (document.body.classList.contains(tabHoverReadyClass) && tab.matches(":hover"));
	};

	const stopTabParallax = (tab) => {
		const data = getTabParallaxData(tab);

		if (!data) {
			return;
		}

		tab.classList.remove(data.config.activeClass);
		data.layers.forEach(({ layer }) => {
			layer.style.setProperty(data.config.xVar, "0px");
			layer.style.setProperty(data.config.yVar, "0px");
		});
	};

	const updateTabParallax = (tab) => {
		if (!hasPointerPosition || !shouldRunTabParallax(tab)) {
			stopTabParallax(tab);
			return;
		}

		const data = getTabParallaxData(tab);

		if (!data) {
			return;
		}

		const rect = tab.getBoundingClientRect();

		if (rect.width <= 0 || rect.height <= 0) {
			return;
		}

		const progressX = Math.max(Math.min(((pointerClientX - rect.left) / rect.width - 0.5) * 2, 1), -1);
		const progressY = Math.max(Math.min(((pointerClientY - rect.top) / rect.height - 0.5) * 2, 1), -1);
		const maxX = getNumberVar(data.art, data.config.rangeXVar, data.config.defaultRangeX);
		const maxY = getNumberVar(data.art, data.config.rangeYVar, data.config.defaultRangeY);

		tab.classList.add(data.config.activeClass);
		data.layers.forEach(({ layer, depth }) => {
			layer.style.setProperty(data.config.xVar, `${(progressX * maxX * depth).toFixed(2)}px`);
			layer.style.setProperty(data.config.yVar, `${(progressY * maxY * depth).toFixed(2)}px`);
		});
	};

	const requestTabParallax = (tab) => {
		pendingParallaxTab = tab;

		if (tabParallaxFrame) {
			return;
		}

		tabParallaxFrame = window.requestAnimationFrame(() => {
			const tabToUpdate = pendingParallaxTab;
			tabParallaxFrame = 0;
			pendingParallaxTab = null;
			updateTabParallax(tabToUpdate);
		});
	};

	const getTabUnderPointer = () => {
		if (!hasPointerPosition) {
			return null;
		}

		return document.elementFromPoint(pointerClientX, pointerClientY)?.closest("[data-project-tab]");
	};

	const setScrollHeldHover = (tab) => {
		if (!tab || scrollHeldHoverTab === tab) {
			return;
		}

		if (scrollHeldHoverTab) {
			const previousTab = scrollHeldHoverTab;
			previousTab.classList.remove(scrollHeldHoverClass);
			stopComicCloudDrift(previousTab);
			stopTabParallax(previousTab);
		}

		scrollHeldHoverTab = tab;
		scrollHeldHoverTab.classList.add(scrollHeldHoverClass);
		startComicCloudDrift(scrollHeldHoverTab);
		requestTabParallax(scrollHeldHoverTab);
	};

	const clearScrollHeldHover = () => {
		if (!scrollHeldHoverTab) {
			return;
		}

		const heldTab = scrollHeldHoverTab;
		heldTab.classList.remove(scrollHeldHoverClass);
		scrollHeldHoverTab = null;
		stopComicCloudDrift(heldTab);
		stopTabParallax(heldTab);
	};

	const releaseScrollHeldHover = () => {
		if (!scrollHeldHoverTab) {
			return;
		}

		const heldTab = scrollHeldHoverTab;
		const tabUnderPointer = getTabUnderPointer();
		const shouldContinueHover = tabUnderPointer === heldTab && !isReaderOpen();

		heldTab.classList.remove(scrollHeldHoverClass);
		scrollHeldHoverTab = null;

		if (shouldContinueHover) {
			startComicCloudDrift(heldTab);
			requestTabParallax(heldTab);
			return;
		}

		stopComicCloudDrift(heldTab);
		stopTabParallax(heldTab);
	};

	const resumeTabHover = () => {
		setTabHoverReady(true);
		releaseScrollHeldHover();
	};

	const updatePointerPosition = (event) => {
		pointerClientX = event.clientX;
		pointerClientY = event.clientY;
		hasPointerPosition = true;

		const tab = event.target.closest?.("[data-project-tab]") || getTabUnderPointer();

		if (!scrollHeldHoverTab && tab && document.body.classList.contains(tabHoverReadyClass) && !isReaderOpen()) {
			startComicCloudDrift(tab);
		}

		if (tab) {
			requestTabParallax(tab);
		}
	};

	const suspendTabHover = () => {
		if (!scrollHeldHoverTab && document.body.classList.contains(tabHoverReadyClass) && !isReaderOpen()) {
			setScrollHeldHover(tabs.find((tab) => tab.matches(":hover")));
		}

		setTabHoverReady(false);
		window.clearTimeout(hoverReadyTimer);
		hoverReadyTimer = window.setTimeout(resumeTabHover, scrollIdleHoverDelay);
	};

	const setTitleAnimationActive = (active) => {
		if (!projectsTitleCard) {
			return;
		}

		const shouldRun = active && !document.hidden;
		projectsTitleCard.classList.toggle("is-title-animation-paused", !shouldRun);
		projectsTitleCard.dataset.spriteParallaxPaused = shouldRun ? "false" : "true";

		if (shouldRun) {
			window.helloTeacherSpriteParallax?.refresh?.();
		}
	};

	const updateTitleAnimationByScroll = () => {
		if (!projectsHero || !projectsTitleCard) {
			return;
		}

		const viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
		const buffer = viewportHeight * 0.75;
		const rect = projectsHero.getBoundingClientRect();
		titleAnimationNearViewport = rect.bottom >= -buffer && rect.top <= viewportHeight + buffer;
		setTitleAnimationActive(titleAnimationNearViewport);
	};

	const initTitleAnimationPause = () => {
		if (!projectsHero || !projectsTitleCard) {
			return;
		}

		if ("IntersectionObserver" in window) {
			const observer = new IntersectionObserver((entries) => {
				titleAnimationNearViewport = entries.some((entry) => entry.isIntersecting);
				setTitleAnimationActive(titleAnimationNearViewport);
			}, {
				root: null,
				rootMargin: "75% 0px 75% 0px",
				threshold: 0,
			});

			observer.observe(projectsHero);
			updateTitleAnimationByScroll();
		} else {
			window.addEventListener("scroll", updateTitleAnimationByScroll, { passive: true });
			window.addEventListener("resize", updateTitleAnimationByScroll);
			updateTitleAnimationByScroll();
		}

		document.addEventListener("visibilitychange", () => {
			setTitleAnimationActive(titleAnimationNearViewport);
		});
	};

	const createGamePlaceholder = () => {
		const placeholder = document.createElement("div");
		placeholder.className = "project-reader__game-placeholder";
		placeholder.textContent = pokerGameFrame?.dataset.projectGamePlaceholder || "Game build sleeps while this project is closed.";
		return placeholder;
	};

	const mountPokerGame = () => {
		if (!pokerGameFrame || pokerGameFrame.querySelector("iframe")) {
			return;
		}

		const iframe = document.createElement("iframe");
		iframe.className = "project-reader__game-embed";
		iframe.src = pokerGameFrame.dataset.projectGameSrc || "/games/poker/";
		iframe.title = pokerGameFrame.dataset.projectGameTitle || "Playable Poker browser build";
		iframe.loading = "eager";
		iframe.allow = "fullscreen";
		iframe.setAttribute("data-project-game-embed", "");
		pokerGameFrame.replaceChildren(iframe);
	};

	const unmountPokerGame = () => {
		const iframe = pokerGameFrame?.querySelector("iframe");

		if (!pokerGameFrame || !iframe) {
			return;
		}

		iframe.src = "about:blank";
		pokerGameFrame.replaceChildren(createGamePlaceholder());
	};

	const syncProjectRuntime = (id) => {
		if (id === "poker" && isReaderOpen() && !document.hidden) {
			mountPokerGame();
			return;
		}

		unmountPokerGame();
	};

	const getActiveProjectId = () => readerPanels.find((panel) => panel.classList.contains("is-active"))?.dataset.projectReaderPanel
		|| tabs.find((tab) => tab.classList.contains("is-active"))?.dataset.projectTab
		|| tabs[0]?.dataset.projectTab;

	const getFocusableReaderItems = () => {
		if (!reader || reader.hidden) {
			return [];
		}

		return [...reader.querySelectorAll("button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])")]
			.filter((item) => !item.disabled && item.offsetParent !== null);
	};

	const projectBarClasses = (tab) => [...tab.classList].filter((className) => (
		className === "project-bar" || className.startsWith("project-bar--")
	));

	const createReaderThumbnail = (tab, className, expanded = true) => {
		const thumbnail = document.createElement("div");
		thumbnail.className = [...projectBarClasses(tab), className].join(" ");
		thumbnail.setAttribute("aria-hidden", "true");
		thumbnail.innerHTML = tab.innerHTML;

		if (expanded) {
			thumbnail.classList.add(scrollHeldHoverClass);
		}

		return thumbnail;
	};

	const setReaderHeader = (id) => {
		if (!readerHeader) {
			return;
		}

		const tab = getProjectTab(id);

		if (!tab) {
			readerHeader.replaceChildren();
			return;
		}

		readerHeader.replaceChildren(createReaderThumbnail(tab, "project-reader__thumbnail-art", true));
	};

	const readerTransitionMs = () => {
		if (reduceMotion.matches) {
			return 0;
		}

		const raw = getComputedStyle(document.body).getPropertyValue("--project-reader-transition-duration").trim();
		const match = raw.match(/^([\d.]+)(ms|s)$/);

		if (!match) {
			return 680;
		}

		const value = Number.parseFloat(match[1]);
		return match[2] === "s" ? value * 1000 : value;
	};

	const setFlyerRect = (flyer, rect) => {
		flyer.style.width = `${Math.max(1, rect.width)}px`;
		flyer.style.height = `${Math.max(1, rect.height)}px`;
		flyer.style.transform = `translate3d(${rect.left}px, ${rect.top}px, 0)`;
	};

	const primeReaderFlyer = (flyer) => {
		flyer.getBoundingClientRect();
	};

	const waitForFlyerTransition = (flyer) => new Promise((resolve) => {
		const duration = readerTransitionMs();

		if (!duration) {
			window.requestAnimationFrame(resolve);
			return;
		}

		let settled = false;
		const finish = () => {
			if (settled) {
				return;
			}

			settled = true;
			flyer.removeEventListener("transitionend", onTransitionEnd);
			resolve();
		};
		const onTransitionEnd = (event) => {
			if (event.target === flyer && event.propertyName === "transform") {
				finish();
			}
		};

		flyer.addEventListener("transitionend", onTransitionEnd);
		window.setTimeout(finish, duration + 120);
	});

	const clearActiveReaderFlyer = () => {
		activeReaderFlyer?.remove();
		activeReaderFlyer = null;
	};

	const finishReaderOpen = (id, triggerTab, flyer) => {
		triggerTab?.classList.remove(readerOriginHiddenClass);
		reader?.classList.remove("is-opening", "is-sheet-visible");
		setReaderHeader(id);
		syncProjectRuntime(id);

		window.requestAnimationFrame(() => {
			flyer?.remove();
			if (activeReaderFlyer === flyer) {
				activeReaderFlyer = null;
			}

			const activeSwitch = reader?.querySelector(`[data-project-reader-switch="${id}"]`);
			const closeButton = reader?.querySelector(".project-reader__close");

			(activeSwitch || closeButton)?.focus({ preventScroll: true });
		});
	};

	const finishReaderClose = (targetTab, flyer) => {
		readerHeader?.replaceChildren();
		targetTab?.classList.remove(readerOriginHiddenClass);

		window.requestAnimationFrame(() => {
			flyer?.remove();
			if (activeReaderFlyer === flyer) {
				activeReaderFlyer = null;
			}

			reader?.classList.remove("is-closing", "is-sheet-visible");

			if (reader) {
				reader.hidden = true;
			}

			document.documentElement.classList.remove("is-project-reader-open");
			document.body.classList.remove("is-project-reader-open");
			tabs.forEach((tab) => tab.setAttribute("aria-expanded", "false"));
			suspendTabHover();

			if (lastTrigger && typeof lastTrigger.focus === "function") {
				lastTrigger.focus({ preventScroll: true });
			}
		});
	};

	const setActiveProject = (id, options = {}) => {
		const { syncRuntime = true, updateHeader = true } = options;
		const activeTab = getProjectTab(id);

		if (reader && activeTab) {
			const accent = getComputedStyle(activeTab).getPropertyValue("--project-accent").trim();
			reader.style.setProperty("--project-accent", accent);
		}

		tabs.forEach((tab) => {
			const isActive = tab.dataset.projectTab === id;

			tab.classList.toggle("is-active", isActive);
			tab.setAttribute("aria-expanded", isActive && isReaderOpen() ? "true" : "false");

			if (isActive) {
				tab.setAttribute("aria-current", "true");
			} else {
				tab.removeAttribute("aria-current");
			}
		});

		readerSwitches.forEach((button) => {
			const isActive = button.dataset.projectReaderSwitch === id;

			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", isActive ? "true" : "false");
		});

		readerPanels.forEach((panel) => {
			const isActive = panel.dataset.projectReaderPanel === id;

			panel.classList.toggle("is-active", isActive);
			panel.setAttribute("aria-hidden", isActive ? "false" : "true");
		});

		const activePanel = readerPanels.find((panel) => panel.dataset.projectReaderPanel === id);

		if (readerTitle && activePanel?.dataset.projectReaderHeading) {
			readerTitle.textContent = activePanel.dataset.projectReaderHeading;
		}

		if (updateHeader && isReaderOpen()) {
			setReaderHeader(id);
		}

		if (syncRuntime) {
			syncProjectRuntime(id);
		}
	};

	const openReader = (id) => {
		if (!reader) {
			return;
		}

		if (!reader.hidden) {
			setActiveProject(id);
			return;
		}

		const triggerTab = getProjectTab(id);
		const sourceRect = triggerTab?.getBoundingClientRect();
		const token = ++readerTransitionToken;

		clearActiveReaderFlyer();
		lastTrigger = triggerTab || document.activeElement;
		reader.hidden = false;
		reader.classList.add("is-opening");
		reader.classList.remove("is-closing", "is-sheet-visible");
		document.documentElement.classList.add("is-project-reader-open");
		document.body.classList.add("is-project-reader-open");
		clearScrollHeldHover();
		setTabHoverReady(false);
		setActiveProject(id, { syncRuntime: false, updateHeader: false });
		setReaderHeader(id);

		const targetRect = readerHeader?.getBoundingClientRect();
		const flyer = triggerTab && sourceRect && targetRect
			? createReaderThumbnail(triggerTab, "project-reader__thumb-flyer", true)
			: null;

		if (!flyer) {
			finishReaderOpen(id, triggerTab, null);
			return;
		}

		triggerTab.classList.add(readerOriginHiddenClass);
		reader.append(flyer);
		activeReaderFlyer = flyer;
		setFlyerRect(flyer, sourceRect);
		primeReaderFlyer(flyer);

		window.requestAnimationFrame(() => {
			if (token !== readerTransitionToken) {
				return;
			}

			setFlyerRect(flyer, targetRect);
			reader.classList.add("is-sheet-visible");
		});

		waitForFlyerTransition(flyer).then(() => {
			if (token === readerTransitionToken) {
				finishReaderOpen(id, triggerTab, flyer);
			}
		});
	};

	const closeReader = () => {
		if (!reader || reader.hidden) {
			return;
		}

		const id = getActiveProjectId();
		const targetTab = getProjectTab(id) || (lastTrigger?.matches?.("[data-project-tab]") ? lastTrigger : null);
		const sourceRect = readerHeader?.getBoundingClientRect();
		const targetRect = targetTab?.getBoundingClientRect();
		const token = ++readerTransitionToken;
		const flyer = targetTab && sourceRect && targetRect
			? createReaderThumbnail(targetTab, "project-reader__thumb-flyer is-returning", true)
			: null;

		clearActiveReaderFlyer();
		unmountPokerGame();
		reader.classList.remove("is-opening", "is-sheet-visible");
		reader.classList.add("is-closing");
		setTabHoverReady(false);

		if (!flyer) {
			finishReaderClose(targetTab, null);
			return;
		}

		targetTab.classList.add(readerOriginHiddenClass);
		reader.append(flyer);
		activeReaderFlyer = flyer;
		setFlyerRect(flyer, sourceRect);
		primeReaderFlyer(flyer);

		window.requestAnimationFrame(() => {
			if (token !== readerTransitionToken) {
				return;
			}

			flyer.classList.remove(scrollHeldHoverClass);
			setFlyerRect(flyer, targetRect);
		});

		waitForFlyerTransition(flyer).then(() => {
			if (token === readerTransitionToken) {
				finishReaderClose(targetTab, flyer);
			}
		});
	};

	const getMostVisibleProject = () => [...visiblePanels.entries()]
		.sort((a, b) => b[1] - a[1])[0]?.[0];

	tabs.forEach((tab) => {
		tab.addEventListener("pointerenter", (event) => {
			updatePointerPosition(event);

			if (document.body.classList.contains(tabHoverReadyClass) && !isReaderOpen()) {
				startComicCloudDrift(tab);
			}
		});

		tab.addEventListener("pointerleave", () => {
			if (scrollHeldHoverTab !== tab) {
				stopComicCloudDrift(tab);
				stopTabParallax(tab);
			}
		});

		tab.addEventListener("click", () => {
			const id = tab.dataset.projectTab;

			openReader(id);
		});
	});

	readerSwitches.forEach((button) => {
		button.addEventListener("click", () => {
			setActiveProject(button.dataset.projectReaderSwitch);
		});
	});

	closeButtons.forEach((button) => {
		button.addEventListener("click", closeReader);
	});

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			tabs.forEach((tab) => stopTabParallax(tab));
		});
	} else {
		reduceMotion.addListener(() => {
			tabs.forEach((tab) => stopTabParallax(tab));
		});
	}

	document.addEventListener("pointermove", updatePointerPosition, { passive: true });
	window.addEventListener("scroll", suspendTabHover, { passive: true });
	window.addEventListener("wheel", suspendTabHover, { passive: true });
	window.addEventListener("touchmove", suspendTabHover, { passive: true });
	window.addEventListener("load", () => suspendTabHover(), { once: true });
	suspendTabHover();
	initTitleAnimationPause();

	document.addEventListener("visibilitychange", () => {
		if (document.hidden) {
			unmountPokerGame();
			return;
		}

		syncProjectRuntime(getActiveProjectId());
	});

	window.addEventListener("pagehide", unmountPokerGame);

	document.addEventListener("click", (event) => {
		const previewButton = event.target.closest("[data-project-preview]");

		if (!previewButton) {
			return;
		}

		const panel = previewButton.closest("[data-project-reader-panel]");
		const previewImage = panel?.querySelector("[data-project-preview-image]");

		if (!previewImage) {
			return;
		}

		previewImage.src = previewButton.dataset.projectPreviewSrc;
		previewImage.alt = previewButton.dataset.projectPreviewAlt || "";

		panel.querySelectorAll("[data-project-preview]").forEach((button) => {
			const isActive = button === previewButton;

			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", isActive ? "true" : "false");
		});
	});

	document.querySelectorAll("[data-project-preview]").forEach((button) => {
		button.setAttribute("aria-pressed", button.classList.contains("is-active") ? "true" : "false");
	});

	stack.addEventListener("keydown", (event) => {
		if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(event.key)) {
			return;
		}

		const currentIndex = tabs.indexOf(document.activeElement);

		if (currentIndex === -1) {
			return;
		}

		event.preventDefault();

		const direction = event.key === "ArrowDown" || event.key === "ArrowRight" ? 1 : -1;
		const nextIndex = (currentIndex + direction + tabs.length) % tabs.length;
		const nextTab = tabs[nextIndex];

		nextTab.focus();
		setActiveProject(nextTab.dataset.projectTab);
	});

	document.addEventListener("keydown", (event) => {
		if (!isReaderOpen()) {
			return;
		}

		if (event.key === "Escape") {
			event.preventDefault();
			closeReader();
			return;
		}

		if (event.key !== "Tab") {
			return;
		}

		const focusableItems = getFocusableReaderItems();

		if (!focusableItems.length) {
			return;
		}

		const firstItem = focusableItems[0];
		const lastItem = focusableItems[focusableItems.length - 1];

		if (event.shiftKey && document.activeElement === firstItem) {
			event.preventDefault();
			lastItem.focus();
		} else if (!event.shiftKey && document.activeElement === lastItem) {
			event.preventDefault();
			firstItem.focus();
		}
	});

	if (panels.length && "IntersectionObserver" in window) {
		const observer = new IntersectionObserver((entries) => {
			if (isReaderOpen()) {
				return;
			}

			entries.forEach((entry) => {
				const id = entry.target.dataset.projectPanel;

				if (!entry.isIntersecting) {
					visiblePanels.delete(id);
					return;
				}

				visiblePanels.set(id, entry.intersectionRatio);
			});

			const activeProject = getMostVisibleProject();

			if (activeProject) {
				setActiveProject(activeProject);
			}
		}, {
			root: null,
			rootMargin: "-30% 0px -48% 0px",
			threshold: [0.12, 0.28, 0.44, 0.6, 0.76],
		});

		panels.forEach((panel) => observer.observe(panel));
		setActiveProject(tabs.find((tab) => tab.classList.contains("is-active"))?.dataset.projectTab || tabs[0].dataset.projectTab);
		return;
	}

	let ticking = false;

	const updateFromScroll = () => {
		if (isReaderOpen() || !panels.length) {
			ticking = false;
			return;
		}

		const viewportAnchor = window.innerHeight * 0.4;
		const closestPanel = panels
			.map((panel) => ({
				panel,
				distance: Math.abs(panel.getBoundingClientRect().top - viewportAnchor),
			}))
			.sort((a, b) => a.distance - b.distance)[0]?.panel;

		if (closestPanel) {
			setActiveProject(closestPanel.dataset.projectPanel);
		}

		ticking = false;
	};

	setActiveProject(tabs.find((tab) => tab.classList.contains("is-active"))?.dataset.projectTab || tabs[0].dataset.projectTab);

	window.addEventListener("scroll", () => {
		if (ticking) {
			return;
		}

		ticking = true;
		window.requestAnimationFrame(updateFromScroll);
	}, { passive: true });
})();
