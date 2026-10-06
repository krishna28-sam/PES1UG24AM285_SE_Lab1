import pygame
import random
from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
YELLOW = (255, 220, 60)
GREY = (170, 170, 170)

GAME_OVER_INPUT_DELAY = 30  # frames (~0.5s at 60 FPS) before menu input is accepted

# enemy_speed: pixels per frame for the enemy grid
# fire_chance: chance PER FRAME that ONE randomly chosen enemy fires
DIFFICULTIES = {
    "Easy":   {"enemy_speed": 1.0, "fire_chance": 0.006},
    "Medium": {"enemy_speed": 1.5, "fire_chance": 0.01},
    "Hard":   {"enemy_speed": 2.5, "fire_chance": 0.02},
}

# Menu entries in display order: (label, key hint)
MENU_OPTIONS = [
    ("Easy", "1"),
    ("Medium", "2"),
    ("Hard", "3"),
    ("Exit", "4 / Esc"),
]
EXIT_INDEX = 3

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.prompt_font = pygame.font.SysFont("Arial", 22)

        self.should_quit = False
        self.difficulty = "Medium"
        self.reset()

    def reset(self, difficulty=None):
        """Start a fresh game. Rebuilds all world state.

        If a difficulty name is given it becomes the current difficulty;
        otherwise the current one is reused.
        """
        if difficulty is not None:
            self.difficulty = difficulty
        settings = DIFFICULTIES[self.difficulty]

        self.player = Player(self.width // 2 - 20, self.height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(self.width, speed=settings["enemy_speed"])

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        # Chance PER FRAME that ONE randomly chosen enemy fires
        self.enemy_fire_chance = settings["fire_chance"]

        self.score = 0
        self.game_over = False
        self._game_over_timer = 0
        self._menu_index = 0

    def _trigger_game_over(self):
        if not self.game_over:
            self.game_over = True
            self._game_over_timer = GAME_OVER_INPUT_DELAY
            # Start the menu highlight on the difficulty just played
            self._menu_index = list(DIFFICULTIES).index(self.difficulty)

    def _game_over_ready(self):
        return self.game_over and self._game_over_timer <= 0

    def _activate_menu_option(self, index):
        if index == EXIT_INDEX:
            self.should_quit = True
        else:
            self.reset(MENU_OPTIONS[index][0])

    def _handle_menu_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self._menu_index = (self._menu_index - 1) % len(MENU_OPTIONS)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._menu_index = (self._menu_index + 1) % len(MENU_OPTIONS)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._activate_menu_option(self._menu_index)
        elif key in (pygame.K_1, pygame.K_KP1):
            self._activate_menu_option(0)
        elif key in (pygame.K_2, pygame.K_KP2):
            self._activate_menu_option(1)
        elif key in (pygame.K_3, pygame.K_KP3):
            self._activate_menu_option(2)
        elif key in (pygame.K_4, pygame.K_KP4, pygame.K_ESCAPE):
            self._activate_menu_option(EXIT_INDEX)

    def handle_event(self, event):
        if self.game_over:
            # Ignore gameplay input; menu keys only work once the delay has passed.
            if event.type == pygame.KEYDOWN and self._game_over_ready():
                self._handle_menu_key(event.key)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2
                self.player_bullets.append(Bullet(bullet_x, self.player.y, direction=-1))
                self._shoot_cooldown = 15

    def handle_input(self):
        if self.game_over:
            return

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
            # World is frozen; only count down the input delay.
            if self._game_over_timer > 0:
                self._game_over_timer -= 1
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
                self._trigger_game_over()
                break

        if self.enemy_grid.reached_bottom(self.player.y):
            self._trigger_game_over()

    def _render_game_over(self, screen):
        # Dim the frozen game behind the text
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        cx, cy = self.width // 2, self.height // 2

        title = self.title_font.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(cx, cy - 160)))

        score = self.font.render(f"Final Score: {self.score}", True, WHITE)
        screen.blit(score, score.get_rect(center=(cx, cy - 100)))

        # Menu appears once input is being accepted
        if not self._game_over_ready():
            return

        header = self.prompt_font.render("Play again? Choose a difficulty:", True, WHITE)
        screen.blit(header, header.get_rect(center=(cx, cy - 45)))

        for i, (label, hint) in enumerate(MENU_OPTIONS):
            selected = (i == self._menu_index)
            color = YELLOW if selected else WHITE
            marker = "> " if selected else "   "
            y = cy + i * 45

            text = self.font.render(f"{marker}{label}", True, color)
            screen.blit(text, text.get_rect(midleft=(cx - 130, y)))

            hint_text = self.prompt_font.render(f"[{hint}]", True, GREY)
            screen.blit(hint_text, hint_text.get_rect(midright=(cx + 140, y)))

        help_text = self.prompt_font.render("Up/Down or W/S to move, Enter to select", True, GREY)
        screen.blit(help_text, help_text.get_rect(center=(cx, cy + 4 * 45 + 20)))

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

        if self.game_over:
            self._render_game_over(screen)
