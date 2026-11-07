import turtle
import random
import math
import colorsys

# 设置屏幕
screen = turtle.Screen()
screen.title("Turtle Fireworks - Fading Lines")
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0, 0)  # 关闭自动刷新，提高性能

#右上角署名
name_pen = turtle.Turtle()
name_pen.hideturtle()
name_pen.speed(0)
name_pen.penup()
name_pen.goto(100,270)
name_pen.color("white")
name_pen.write("周莉莉202615191028,由千问辅助生成", font=("Arial",16,"bold"))

# 隐藏默认乌龟
turtle.hideturtle()

class Particle:
    """代表爆炸后的一条线（粒子）"""
    def __init__(self, x, y, hue):
        self.x = x
        self.y = y
        self.hue = hue  # 使用HSV色相，方便控制亮度
        
        # 随机角度和速度
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(3, 6)
        self.vx = math.cos(math.radians(self.angle)) * self.speed
        self.vy = math.sin(math.radians(self.angle)) * self.speed
        
        self.gravity = 0.08  # 重力
        self.life = 1.0      # 生命值 (1.0 -> 0.0)
        self.decay = random.uniform(0.015, 0.03) # 衰减速度
        
        # 创建专用的turtle对象用于绘制这条线
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.turtle.pensize(2)
        self.turtle.penup()
        self.turtle.goto(self.x, self.y)
        self.turtle.pendown()

    def move_and_draw(self):
        """更新位置并绘制，返回是否还存活"""
        if self.life <= 0:
            return False

        # 计算新位置
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # 应用重力
        self.vy -= self.gravity
        
        # 计算当前颜色 (HSV -> RGB)
        # 随着life减小，value(亮度)降低，模拟消失效果
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, self.life)
        color_tuple = (r, g, b)
        
        # 绘制线条
        self.turtle.pencolor(color_tuple)
        self.turtle.goto(new_x, new_y)
        
        # 更新坐标
        self.x = new_x
        self.y = new_y
        
        # 减少生命
        self.life -= self.decay
        
        return True

    def clear(self):
        """清理资源"""
        self.turtle.clear()
        self.turtle.hideturtle()
        self.turtle.penup() # 重置状态

class Firework:
    """代表整个烟花效果"""
    def __init__(self):
        self.particles = []
        self.exploded = False
        self.rocket = turtle.Turtle()
        self.rocket.hideturtle()
        self.rocket.speed(0)
        self.rocket.pensize(3)
        self.rocket.color("white")
        
        # 火箭初始位置
        self.x = random.randint(-350, 350)
        self.y = -300
        self.target_y = random.randint(50, 250)
        self.rocket_speed = 5
        
        # 预创建火箭轨迹
        self.rocket.penup()
        self.rocket.goto(self.x, self.y)
        self.rocket.pendown()
        
        # 随机选择主色调
        self.hue = random.random()

    def update(self):
        """更新烟花状态"""
        if not self.exploded:
            # 火箭上升阶段
            self.y += self.rocket_speed
            self.rocket.goto(self.x, self.y)
            
            # 到达目标高度，爆炸
            if self.y >= self.target_y:
                self.explode()
                self.rocket.hideturtle() 
        else:
            # 爆炸粒子阶段
            # 过滤掉已经消失的粒子
            alive_particles = []
            for p in self.particles:
                if p.move_and_draw():
                    alive_particles.append(p)
                else:
                    p.clear() # 清理死掉的粒子
            
            self.particles = alive_particles
            
        # 如果还在上升或者还有活着的粒子，则返回True
        return len(self.particles) > 0 or not self.exploded

    def explode(self):
        """生成爆炸粒子"""
        self.exploded = True
        num_particles = random.randint(30, 50) # 粒子数量
        
        for _ in range(num_particles):
            # 稍微变化一点色相，让颜色更丰富
            particle_hue = (self.hue + random.uniform(-0.1, 0.1)) % 1.0
            self.particles.append(Particle(self.x, self.y, particle_hue))

    def clear(self):
        """清理资源"""
        self.rocket.clear()
        self.rocket.hideturtle()
        for p in self.particles:
            p.clear()

# 主程序
fireworks = []
frame_count = 0

def animate():
    global frame_count
    
    # 每隔一定帧数生成一个新烟花
    if frame_count % 30 == 0:
        fireworks.append(Firework())
    
    # 更新所有烟花
    active_fireworks = []
    for fw in fireworks:
        if fw.update():
            active_fireworks.append(fw)
        else:
            fw.clear()
            
    fireworks.clear()
    fireworks.extend(active_fireworks)
    
    screen.update()
    frame_count += 1
    
    # 继续动画
    screen.ontimer(animate, 20) # 每20毫秒刷新一次

# 启动动画
animate()

# 保持窗口打开
screen.mainloop()
