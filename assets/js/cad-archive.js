(() => {
	const archive = document.querySelector("[data-cad-archive]");

	if (!archive) {
		return;
	}

	// Add, remove, or reorder CAD records here as the archive grows.
	const models = [
		{
			name: "Placeholder (1)",
			date: "TBD",
			category: "assemblies",
			type: "Assembly",
			status: "Coming soon",
			tags: [],
		},
		{
			name: "Placeholder (2)",
			date: "TBD",
			category: "parts",
			type: "Part",
			status: "Coming soon",
			tags: [],
		},
		{
			name: "Placeholder (3)",
			date: "TBD",
			category: "mechanisms",
			type: "Mechanism",
			status: "Coming soon",
			tags: [],
		},
		{
			name: "Placeholder (4)",
			date: "TBD",
			category: "fixtures",
			type: "Fixture",
			status: "Coming soon",
			tags: [],
		},
		{
			name: "Placeholder (5)",
			date: "TBD",
			category: "experiments",
			type: "Experiment",
			status: "Coming soon",
			tags: [],
		},
	];

	const filterButtons = [...archive.querySelectorAll("[data-cad-filter]")];
	const panel = archive.querySelector(".cad-archive__panel");
	const toolbar = archive.querySelector(".cad-archive__toolbar");
	const list = archive.querySelector("[data-cad-model-list]");
	const count = archive.querySelector("[data-cad-model-count]");
	const archiveStatus = archive.querySelector("[data-cad-archive-status]");
	let activeFilter = "all";
	let filterTimer = 0;

	if (!list) {
		return;
	}

	const formatDescription = (model) => model.description || "";

	const createMetaItem = (label, value) => {
		const item = document.createElement("div");
		const term = document.createElement("dt");
		const detail = document.createElement("dd");

		term.textContent = label;
		detail.textContent = value;
		item.append(term, detail);

		return item;
	};

	const createTag = (tag) => {
		const item = document.createElement("span");
		item.className = "cad-model-row__tag";
		item.textContent = tag;

		return item;
	};

	const createModelRow = (model, index) => {
		const article = document.createElement("article");
		const preview = document.createElement("div");
		const marker = document.createElement("span");
		const detail = document.createElement("div");
		const header = document.createElement("header");
		const title = document.createElement("h3");
		const type = document.createElement("p");
		const description = document.createElement("p");
		const meta = document.createElement("dl");
		const tags = document.createElement("div");
		const actions = document.createElement("div");
		const load = document.createElement("button");

		article.className = "cad-model-row";
		article.dataset.cadModelCategory = model.category;
		article.dataset.cadModelName = model.name;
		article.style.setProperty("--cad-row-index", index);

		preview.className = "cad-model-row__preview";
		preview.setAttribute("aria-hidden", "true");
		marker.className = "cad-model-row__marker";
		marker.textContent = String(index + 1).padStart(2, "0");
		preview.append(marker);

		detail.className = "cad-model-row__detail";
		header.className = "cad-model-row__header";
		title.textContent = model.name;
		type.textContent = `${model.type} / ${model.status}`;
		header.append(title, type);

		description.className = "cad-model-row__description";
		description.textContent = formatDescription(model);

		meta.className = "cad-model-row__meta";
		meta.append(
			createMetaItem("Date", model.date),
			createMetaItem("Class", model.type),
			createMetaItem("State", model.status),
		);

		tags.className = "cad-model-row__tags";
		(model.tags || []).forEach((tag) => tags.append(createTag(tag)));

		actions.className = "cad-model-row__actions";
		load.className = "cad-model-row__action";
		load.type = "button";
		load.dataset.cadModelAction = "load";
		load.textContent = "Load Viewer";
		actions.append(load);

		detail.append(header, description, meta, tags, actions);
		article.append(preview, detail);

		return article;
	};

	const getMaxPanelHeight = () => {
		if (!panel) {
			return Number.POSITIVE_INFINITY;
		}

		const maxHeight = Number.parseFloat(getComputedStyle(panel).maxHeight);

		return Number.isFinite(maxHeight) ? maxHeight : Number.POSITIVE_INFINITY;
	};

	const setPanelHeight = () => {
		if (!panel) {
			return;
		}

		const nextHeight = Math.min((toolbar?.offsetHeight || 0) + list.scrollHeight, getMaxPanelHeight());

		panel.style.setProperty("--cad-archive-panel-height", `${Math.ceil(nextHeight)}px`);
	};

	const renderModels = (selectedModels) => {
		list.replaceChildren(...selectedModels.map(createModelRow));
		setPanelHeight();
	};

	const updateFilterChrome = (filter) => {
		filterButtons.forEach((button) => {
			const isActive = button.dataset.cadFilter === filter;

			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", String(isActive));
		});
	};

	const updateCount = (selectedModels) => {
		if (count) {
			count.textContent = `${selectedModels.length} ${selectedModels.length === 1 ? "record" : "records"}`;
		}

		if (archiveStatus) {
			archiveStatus.textContent = "Viewport / Archive Bay 02";
		}
	};

	const setActiveFilter = (filter, options = {}) => {
		if (filter === activeFilter && options.initial !== true) {
			return;
		}

		const selectedModels = filter === "all"
			? models
			: models.filter((model) => model.category === filter);

		window.clearTimeout(filterTimer);
		activeFilter = filter;
		updateFilterChrome(filter);

		if (options.initial === true || list.children.length === 0) {
			renderModels(selectedModels);
			updateCount(selectedModels);
			list.classList.add("is-filtering-in");
			filterTimer = window.setTimeout(() => list.classList.remove("is-filtering-in"), 420);
			return;
		}

		panel?.style.setProperty("--cad-archive-panel-height", `${Math.ceil(panel.offsetHeight)}px`);
		list.classList.remove("is-filtering-in");
		list.classList.add("is-filtering-out");

		filterTimer = window.setTimeout(() => {
			renderModels(selectedModels);
			updateCount(selectedModels);
			list.classList.remove("is-filtering-out");
			list.classList.add("is-filtering-in");

			filterTimer = window.setTimeout(() => list.classList.remove("is-filtering-in"), 520);
		}, 260);
	};

	filterButtons.forEach((button) => {
		button.addEventListener("click", () => setActiveFilter(button.dataset.cadFilter || "all"));
	});

	list.addEventListener("click", (event) => {
		const action = event.target.closest("[data-cad-model-action]");

		if (!action) {
			return;
		}

		const row = action.closest("[data-cad-model-name]");

		if (!row) {
			return;
		}

		list.querySelectorAll(".is-selected").forEach((selected) => selected.classList.remove("is-selected"));
		row.classList.add("is-selected");

		if (archiveStatus) {
			archiveStatus.textContent = `${row.dataset.cadModelName} / Viewer standby`;
		}

		document.dispatchEvent(new CustomEvent("cad:open-viewer", {
			detail: {
				action: action.dataset.cadModelAction,
				copy: "",
				hasModel: false,
				model: row.dataset.cadModelName,
			},
		}));
	});

	window.addEventListener("resize", setPanelHeight);

	setActiveFilter("all", { initial: true });
})();
