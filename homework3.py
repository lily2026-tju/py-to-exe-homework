import pygame
import sys
import os

# 初始化 Pygame
pygame.init()

# --- 常量定义 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 50, 220)
GREEN = (50, 200, 50)

# 游戏参数
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 8
BRICK_ROWS = 5
BRICK_COLS = 9
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 10
BRICK_OFFSET_TOP = 60
BRICK_OFFSET_LEFT = 35

def load_mac_chinese_font(size):
    """
    强制加载 macOS 系统内置中文字体文件，解决方格问题
    """
    # macOS 常见中文字体文件路径列表
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",             # 现代 macOS (苹方)
        "/Library/Fonts/PingFang.ttc",                    # 用户安装或旧版
        "/System/Library/Fonts/STHeiti Medium.ttc",       # 旧版 macOS (华文黑体)
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",     # 冬青黑体
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                # index=0 通常对应字体中的 Regular 或 Medium 字重
                font = pygame.font.Font(path, size)
                return font
            except:
                continue
    
    # 如果都没找到，尝试使用 SysFont 的最后机会
    try:
        return pygame.font.SysFont("Arial Unicode MS", size)
    except:
        return pygame.font.Font(None, size)

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 7

    def move(self, direction):
        if direction == 'left' and self.x > 0:
            self.x -= self.speed
        elif direction == 'right' and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect, border_radius=5)

class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.reset()

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = 4
        self.dy = -4

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def bounce_x(self):
        self.dx = -self.dx

    def bounce_y(self):
        self.dy = -self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Brick:
    def __init__(self, x, y, row_idx):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.status = 1
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        colors = [GREEN, (0, 180, 0), (200, 200, 0), (200, 100, 0), RED]
        self.color = colors[row_idx % len(colors)]

    def draw(self, screen):
        if self.status == 1:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=3)

def create_bricks():
    bricks = []
    for c in range(BRICK_COLS):
        for r in range(BRICK_ROWS):
            brick_x = (c * (BRICK_WIDTH + BRICK_PADDING)) + BRICK_OFFSET_LEFT
            brick_y = (r * (BRICK_HEIGHT + BRICK_PADDING)) + BRICK_OFFSET_TOP
            bricks.append(Brick(brick_x, brick_y, r))
    return bricks

def draw_custom_info(screen, font):
    """
    在右上角隔行显示指定文字
    """
    info_lines = [
        "周莉莉",
        "202615191028",
        "由千问辅助生成"
    ]
    
    margin_right = 20
    start_y = 20
    line_height = 30 # 行高稍微大一点，防止重叠
    
    screen_width = screen.get_width()

    for i, text in enumerate(info_lines):
        # 隔行变色
        if i % 2 == 0:
            color = (50, 50, 50) # 深灰
        else:
            color = (200, 50, 50) # 红色
            
        # 渲染文字
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # 右对齐定位
        text_rect.right = screen_width - margin_right
        text_rect.top = start_y + (i * line_height)
        
        screen.blit(text_surface, text_rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout - Mac Chinese Fix")
    clock = pygame.time.Clock()
    
    # 【关键步骤】加载 macOS 专用中文字体
    print("正在加载 macOS 中文字体...")
    font_info = load_mac_chinese_font(22)
    font_small = load_mac_chinese_font(16)
    
    # 验证字体是否加载成功（可选调试）
    test_surf = font_info.render("测试", True, (0,0,0))
    if test_surf.get_width() > 10:
        print("中文字体加载成功！")
    else:
        print("警告：中文字体可能仍然显示为方格，请检查系统字体路径。")

    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    
    score = 0
    lives = 3
    game_state = "playing"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game_state != "playing":
                        ball.reset()
                        paddle.x = (SCREEN_WIDTH - paddle.width) // 2
                        paddle.rect.x = paddle.x
                        bricks = create_bricks()
                        score = 0
                        lives = 3
                        game_state = "playing"

        if game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                paddle.move('left')
            if keys[pygame.K_RIGHT]:
                paddle.move('right')

            ball.move()

            # 边界碰撞
            if ball.x + ball.radius >= SCREEN_WIDTH or ball.x - ball.radius <= 0:
                ball.bounce_x()
            if ball.y - ball.radius <= 0:
                ball.bounce_y()
            
            # 掉落
            if ball.y + ball.radius >= SCREEN_HEIGHT:
                lives -= 1
                if lives <= 0:
                    game_state = "gameover"
                else:
                    ball.reset()
                    ball.dy = -abs(ball.dy)

            # 挡板碰撞
            if ball.get_rect().colliderect(paddle.rect):
                if ball.dy > 0:
                    ball.bounce_y()
                    hit_pos = (ball.x - paddle.x) / paddle.width
                    ball.dx = 6 * (hit_pos - 0.5)

            # 砖块碰撞
            for brick in bricks:
                if brick.status == 1:
                    if ball.get_rect().colliderect(brick.rect):
                        ball.bounce_y()
                        brick.status = 0
                        score += 10
                        break

            if all(b.status == 0 for b in bricks):
                game_state = "win"

        # 绘制背景
        screen.fill(WHITE)
        
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
            
        # 左上角分数
        score_text = font_small.render(f"Score: {score}", True, BLACK)
        lives_text = font_small.render(f"Lives: {lives}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))

        # 【核心功能】绘制右上角定制中文信息
        draw_custom_info(screen, font_info)

        # 游戏状态覆盖层
        if game_state == "gameover":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            text_go = font_info.render("GAME OVER", True, WHITE)
            text_restart = font_small.render("Press 'R' to Restart", True, WHITE)
            
            rect_go = text_go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            rect_re = text_restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            
            screen.blit(text_go, rect_go)
            screen.blit(text_restart, rect_re)

        elif game_state == "win":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((255,255,255))
            screen.blit(overlay, (0,0))
            
            text_win = font_info.render("YOU WIN!", True, GREEN)
            text_restart = font_small.render("Press 'R' to Play Again", True, BLACK)
            
            rect_win = text_win.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            rect_re = text_restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            
            screen.blit(text_win, rect_win)
            screen.blit(text_restart, rect_re)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
