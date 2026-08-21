(() => {
	const stack = document.querySelector("[data-project-rail]");
	const tabs = [...document.querySelectorAll("[data-project-tab]")];
	const panels = [...document.querySelectorAll("[data-project-panel]")];
	const reader = document.querySelector("[data-project-reader]");
	const readerTitle = document.querySelector("[data-project-reader-title]");
	const readerPanels = [...document.querySelectorAll("[data-project-reader-panel]")];
	const readerSwitches = [...document.querySelectorAll("[data-project-reader-switch]")];
	const closeButtons = [...document.querySelectorAll("[data-project-close]")];

	if (!stack || !tabs.length) {
		return;
	}

	const visiblePanels = new Map();
	let lastTrigger = null;

	const isReaderOpen = () => Boolean(reader && !reader.hidden);

	const getFocusableReaderItems = () => {
		if (!reader || reader.hidden) {
			return [];
		}

		return [...reader.querySelectorAll("button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])")]
			.filter((item) => !item.disabled && item.offsetParent !== null);
	};

	const setActiveProject = (id) => {
		const activeTab = tabs.find((tab) => tab.dataset.projectTab === id);

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
	};

	const openReader = (id) => {
		if (!reader) {
			return;
		}

		lastTrigger = tabs.find((tab) => tab.dataset.projectTab === id) || document.activeElement;
		reader.hidden = false;
		document.body.classList.add("is-project-reader-open");
		setActiveProject(id);

		window.requestAnimationFrame(() => {
			const activeSwitch = reader.querySelector(`[data-project-reader-switch="${id}"]`);
			const closeButton = reader.querySelector(".project-reader__close");

			(activeSwitch || closeButton)?.focus({ preventScroll: true });
		});
	};

	const closeReader = () => {
		if (!reader || reader.hidden) {
			return;
		}

		reader.hidden = true;
		document.body.classList.remove("is-project-reader-open");
		tabs.forEach((tab) => tab.setAttribute("aria-expanded", "false"));

		if (lastTrigger && typeof lastTrigger.focus === "function") {
			lastTrigger.focus({ preventScroll: true });
		}
	};

	const getMostVisibleProject = () => [...visiblePanels.entries()]
		.sort((a, b) => b[1] - a[1])[0]?.[0];

	tabs.forEach((tab) => {
		tab.addEventListener("click", () => {
			const id = tab.dataset.projectTab;

			setActiveProject(id);
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
