import argparse
import math
import os
import random
import sys
from dataclasses import dataclass, field

import pygame


def find_project_root(start_dir):
    current = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(current, "poker_rules.py")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start_dir)
        current = parent


PROJECT_ROOT = find_project_root(os.path.dirname(__file__))
WIDTH, HEIGHT = 1200, 800
FPS = 60
BG = (17, 19, 24)
BLEND_EDGE_FEATHER = 220
SECONDARY_OFFSET_FOLLOW_SPEED = 4.0
BACKGROUND_DIR = os.path.join(PROJECT_ROOT, "Game Screen", "Background")
BACKGROUND_LAYER_ORDER = (
    "BG_Solid.png",
    "BG_Dots.png",
    "BG_Blend_Blue.png",
    "BG_Blend_Pink.png",
    "BG_Box.png",
    "BG_Box2.png",
    "BG_Box3.png",
    "BG_Box4.png",
    "BG_Button.png",
    "BG_Button2.png",
    "BG_Cap.png",
    "BG_Card1.png",
    "BG_Card2.png",
    "BG_Card3.png",
    "BG_Eye.png",
    "BG_Sticky.png",
    "BG_Pic.png",
)
STAGE_INTENSITIES = {
    pygame.K_1: ("IDLE", 0.2),
    pygame.K_2: ("PREFLOP", 0.4),
    pygame.K_3: ("FLOP", 0.6),
    pygame.K_4: ("TURN", 0.8),
    pygame.K_5: ("RIVER", 1.0),
}


@dataclass
class MotionProfile:
    pattern: str
    velocity: pygame.Vector2
    wave_amplitude: pygame.Vector2
    wave_speed: float
    phase: float
    wrap: bool = True
    y_amplitude: float = 0.0
    y_speed: float = 0.0
    y_direction: float = 1.0


@dataclass
class AnimatedLayer:
    name: str
    image: pygame.Surface
    motion: MotionProfile
    blend_flags: int = 0
    offset: pygame.Vector2 = field(default_factory=pygame.Vector2)
    drift_offset: pygame.Vector2 = field(default_factory=pygame.Vector2)
    secondary_offset: pygame.Vector2 = field(default_factory=pygame.Vector2)


class BackgroundAnimator:
    def __init__(self, background_dir):
        self.background_dir = background_dir
        self.layers = self._load_layers()
        self.elapsed = 0.0
        self.intensity = 0.35
        self.target_intensity = 0.35
        self.paused = False
        self.auto_cycle = False
        self.auto_timer = 0.0
        self.auto_index = 0
        self.trajectory_angle = 0.0
        self.target_trajectory_angle = 0.0

    def reset(self):
        self.elapsed = 0.0
        self.auto_timer = 0.0
        self.trajectory_angle = 0.0
        self.target_trajectory_angle = 0.0
        for layer in self.layers:
            layer.offset.update(0, 0)
            layer.drift_offset.update(0, 0)
            layer.secondary_offset.update(0, 0)

    def set_stage(self, value):
        self.target_intensity = max(0.0, min(1.0, value))
        self._advance_trajectory()

    def update(self, dt):
        if self.paused:
            return

        seconds = dt / 1000
        self.elapsed += seconds
        self.intensity += (self.target_intensity - self.intensity) * min(1.0, seconds * 3.0)
        self.trajectory_angle += (self.target_trajectory_angle - self.trajectory_angle) * min(1.0, seconds * 1.6)

        if self.auto_cycle:
            self.auto_timer += seconds
            if self.auto_timer >= 7.0:
                self.auto_timer = 0.0
                values = list(STAGE_INTENSITIES.values())
                self.auto_index = (self.auto_index + 1) % len(values)
                self.set_stage(values[self.auto_index][1])

        speed_multiplier = 0.35 + self.intensity * 1.65
        drift_multiplier = 0.45 + self.intensity * 1.1
        for layer in self.layers:
            layer.offset = self._layer_offset(layer, seconds, speed_multiplier, drift_multiplier)

    def _layer_offset(self, layer, seconds, speed_multiplier, drift_multiplier):
        motion = layer.motion

        if motion.pattern == "subtle_oscillation":
            radius_multiplier = 0.82 + self.intensity * 0.25
            x = math.sin(self.elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x
            y = math.cos(self.elapsed * motion.wave_speed * 0.73 + motion.phase) * motion.wave_amplitude.y
            return pygame.Vector2(x, y) * radius_multiplier

        if motion.pattern == "box_wave":
            drift = self._trajectory_vector(motion.velocity.x, motion.velocity.y)
            layer.drift_offset += drift * seconds * speed_multiplier
            self._wrap_drift_offset(layer)
            wave_x = math.sin(self.elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x
            gentle_y = math.cos(self.elapsed * motion.wave_speed * 0.85 + motion.phase) * motion.wave_amplitude.y
            wave_speed_multiplier = 0.55 + self.intensity * 1.75
            wave_y = math.sin(self.elapsed * motion.y_speed * wave_speed_multiplier + motion.phase) * motion.y_amplitude
            wave = pygame.Vector2(wave_x, gentle_y) * drift_multiplier
            secondary = self._smooth_secondary_offset(layer, self._perpendicular_to(drift) * wave_y, seconds)
            return layer.drift_offset + wave + secondary

        if motion.pattern == "card_pulse":
            drift = self._trajectory_vector(motion.velocity.x, motion.velocity.y)
            layer.drift_offset += drift * seconds * (speed_multiplier * 1.28)
            self._wrap_drift_offset(layer)
            wave_x = math.sin(self.elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x * drift_multiplier
            pulse_speed_multiplier = 0.55 + self.intensity * 1.75
            pulse_y = motion.y_direction * self._ease_pulse_y(self.elapsed * motion.y_speed * pulse_speed_multiplier, motion.y_amplitude)
            secondary = self._smooth_secondary_offset(layer, self._perpendicular_to(drift) * pulse_y, seconds)
            return layer.drift_offset + pygame.Vector2(wave_x, 0) + secondary

        drift = self._trajectory_vector(motion.velocity.x, motion.velocity.y)
        layer.drift_offset += drift * seconds * speed_multiplier
        self._wrap_drift_offset(layer)
        wave_x = math.sin(self.elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x
        wave_y = math.cos(self.elapsed * motion.wave_speed * 0.85 + motion.phase) * motion.wave_amplitude.y
        return layer.drift_offset + pygame.Vector2(wave_x, wave_y) * drift_multiplier

    def _advance_trajectory(self):
        self.trajectory_angle = self._normalized_angle(self.trajectory_angle)
        self.target_trajectory_angle = self.trajectory_angle + math.pi / 2

    def _normalized_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def _wrap_drift_offset(self, layer):
        if not layer.motion.wrap:
            return
        image_w, image_h = layer.image.get_size()
        layer.drift_offset.update(
            self._wrapped_offset(layer.drift_offset.x, image_w),
            self._wrapped_offset(layer.drift_offset.y, image_h),
        )

    def _smooth_secondary_offset(self, layer, target, seconds):
        follow = min(1.0, seconds * SECONDARY_OFFSET_FOLLOW_SPEED)
        layer.secondary_offset += (target - layer.secondary_offset) * follow
        return layer.secondary_offset

    def _trajectory_vector(self, x, y):
        return pygame.Vector2(x, y).rotate_rad(self.trajectory_angle)

    def _perpendicular_to(self, vector):
        if vector.length_squared() == 0:
            return pygame.Vector2(0, 1)
        direction = vector.normalize()
        return pygame.Vector2(-direction.y, direction.x)

    def _ease_pulse_y(self, cycle_position, amplitude):
        position = cycle_position % 1.0
        if position < 0.5:
            eased = ease_out_cubic(position * 2)
            return amplitude - amplitude * 2 * eased

        eased = ease_out_cubic((position - 0.5) * 2)
        return -amplitude + amplitude * 2 * eased

    def draw(self, surface):
        surface.fill(BG)
        screen_rect = surface.get_rect()
        for layer in self.layers:
            if layer.motion.wrap:
                self._draw_wrapped_layer(surface, screen_rect, layer)
            else:
                rect = layer.image.get_rect(center=(WIDTH // 2 + round(layer.offset.x), HEIGHT // 2 + round(layer.offset.y)))
                surface.blit(layer.image, rect, special_flags=layer.blend_flags)

    def _draw_wrapped_layer(self, surface, screen_rect, layer):
        image_w, image_h = layer.image.get_size()
        offset_x = self._wrapped_offset(layer.offset.x, image_w)
        offset_y = self._wrapped_offset(layer.offset.y, image_h)

        for tile_y in (-1, 0, 1):
            for tile_x in (-1, 0, 1):
                center = (
                    WIDTH // 2 + round(offset_x + tile_x * image_w),
                    HEIGHT // 2 + round(offset_y + tile_y * image_h),
                )
                rect = layer.image.get_rect(center=center)
                if rect.colliderect(screen_rect):
                    surface.blit(layer.image, rect, special_flags=layer.blend_flags)

    def _wrapped_offset(self, value, span):
        return ((value + span / 2) % span) - span / 2

    def _load_layers(self):
        if not os.path.isdir(self.background_dir):
            raise SystemExit(f"Missing background folder: {self.background_dir}")

        rng = random.Random(17)
        layers = []
        for index, filename in enumerate(BACKGROUND_LAYER_ORDER):
            path = os.path.join(self.background_dir, filename)
            if not os.path.isfile(path):
                continue

            image = pygame.image.load(path).convert_alpha()
            is_blend_layer = "blend" in filename.lower()
            blend_flags = 0
            if is_blend_layer:
                image = prepare_additive_light_layer(image)
                blend_flags = pygame.BLEND_RGB_ADD

            name = os.path.splitext(filename)[0]
            motion = self._motion_for_layer(name, index, rng)
            layers.append(AnimatedLayer(name, image, motion, blend_flags))

        return layers

    def _motion_for_layer(self, name, index, rng):
        if name == "BG_Solid":
            return MotionProfile("subtle_oscillation", pygame.Vector2(), pygame.Vector2(4, 3), 0.08, 0.0, wrap=False)

        if name in {"BG_Dots", "BG_Blend_Blue", "BG_Blend_Pink"}:
            return MotionProfile(
                "subtle_oscillation",
                pygame.Vector2(),
                pygame.Vector2(rng.uniform(8.0, 20.0), rng.uniform(6.0, 16.0)),
                rng.uniform(0.035, 0.075),
                rng.uniform(0, math.tau),
                wrap=False,
            )

        direction = -1 if index % 2 else 1
        speed = 5 + index * 1.8
        velocity = pygame.Vector2(
            direction * speed,
            rng.uniform(-4.0, 4.0) + math.sin(index) * 3,
        )
        wave_amplitude = pygame.Vector2(
            rng.uniform(8.0, 28.0),
            rng.uniform(6.0, 22.0),
        )
        wave_speed = rng.uniform(0.16, 0.42)
        phase = rng.uniform(0, math.tau)

        if "Box" in name:
            return MotionProfile(
                "box_wave",
                velocity,
                wave_amplitude,
                wave_speed,
                phase,
                wrap=True,
                y_amplitude=rng.uniform(22.0, 46.0),
                y_speed=rng.uniform(0.36, 0.72),
            )

        if "Card" in name:
            direction = 1 if index % 2 else -1
            velocity = pygame.Vector2(
                direction * (speed * 1.35),
                rng.uniform(-2.0, 2.0),
            )
            y_direction = -1 if name in {"BG_Card1", "BG_Card3"} else 1
            return MotionProfile(
                "card_pulse",
                velocity,
                pygame.Vector2(rng.uniform(5.0, 13.0), 0),
                rng.uniform(0.14, 0.24),
                rng.uniform(0, math.tau),
                wrap=True,
                y_amplitude=42.0,
                y_speed=0.12,
                y_direction=y_direction,
            )

        if name in {"BG_Dots", "BG_Pic"}:
            velocity *= 0.45
            wave_amplitude *= 0.7

        return MotionProfile("drift", velocity, wave_amplitude, wave_speed, phase, wrap=True)


def prepare_additive_light_layer(surface):
    prepared = pygame.Surface(surface.get_size())
    width, height = surface.get_size()
    feather = max(1, min(BLEND_EDGE_FEATHER, width // 2, height // 2))

    surface.lock()
    prepared.lock()
    try:
        for y in range(height):
            y_edge = min(y, height - 1 - y)
            y_factor = min(1.0, y_edge / feather)
            for x in range(width):
                red, green, blue, alpha = surface.get_at((x, y))
                if alpha == 0:
                    prepared.set_at((x, y), (0, 0, 0))
                    continue

                x_edge = min(x, width - 1 - x)
                edge_factor = min(y_factor, min(1.0, x_edge / feather))
                intensity = (alpha / 255) * edge_factor
                prepared.set_at(
                    (x, y),
                    (
                        round(red * intensity),
                        round(green * intensity),
                        round(blue * intensity),
                    ),
                )
    finally:
        prepared.unlock()
        surface.unlock()

    return prepared.convert()


def ease_out_cubic(value):
    return 1 - (1 - value) ** 3


def run_preview(output_path, frames):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    animator = BackgroundAnimator(BACKGROUND_DIR)
    for _ in range(frames):
        animator.update(1000 / FPS)
    animator.draw(screen)
    pygame.image.save(screen, output_path)
    print(f"saved={output_path} layers={len(animator.layers)}")


def run_window():
    pygame.display.set_caption("Background Animation Test")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    animator = BackgroundAnimator(BACKGROUND_DIR)
    running = True

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    animator.paused = not animator.paused
                elif event.key == pygame.K_a:
                    animator.auto_cycle = not animator.auto_cycle
                elif event.key == pygame.K_r:
                    animator.reset()
                elif event.key in STAGE_INTENSITIES:
                    animator.auto_cycle = False
                    pygame.display.set_caption(f"Background Animation Test - {STAGE_INTENSITIES[event.key][0]}")
                    animator.set_stage(STAGE_INTENSITIES[event.key][1])

        animator.update(dt)
        animator.draw(screen)
        pygame.display.flip()

    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Preview procedural background wrapping and drift.")
    parser.add_argument("--preview", help="Save one rendered frame instead of opening a window.")
    parser.add_argument("--frames", type=int, default=180, help="Number of frames to simulate before saving a preview.")
    args = parser.parse_args()

    pygame.init()
    try:
        if args.preview:
            run_preview(args.preview, args.frames)
        else:
            run_window()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
