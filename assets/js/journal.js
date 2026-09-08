(() => {
	const app = document.querySelector("[data-journal-app]");

	if (!app) {
		return;
	}

	const DATA_SRC = "/assets/data/journal-entries.txt";
	const index = app.querySelector("[data-journal-index]");
	const countLabel = app.querySelector("[data-journal-count]");
	const reader = app.querySelector("[data-journal-reader]");
	const readerTitle = app.querySelector("[data-journal-reader-title]");
	const readerDate = app.querySelector("[data-journal-reader-date]");
	const readerContent = app.querySelector("[data-journal-reader-content]");
	const closeButton = app.querySelector("[data-journal-close]");
	let activeTrigger = null;

	const slugify = (value, fallback) => {
		const slug = String(value || "")
			.toLowerCase()
			.replace(/[^a-z0-9]+/g, "-")
			.replace(/^-+|-+$/g, "");

		return slug || fallback;
	};

	const parseEntryBlock = (block, index) => {
		const lines = block.replace(/\r\n?/g, "\n").split("\n");

		while (lines.length && !lines[0].trim()) {
			lines.shift();
		}

		const fields = {};
		let bodyStart = 0;

		for (; bodyStart < lines.length; bodyStart += 1) {
			const line = lines[bodyStart];

			if (!line.trim()) {
				bodyStart += 1;
				break;
			}

			const match = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/);

			if (!match) {
				break;
			}

			fields[match[1].toLowerCase()] = match[2].trim();
		}

		const title = fields.title || `Entry ${index + 1}`;
		const date = fields.date || "";

		return {
			body: lines.slice(bodyStart).join("\n").trim(),
			date,
			id: slugify(`${date}-${title}`, `entry-${index + 1}`),
			image: fields.image || "",
			imageAlt: fields.imagealt || title,
			order: index,
			summary: fields.summary || "",
			title,
		};
	};

	const entryTime = (entry) => {
		const match = String(entry.date).match(/^(\d{4})-(\d{2})-(\d{2})$/);

		if (!match) {
			return Number.NEGATIVE_INFINITY;
		}

		return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
	};

	const parseEntries = (source) => {
		const blocks = [];
		let current = null;

		source.replace(/\r\n?/g, "\n").split("\n").forEach((line) => {
			if (line.trim() === "---") {
				if (current) {
					blocks.push(current.join("\n"));
				}

				current = [];
				return;
			}

			if (current) {
				current.push(line);
			}
		});

		if (current) {
			blocks.push(current.join("\n"));
		}

		return blocks
			.map(parseEntryBlock)
			.filter((entry) => entry.title || entry.body)
			.sort((first, second) => {
				const byDate = entryTime(second) - entryTime(first);

				return byDate || first.order - second.order;
			});
	};

	const formatDate = (date) => {
		const match = String(date).match(/^(\d{4})-(\d{2})-(\d{2})$/);

		if (!match) {
			return date || "Undated";
		}

		return new Intl.DateTimeFormat("en-US", {
			day: "numeric",
			month: "long",
			timeZone: "UTC",
			year: "numeric",
		}).format(new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]))));
	};

	const normalizeImageSrc = (src) => {
		const trimmed = String(src || "").trim();

		if (!trimmed || /^(?:javascript|data):/i.test(trimmed)) {
			return "";
		}

		return trimmed;
	};

	const appendParagraph = (fragment, lines) => {
		if (!lines.length) {
			return;
		}

		const paragraph = document.createElement("p");
		paragraph.textContent = lines.join(" ");
		fragment.append(paragraph);
		lines.length = 0;
	};

	const appendImage = (fragment, src, alt) => {
		const imageSrc = normalizeImageSrc(src);

		if (!imageSrc) {
			return;
		}

		const figure = document.createElement("figure");
		const image = document.createElement("img");

		figure.className = "journal-reader__image";
		image.src = imageSrc;
		image.alt = alt || "";
		image.loading = "lazy";
		image.decoding = "async";
		figure.append(image);
		fragment.append(figure);
	};

	const renderBody = (entry) => {
		const fragment = document.createDocumentFragment();
		const paragraphLines = [];

		if (entry.image) {
			appendImage(fragment, entry.image, entry.imageAlt);
		}

		entry.body.split("\n").forEach((line) => {
			const trimmed = line.trim();
			const imageMatch = trimmed.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);

			if (!trimmed) {
				appendParagraph(fragment, paragraphLines);
				return;
			}

			if (imageMatch) {
				appendParagraph(fragment, paragraphLines);
				appendImage(fragment, imageMatch[2], imageMatch[1]);
				return;
			}

			if (trimmed.startsWith("## ")) {
				appendParagraph(fragment, paragraphLines);
				const heading = document.createElement("h3");
				heading.textContent = trimmed.replace(/^##\s+/, "");
				fragment.append(heading);
				return;
			}

			paragraphLines.push(trimmed);
		});

		appendParagraph(fragment, paragraphLines);

		if (!fragment.childNodes.length) {
			const empty = document.createElement("p");
			empty.textContent = "This entry is empty for now.";
			fragment.append(empty);
		}

		return fragment;
	};

	const openEntry = (entry, trigger) => {
		if (!reader || !readerTitle || !readerDate || !readerContent) {
			return;
		}

		activeTrigger = trigger;
		readerTitle.textContent = entry.title;
		readerDate.dateTime = entry.date;
		readerDate.textContent = formatDate(entry.date);
		readerContent.replaceChildren(renderBody(entry));
		reader.scrollTop = 0;
		readerContent.scrollTop = 0;
		reader.hidden = false;
		document.documentElement.classList.add("is-journal-reader-open");
		document.body.classList.add("is-journal-reader-open");
		trigger?.setAttribute("aria-expanded", "true");

		window.requestAnimationFrame(() => {
			readerContent.focus({ preventScroll: true });
		});
	};

	const closeEntry = () => {
		if (!reader || reader.hidden) {
			return;
		}

		reader.hidden = true;
		document.documentElement.classList.remove("is-journal-reader-open");
		document.body.classList.remove("is-journal-reader-open");

		if (activeTrigger) {
			activeTrigger.setAttribute("aria-expanded", "false");
			activeTrigger.focus({ preventScroll: true });
			activeTrigger = null;
		}
	};

	const createEntryButton = (entry, index) => {
		const button = document.createElement("button");
		const date = document.createElement("time");
		const title = document.createElement("span");
		const summary = document.createElement("span");

		button.className = "journal-entry-row";
		button.type = "button";
		button.dataset.journalEntry = entry.id;
		button.setAttribute("aria-expanded", "false");

		date.className = "journal-entry-row__date";
		date.dateTime = entry.date;
		date.textContent = formatDate(entry.date);

		title.className = "journal-entry-row__title";
		title.textContent = entry.title;

		summary.className = "journal-entry-row__summary";
		summary.textContent = entry.summary || entry.body.split(/\n\s*\n/)[0] || "Open entry";

		button.style.setProperty("--journal-entry-index", index);
		button.append(date, title, summary);
		button.addEventListener("click", () => openEntry(entry, button));

		return button;
	};

	const renderIndex = (entries) => {
		if (!entries.length) {
			index.replaceChildren();
			const empty = document.createElement("p");
			empty.className = "journal-index__status";
			empty.textContent = "No journal entries yet.";
			index.append(empty);
			countLabel.textContent = "0 entries";
			return;
		}

		index.replaceChildren(...entries.map(createEntryButton));
		countLabel.textContent = `${entries.length} ${entries.length === 1 ? "entry" : "entries"}`;
	};

	const showError = () => {
		index.replaceChildren();
		const error = document.createElement("p");
		error.className = "journal-index__status";
		error.textContent = "The journal entries could not be loaded.";
		index.append(error);
		countLabel.textContent = "Entries unavailable";
	};

	closeButton?.addEventListener("click", closeEntry);
	window.addEventListener("keydown", (event) => {
		if (event.key === "Escape") {
			closeEntry();
		}
	});

	fetch(DATA_SRC)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Journal entries request failed: ${response.status}`);
			}

			return response.text();
		})
		.then((source) => renderIndex(parseEntries(source)))
		.catch(showError);
})();
