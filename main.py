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
