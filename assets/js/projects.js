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
	const pokerLaunchThumbnailSrc = "/assets/images/projects/sprites/pokertab/poker_launch_thumbnail.png";
	const projectsHero = document.querySelector(".projects-hero");
	const projectsTitleCard = document.querySelector(".projects-title-card[data-sprite-card='projects']");
	const comicViewer = document.querySelector("[data-comic-viewer]");
	const comicPageImage = document.querySelector("[data-comic-page-image]");
	const comicPageStrip = document.querySelector("[data-comic-page-strip]");
	const comicChapterButtons = [...document.querySelectorAll("[data-comic-chapter]")];
	const beetZoomViewers = [...document.querySelectorAll("[data-zoom-viewer]")];
	const spriteViewers = [...document.querySelectorAll("[data-sprite-viewer]")];

	if (!stack || !tabs.length) {
		return;
	}

	const visiblePanels = new Map();
	const tabHoverReadyClass = "is-project-tabs-hover-ready";
	const scrollHeldHoverClass = "is-scroll-held-hover";
	const comicCloudDriftClass = "is-comic-cloud-drifting";
	const comicParallaxActiveClass = "is-comic-parallax-active";
	const beetParallaxActiveClass = "is-beet-parallax-active";
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
	const comicChapters = [
		{ title: "Chapter 1", dir: "ch1", pages: Array.from({ length: 16 }, (_, index) => index) },
		{ title: "Chapter 2", dir: "ch2", pages: Array.from({ length: 20 }, (_, index) => index + 1) },
		{ title: "Chapter 3", dir: "ch3", pages: Array.from({ length: 20 }, (_, index) => index + 1) },
	];
	let comicChapterIndex = 0;
	let comicPageIndex = 0;
	const zoomViewerStates = new WeakMap();

	const isReaderOpen = () => Boolean(reader && !reader.hidden);

	const setTabHoverReady = (ready) => {
		document.body.classList.toggle(tabHoverReadyClass, ready && !isReaderOpen());
	};

	const isComicTab = (tab) => tab?.classList.contains("project-bar--comic");
	const isBeetTab = (tab) => tab?.classList.contains("project-bar--beet");
	const isPokerTab = (tab) => tab?.classList.contains("project-bar--poker");
	const getProjectTab = (id) => tabs.find((tab) => tab.dataset.projectTab === id);

	const getComicCloudLayers = (tab) => [...(tab?.querySelectorAll(".project-comic-tab__layer--cloud") || [])];

	const getNumberVar = (element, name, fallback) => {
		const parsed = Number.parseFloat(getComputedStyle(element).getPropertyValue(name));

		return Number.isFinite(parsed) ? parsed : fallback;
	};

	const getDatasetNumber = (element, name, fallback) => {
		const parsed = Number.parseFloat(element?.dataset?.[name]);

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

		if (isBeetTab(tab)) {
			return {
				activeClass: beetParallaxActiveClass,
				artSelector: ".project-beet-tab",
				defaultRangeX: 14,
				defaultRangeY: 8,
				depthVar: "--beet-parallax-depth",
				layerSelector: ".project-beet-tab__layer, .project-beet-tab__title",
				rangeXVar: "--beet-parallax-range-x",
				rangeYVar: "--beet-parallax-range-y",
				xVar: "--beet-parallax-x",
				yVar: "--beet-parallax-y",
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
		const data = {
			art,
			config,
			layers,
			maxX: getNumberVar(art, config.rangeXVar, config.defaultRangeX),
			maxY: getNumberVar(art, config.rangeYVar, config.defaultRangeY),
		};
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

		if (!tab.classList.contains(data.config.activeClass)) {
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

		tab.classList.add(data.config.activeClass);
		data.layers.forEach(({ layer, depth }) => {
			layer.style.setProperty(data.config.xVar, `${(progressX * data.maxX * depth).toFixed(2)}px`);
			layer.style.setProperty(data.config.yVar, `${(progressY * data.maxY * depth).toFixed(2)}px`);
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
		const button = document.createElement("button");
		button.className = "project-reader__game-launch";
		button.type = "button";
		button.setAttribute("aria-label", "Play Poker");
		button.setAttribute("data-project-game-start", "");
		button.innerHTML = `
			<span class="project-reader__game-launch-art" aria-hidden="true">
				<img src="${pokerLaunchThumbnailSrc}" alt="" width="1844" height="1250" loading="lazy" decoding="async">
			</span>
			<span class="project-reader__game-launch-copy" aria-hidden="true">
				<span class="project-reader__game-play-icon"></span>
			</span>
		`;
		return button;
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
		if (id !== "poker") {
			unmountPokerGame();
		}
	};

	const comicPageSrc = (chapterIndex, pageIndex) => {
		const chapter = comicChapters[chapterIndex];
		const page = chapter.pages[pageIndex];
		return `/assets/images/projects/comic/${chapter.dir}/${page}.jpg`;
	};

	const setComicPage = (chapterIndex, pageIndex) => {
		if (!comicPageImage || !comicPageStrip) {
			return;
		}

		const chapter = comicChapters[chapterIndex] || comicChapters[0];
		const nextPageIndex = Math.max(0, Math.min(pageIndex, chapter.pages.length - 1));
		comicChapterIndex = Math.max(0, Math.min(chapterIndex, comicChapters.length - 1));
		comicPageIndex = nextPageIndex;

		comicPageImage.src = comicPageSrc(comicChapterIndex, comicPageIndex);
		comicPageImage.alt = `${chapter.title} page ${comicPageIndex + 1}.`;

		comicChapterButtons.forEach((button, index) => {
			const isActive = index === comicChapterIndex;
			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", isActive ? "true" : "false");
		});

		comicPageStrip.querySelectorAll("[data-comic-page]").forEach((button) => {
			const isActive = Number(button.dataset.comicPage) === comicPageIndex;
			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", isActive ? "true" : "false");
		});
	};

	const renderComicPageStrip = () => {
		if (!comicPageStrip) {
			return;
		}

		comicPageStrip.replaceChildren();
		comicChapters[comicChapterIndex].pages.forEach((_, index) => {
			const button = document.createElement("button");
			button.type = "button";
			button.dataset.comicPage = String(index);
			button.textContent = String(index + 1);
			button.setAttribute("aria-label", `Open page ${index + 1}`);
			button.addEventListener("click", () => setComicPage(comicChapterIndex, index));
			comicPageStrip.append(button);
		});
		setComicPage(comicChapterIndex, comicPageIndex);
	};

	const stepComicPage = (direction) => {
		const chapter = comicChapters[comicChapterIndex];
		let nextChapterIndex = comicChapterIndex;
		let nextPageIndex = comicPageIndex + direction;

		if (nextPageIndex < 0 && comicChapterIndex > 0) {
			nextChapterIndex -= 1;
			nextPageIndex = comicChapters[nextChapterIndex].pages.length - 1;
		} else if (nextPageIndex >= chapter.pages.length && comicChapterIndex < comicChapters.length - 1) {
			nextChapterIndex += 1;
			nextPageIndex = 0;
		}

		if (nextChapterIndex !== comicChapterIndex) {
			comicChapterIndex = nextChapterIndex;
			comicPageIndex = nextPageIndex;
			renderComicPageStrip();
			return;
		}

		setComicPage(nextChapterIndex, nextPageIndex);
	};

	const getZoomContent = (viewer) => viewer?.querySelector("[data-zoom-content]");

	const getZoomViewerState = (viewer) => {
		if (!viewer) {
			return null;
		}

		const content = getZoomContent(viewer);

		if (!content) {
			return null;
		}

		if (!zoomViewerStates.has(viewer)) {
			const defaultScale = getDatasetNumber(viewer, "zoomDefaultScale", 1);
			const minScale = getDatasetNumber(viewer, "zoomMinScale", Math.min(0.45, defaultScale));
			const maxScale = getDatasetNumber(viewer, "zoomMaxScale", 4);

			zoomViewerStates.set(viewer, {
				content,
				defaultScale,
				minScale,
				maxScale,
				scale: defaultScale,
				x: 0,
				y: 0,
				dragging: false,
				startX: 0,
				startY: 0,
				originX: 0,
				originY: 0,
			});
		}

		const state = zoomViewerStates.get(viewer);
		state.content = content;
		return state;
	};

	const clampZoomScale = (state, scale) => Math.max(state.minScale, Math.min(state.maxScale, scale));

	const applyBeetZoom = (viewer) => {
		const state = getZoomViewerState(viewer);

		if (!state) {
			return;
		}

		state.content.style.transform = `translate3d(${state.x}px, ${state.y}px, 0) scale(${state.scale})`;
	};

	const resetBeetZoom = (viewer, scale = null) => {
		const state = getZoomViewerState(viewer);

		if (!state) {
			return;
		}

		const nextDefaultScale = Number.isFinite(scale) ? scale : state.defaultScale;
		state.defaultScale = clampZoomScale(state, nextDefaultScale);
		state.scale = state.defaultScale;
		state.x = 0;
		state.y = 0;
		applyBeetZoom(viewer);
	};

	const adjustBeetZoom = (viewer, delta) => {
		const state = getZoomViewerState(viewer);

		if (!state) {
			return;
		}

		state.scale = clampZoomScale(state, state.scale + delta);
		applyBeetZoom(viewer);
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
		tab.childNodes.forEach((child) => thumbnail.append(child.cloneNode(true)));

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

			const activePanel = readerPanels.find((panel) => panel.dataset.projectReaderPanel === id);
			const closeButton = activePanel?.querySelector("[data-project-close]");

			closeButton?.focus({ preventScroll: true });
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
		readerHeader?.replaceChildren();

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

	comicChapterButtons.forEach((button) => {
		button.setAttribute("aria-pressed", button.classList.contains("is-active") ? "true" : "false");
		button.addEventListener("click", () => {
			comicChapterIndex = Number(button.dataset.comicChapter) || 0;
			comicPageIndex = 0;
			renderComicPageStrip();
		});
	});

	document.querySelector("[data-comic-prev]")?.addEventListener("click", () => stepComicPage(-1));
	document.querySelector("[data-comic-next]")?.addEventListener("click", () => stepComicPage(1));
	renderComicPageStrip();

	beetZoomViewers.forEach((viewer) => {
		const content = getZoomContent(viewer);

		content?.setAttribute("draggable", "false");
		content?.addEventListener("dragstart", (event) => event.preventDefault());
		content?.querySelectorAll?.("img").forEach((image) => {
			image.setAttribute("draggable", "false");
			image.addEventListener("dragstart", (event) => event.preventDefault());
		});
		resetBeetZoom(viewer);

		viewer.querySelector("[data-zoom-out]")?.addEventListener("click", () => adjustBeetZoom(viewer, -0.25));
		viewer.querySelector("[data-zoom-in]")?.addEventListener("click", () => adjustBeetZoom(viewer, 0.25));
		viewer.querySelector("[data-zoom-reset]")?.addEventListener("click", () => resetBeetZoom(viewer));

		viewer.addEventListener("wheel", (event) => {
			event.preventDefault();
			adjustBeetZoom(viewer, event.deltaY > 0 ? -0.2 : 0.2);
		}, { passive: false });

		viewer.addEventListener("pointerdown", (event) => {
			if (event.target.closest(".project-zoom-viewer__controls")) {
				return;
			}

			if (event.button !== undefined && event.button !== 0) {
				return;
			}

			const state = getZoomViewerState(viewer);

			if (!state) {
				return;
			}

			event.preventDefault();
			state.dragging = true;
			state.startX = event.clientX;
			state.startY = event.clientY;
			state.originX = state.x;
			state.originY = state.y;
			viewer.setPointerCapture(event.pointerId);
			viewer.classList.add("is-dragging");
		});

		viewer.addEventListener("pointermove", (event) => {
			const state = getZoomViewerState(viewer);

			if (!state?.dragging) {
				return;
			}

			state.x = state.originX + event.clientX - state.startX;
			state.y = state.originY + event.clientY - state.startY;
			applyBeetZoom(viewer);
		});

		const stopBeetDrag = () => {
			const state = getZoomViewerState(viewer);

			if (state) {
				state.dragging = false;
			}

			viewer.classList.remove("is-dragging");
		};

		viewer.addEventListener("pointerup", stopBeetDrag);
		viewer.addEventListener("pointercancel", stopBeetDrag);
	});

	const setSpriteViewerIndex = (viewer, index) => {
		const image = viewer.querySelector("[data-sprite-viewer-image]");
		const thumbs = [...viewer.querySelectorAll("[data-sprite-thumb]")];

		if (!image || !thumbs.length) {
			return;
		}

		const nextIndex = (index + thumbs.length) % thumbs.length;
		const activeThumb = thumbs[nextIndex];

		image.src = activeThumb.dataset.spriteSrc;
		image.alt = activeThumb.dataset.spriteAlt || "";
		viewer.dataset.spriteIndex = String(nextIndex);

		thumbs.forEach((thumb, thumbIndex) => {
			const isActive = thumbIndex === nextIndex;

			thumb.classList.toggle("is-active", isActive);
			thumb.setAttribute("aria-pressed", isActive ? "true" : "false");
		});
	};

	spriteViewers.forEach((viewer) => {
		const thumbs = [...viewer.querySelectorAll("[data-sprite-thumb]")];

		thumbs.forEach((thumb, index) => {
			thumb.setAttribute("aria-pressed", thumb.classList.contains("is-active") ? "true" : "false");
			thumb.addEventListener("click", () => setSpriteViewerIndex(viewer, index));
		});

		viewer.querySelector("[data-sprite-prev]")?.addEventListener("click", () => {
			setSpriteViewerIndex(viewer, Number(viewer.dataset.spriteIndex || 0) - 1);
		});
		viewer.querySelector("[data-sprite-next]")?.addEventListener("click", () => {
			setSpriteViewerIndex(viewer, Number(viewer.dataset.spriteIndex || 0) + 1);
		});
		setSpriteViewerIndex(viewer, 0);
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
		const gameStart = event.target.closest("[data-project-game-start]");

		if (gameStart) {
			mountPokerGame();
			return;
		}

		const previewButton = event.target.closest("[data-project-preview]");

		if (!previewButton) {
			return;
		}

		const previewScope = previewButton.closest("[data-project-preview-scope]")
			|| previewButton.closest("[data-project-reader-panel]");
		const previewImage = previewScope?.querySelector("[data-project-preview-image]");

		if (!previewImage) {
			return;
		}

		if (previewButton.dataset.projectPreviewWidth && previewButton.dataset.projectPreviewHeight) {
			previewImage.width = Number(previewButton.dataset.projectPreviewWidth);
			previewImage.height = Number(previewButton.dataset.projectPreviewHeight);
		}
		previewImage.alt = previewButton.dataset.projectPreviewAlt || "";
		previewImage.setAttribute("draggable", "false");

		const zoomViewer = previewImage.closest("[data-zoom-viewer]");
		if (zoomViewer) {
			const previewScale = Number.parseFloat(previewButton.dataset.projectPreviewScale);
			previewImage.addEventListener("load", () => resetBeetZoom(zoomViewer, previewScale), { once: true });
			previewImage.src = previewButton.dataset.projectPreviewSrc;
			resetBeetZoom(zoomViewer, previewScale);
		} else {
			previewImage.src = previewButton.dataset.projectPreviewSrc;
		}

		previewScope.querySelectorAll("[data-project-preview]").forEach((button) => {
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

		if (getActiveProjectId() === "comic" && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
			event.preventDefault();
			stepComicPage(event.key === "ArrowRight" ? 1 : -1);
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
