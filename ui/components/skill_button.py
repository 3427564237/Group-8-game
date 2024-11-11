import pygame
import math
from pygame import Surface, Rect
from typing import Optional, Dict, Tuple
import random

class SkillButton:
    """技能按钮组件 / Skill button component"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = Rect(x, y, width, height)
        self.skill = None
        self.cooldown = 0
        self.is_active = False
        self.hover = False
        
        # QTE相关属性
        self.qte_active = False
        self.qte_progress = 0
        self.qte_success_zone = (0.4, 0.6)
        self.qte_result = None
        self.qte_key_pressed = False
        
        # Combo相关属性
        self.combo_ready = False
        self.combo_type = None
        self.combo_rating = None
        self.combo_chain = 0
        
        # 动画属性
        self.animation_timer = 0
        self.pulse_scale = 1.0
        self.glow_alpha = 0
        self.particles = []
        
        # 特效颜色
        self.effect_colors = {
            'normal': (255, 255, 255),
            'good': (255, 215, 0),
            'perfect': (255, 100, 100),
            'combo': (100, 200, 255)
        }
        
    def update(self, dt: float, battle_state: dict):
        """更新按钮状态"""
        # 更新冷却时间
        if self.cooldown > 0:
            self.cooldown = max(0, self.cooldown - dt)
            
        # 更新QTE
        if self.qte_active:
            self.qte_progress += dt * 2.0  # QTE进度速度
            if self.qte_progress >= 1.0:
                self._handle_qte_end()
                
        # 更新动画
        self.animation_timer += dt
        self.pulse_scale = 1.0 + math.sin(self.animation_timer * 4) * 0.1
        
        # 更新特效
        if self.combo_ready:
            self.glow_alpha = abs(math.sin(self.animation_timer * 3)) * 255
            
        # 更新粒子
        self._update_particles(dt)
        
    def render(self, surface: Surface, ui_assets: Dict[str, Surface]):
        """渲染按钮"""
        if not self.skill:
            return
            
        # 绘制基础按钮
        self._render_base(surface)
        
        # 绘制技能图标
        if 'skill_icons' in ui_assets:
            self._render_skill_icon(surface, ui_assets['skill_icons'])
            
        # 绘制QTE
        if self.qte_active:
            self._render_qte(surface)
            
        # 绘制Combo提示
        if self.combo_ready:
            self._render_combo_hint(surface)
            
        # 绘制冷却遮罩
        if self.cooldown > 0:
            self._render_cooldown(surface)
            
        # 绘制特效
        self._render_effects(surface)
        
    def _render_base(self, surface: Surface):
        """渲染基础按钮"""
        # 基础颜色
        base_color = (40, 40, 40)
        if self.hover:
            base_color = (60, 60, 60)
        if self.is_active:
            base_color = (80, 80, 80)
            
        # 绘制按钮背景
        pygame.draw.rect(surface, base_color, self.rect)
        
        # 绘制边框
        border_color = self.effect_colors.get(self.combo_rating, (100, 100, 100))
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
    def _render_skill_icon(self, surface, skill_icons):
        """渲染技能图标 / Render skill icon"""
        icon = skill_icons[self.skill.icon_id]
        icon_rect = icon.get_rect(center=self.rect.center)
        
        # 应用呼吸动画
        if self.is_active:
            scale = 1 + self.pulse_animation
            scaled_icon = pygame.transform.scale(
                icon,
                (int(icon.get_width() * scale), 
                 int(icon.get_height() * scale))
            )
            icon_rect = scaled_icon.get_rect(center=self.rect.center)
            surface.blit(scaled_icon, icon_rect)
        else:
            surface.blit(icon, icon_rect)
            
    def _render_cooldown_mask(self, surface):
        """渲染冷却遮罩 / Render cooldown mask"""
        mask = Surface(self.rect.size, pygame.SRCALPHA)
        mask.fill((0, 0, 0, 180))
        surface.blit(mask, self.rect)
        
        # 绘制冷却时间文本
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.cooldown:.1f}", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def _render_qte(self, surface: Surface):
        """渲染QTE界面"""
        bar_height = 5
        bar_rect = Rect(
            self.rect.x,
            self.rect.bottom + 2,
            self.rect.width,
            bar_height
        )
        
        # 绘制背景
        pygame.draw.rect(surface, (40, 40, 40), bar_rect)
        
        # 绘制成功区域
        success_x = bar_rect.x + bar_rect.width * self.qte_success_zone[0]
        success_width = bar_rect.width * (self.qte_success_zone[1] - self.qte_success_zone[0])
        pygame.draw.rect(surface, (50, 200, 50), 
                        (success_x, bar_rect.y, success_width, bar_height))
        
        # 绘制进度指示器
        indicator_x = bar_rect.x + bar_rect.width * self.qte_progress
        pygame.draw.rect(surface, (255, 255, 255),
                        (indicator_x - 1, bar_rect.y - 2, 2, bar_height + 4))
                        
    def _render_effects(self, surface):
        """渲染特效 / Render effects"""
        # 绘制光晕效果
        if self.combo_ready and self.glow_alpha > 0:
            glow = Surface(self.rect.size, pygame.SRCALPHA)
            glow_color = self.effect_colors['combo']
            glow.fill((*glow_color, int(self.glow_alpha)))
            surface.blit(glow, self.rect)
            
        # 绘制粒子
        for particle in self.particles:
            pygame.draw.circle(
                surface,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                int(particle['size'])
            )
            
    def _render_combo_hint(self, surface):
        """渲染连击提示 / Render combo hint"""
        if not self.combo_type:
            return
            
        # 绘制连击类型图标
        icon_size = 24
        icon_pos = (
            self.rect.right - icon_size - 4,
            self.rect.top - icon_size - 4
        )
        pygame.draw.circle(
            surface,
            self.effect_colors['combo'],
            (icon_pos[0] + icon_size//2, icon_pos[1] + icon_size//2),
            icon_size//2
        )
        
        # 绘制连击计数
        if self.combo_chain > 1:
            font = pygame.font.Font(None, 20)
            text = font.render(f"x{self.combo_chain}", True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(icon_pos[0] + icon_size//2, icon_pos[1] + icon_size//2)
            )
            surface.blit(text, text_rect)
            
    def _update_particles(self, dt):
        """更新粒子效果 / Update particle effects"""
        for particle in self.particles[:]:
            # 更新位置
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 200 * dt  # 添加重力效果
            
            # 更新生命周期
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                # 缩小粒子
                particle['size'] *= 0.95
            
    def _handle_qte_end(self):
        """处理QTE结束"""
        self.qte_active = False
        position = self.qte_progress
        
        # 判断成功等级
        if self.qte_success_zone[0] <= position <= self.qte_success_zone[1]:
            center_dist = abs(position - sum(self.qte_success_zone) / 2)
            if center_dist < 0.05:
                self.qte_result = 'perfect'
                self.combo_chain += 2
            else:
                self.qte_result = 'good'
                self.combo_chain += 1
        else:
            self.qte_result = 'normal'
            self.combo_chain = 0
            
        # 创建结果特效
        self._create_result_effect()
        
    def _create_result_effect(self):
        """创建结果特效 / Create result effects"""
        color = self.effect_colors[self.qte_result]
        
        # 添加粒子效果
        for _ in range(10):
            angle = math.radians(random.randint(0, 360))
            speed = random.uniform(50, 100)
            self.particles.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': color,
                'size': random.uniform(2, 4)
            })
        
    def handle_event(self, event):
        """处理输入事件 / Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.qte_active:
                    self._handle_qte_input()
                elif not self.cooldown and self.skill:
                    return True
        return False
        
    def _handle_qte_input(self):
        """处理QTE输入 / Handle QTE input"""
        if not self.qte_active or self.qte_key_pressed:
            return
            
        self.qte_key_pressed = True
        position = self.qte_progress
        
        # 判断QTE成功等级
        if self.qte_success_zone[0] <= position <= self.qte_success_zone[1]:
            center_dist = abs(position - sum(self.qte_success_zone) / 2)
            if center_dist < 0.05:
                self._handle_perfect_qte()
            else:
                self._handle_good_qte()
        else:
            self._handle_miss_qte()
            
    def _handle_perfect_qte(self):
        """处理完美QTE"""
        self.qte_result = 'perfect'
        self.combo_chain += 2
        self._create_result_effect('perfect')
        self._trigger_skill_effect(2.0)  # 双倍伤害
        
    def _handle_good_qte(self):
        """处理优秀QTE"""
        self.qte_result = 'good'
        self.combo_chain += 1
        self._create_result_effect('good')
        self._trigger_skill_effect(1.5)  # 1.5倍伤害
        
    def _handle_miss_qte(self):
        """处理失败QTE"""
        self.qte_result = 'miss'
        self.combo_chain = 0
        self._create_result_effect('normal')
        self._trigger_skill_effect(0.8)  # 伤害降低
        
    def trigger_combo(self, combo_type):
        """触发连击效果 / Trigger combo effect"""
        self.combo_ready = True
        self.combo_type = combo_type
        self._create_combo_particles()
        
    def _create_combo_particles(self):
        """创建连击特效粒子 / Create combo effect particles"""
        color = self.effect_colors['combo']
        
        # 创建环形粒子
        num_particles = 12
        for i in range(num_particles):
            angle = math.radians(i * (360 / num_particles))
            speed = random.uniform(100, 150)
            self.particles.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.5, 1.0),
                'color': color,
                'size': random.uniform(3, 5)
            })