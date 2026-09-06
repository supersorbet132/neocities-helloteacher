(() => {
	const viewer = document.querySelector("[data-cad-model-viewer]");

	if (!viewer) {
		return;
	}

	const stage = viewer.querySelector("[data-cad-model-stage]");
	const launchButton = viewer.querySelector("[data-cad-model-start]");
	const launchText = viewer.querySelector(".cad-display-window__model-launch-text");
	const status = document.querySelector("[data-cad-viewer-status]");
	const modelSrc = viewer.dataset.cadModelSrc;
	const modelTitle = viewer.dataset.cadModelTitle || "CAD model";
	const maxDevicePixelRatio = 1.75;

	let modulePromise = null;
	let renderer = null;
	let scene = null;
	let camera = null;
	let controls = null;
	let resizeObserver = null;
	let animationFrame = 0;
	let isLoaded = false;
	let isLoading = false;
	let isViewerOpen = false;

	const setStatus = (message) => {
		if (status) {
			status.textContent = message;
		}

		viewer.dataset.cadModelStatus = message;
	};

	const setLaunchLabel = (message) => {
		if (launchText) {
			launchText.textContent = message;
		}
	};

	const loadThreeModules = () => {
		if (!modulePromise) {
			modulePromise = Promise.all([
				import("three"),
				import("three/addons/loaders/GLTFLoader.js"),
				import("three/addons/controls/OrbitControls.js"),
			]).then(([THREE, loaderModule, controlsModule]) => ({
				THREE,
				GLTFLoader: loaderModule.GLTFLoader,
				OrbitControls: controlsModule.OrbitControls,
			}));
		}

		return modulePromise;
	};

	const stopRendering = () => {
		if (animationFrame) {
			window.cancelAnimationFrame(animationFrame);
			animationFrame = 0;
		}
	};

	const resizeRenderer = () => {
		if (!renderer || !camera || !stage) {
			return;
		}

		const { width, height } = stage.getBoundingClientRect();

		if (width <= 0 || height <= 0) {
			return;
		}

		renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, maxDevicePixelRatio));
		renderer.setSize(Math.floor(width), Math.floor(height), false);
		camera.aspect = width / height;
		camera.updateProjectionMatrix();
	};

	const startRendering = () => {
		if (!renderer || !scene || !camera || animationFrame || !isViewerOpen || document.hidden) {
			return;
		}

		resizeRenderer();

		const render = () => {
			if (!isViewerOpen || document.hidden) {
				stopRendering();
				return;
			}

			controls?.update();
			renderer.render(scene, camera);
			animationFrame = window.requestAnimationFrame(render);
		};

		animationFrame = window.requestAnimationFrame(render);
	};

	const tuneModelMaterials = (THREE, root) => {
		const tuneMaterial = (material) => {
			if (!material) {
				return material;
			}

			const tuned = material.clone ? material.clone() : material;

			if (tuned.emissive) {
				tuned.emissive.set(0x08242b);
				tuned.emissiveIntensity = Math.max(tuned.emissiveIntensity || 0, 0.18);
			}

			if ("roughness" in tuned) {
				tuned.roughness = Math.min(Math.max(tuned.roughness ?? 0.72, 0.48), 0.86);
			}

			if ("metalness" in tuned) {
				tuned.metalness = Math.max(tuned.metalness ?? 0, 0.16);
			}

			return tuned;
		};

		const edgeMaterial = new THREE.LineBasicMaterial({
			color: 0x8af7ff,
			transparent: true,
			opacity: 0.24,
			depthTest: true,
		});

		root.traverse((child) => {
			if (!child.isMesh) {
				return;
			}

			child.material = Array.isArray(child.material)
				? child.material.map(tuneMaterial)
				: tuneMaterial(child.material);

			if (child.geometry) {
				const edges = new THREE.LineSegments(new THREE.EdgesGeometry(child.geometry, 32), edgeMaterial);
				edges.renderOrder = 2;
				child.add(edges);
			}
		});
	};

	const fitCameraToModel = (THREE, modelRoot) => {
		const box = new THREE.Box3().setFromObject(modelRoot);
		const size = box.getSize(new THREE.Vector3());
		const center = box.getCenter(new THREE.Vector3());
		const maxDimension = Math.max(size.x, size.y, size.z, 1);
		const cameraDistance = maxDimension * 0.45;
		const cameraPosition = new THREE.Vector3(0.72, 0.45, 1.08).normalize().multiplyScalar(cameraDistance);

		modelRoot.position.sub(center);
		camera.near = Math.max(maxDimension / 1000, 0.01);
		camera.far = maxDimension * 30;
		camera.position.copy(cameraPosition);
		camera.lookAt(0, 0, 0);
		camera.updateProjectionMatrix();

		controls.target.set(0, 0, 0);
		controls.minDistance = maxDimension * 0.36;
		controls.maxDistance = maxDimension * 2.6;
		controls.update();

		const grid = new THREE.GridHelper(maxDimension * 2.7, 24, 0x8af7ff, 0x155667);
		grid.position.y = -size.y / 2;
		grid.material.transparent = true;
		grid.material.opacity = 0.28;
		scene.add(grid);
	};

	const mountModel = async () => {
		if (isLoaded || isLoading || !modelSrc || !stage) {
			return;
		}

		isLoading = true;
		viewer.classList.add("is-model-loading");
		viewer.classList.remove("is-model-error");
		if (launchButton) {
			launchButton.disabled = true;
		}
		setLaunchLabel("Loading Model");
		setStatus("Loading 3D Model");

		try {
			const { THREE, GLTFLoader, OrbitControls } = await loadThreeModules();
			const loader = new GLTFLoader();

			renderer = new THREE.WebGLRenderer({
				alpha: true,
				antialias: true,
				powerPreference: "high-performance",
			});
			renderer.setClearColor(0x000000, 0);
			renderer.outputColorSpace = THREE.SRGBColorSpace;
			renderer.domElement.className = "cad-display-window__model-canvas";
			renderer.domElement.setAttribute("aria-label", `Interactive 3D view of ${modelTitle}`);
			renderer.domElement.setAttribute("role", "img");

			scene = new THREE.Scene();
			camera = new THREE.PerspectiveCamera(38, 1, 0.01, 1000);
			camera.up.set(0, 1, 0);

			const ambient = new THREE.AmbientLight(0x8af7ff, 1.25);
			const key = new THREE.DirectionalLight(0xd8fdff, 2.1);
			const rim = new THREE.DirectionalLight(0x2799ff, 1.35);
			key.position.set(3, 5, 4);
			rim.position.set(-4, 2, -5);
			scene.add(ambient, key, rim);

			const gltf = await loader.loadAsync(modelSrc, (progress) => {
				if (!progress.lengthComputable) {
					setStatus("Loading 3D Model");
					return;
				}

				const percentLoaded = Math.round((progress.loaded / progress.total) * 100);

				setLaunchLabel(`Loading ${percentLoaded}%`);
				setStatus(`Loading ${percentLoaded}%`);
			});
			const modelRoot = gltf.scene || gltf.scenes?.[0];

			if (!modelRoot) {
				throw new Error("GLB contained no scene");
			}

			tuneModelMaterials(THREE, modelRoot);
			scene.add(modelRoot);

			controls = new OrbitControls(camera, renderer.domElement);
			controls.enableDamping = true;
			controls.dampingFactor = 0.08;
			controls.enablePan = false;
			controls.enableRotate = true;
			controls.enableZoom = true;
			controls.rotateSpeed = 0.55;
			controls.zoomSpeed = 0.82;
			controls.screenSpacePanning = false;
			controls.minPolarAngle = Math.PI * 0.08;
			controls.maxPolarAngle = Math.PI * 0.92;
			controls.mouseButtons = {
				LEFT: THREE.MOUSE.ROTATE,
				MIDDLE: THREE.MOUSE.DOLLY,
				RIGHT: THREE.MOUSE.ROTATE,
			};
			controls.touches = {
				ONE: THREE.TOUCH.ROTATE,
				TWO: THREE.TOUCH.DOLLY_ROTATE,
			};

			stage.append(renderer.domElement);
			fitCameraToModel(THREE, modelRoot);

			if ("ResizeObserver" in window) {
				resizeObserver = new ResizeObserver(resizeRenderer);
				resizeObserver.observe(stage);
			}

			isLoaded = true;
			isLoading = false;
			viewer.classList.remove("is-model-loading");
			viewer.classList.add("is-model-loaded");
			setStatus("Interactive Model Ready");
			startRendering();
		} catch (error) {
			console.warn("CAD model viewer failed to load", error);
			isLoading = false;
			viewer.classList.remove("is-model-loading");
			viewer.classList.add("is-model-error");
			if (launchButton) {
				launchButton.disabled = false;
			}
			setLaunchLabel("Retry Model");
			setStatus("Model Load Failed");
		}
	};

	launchButton?.addEventListener("click", (event) => {
		event.preventDefault();
		event.stopPropagation();
		mountModel();
	});

	document.addEventListener("cad:viewer-opened", () => {
		isViewerOpen = true;

		if (isLoaded) {
			setStatus("Interactive Model Ready");
			startRendering();
		} else if (!isLoading) {
			setLaunchLabel("Load 3D Model");
			setStatus("Viewer Standby");
		}
	});

	document.addEventListener("cad:viewer-closed", () => {
		isViewerOpen = false;
		stopRendering();
	});

	document.addEventListener("visibilitychange", () => {
		if (document.hidden) {
			stopRendering();
			return;
		}

		startRendering();
	});

	window.addEventListener("resize", resizeRenderer);
	setStatus("Viewer Standby");
})();
