import pygame
import sys
import os
import random
import time

# --- 配置常量 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
FPS = 60

# 颜色定义
BG_COLOR = (30, 144, 255)       # 蓝色背景
SNAKE_BODY = (255, 255, 255)    # 白色蛇身
SNAKE_HEAD = (255, 215, 0)      # 金色蛇头
FOOD_COLOR = (255, 69, 0)       # 橙红食物
BONUS_COLOR = (255, 255, 0)     # 亮黄道具
TEXT_COLOR = (255, 255, 255)    # 纯白文字

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def load_font(size):
    """
    安全加载字体：优先尝试 macOS 中文字体，失败则使用默认字体
    """
    # macOS 常见中文字体路径
    paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc"
    ]
    
    for path in paths:
        if os.path.exists(path):
            try:
                f = pygame.font.Font(path, size)
                # 简单测试是否能渲染
                if f.render("A", True, (0,0,0)).get_width() > 0:
                    return f
            except:
                pass
    
    # 兜底方案：使用系统默认字体
    return pygame.font.SysFont(None, size)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game by Owen")
        self.clock = pygame.time.Clock()
        
        # 加载字体
        self.font_title = load_font(48)
        self.font_text = load_font(24)
        
        self.reset()

    def reset(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.dir = RIGHT
        self.next_dir = RIGHT
        self.food = self._random_pos()
        self.bonus = None
        self.score = 0
        self.state = 'waiting' # waiting, playing, gameover
        
        # 双倍得分逻辑
        self.double_active = False
        self.double_end_time = 0
        self.bonus_timer = 0
        
        self.frame = 0

    def _random_pos(self):
        while True:
            x = random.randint(0, SCREEN_WIDTH // GRID_SIZE - 1)
            y = random.randint(0, SCREEN_HEIGHT // GRID_SIZE - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == 'waiting':
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        self.state = 'playing'
                        if event.key == pygame.K_UP: self.next_dir = UP
                        elif event.key == pygame.K_DOWN: self.next_dir = DOWN
                        elif event.key == pygame.K_LEFT: self.next_dir = LEFT
                        elif event.key == pygame.K_RIGHT: self.next_dir = RIGHT
                
                elif self.state == 'playing':
                    if event.key == pygame.K_UP and self.dir != DOWN: self.next_dir = UP
                    elif event.key == pygame.K_DOWN and self.dir != UP: self.next_dir = DOWN
                    elif event.key == pygame.K_LEFT and self.dir != RIGHT: self.next_dir = LEFT
                    elif event.key == pygame.K_RIGHT and self.dir != LEFT: self.next_dir = RIGHT
                
                elif self.state == 'gameover':
                    if event.key == pygame.K_r:
                        self.reset()
        return True

    def update(self):
        if self.state != 'playing':
            return

        self.frame += 1
        now = time.time()

        # 处理双倍状态
        if self.double_active:
            if now > self.double_end_time:
                self.double_active = False
            else:
                # 生成道具
                if self.bonus is None and random.random() < 0.02:
                    self.bonus = self._random_pos()
                    self.bonus_timer = now + 8
        
        # 道具消失
        if self.bonus and now > self.bonus_timer:
            self.bonus = None

        # 移动
        if self.frame % 8 == 0:
            self.dir = self.next_dir
            hx, hy = self.snake[0]
            dx, dy = self.dir
            new_head = (hx + dx, hy + dy)
            
            # 碰撞检测
            w = SCREEN_WIDTH // GRID_SIZE
            h = SCREEN_HEIGHT // GRID_SIZE
            if new_head[0] < 0 or new_head[0] >= w or new_head[1] < 0 or new_head[1] >= h or new_head in self.snake:
                self.state = 'gameover'
                return
            
            self.snake.insert(0, new_head)
            
            # 吃食物
            if new_head == self.food:
                self.score += 1
                if self.double_active:
                    self.score += 1 # 双倍模式下额外加1分
                self.food = self._random_pos()
                
                # 随机刷道具
                if self.bonus is None and random.random() < 0.1:
                    self.bonus = self._random_pos()
                    self.bonus_timer = now + 8
                    
            elif new_head == self.bonus:
                self.double_active = True
                self.double_end_time = now + 10
                self.bonus = None
                self.score += 5
            else:
                self.snake.pop()

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # 画蛇
        for i, pos in enumerate(self.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            rect = pygame.Rect(pos[0]*GRID_SIZE, pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
        
        # 画食物
        fx, fy = self.food
        pygame.draw.circle(self.screen, FOOD_COLOR, 
                           (fx*GRID_SIZE + GRID_SIZE//2, fy*GRID_SIZE + GRID_SIZE//2), 
                           GRID_SIZE//2 - 2)
        
        # 画道具
        if self.bonus:
            bx, by = self.bonus
            center = (bx*GRID_SIZE + GRID_SIZE//2, by*GRID_SIZE + GRID_SIZE//2)
            pygame.draw.polygon(self.screen, BONUS_COLOR, [
                (center[0], by*GRID_SIZE),
                (bx*GRID_SIZE + GRID_SIZE, center[1]),
                (center[0], by*GRID_SIZE + GRID_SIZE),
                (bx*GRID_SIZE, center[1])
            ])

        # 画右上角信息 (统一白色)
        infos = ["周莉莉", "202615191028", "由千问辅助生成"]
        y_offset = 20
        for text in infos:
            surf = self.font_text.render(text, True, TEXT_COLOR)
            rect = surf.get_rect()
            rect.right = SCREEN_WIDTH - 20
            rect.top = y_offset
            self.screen.blit(surf, rect)
            y_offset += 30

        # 画分数
        score_txt = f"Score: {self.score}"
        if self.double_active:
            remain = int(self.double_end_time - time.time()) + 1
            score_txt += f" | DOUBLE ({remain}s)"
        s_surf = self.font_text.render(score_txt, True, TEXT_COLOR)
        self.screen.blit(s_surf, (10, 10))

        # 状态界面
        if self.state == 'waiting':
            t1 = self.font_title.render("Snake Game by Owen", True, TEXT_COLOR)
            t2 = self.font_text.render("Press Arrow Keys to Start", True, TEXT_COLOR)
            self.screen.blit(t1, t1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
            self.screen.blit(t2, t2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))
        
        elif self.state == 'gameover':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            g1 = self.font_title.render("GAME OVER", True, TEXT_COLOR)
            g2 = self.font_text.render("Press 'R' to Restart", True, TEXT_COLOR)
            self.screen.blit(g1, g1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
            self.screen.blit(g2, g2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
