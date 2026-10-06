import pygame
import random
from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.player = Player(width // 2 - 20, height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(width)

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        # Chance PER FRAME that ONE randomly chosen enemy fires (~1 shot / 1.7s at 60 FPS)
        self.enemy_fire_chance = 0.01

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2
                self.player_bullets.append(Bullet(bullet_x, self.player.y, direction=-1))
                self._shoot_cooldown = 15

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    def _resolve_player_bullet_hits(self):
        """Check every player bullet against every alive enemy.

        Nothing is removed while looping. Hits are collected first and
        applied afterwards, so every bullet gets checked every frame.
        Each bullet can destroy at most one enemy, and each enemy can be
        destroyed (and scored) at most once per frame.
        """
        enemies = self.enemy_grid.alive_enemies()
        hit_enemies = set()
        spent_bullets = set()

        for bullet in self.player_bullets:
            bullet_rect = bullet.rect()
            for enemy in enemies:
                if enemy in hit_enemies:
                    continue  # already claimed by another bullet this frame
                if bullet_rect.colliderect(enemy.rect()):
                    hit_enemies.add(enemy)
                    spent_bullets.add(bullet)
                    break  # one bullet destroys only one enemy

        # Apply results after all detection is done
        for enemy in hit_enemies:
            enemy.alive = False
        self.score += len(hit_enemies)
        self.player_bullets = [b for b in self.player_bullets if b not in spent_bullets]

    def update(self):
        if self.game_over:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        self.enemy_grid.move()

        # Roll once per frame, then pick a single enemy to fire.
        alive = self.enemy_grid.alive_enemies()
        if alive and random.random() < self.enemy_fire_chance:
            shooter = random.choice(alive)
            bullet_x = shooter.x + shooter.width // 2
            self.enemy_bullets.append(Bullet(bullet_x, shooter.y + shooter.height, direction=1))

        for bullet in self.player_bullets:
            bullet.move()
        for bullet in self.enemy_bullets:
            bullet.move()

        self.player_bullets = [b for b in self.player_bullets if not b.off_screen(self.height)]
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.off_screen(self.height)]

        self._resolve_player_bullet_hits()

        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                break

        if self.enemy_grid.reached_bottom(self.player.y):
            self.game_over = True

    def render(self, screen):
        pygame.draw.rect(screen, GREEN, self.player.rect())

        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(screen, WHITE, enemy.rect())

        for bullet in self.player_bullets:
            pygame.draw.rect(screen, WHITE, bullet.rect())
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over and not getattr(self, "_game_over_logged", False):
            # NOTE: no proper game-over screen yet - see Task 2 in the README.
            print("Game over! Final score:", self.score)
            self._game_over_logged = True
