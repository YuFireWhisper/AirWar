import pygame
import random
import pygame.freetype
import os
import json

os.chdir(r"E:\Program\Dev\Private_code\AirWar")


def save_game_score(game_name, score):
    try:
        with open("game_info.json", "r") as f:
            game_info = json.load(f)
    except FileNotFoundError:
        game_info = {}

    for game in game_info.values():
        if game["game_name"] == game_name:
            if "high_score" not in game:
                game["high_score"] = score
            else:
                game["high_score"] = max(game["high_score"], score)
            break
    else:
        game_info[game_name] = {"high_score": score}

    with open("game_info.json", "w") as f:
        json.dump(game_info, f)

class Game:
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    FPS = 60
    PLAYER_SPEED = 5
    ENEMY_SPAWN_RATE = 100
    BULLET_SPEED = 10
    SCORE_INCREMENT_PER_SECOND = 3
    FONT_SIZE = 72

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.font = pygame.freetype.Font(os.path.join("font", "mexcellent.otf"), self.FONT_SIZE)
        self.assets = self.load_assets()
        self.player = Player(self)
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.last_score_increment_time = pygame.time.get_ticks()
        self.game_over = False

    def load_assets(self):
        assets = {}
        assets_dir = "public"
        for asset_file in os.listdir(assets_dir):
            asset_path = os.path.join(assets_dir, asset_file)
            assets[asset_file.split(".")[0]] = pygame.image.load(asset_path).convert_alpha()

        assets["bullet"] = pygame.image.load(os.path.join(assets_dir, "bullet_player.png")).convert_alpha()
        assets["bullet_big"] = pygame.image.load(os.path.join(assets_dir, "bullet_big.png")).convert_alpha()
        assets["bullet_middle"] = pygame.image.load(os.path.join(assets_dir, "bullet_middle.png")).convert_alpha()
        assets["bullet_small"] = pygame.image.load(os.path.join(assets_dir, "bullet_small.png")).convert_alpha()
        assets["game_over"] = pygame.image.load(os.path.join(assets_dir, "game_over.png")).convert_alpha()
        assets["again"] = pygame.image.load(os.path.join(assets_dir, "again.png")).convert_alpha()

        for enemy_type in ["boss", "middle_1", "middle_2", "small_1", "small_2"]:
            assets[enemy_type] = pygame.image.load(os.path.join(assets_dir, f"enemy_{enemy_type}.png")).convert_alpha()

        return assets

    def run(self):
        while True:
            self.handle_events()
            if not self.game_over:
                self.update_game_state()
            self.draw()
            self.clock.tick(self.FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.start_fire()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.stop_fire()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                # 檢查是否點擊了重新遊戲按鈕
                if self.again_rect.collidepoint(event.pos):
                    self.restart_game()

    def update_game_state(self):
        self.player.update()
        self.player.move()
        self.spawn_enemies()
        self.update_enemies()
        self.update_bullets()
        self.update_enemy_bullets()
        self.update_score()
        if self.player.health <= 0:
            self.game_over = True

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
        if self.game_over:
            self.draw_game_over()
        else:
            self.draw_hud()
        pygame.display.flip()

    def spawn_enemies(self):
        if pygame.time.get_ticks() % self.ENEMY_SPAWN_RATE == 0:
            enemy_type = random.choice(["boss", "middle_1", "middle_2", "small_1", "small_2"])
            enemy = Enemy(self.screen, self.assets[enemy_type], enemy_type, self)
            self.enemies.append(enemy)

    def update_enemies(self):
        for enemy in self.enemies[:]:
            if enemy.update():
                self.enemies.remove(enemy)
            else:
                for bullet in self.bullets[:]:
                    if bullet.owner == "player" and bullet.rect.colliderect(enemy.rect):
                        self.bullets.remove(bullet)
                        enemy.health -= bullet.hit
                        if enemy.health <= 0:
                            for bullet in enemy.bullets:
                                if bullet in self.enemy_bullets:
                                    self.enemy_bullets.remove(bullet)
                            self.enemies.remove(enemy)
                            self.score += enemy.score
                            
                if self.player.rect.colliderect(enemy.rect):
                    self.player.health -= 5
                    self.enemies.remove(enemy)
                    if self.player.health <= 0:
                        self.game_over = True

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            if bullet.update():
                self.enemy_bullets.remove(bullet)
            elif bullet.rect.colliderect(self.player.rect):
                self.player.health -= bullet.hit
                self.enemy_bullets.remove(bullet)
                if self.player.health <= 0:
                    self.game_over = True

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet.update():
                self.bullets.remove(bullet)
            elif bullet.rect.bottom < 0:
                self.bullets.remove(bullet)

    def draw_hud(self):
        score_text_surface, _ = self.font.render(f"Score: {self.score}", (0, 0, 0))
        self.screen.blit(score_text_surface, (10, 10))

        health_text_surface, _ = self.font.render(f"Health: {self.player.health}", (0, 0, 0))
        self.screen.blit(health_text_surface, (10, 100))

    def draw_game_over(self):
        self.screen.fill((255, 255, 255))
        game_over_image = pygame.transform.scale(self.assets["game_over"], (self.assets["game_over"].get_width() // 4, self.assets["game_over"].get_height() // 4))
        game_over_rect = game_over_image.get_rect()
        game_over_rect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 100)  # 調整位置
        self.screen.blit(game_over_image, game_over_rect)

        again_image = pygame.transform.scale(self.assets["again"], (self.assets["again"].get_width() // 4, self.assets["again"].get_height() // 4))
        again_rect = again_image.get_rect()
        again_rect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 100)  # 調整位置
        self.again_rect = self.screen.blit(again_image, again_rect)
        save_game_score("AirWar", self.score)

    def update_score(self):
        now = pygame.time.get_ticks()
        if now - self.last_score_increment_time >= 1000:
            self.score += self.SCORE_INCREMENT_PER_SECOND
            self.last_score_increment_time = now

    def restart_game(self):
        self.player.health = 10
        self.score = 0
        self.enemies.clear()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.game_over = False

    def quit(self):
        pygame.quit()
        quit()

class Player:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.image = game.assets["player"]
        rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (rect.width // 8, rect.height // 8))
        self.rect = self.image.get_rect()
        self.rect.centerx = game.SCREEN_WIDTH // 2
        self.rect.bottom = game.SCREEN_HEIGHT - 10
        self.is_firing = False
        self.last_shot_time = 0
        self.shoot_delay = 100
        self.health = 10

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.game.PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.game.PLAYER_SPEED
        self.rect.clamp_ip(self.screen.get_rect())

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def start_fire(self):
        self.is_firing = True

    def stop_fire(self):
        self.is_firing = False

    def update(self):
        if self.is_firing:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time > self.shoot_delay:
                self.last_shot_time = now
                self.fire_bullet()
        else:
            self.stop_fire()

    def fire_bullet(self):
        bullet_image_scaled = pygame.transform.scale(self.game.assets["bullet"], (self.game.assets["bullet"].get_width() // 12, self.game.assets["bullet"].get_height() // 12))
        bullet = Bullet(self.game, self.rect.midtop, bullet_image_scaled, self.game.BULLET_SPEED, hit=10, screen=self.screen)
        self.game.bullets.append(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, image, enemy_type, game):
        super().__init__()
        self.screen = screen
        self.original_image = image
        rect = self.original_image.get_rect()
        self.image = pygame.transform.scale(self.original_image, (rect.width // 8, rect.height // 8))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, game.SCREEN_WIDTH - self.rect.width)
        self.rect.y = 0
        self.bullets = []
        self.game = game
        self.last_shot_time = 0
        self.shoot_delay = 1000
        self.set_enemy_properties(enemy_type)

    def set_enemy_properties(self, enemy_type):
        if enemy_type == "small_1" or enemy_type == "small_2":
            self.speed = 3
            self.score = 10
            self.bullet_speed = 10
            self.hit = 1
            self.health = 1
            self.bullet_image = self.game.assets["bullet_small"]  # 小型敵人的子彈圖像

        elif enemy_type == "middle_1" or enemy_type == "middle_2":
            self.speed = 2
            self.score = 20
            self.bullet_speed = 4
            self.hit = 3
            self.health = 10
            self.bullet_image = self.game.assets["bullet_middle"]  # 中型敵人的子彈圖像
        else:
            self.speed = 0.5
            self.score = 30
            self.bullet_speed = 2
            self.hit = 5
            self.health = 20
            self.bullet_image = self.game.assets["bullet_big"]  # 大型敵人的子彈圖像

    def update(self):
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.shoot()
            self.last_shot_time = now
        return self.rect.top > self.game.SCREEN_HEIGHT

    def shoot(self):
        bullet = Bullet(self.screen, self.rect.midbottom, pygame.transform.scale(self.bullet_image, (self.bullet_image.get_width() // 12, self.bullet_image.get_height() // 12)), self.bullet_speed, hit=self.hit, screen=self.screen)
        bullet.owner = "enemy"
        self.game.enemy_bullets.append(bullet)
        self.bullets.append(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Bullet:
    def __init__(self, game, pos, image, speed, hit, screen):
        self.game = game
        self.screen = screen
        self.image = image
        self.rect = self.image.get_rect(midbottom=pos)
        self.owner = "player"
        self.speed = speed
        self.hit = hit

    def update(self):
        if self.owner == "player":
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        return self.rect.bottom < 0 or self.rect.top > self.screen.get_height()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

if __name__ == "__main__":
    game = Game()
    game.run()
