import time
import os
import pygame


# 初始化
pygame.init()

# 初始化聲音
pygame.mixer.init()

# 初始化元素容器
all_sprites = pygame.sprite.Group()

# 設定幀數
FPS = 60

# 設置視窗大小
WIDTH, HEIGHT = 600, 800

# 設定常用RGB
BLACK = (0, 0, 0)

# 設定字體
font = pygame.font.SysFont("Arial", 108)

# 視窗
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# 設定視窗名稱
pygame.display.set_caption("Airwar")

# 引入背景音效
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))

# 無限重複播放
pygame.mixer.music.play(-1)

class Player(pygame.sprite.Sprite):
    """玩家"""

    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("img/player.png"), (512, 512))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT - 250

    def update(self) -> None:
        """更新畫面"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 20
        if keys[pygame.K_RIGHT]:
            self.rect.x += 20
        self.rect.clamp_ip(screen.get_rect())

airwar = Player()

all_sprites.add(airwar)

clock = pygame.time.Clock()
running = True
t = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    clock.tick(FPS)
    screen.fill(BLACK)
    all_sprites.update()
    # screen.blit(board, (0, 0))
    all_sprites.draw(screen)
