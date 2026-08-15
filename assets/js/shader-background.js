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
	const fragmentSource = `
		precision mediump float;

		uniform vec2 u_resolution;
		uniform float u_time;
		uniform float u_scrollY;
		uniform float u_speed;
		uniform float u_scale;
		uniform float u_strength;
		varying vec2 v_uv;

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

		void main() {
			vec2 uv = v_uv;
			float aspect = u_resolution.x / max(u_resolution.y, 1.0);
			vec2 p = (uv - 0.5) * vec2(aspect, 1.0);
			float t = u_time * u_speed;
			float scale = max(u_scale, 0.001);
			float strength = max(u_strength, 0.0);
			vec2 drift = vec2(t * 0.055, -t * 0.024) + vec2(u_scrollY * 0.000035, -u_scrollY * 0.000018);
			vec2 field = flowField(p * scale + drift, t);
			vec2 q = p + field * 0.42 * strength;
			float wovenNoise = fbm(q * 1.7 + field * 0.85 + vec2(t * 0.04));
			float streamA = sin((q.x * 2.8 + q.y * 1.15 + wovenNoise * 1.9 + t * 0.42) * 6.2831853);
			float streamB = sin((-q.x * 1.05 + q.y * 3.3 + fbm(q.yx * 1.9 - t * 0.035) * 1.5 - t * 0.30) * 6.2831853);
			float broadCurrent = smoothstep(0.34, 0.96, streamA * 0.5 + 0.5);
			float crossCurrent = smoothstep(0.56, 1.0, streamB * 0.5 + 0.5);
			float eddy = smoothstep(0.42, 0.82, fbm(q * 5.0 + field * 2.1 + t * 0.08));
			float current = broadCurrent * 0.58 + crossCurrent * 0.32 + eddy * 0.22;

			vec3 deepBlue = vec3(0.02, 0.25, 0.50);
			vec3 violet = vec3(0.52, 0.11, 0.52);
			vec3 aqua = vec3(0.08, 0.76, 0.78);
			vec3 color = mix(violet, deepBlue, uv.y);
			color = mix(color, aqua, broadCurrent * 0.38 + eddy * 0.16);

			float alpha = (0.018 + current * 0.105) * strength;
			gl_FragColor = vec4(color, clamp(alpha, 0.0, 0.18));
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
	const vertexShader = createShader(gl.VERTEX_SHADER, vertexSource);
	const fragmentShader = createShader(gl.FRAGMENT_SHADER, fragmentSource);

	if (!vertexShader || !fragmentShader) {
		canvas.hidden = true;
		return;
	}

	const program = gl.createProgram();

	gl.attachShader(program, vertexShader);
	gl.attachShader(program, fragmentShader);
	gl.linkProgram(program);

	if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		console.warn("Gradient shader link failed", gl.getProgramInfoLog(program));
		canvas.hidden = true;
		return;
	}

	const positionBuffer = gl.createBuffer();
	const positionLocation = gl.getAttribLocation(program, "a_position");
	const resolutionLocation = gl.getUniformLocation(program, "u_resolution");
	const timeLocation = gl.getUniformLocation(program, "u_time");
	const scrollLocation = gl.getUniformLocation(program, "u_scrollY");
	const speedLocation = gl.getUniformLocation(program, "u_speed");
	const scaleLocation = gl.getUniformLocation(program, "u_scale");
	const strengthLocation = gl.getUniformLocation(program, "u_strength");
	const positions = new Float32Array([
		-1, -1,
		3, -1,
		-1, 3,
	]);
	let width = 0;
	let height = 0;
	let animationFrame = 0;
	let lastFrameTime = 0;
	const maxDpr = 1.15;
	const settingsRoot = document.body;

	const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

	const getCssNumber = (name, fallback) => {
		const value = getComputedStyle(settingsRoot).getPropertyValue(name).trim();
		const numeric = Number.parseFloat(value);

		return Number.isFinite(numeric) ? numeric : fallback;
	};

	const resize = () => {
		const resolutionScale = clamp(getCssNumber("--gradient-shader-resolution-scale", 0.72), 0.25, 1);
		const dpr = Math.min(window.devicePixelRatio || 1, maxDpr) * resolutionScale;
		const nextWidth = Math.max(1, Math.round(window.innerWidth * dpr));
		const nextHeight = Math.max(1, Math.round(window.innerHeight * dpr));

		if (nextWidth === width && nextHeight === height) {
			return;
		}

		width = nextWidth;
		height = nextHeight;
		canvas.width = width;
		canvas.height = height;
		gl.viewport(0, 0, width, height);
	};

	const render = (time) => {
		if (document.hidden || reduceMotion.matches) {
			animationFrame = 0;
			return;
		}

		animationFrame = window.requestAnimationFrame(render);

		const fps = clamp(getCssNumber("--gradient-shader-fps", 30), 10, 60);
		const frameInterval = 1000 / fps;

		if (time - lastFrameTime < frameInterval) {
			return;
		}

		lastFrameTime = time;
		resize();
		gl.clearColor(0, 0, 0, 0);
		gl.clear(gl.COLOR_BUFFER_BIT);
		gl.useProgram(program);
		gl.uniform2f(resolutionLocation, width, height);
		gl.uniform1f(timeLocation, time * 0.001);
		gl.uniform1f(scrollLocation, window.scrollY || window.pageYOffset || 0);
		gl.uniform1f(speedLocation, getCssNumber("--gradient-current-speed", 0.62));
		gl.uniform1f(scaleLocation, getCssNumber("--gradient-current-scale", 1));
		gl.uniform1f(strengthLocation, getCssNumber("--gradient-current-strength", 1));
		gl.drawArrays(gl.TRIANGLES, 0, 3);
	};

	const start = () => {
		if (!animationFrame && !document.hidden && !reduceMotion.matches) {
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
	gl.useProgram(program);
	gl.enableVertexAttribArray(positionLocation);
	gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

	window.addEventListener("resize", resize);
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
