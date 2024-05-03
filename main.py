"""空中大戰遊戲"""

import pygame
import random
import pygame.freetype
import os
import json


# def save_game_score(game_name, score):
#     try:
#         with open("game_info.json", "r") as f:
#             game_info = json.load(f)
#     except FileNotFoundError:
#         game_info = {}

#     for game in game_info.values():
#         if game["game_name"] == game_name:
#             if "high_score" not in game:
#                 game["high_score"] = score
#             else:
#                 game["high_score"] = max(game["high_score"], score)
#             break
#     else:
#         game_info[game_name] = {"high_score": score}

#     with open("game_info.json", "w") as f:
#         json.dump(game_info, f)

# 常用常數
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPAWN_RATE = 100
BULLET_SPEED = 10
SCORE_INCREMENT_PER_SECOND = 3
FONT_SIZE = 72

# 常用RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.freetype.Font(os.path.join("font", "mexcellent.otf"), FONT_SIZE)

all_sprites = pygame.sprite.Group()


class Game:
    """遊戲主控的class"""

    def __init__(self):
        self.load_assets()
        self.space_ship = Player(self)
        all_sprites.add(self.space_ship)
        self.enemies = set()
        self.bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.last_score_increment_time = pygame.time.get_ticks()
        self.game_over = False

    def load_assets(self):
        """加載遊戲物件"""
        self.assets = {}
        # assets_dir = "public"
        for asset_file in os.listdir("public"):
            asset_path = os.path.join("public", asset_file)
            self.assets[asset_file.split(".")[0]] = pygame.image.load(asset_path).convert_alpha()

        # self.assets["bullet_player"] = pygame.image.load(os.path.join("public", "bullet_player.png")).convert_alpha()
        # self.assets["bullet_big"] = pygame.image.load(os.path.join("public", "bullet_big.png")).convert_alpha()
        # self.assets["bullet_middle"] = pygame.image.load(os.path.join("public", "bullet_middle.png")).convert_alpha()
        # self.assets["bullet_small"] = pygame.image.load(os.path.join("public", "bullet_small.png")).convert_alpha()
        # self.assets["game_over"] = pygame.image.load(os.path.join("public", "game_over.png")).convert_alpha()
        # self.assets["again"] = pygame.image.load(os.path.join("public", "again.png")).convert_alpha()

        # for enemy_type in ["boss", "middle_1", "middle_2", "small_1", "small_2"]:
        #     self.assets[enemy_type] = pygame.image.load(os.path.join("public", f"enemy_{enemy_type}.png")).convert_alpha()

    def run(self):
        while True:
            self.handle_events()
            if not self.game_over:
                self.update_game_state()
            self.draw()
            clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.space_ship.start_fire()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_ship.stop_fire()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                # 檢查是否點擊了重新遊戲按鈕
                if self.again_rect.collidepoint(event.pos):
                    self.restart_game()

    def update_game_state(self):
        self.space_ship.update_fire()
        self.space_ship.update()
        self.spawn_enemies()
        self.update_enemies()
        self.update_bullets()
        self.update_enemy_bullets()
        self.update_score()
        if self.space_ship.health <= 0:
            self.game_over = True

    def draw(self):
        screen.fill(WHITE)
        all_sprites.draw(screen)
        # self.space_ship.draw()
        # for enemy in self.enemies:
        #     enemy.draw(self.screen)
        # for bullet in self.bullets:
        #     bullet.draw(self.screen)
        # for bullet in self.enemy_bullets:
        #     bullet.draw(self.screen)
        if self.game_over:
            self.draw_game_over()
        else:
            self.draw_hud()
        pygame.display.update()

    def spawn_enemies(self):
        if pygame.time.get_ticks() % 100 == 0:
            enemy_type = random.choice(["boss", "middle_1", "middle_2", "small_1", "small_2"])
            enemy = Enemy(self.assets[enemy_type], enemy_type, self)
            self.enemies.add(enemy)

    def update_enemies(self):
        for enemy in self.enemies[:]:
            # if enemy.update():
            #     self.enemies.remove(enemy)
            # else:
            for bullet in self.bullets[:]:
                if not (bullet.owner == "player" and bullet.rect.colliderect(enemy.rect)):
                    continue
                self.bullets.remove(bullet)
                # enemy.health -= bullet.hit
                if enemy.health > 0:
                    continue
                # for bullet in enemy.bullets:
                #     if bullet in self.enemy_bullets:
                #         self.enemy_bullets.remove(bullet)
                for bullet in self.enemy_bullets:
                    if bullet in enemy.bullets:
                        self.enemy_bullets.remove(bullet)
                self.enemies.remove(enemy)
                self.score += enemy.score

            if self.space_ship.rect.colliderect(enemy.rect):
                self.space_ship.health -= 5
                self.enemies.remove(enemy)
                if self.space_ship.health <= 0:
                    self.game_over = True

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            if bullet.update():
                self.enemy_bullets.remove(bullet)
            elif bullet.rect.colliderect(self.space_ship.rect):
                self.space_ship.health -= bullet.hit
                self.enemy_bullets.remove(bullet)
                if self.space_ship.health <= 0:
                    self.game_over = True

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet.update():
                self.bullets.remove(bullet)
            elif bullet.rect.bottom < 0:
                self.bullets.remove(bullet)

    def draw_hud(self):
        score_text_surface, _ = font.render(f"Score: {self.score}", (0, 0, 0))
        screen.blit(score_text_surface, (10, 10))

        health_text_surface, _ = font.render(f"Health: {self.space_ship.health}", (0, 0, 0))
        screen.blit(health_text_surface, (10, 100))

    def draw_game_over(self):
        screen.fill(WHITE)
        game_over_image = pygame.transform.scale(self.assets["game_over"], (self.assets["game_over"].get_width() // 4, self.assets["game_over"].get_height() // 4))
        game_over_rect = game_over_image.get_rect()
        game_over_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)  # 調整位置
        screen.blit(game_over_image, game_over_rect)

        again_image = pygame.transform.scale(self.assets["again"], (self.assets["again"].get_width() // 4, self.assets["again"].get_height() // 4))
        again_rect = again_image.get_rect()
        again_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)  # 調整位置
        self.again_rect = screen.blit(again_image, again_rect)
        # save_game_score("AirWar", self.score)

    def update_score(self):
        now = pygame.time.get_ticks()
        if now - self.last_score_increment_time >= 1000:
            self.score += SCORE_INCREMENT_PER_SECOND
            self.last_score_increment_time = now

    def restart_game(self):
        self.space_ship.health = 10
        self.score = 0
        self.enemies.clear()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.game_over = False
        # save_game_score("AirWar", self.score)

    def quit(self):
        pygame.quit()
        quit()


class Player(pygame.sprite.Sprite):
    """玩家用飛船"""

    def __init__(self, playground_info: Game):
        super.__init__()
        self.image = pygame.image.load("public/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 4, self.image.get_height() // 4))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_HEIGHT // 2 - self.rect.width // 2
        self.rect.centery = SCREEN_WIDTH - self.rect.height
        self.playground_info = playground_info
        self.shoot_delay = 100
        self.speed = 10  # 移動速度
        self.health = 50

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())  # 這行能夠處理邊界問題

    def start_fire(self):
        self.is_firing = True

    def stop_fire(self):
        self.is_firing = False

    def update_fire(self):
        if self.is_firing:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time > self.shoot_delay:
                self.last_shot_time = now
                self.fire_bullet()
        else:
            self.stop_fire()

    def fire_bullet(self):
        bullet_image_scaled = pygame.transform.scale(self.playground_info.assets["bullet"], (self.playground_info.assets["bullet"].get_width() // 12, self.playground_info.assets["bullet"].get_height() // 12))
        bullet = Bullet(self.playground_info, self.rect.midtop, bullet_image_scaled, BULLET_SPEED, hit=10)
        all_sprites.add(bullet)
        self.playground_info.bullets.append(bullet)


# class bullet_player(pygame.sprite.Sprite):
#     """玩家用子彈"""

#     def __init__(self, playground_info: Game) -> None:
#         super.__init__()
#         self.speed = 4
#         self.hit = 1
#         self.image = pygame.image.load("public/bullet_player.png")
#         self.rect = self.image.get_rect()
#         self.rect.centerx = playground_info.space_ship.rect.x
#         self.rect.centery = playground_info.space_ship.rect.top
#         self.playground_info = playground_info

#     def update(self) -> None:
#         """更新玩家用子彈"""
#         self.rect.y += self.speed
#         if self.rect.bottom < 0:
#             self.kill()
#         if pygame.sprite.spritecollide(self, self.playground_info.enemies, False):
#             for enemie in self.playground_info.enemies:
#                 enemie.health -= self.hit
#             self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, enemy_type, playground_info: Game):
        super().__init__()
        self.original_image = image
        rect = self.original_image.get_rect()
        self.image = pygame.transform.scale(self.original_image, (rect.width // 8, rect.height // 8))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = 0
        self.bullets = []
        self.playground_info = playground_info
        self.last_shot_time = 0
        self.shoot_delay = 1000
        self.set_enemy_properties(enemy_type)
        self.shots_remaining = self.get_random_shots_remaining()

    def set_enemy_properties(self, enemy_type):
        if enemy_type == "small_1" or enemy_type == "small_2":
            self.speed = 3
            self.score = 10
            self.bullet_speed = 10
            self.hit = 1
            self.health = 1
            self.bullet_image = self.playground_info.assets["bullet_small"]  # 小型敵人的子彈圖像

        elif enemy_type == "middle_1" or enemy_type == "middle_2":
            self.speed = 2
            self.score = 20
            self.bullet_speed = 4
            self.hit = 3
            self.health = 10
            self.bullet_image = self.playground_info.assets["bullet_middle"]  # 中型敵人的子彈圖像
        else:
            self.speed = 0.5
            self.score = 30
            self.bullet_speed = 2
            self.hit = 5
            self.health = 20
            self.bullet_image = self.playground_info.assets["bullet_big"]  # 大型敵人的子彈圖像

    def update(self):
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.shoot()
            self.last_shot_time = now
        return self.rect.top > SCREEN_HEIGHT

    def shoot(self):
        if self.shots_remaining > 0:
            bullet = Bullet(self.playground_info, self.rect.midbottom, pygame.transform.scale(self.bullet_image, (self.bullet_image.get_width() // 12, self.bullet_image.get_height() // 12)), self.bullet_speed, hit=self.hit, screen=self.screen)
            bullet.owner = "enemy"
            self.playground_info.enemy_bullets.append(bullet)
            self.bullets.append(bullet)
            self.shots_remaining -= 1
        else:
            self.shots_remaining = self.get_random_shots_remaining()
            self.shoot_delay = random.randint(1500, 3000)

    def draw(self):
        screen.blit(self.image, self.rect)

    def get_random_shots_remaining(self):
        if self.speed == 3:
            return random.choice([3, 4, 5])
        elif self.speed == 2:
            return random.choice([1, 2, 3])
        else:
            return random.choice([1, 2])


class Bullet(pygame.sprite.Sprite):
    """子彈"""

    def __init__(self, playground_info: Game, pos: int, image, speed: int, hit: int):
        super.__init__()
        self.playground_info = playground_info
        self.image = image
        self.rect = image.get_rect(midbottom=pos)
        self.owner = "player"
        self.speed = speed
        self.hit = hit

    def update(self) -> None:
        if self.owner == "player":
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
            return
        if self.rect.top > screen.get_height():
            self.kill()
            return
        if self.owner == "enemy":
            if pygame.sprite.spritecollide(self, [self.playground_info.space_ship], False):
                self.playground_info.space_ship.health -= self.hit
                self.kill()
            return
        temp_maybe_touch = pygame.sprite.spritecollide(self, self.playground_info.enemies, False)
        if not temp_maybe_touch:
            return
        temp_maybe_touch[0].health -= self.hit

    def draw(self):
        screen.blit(self.image, self.rect)


if __name__ == "__main__":
    game = Game()
    game.run()
