"""
Visual effects and particle systems for the Heavy Bag Training game.
"""

import pygame
import math
import random
from typing import Tuple, Optional, List
from ..utils.constants import BLACK, WHITE, RED, GREEN, BLUE, GOLD
from .graphics import graphics_manager


class ParticlePool:
    """
    Object pool for particle reuse to improve performance.

    Instead of creating and destroying particles constantly,
    we maintain a pool of particle objects that can be reused.
    """

    def __init__(self, initial_size: int = 100):
        """Initialize the particle pool with a set of inactive particles."""
        self.pool: List[Particle] = []
        self.active_particles: List[Particle] = []
        self.max_pool_size = 200

        # Pre-allocate particles
        for _ in range(initial_size):
            self.pool.append(Particle(0, 0, 0, 0, WHITE))

    def get_particle(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        size: int = 3,
        lifetime: int = 30,
        gravity: float = 0.3,
        texture_name: Optional[str] = None,
    ) -> Optional['Particle']:
        """
        Get a particle from the pool or create a new one if pool is empty.

        Returns None if max pool size is exceeded (to prevent memory issues).
        """
        # Try to reuse from pool
        if self.pool:
            particle = self.pool.pop()
            particle.reset(x, y, vx, vy, color, size, lifetime, gravity,
                           texture_name)
        else:
            # Create new particle only if we haven't exceeded max size
            if len(self.active_particles) < self.max_pool_size:
                particle = Particle(x, y, vx, vy, color, size, lifetime,
                                    gravity, texture_name)
            else:
                return None  # Too many particles, skip this one

        self.active_particles.append(particle)
        return particle

    def update(self) -> None:
        """Update all active particles and return dead ones to pool."""
        still_alive = []

        for particle in self.active_particles:
            if particle.update():
                still_alive.append(particle)
            else:
                # Return to pool for reuse
                self.pool.append(particle)

        self.active_particles = still_alive

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all active particles."""
        for particle in self.active_particles:
            particle.draw(screen)

    def clear(self) -> None:
        """Return all active particles to the pool."""
        self.pool.extend(self.active_particles)
        self.active_particles.clear()

    def get_active_count(self) -> int:
        """Get the number of active particles."""
        return len(self.active_particles)


class FloatingText:
    """Animated floating text for score displays."""

    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        color: Tuple[int, int, int],
        size: int = 36,
        lifetime: int = 60,
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vy = -2
        self.font = pygame.font.Font(None, size)
        self.scale = 1.0
        self.rotation = 0

    def update(self) -> bool:
        """Update the floating text position and lifetime."""
        self.y += self.vy
        self.vy *= 0.95
        self.lifetime -= 1

        # Add some dynamic scaling and rotation for special texts
        if "AMAZING" in self.text or "PERFECT" in self.text:
            self.scale = 1.0 + math.sin(self.lifetime * 0.3) * 0.2
            self.rotation += 2

        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the floating text with enhanced effects."""
        alpha = self.lifetime / self.max_lifetime

        # Create text surface with outline for better visibility
        text_surface = self.font.render(self.text, True, self.color)
        outline_surface = self.font.render(self.text, True, BLACK)

        # Apply transformations for special effects
        if self.scale != 1.0 or self.rotation != 0:
            scaled_size = (
                int(text_surface.get_width() * self.scale),
                int(text_surface.get_height() * self.scale),
            )
            text_surface = pygame.transform.scale(text_surface, scaled_size)
            outline_surface = pygame.transform.scale(
                outline_surface, scaled_size
            )

            if self.rotation != 0:
                text_surface = pygame.transform.rotate(
                    text_surface, self.rotation
                )
                outline_surface = pygame.transform.rotate(
                    outline_surface, self.rotation
                )

        # Set alpha
        text_surface.set_alpha(int(255 * alpha))
        outline_surface.set_alpha(int(128 * alpha))

        # Draw with outline
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        outline_rect = outline_surface.get_rect(
            center=(self.x + 2, self.y + 2)
        )

        screen.blit(outline_surface, outline_rect)
        screen.blit(text_surface, text_rect)


class Particle:
    """Enhanced particle class with texture support."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        size: int = 3,
        lifetime: int = 30,
        gravity: float = 0.3,
        texture_name: Optional[str] = None,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.texture_name = texture_name
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)

    def reset(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        size: int = 3,
        lifetime: int = 30,
        gravity: float = 0.3,
        texture_name: Optional[str] = None,
    ) -> None:
        """Reset particle properties for reuse from pool."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.texture_name = texture_name
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)

    def update(self) -> bool:
        """Update particle physics and lifetime."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98
        self.lifetime -= 1
        self.rotation += self.rotation_speed
        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle with texture or basic shape."""
        alpha = self.lifetime / self.max_lifetime

        if self.texture_name:
            texture = graphics_manager.get_particle_texture(self.texture_name)
            if texture:
                # Scale texture based on size and alpha
                scale_factor = (self.size / 4) * alpha
                if scale_factor > 0.1:
                    scaled_size = (
                        max(1, int(texture.get_width() * scale_factor)),
                        max(1, int(texture.get_height() * scale_factor)),
                    )
                    scaled_texture = pygame.transform.scale(
                        texture, scaled_size
                    )

                    # Apply rotation if needed
                    if self.rotation != 0:
                        scaled_texture = pygame.transform.rotate(
                            scaled_texture, self.rotation
                        )

                    scaled_texture.set_alpha(int(255 * alpha))
                    rect = scaled_texture.get_rect(
                        center=(int(self.x), int(self.y))
                    )
                    screen.blit(scaled_texture, rect)
                return

        # Fallback to basic shape rendering
        size = int(self.size * alpha)
        if size > 0:
            color = (
                (*self.color[:3], int(255 * alpha))
                if len(self.color) == 3
                else self.color
            )
            pygame.draw.circle(
                screen, color[:3], (int(self.x), int(self.y)), size
            )


class SweatDrop(Particle):
    """Enhanced sweat particle with texture."""

    def __init__(self, x: float, y: float):
        super().__init__(
            x,
            y,
            random.uniform(-1, 1),
            random.uniform(0, 2),
            (100, 150, 255),
            size=2,
            lifetime=40,
            gravity=0.5,
            texture_name="sweat",
        )


# Global particle pool instance (must be after Particle class definition)
particle_pool = ParticlePool()


class HitEffect:
    """Enhanced visual effect for punch impacts."""

    def __init__(self, x: float, y: float, power: float):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 20 + power * 5
        self.lifetime = 15
        self.power = power
        self.burst_surface = None
        self.rings = []

        # Create dynamic burst effect
        color = (
            (255, int(200), int(100)) if power < 5
            else (255, int(150), int(50))
        )
        self.burst_surface = graphics_manager.create_hit_burst_effect(
            x, y, power, color
        )

        # Create expanding rings
        for i in range(3):
            self.rings.append({
                "radius": 5 + i * 3,
                "speed": 2 + i * 0.5,
                "alpha": 255 - i * 60
            })

    def update(self) -> bool:
        """Update the hit effect expansion."""
        self.radius += 3
        self.lifetime -= 1

        # Update rings
        for ring in self.rings:
            ring["radius"] += ring["speed"]
            ring["alpha"] *= 0.95

        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the enhanced hit effect."""
        if self.lifetime <= 0:
            return

        alpha = self.lifetime / 15

        # Draw burst surface if available
        if self.burst_surface:
            burst_copy = self.burst_surface.copy()
            burst_copy.set_alpha(int(255 * alpha))
            rect = burst_copy.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(burst_copy, rect)

        # Draw expanding rings
        for ring in self.rings:
            if ring["alpha"] > 10:
                color = (255, int(200 * alpha), int(100 * alpha))
                pygame.draw.circle(
                    screen,
                    color,
                    (int(self.x), int(self.y)),
                    int(ring["radius"]),
                    max(1, int(3 * alpha)),
                )


class PowerUp:
    """Enhanced collectible power-up items with sprite graphics."""

    def __init__(self, x: float, y: float, type_name: str):
        self.x = x
        self.y = y
        self.type = type_name
        self.lifetime = 300  # 5 seconds at 60 FPS
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.pulse_scale = 1.0
        self.rotation = 0
        self.particle_timer = 0

    def update(self) -> bool:
        """Update power-up animation and lifetime."""
        self.lifetime -= 1
        self.bob_offset = math.sin(self.lifetime * self.bob_speed) * 5
        self.pulse_scale = 1.0 + math.sin(self.lifetime * 0.2) * 0.2
        self.rotation += 2
        self.particle_timer += 1
        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the enhanced power-up with sprite graphics."""
        y_pos = self.y + self.bob_offset

        # Get sprite from graphics manager
        sprite_name = f"powerup_{self.type}"
        sprite = graphics_manager.get_sprite(sprite_name)

        if sprite:
            # Apply transformations
            scaled_sprite = sprite
            if self.pulse_scale != 1.0:
                new_size = (
                    int(sprite.get_width() * self.pulse_scale),
                    int(sprite.get_height() * self.pulse_scale),
                )
                scaled_sprite = pygame.transform.scale(sprite, new_size)

            if self.rotation != 0:
                scaled_sprite = pygame.transform.rotate(
                    scaled_sprite, self.rotation
                )

            # Add blinking effect when about to expire
            if self.lifetime < 60:
                if (self.lifetime // 10) % 2 == 0:
                    scaled_sprite.set_alpha(128)

            rect = scaled_sprite.get_rect(center=(self.x, y_pos))
            screen.blit(scaled_sprite, rect)

            # Add particle trail
            if self.particle_timer % 5 == 0:
                self._create_trail_particle()
        else:
            # Fallback to original drawing method
            colors = {
                "stamina": GREEN, "power": BLUE,
                "multiplier": GOLD, "rage": RED
            }
            color = colors.get(self.type, WHITE)

            pygame.draw.circle(screen, color, (int(self.x), int(y_pos)), 15)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), 15, 2)

            # Draw icon
            font = pygame.font.Font(None, 20)
            icons = {
                "stamina": "S", "power": "P",
                "multiplier": "2X", "rage": "R"
            }
            text = font.render(icons.get(self.type, "?"), True, WHITE)
            text_rect = text.get_rect(center=(self.x, y_pos))
            screen.blit(text, text_rect)

    def _create_trail_particle(self) -> None:
        """Create trailing particles for enhanced visual appeal."""
        colors = {
            "stamina": GREEN, "power": BLUE,
            "multiplier": GOLD, "rage": RED
        }
        color = colors.get(self.type, WHITE)

        # Create small trailing particles
        for _ in range(2):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 1.5)
            px = self.x + math.cos(angle) * random.uniform(10, 20)
            py = (self.y + self.bob_offset +
                  math.sin(angle) * random.uniform(10, 20))

            particle_pool.get_particle(
                px,
                py,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 0.5,
                color,
                size=random.randint(1, 3),
                lifetime=15,
                gravity=0.1,
                texture_name="energy"
            )


class ComboEffect:
    """Special effect for combo achievements."""

    def __init__(self, x: float, y: float, combo_count: int):
        self.x = x
        self.y = y
        self.combo_count = combo_count
        self.lifetime = 60
        self.max_lifetime = 60
        self.effect_surface = graphics_manager.create_combo_effect(combo_count)
        self.scale = 0.1

    def update(self) -> bool:
        """Update combo effect animation."""
        self.lifetime -= 1

        # Scale animation
        progress = 1 - (self.lifetime / self.max_lifetime)
        if progress < 0.5:
            self.scale = progress * 2  # Scale up
        else:
            self.scale = 1.0  # Hold scale

        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the combo effect."""
        if self.lifetime <= 0 or not self.effect_surface:
            return

        alpha = self.lifetime / self.max_lifetime

        # Scale the effect surface
        if self.scale > 0:
            scaled_size = (
                int(self.effect_surface.get_width() * self.scale),
                int(self.effect_surface.get_height() * self.scale),
            )
            scaled_surface = pygame.transform.scale(
                self.effect_surface, scaled_size
            )
            scaled_surface.set_alpha(int(255 * alpha))

            rect = scaled_surface.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(scaled_surface, rect)
