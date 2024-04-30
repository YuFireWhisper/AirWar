import pygame
import random
import pygame.freetype
import os
from pathlib import Path

# 初始化
pygame.init()

# 定義常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPAWN_RATE = 100  # 每 100 幀生成一個新的敵機
BULLET_SPEED = 10
SCORE_INCREMENT_PER_SECOND = 3
FONT_SIZE = 72

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

os.chdir(r"E:\Program\Dev\Private_code\AirWar")
font = pygame.freetype.Font(r"font\mexcellent.otf", FONT_SIZE)

# 載入資源
assets = {}
assets_dir = "public"
for asset_file in os.listdir(assets_dir):
    asset_path = os.path.join(assets_dir, asset_file)
    assets[asset_file.split(".")[0]] = pygame.image.load(asset_path).convert_alpha()

assets["bullet"] = pygame.image.load(os.path.join(assets_dir, "bullet_player.png")).convert_alpha()
assets["bullet_big"] = pygame.image.load(os.path.join(assets_dir, "bullet_big.png")).convert_alpha()
assets["bullet_middle"] = pygame.image.load(os.path.join(assets_dir, "bullet_middle.png")).convert_alpha()
assets["bullet_small"] = pygame.image.load(os.path.join(assets_dir, "bullet_small.png")).convert_alpha()

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.player = Player(screen, assets["player"], self)
        self.enemies = []
        self.bullets = []
        self.enemy_count = 0
        self.score = 0
        self.enemy_bullets = []
        self.last_score_increment_time = pygame.time.get_ticks()
        self.game = self

    def run(self):
        while True:
            self.handle_events()
            self.update_game_state()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.start_fire()  # 玩家按下空白鍵時開始開火
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.stop_fire()  # 玩家放開空白鍵時停止開火


    def update_game_state(self):
        self.player.move()
        self.player.update()  # 添加這一行
        self.spawn_enemies()
        self.update_enemies()
        self.update_bullets()
        self.update_enemy_bullets()
        self.update_score()

    def draw(self):
        screen.fill((255, 255, 255))
        self.player.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for bullet in self.enemy_bullets:
            bullet.draw(screen)
        self.draw_hud()
        pygame.display.flip()

    def spawn_enemies(self):
        if pygame.time.get_ticks() % ENEMY_SPAWN_RATE == 0:
            enemy_type = random.choice(["boss", "middle_1", "middle_2", "small_1", "small_2"])
            enemy = Enemy(screen, assets[f"enemy_{enemy_type}"], enemy_type, self.game)
            self.enemies.append(enemy)
            self.enemy_count += 1

    def update_enemies(self):
        for enemy in self.enemies[:]:
            if enemy.update():
                self.enemies.remove(enemy)
            else:
                for bullet in self.bullets[:]:
                    if bullet.owner == "player" and bullet.rect.colliderect(enemy.rect):
                        self.bullets.remove(bullet)
                        self.enemies.remove(enemy)
                        self.score += enemy.score

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            if bullet.update():
                self.enemy_bullets.remove(bullet)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet.update():
                self.bullets.remove(bullet)

    def draw_hud(self):
        score_text_surface, _ = font.render(f"Score: {self.score}", (0, 0, 0))
        screen.blit(score_text_surface, (10, 10))

    def update_score(self):
        now = pygame.time.get_ticks()
        if now - self.last_score_increment_time >= 1000:
            self.score += SCORE_INCREMENT_PER_SECOND
            self.last_score_increment_time = now

    def quit(self):
        pygame.quit()
        quit()

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, image, game):
        super().__init__()
        self.screen = screen
        self.original_image = image  # 儲存原始圖像
        rect = self.original_image.get_rect()
        self.image = pygame.transform.scale(self.original_image, (rect.width // 8, rect.height // 8))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.is_firing = False  # 玩家是否正在開火
        self.last_shot_time = 0  # 上一次開火的時間
        self.shoot_delay = 100  # 子彈發射間隔（毫秒）
        self.game = game
        self.health = 100

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
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
            self.stop_fire()  # 如果未開火，則停止開火

        for bullet in self.enemy_bullets:
            if bullet.rect.colliderect(self.player.rect):
                self.player.health -= 10  # 如果敵人的子彈擊中了玩家，則減少玩家的生命值
                self.enemy_bullets.remove(bullet)  # 刪除這個子彈

    def fire_bullet(self):
        bullet_image_scaled = pygame.transform.scale(assets["bullet"], (assets["bullet"].get_width() // 12, assets["bullet"].get_height() // 12))
        bullet = Bullet(self.screen, self.rect.midtop, bullet_image_scaled)
        self.game.bullets.append(bullet)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, image, enemy_type, game):
        super().__init__()
        screen = screen
        self.original_image = image
        rect = self.original_image.get_rect()
        self.image = pygame.transform.scale(self.original_image, (rect.width // 8, rect.height // 8))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = 0
        if enemy_type == "small":
            self.speed = 3
            self.score = 10
            self.bullet_speed = 3  # 小型敵人的子彈速度設為 3
            self.hit = 0.5
            self.health = 1
            self.bump_hit = 10
        elif enemy_type == "medium":
            self.speed = 2
            self.score = 20
            self.bullet_speed = 2  # 中型敵人的子彈速度設為 2
            self.hit = 3
            self.health = 10
            self.bump_hit = 20
        else:
            self.speed = 1
            self.score = 30
            self.bullet_speed = 0.5  # 大型敵人的子彈速度設為 0.5
            self.hit = 5
            self.health = 20
            self.bump_hit = 100
            
        self.last_shot_time = 0
        self.shoot_delay = 1000
        self.game = game
        if enemy_type == "boss":
            self.bullet_image = assets["bullet_big"]
        elif enemy_type.startswith("middle"):
            self.bullet_image = assets["bullet_middle"]
        else:
            self.bullet_image = assets["bullet_small"]

    def update(self):
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.shoot()
            self.last_shot_time = now
        return self.rect.top > SCREEN_HEIGHT

    def shoot(self):
        bullet = Bullet(screen, self.rect.midbottom, pygame.transform.scale(self.bullet_image, (self.bullet_image.get_width() // 12, self.bullet_image.get_height() // 12)), self.bullet_speed)
        bullet.owner = "enemy"
        self.game.enemy_bullets.append(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, screen, pos, image, speed):
        super().__init__()
        screen = screen
        self.image = image
        self.rect = self.image.get_rect(midbottom=pos)
        self.owner = "player"
        self.speed = speed

    def update(self):
        if self.owner == "player":
            self.rect.y -= BULLET_SPEED  # 向上移動
        else:
            self.rect.y += self.speed  # 向下移動
        return self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT  # 如果子彈超出屏幕，返回True以便刪除子彈


    def draw(self, screen):
        screen.blit(self.image, self.rect)

if __name__ == "__main__":
    game = Game()
    game.run()
