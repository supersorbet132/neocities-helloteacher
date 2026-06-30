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
