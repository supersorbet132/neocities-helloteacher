(() => {
	const canvas = document.querySelector("[data-gradient-shader]");

	if (!canvas) {
		return;
	}

	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

	if (reduceMotion.matches) {
		canvas.hidden = true;
		return;
	}

	const gl = canvas.getContext("webgl", {
		alpha: true,
		antialias: false,
		depth: false,
		powerPreference: "low-power",
		premultipliedAlpha: true,
		stencil: false,
	});

	if (!gl) {
		canvas.hidden = true;
		return;
	}

	const vertexSource = `
		attribute vec2 a_position;
		varying vec2 v_uv;

		void main() {
			v_uv = a_position * 0.5 + 0.5;
			gl_Position = vec4(a_position, 0.0, 1.0);
		}
	`;
	const sharedFragmentHelpers = `
		precision mediump float;

		float hash(vec2 p) {
			p = fract(p * vec2(123.34, 456.21));
			p += dot(p, p + 45.32);
			return fract(p.x * p.y);
		}

		float noise(vec2 p) {
			vec2 i = floor(p);
			vec2 f = fract(p);
			f = f * f * (3.0 - 2.0 * f);

			float a = hash(i);
			float b = hash(i + vec2(1.0, 0.0));
			float c = hash(i + vec2(0.0, 1.0));
			float d = hash(i + vec2(1.0, 1.0));

			return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
		}

		float fbm(vec2 p) {
			float value = 0.0;
			float amplitude = 0.5;
			mat2 turn = mat2(0.86, -0.50, 0.50, 0.86);

			for (int i = 0; i < 4; i++) {
				value += amplitude * noise(p);
				p = turn * p * 2.04 + vec2(13.7);
				amplitude *= 0.5;
			}

			return value;
		}

		vec2 flowField(vec2 p, float t) {
			float a = fbm(p * 1.12 + vec2(t * 0.08, -t * 0.035));
			float b = fbm(p * 1.28 + vec2(-t * 0.045, t * 0.06) + vec2(8.4));

			return vec2(a - 0.5, b - 0.5);
		}
	`;
	const simulationFragmentSource = `
		${sharedFragmentHelpers}

			uniform sampler2D u_state;
			uniform vec2 u_simulationSize;
			uniform float u_viewAspect;
		uniform float u_time;
		uniform float u_delta;
		uniform float u_scrollY;
		uniform float u_speed;
		uniform float u_scale;
		uniform float u_strength;
		uniform float u_feedback;
		uniform float u_diffusion;
		uniform float u_injection;
		varying vec2 v_uv;

		float wavefront(vec2 p, float t) {
			float woven = fbm(p * 1.45 + vec2(t * 0.035, -t * 0.055));
			float frontA = sin((p.x * 1.55 + p.y * 0.72 + woven * 1.85 + t * 0.26) * 6.2831853);
			float frontB = sin((-p.x * 0.82 + p.y * 1.92 + fbm(p.yx * 1.6 - vec2(t * 0.04)) * 1.42 - t * 0.19) * 6.2831853);
			float ribbonA = smoothstep(0.86, 1.0, frontA * 0.5 + 0.5);
			float ribbonB = smoothstep(0.90, 1.0, frontB * 0.5 + 0.5);
			float eddy = smoothstep(0.58, 0.88, fbm(p * 4.2 + woven + vec2(t * 0.035, t * 0.02)));

			return ribbonA * 0.62 + ribbonB * 0.36 + eddy * 0.18;
		}

		void main() {
				float aspect = u_viewAspect;
			float t = u_time * u_speed;
			float scale = max(u_scale, 0.001);
			float strength = max(u_strength, 0.0);
			float dt = clamp(u_delta, 0.2, 2.0);
			vec2 texel = 1.0 / u_simulationSize;
			vec2 p = (v_uv - 0.5) * vec2(aspect, 1.0);
			vec2 drift = vec2(t * 0.052, -t * 0.026) + vec2(u_scrollY * 0.000025, -u_scrollY * 0.000012);
			vec2 field = flowField(p * scale + drift, t);
			vec2 stateUv = clamp(v_uv - field * 0.006 * strength, texel, vec2(1.0) - texel);

			vec4 centerState = texture2D(u_state, stateUv);
			float center = centerState.r * 2.0 - 1.0;
			float velocity = centerState.g * 2.0 - 1.0;
			float north = texture2D(u_state, clamp(stateUv + vec2(0.0, texel.y), texel, vec2(1.0) - texel)).r * 2.0 - 1.0;
			float south = texture2D(u_state, clamp(stateUv - vec2(0.0, texel.y), texel, vec2(1.0) - texel)).r * 2.0 - 1.0;
			float east = texture2D(u_state, clamp(stateUv + vec2(texel.x, 0.0), texel, vec2(1.0) - texel)).r * 2.0 - 1.0;
			float west = texture2D(u_state, clamp(stateUv - vec2(texel.x, 0.0), texel, vec2(1.0) - texel)).r * 2.0 - 1.0;
			float laplace = (north + south + east + west) * 0.25 - center;
			float source = wavefront(p * scale + field * 0.95 + drift * 0.8, t) * u_injection * strength;

			velocity = velocity * u_feedback + laplace * u_diffusion * dt + source * 0.16 * dt - center * 0.018 * dt;
			center = center + velocity * 0.24 * dt;
			center *= 0.998;

			float displaySource = mix(centerState.b, source, 0.18);

			gl_FragColor = vec4(
				clamp(center * 0.5 + 0.5, 0.0, 1.0),
				clamp(velocity * 0.5 + 0.5, 0.0, 1.0),
				clamp(displaySource, 0.0, 1.0),
				1.0
			);
		}
	`;
	const displayFragmentSource = `
		${sharedFragmentHelpers}

		uniform sampler2D u_state;
		uniform vec2 u_resolution;
		uniform float u_time;
		uniform float u_scrollY;
		uniform float u_speed;
		uniform float u_scale;
		uniform float u_strength;
		uniform float u_contrast;
		varying vec2 v_uv;

		void main() {
			vec2 uv = v_uv;
			float aspect = u_resolution.x / max(u_resolution.y, 1.0);
			float t = u_time * u_speed;
			float scale = max(u_scale, 0.001);
			float strength = max(u_strength, 0.0);
			vec2 p = (uv - 0.5) * vec2(aspect, 1.0);
			vec2 field = flowField(p * scale + vec2(t * 0.04, -t * 0.02) + vec2(u_scrollY * 0.000025), t);
			vec2 sampledUv = clamp(uv + field * 0.012 * strength, vec2(0.001), vec2(0.999));
			vec4 state = texture2D(u_state, sampledUv);
			float height = state.r * 2.0 - 1.0;
			float velocity = state.g * 2.0 - 1.0;
			float source = state.b;
			float contrast = max(u_contrast, 0.001);
			float crest = smoothstep(0.035, 0.62, abs(height) * contrast + source * 0.34);
			float brightRidge = smoothstep(0.12, 0.68, height * contrast + source * 0.22);
			float softWake = smoothstep(0.04, 0.48, abs(velocity) * contrast);

			vec3 deepBlue = vec3(0.02, 0.24, 0.52);
			vec3 violet = vec3(0.53, 0.11, 0.54);
			vec3 aqua = vec3(0.08, 0.77, 0.78);
			vec3 rose = vec3(0.78, 0.24, 0.64);
			vec3 color = mix(violet, deepBlue, uv.y);
			color = mix(color, aqua, brightRidge * 0.52 + softWake * 0.14);
			color = mix(color, rose, source * 0.24);

			float alpha = (0.014 + crest * 0.115 + source * 0.045) * strength;
			gl_FragColor = vec4(color, clamp(alpha, 0.0, 0.20));
		}
	`;
	const createShader = (type, source) => {
		const shader = gl.createShader(type);

		gl.shaderSource(shader, source);
		gl.compileShader(shader);

		if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
			console.warn("Gradient shader compile failed", gl.getShaderInfoLog(shader));
			gl.deleteShader(shader);
			return null;
		}

		return shader;
	};
	const createProgram = (fragmentSource) => {
		const vertexShader = createShader(gl.VERTEX_SHADER, vertexSource);
		const fragmentShader = createShader(gl.FRAGMENT_SHADER, fragmentSource);

		if (!vertexShader || !fragmentShader) {
			return null;
		}

		const program = gl.createProgram();

		gl.attachShader(program, vertexShader);
		gl.attachShader(program, fragmentShader);
		gl.linkProgram(program);

		if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
			console.warn("Gradient shader link failed", gl.getProgramInfoLog(program));
			return null;
		}

		return {
			program,
			positionLocation: gl.getAttribLocation(program, "a_position"),
		};
	};
	const simulationProgram = createProgram(simulationFragmentSource);
	const displayProgram = createProgram(displayFragmentSource);

	if (!simulationProgram || !displayProgram) {
		canvas.hidden = true;
		return;
	}

	const positionBuffer = gl.createBuffer();
	const positions = new Float32Array([
		-1, -1,
		3, -1,
		-1, 3,
	]);
	const simulationUniforms = {
		state: gl.getUniformLocation(simulationProgram.program, "u_state"),
		simulationSize: gl.getUniformLocation(simulationProgram.program, "u_simulationSize"),
		viewAspect: gl.getUniformLocation(simulationProgram.program, "u_viewAspect"),
		time: gl.getUniformLocation(simulationProgram.program, "u_time"),
		delta: gl.getUniformLocation(simulationProgram.program, "u_delta"),
		scrollY: gl.getUniformLocation(simulationProgram.program, "u_scrollY"),
		speed: gl.getUniformLocation(simulationProgram.program, "u_speed"),
		scale: gl.getUniformLocation(simulationProgram.program, "u_scale"),
		strength: gl.getUniformLocation(simulationProgram.program, "u_strength"),
		feedback: gl.getUniformLocation(simulationProgram.program, "u_feedback"),
		diffusion: gl.getUniformLocation(simulationProgram.program, "u_diffusion"),
		injection: gl.getUniformLocation(simulationProgram.program, "u_injection"),
	};
	const displayUniforms = {
		state: gl.getUniformLocation(displayProgram.program, "u_state"),
		resolution: gl.getUniformLocation(displayProgram.program, "u_resolution"),
		time: gl.getUniformLocation(displayProgram.program, "u_time"),
		scrollY: gl.getUniformLocation(displayProgram.program, "u_scrollY"),
		speed: gl.getUniformLocation(displayProgram.program, "u_speed"),
		scale: gl.getUniformLocation(displayProgram.program, "u_scale"),
		strength: gl.getUniformLocation(displayProgram.program, "u_strength"),
		contrast: gl.getUniformLocation(displayProgram.program, "u_contrast"),
	};
	let simulation = null;
	let width = 0;
	let height = 0;
	let animationFrame = 0;
	let lastFrameTime = 0;
	const maxDpr = 1.15;
	const referenceViewportAspect = 2560 / 1600;
	const settingsRoot = document.body;

	const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

	const readSettings = () => {
		const style = getComputedStyle(settingsRoot);
		const getNumber = (name, fallback) => {
			const numeric = Number.parseFloat(style.getPropertyValue(name).trim());

			return Number.isFinite(numeric) ? numeric : fallback;
		};

		return {
			resolutionScale: clamp(getNumber("--gradient-shader-resolution-scale", 0.72), 0.25, 1),
			fps: clamp(getNumber("--gradient-shader-fps", 30), 10, 60),
			simulationWidth: Math.round(clamp(getNumber("--gradient-simulation-width", 512), 128, 1024)),
			simulationHeight: Math.round(clamp(getNumber("--gradient-simulation-height", 256), 64, 512)),
			speed: getNumber("--gradient-current-speed", 0.62),
			scale: getNumber("--gradient-current-scale", 1),
			strength: getNumber("--gradient-current-strength", 1),
			feedback: clamp(getNumber("--gradient-wavefront-feedback", 0.986), 0.9, 0.999),
			diffusion: clamp(getNumber("--gradient-wavefront-diffusion", 0.74), 0, 1.5),
			injection: clamp(getNumber("--gradient-wavefront-injection", 0.58), 0, 1.5),
			contrast: clamp(getNumber("--gradient-wavefront-contrast", 1), 0.2, 3),
		};
	};
	let settings = readSettings();

	const useProgram = (programInfo) => {
		gl.useProgram(programInfo.program);
		gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
		gl.enableVertexAttribArray(programInfo.positionLocation);
		gl.vertexAttribPointer(programInfo.positionLocation, 2, gl.FLOAT, false, 0, 0);
	};

	const createStateData = (textureWidth, textureHeight) => {
		const data = new Uint8Array(textureWidth * textureHeight * 4);

		for (let i = 0; i < data.length; i += 4) {
			data[i] = 126 + Math.floor(Math.random() * 5);
			data[i + 1] = 128;
			data[i + 2] = 0;
			data[i + 3] = 255;
		}

		return data;
	};

	const createTexture = (textureWidth, textureHeight, data) => {
		const texture = gl.createTexture();

		gl.bindTexture(gl.TEXTURE_2D, texture);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
		gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, textureWidth, textureHeight, 0, gl.RGBA, gl.UNSIGNED_BYTE, data);

		return texture;
	};

	const createFramebuffer = (texture) => {
		const framebuffer = gl.createFramebuffer();

		gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer);
		gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);

		if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) {
			gl.deleteFramebuffer(framebuffer);
			return null;
		}

		return framebuffer;
	};

	const deleteSimulation = () => {
		if (!simulation) {
			return;
		}

		simulation.textures.forEach((texture) => gl.deleteTexture(texture));
		simulation.framebuffers.forEach((framebuffer) => gl.deleteFramebuffer(framebuffer));
		simulation = null;
	};

	const ensureSimulation = (settings) => {
		if (
			simulation &&
			simulation.width === settings.simulationWidth &&
			simulation.height === settings.simulationHeight
		) {
			return true;
		}

		deleteSimulation();

		const initialState = createStateData(settings.simulationWidth, settings.simulationHeight);
		const textures = [
			createTexture(settings.simulationWidth, settings.simulationHeight, initialState),
			createTexture(settings.simulationWidth, settings.simulationHeight, initialState),
		];
		const framebuffers = textures.map(createFramebuffer);

		if (framebuffers.some((framebuffer) => !framebuffer)) {
			textures.forEach((texture) => gl.deleteTexture(texture));
			framebuffers.forEach((framebuffer) => {
				if (framebuffer) {
					gl.deleteFramebuffer(framebuffer);
				}
			});
			canvas.hidden = true;
			return false;
		}

		simulation = {
			width: settings.simulationWidth,
			height: settings.simulationHeight,
			textures,
			framebuffers,
			readIndex: 0,
			writeIndex: 1,
		};

		return true;
	};

	const resizeCanvas = (settings) => {
		const dpr = Math.min(window.devicePixelRatio || 1, maxDpr) * settings.resolutionScale;
		const nextWidth = Math.max(1, Math.round(window.innerWidth * dpr));
		const nextHeight = Math.max(1, Math.round(window.innerHeight * dpr));

		if (nextWidth === width && nextHeight === height) {
			return;
		}

		width = nextWidth;
		height = nextHeight;
		canvas.width = width;
		canvas.height = height;
	};

	const stepSimulation = (time, delta, scrollY, settings) => {
		useProgram(simulationProgram);
		gl.bindFramebuffer(gl.FRAMEBUFFER, simulation.framebuffers[simulation.writeIndex]);
		gl.viewport(0, 0, simulation.width, simulation.height);
		gl.activeTexture(gl.TEXTURE0);
		gl.bindTexture(gl.TEXTURE_2D, simulation.textures[simulation.readIndex]);
		gl.uniform1i(simulationUniforms.state, 0);
		gl.uniform2f(simulationUniforms.simulationSize, simulation.width, simulation.height);
		const simulationAspect = simulation.width / Math.max(simulation.height, 1);
		const viewportAspect = width / Math.max(height, 1);
		gl.uniform1f(simulationUniforms.viewAspect, viewportAspect * (simulationAspect / referenceViewportAspect));
		gl.uniform1f(simulationUniforms.time, time);
		gl.uniform1f(simulationUniforms.delta, delta);
		gl.uniform1f(simulationUniforms.scrollY, scrollY);
		gl.uniform1f(simulationUniforms.speed, settings.speed);
		gl.uniform1f(simulationUniforms.scale, settings.scale);
		gl.uniform1f(simulationUniforms.strength, settings.strength);
		gl.uniform1f(simulationUniforms.feedback, settings.feedback);
		gl.uniform1f(simulationUniforms.diffusion, settings.diffusion);
		gl.uniform1f(simulationUniforms.injection, settings.injection);
		gl.drawArrays(gl.TRIANGLES, 0, 3);

		const nextRead = simulation.writeIndex;

		simulation.writeIndex = simulation.readIndex;
		simulation.readIndex = nextRead;
	};

	const drawDisplay = (time, scrollY, settings) => {
		useProgram(displayProgram);
		gl.bindFramebuffer(gl.FRAMEBUFFER, null);
		gl.viewport(0, 0, width, height);
		gl.clearColor(0, 0, 0, 0);
		gl.clear(gl.COLOR_BUFFER_BIT);
		gl.activeTexture(gl.TEXTURE0);
		gl.bindTexture(gl.TEXTURE_2D, simulation.textures[simulation.readIndex]);
		gl.uniform1i(displayUniforms.state, 0);
		gl.uniform2f(displayUniforms.resolution, width, height);
		gl.uniform1f(displayUniforms.time, time);
		gl.uniform1f(displayUniforms.scrollY, scrollY);
		gl.uniform1f(displayUniforms.speed, settings.speed);
		gl.uniform1f(displayUniforms.scale, settings.scale);
		gl.uniform1f(displayUniforms.strength, settings.strength);
		gl.uniform1f(displayUniforms.contrast, settings.contrast);
		gl.drawArrays(gl.TRIANGLES, 0, 3);
	};

	const render = (time) => {
		if (document.hidden || reduceMotion.matches) {
			animationFrame = 0;
			return;
		}

		animationFrame = window.requestAnimationFrame(render);

		const frameInterval = 1000 / settings.fps;

		if (lastFrameTime && time - lastFrameTime < frameInterval) {
			return;
		}

		const delta = lastFrameTime ? clamp((time - lastFrameTime) * 0.03, 0.2, 2.0) : 1;

		lastFrameTime = time;

		if (!ensureSimulation(settings)) {
			return;
		}

		const seconds = time * 0.001;
		const scrollY = window.scrollY || window.pageYOffset || 0;

		stepSimulation(seconds, delta, scrollY, settings);
		drawDisplay(seconds, scrollY, settings);
	};

	const start = () => {
		if (!animationFrame && !document.hidden && !reduceMotion.matches) {
			lastFrameTime = 0;
			animationFrame = window.requestAnimationFrame(render);
		}
	};

	const stop = () => {
		if (animationFrame) {
			window.cancelAnimationFrame(animationFrame);
			animationFrame = 0;
		}
	};

	gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);
	gl.disable(gl.DEPTH_TEST);
	gl.disable(gl.STENCIL_TEST);
	resizeCanvas(settings);

	window.addEventListener("resize", () => {
		settings = readSettings();
		resizeCanvas(settings);
	});
	document.addEventListener("visibilitychange", () => {
		if (document.hidden) {
			stop();
			return;
		}

		start();
	});

	if (typeof reduceMotion.addEventListener === "function") {
		reduceMotion.addEventListener("change", () => {
			canvas.hidden = reduceMotion.matches;
			if (reduceMotion.matches) {
				stop();
				return;
			}

			start();
		});
	}

	start();
})();
