import pygame
import math

class StatusIconDisplay:
    """状态图标显示组件 / Status icon display component"""
    def __init__(self):
        self.icon_size = 24
        self.spacing = 4
        self.animation_timer = 0
        self.flash_duration = 0.5  # 闪烁周期
        self.flash_icons = set()  # 正在闪烁的图标

        # 加载状态图标
        status_sheet = pygame.image.load('@resources/ui/sprites/status.png')
        icons_sheet = pygame.image.load('@resources/ui/icons/Icons.png')
        
        # 从status.png获取基础状态图标
        icon_width = status_sheet.get_width() // 10  # 10列
        self.status_icons = {
            'stun': self._get_icon_from_sheet(status_sheet, 3, 0, icon_width),
            'poison': self._get_icon_from_sheet(status_sheet, 0, 0, icon_width),
        }
        
        # 从Icons.png获取其他状态图标
        icons_cell_size = icons_sheet.get_width() // 12  # 12列
        
        # 获取增益/减益箭头图标
        get_buff_icon = self._get_icon_from_sheet(icons_sheet, 5, 5, icons_cell_size)
        buff_icon = pygame.transform.rotate(get_buff_icon, 90)  # 旋转90度作为增益图标
        debuff_icon = pygame.transform.rotate(buff_icon, 180)  # 旋转180度作为减益图标
        
        # 获取士气图标
        morale_high = self._get_icon_from_sheet(icons_sheet, 8, 1, icons_cell_size)
        morale_low = self._get_icon_from_sheet(icons_sheet, 7, 1, icons_cell_size)
        
        # 添加到图标字典
        self.status_icons.update({
            'buff': buff_icon,
            'debuff': debuff_icon,
            'morale_high': morale_high,
            'morale_low': morale_low
        })  

    def _get_icon_from_sheet(self, sheet, col, row, cell_size):
        """从图标表中获取单个图标 / Get single icon from sprite sheet"""
        icon = sheet.subsurface((col * cell_size, row * cell_size, 
                               cell_size, cell_size))
        return pygame.transform.scale(icon, (self.icon_size, self.icon_size))
        
    def render(self, surface, character, x, y):
        """渲染状态图标 / Render status icons"""
        if not character:
            return
            
        current_x = x
        current_y = y + 60
        
        # 计算闪烁alpha值
        flash_alpha = abs(math.sin(self.animation_timer * math.pi / self.flash_duration)) * 155 + 100
        
        # 渲染士气状态
        if character.morale >= 80:
            self._render_icon_with_flash(surface, 'morale_high', current_x, current_y, 
                                       'morale_high' in self.flash_icons, flash_alpha)
            current_x += self.icon_size + self.spacing
        elif character.morale <= 30:
            self._render_icon_with_flash(surface, 'morale_low', current_x, current_y,
                                       'morale_low' in self.flash_icons, flash_alpha)
            current_x += self.icon_size + self.spacing
            
        # 渲染buff效果
        for buff in character.buffs:
            self._render_icon_with_flash(surface, 'buff', current_x, current_y,
                                       'buff' in self.flash_icons, flash_alpha)
            self._render_duration(surface, buff['duration'], current_x, current_y)
            current_x += self.icon_size + self.spacing
            
        # 渲染debuff效果
        for debuff in character.debuffs:
            icon_name = debuff['type'] if debuff['type'] in ['stun', 'poison'] else 'debuff'
            self._render_icon_with_flash(surface, icon_name, current_x, current_y,
                                       icon_name in self.flash_icons, flash_alpha)
            self._render_duration(surface, debuff['duration'], current_x, current_y)
            current_x += self.icon_size + self.spacing
            
    def _render_icon_with_flash(self, surface, icon_name, x, y, is_flashing, flash_alpha):
        """渲染带闪烁效果的图标 / Render icon with flash effect"""
        if icon_name not in self.status_icons:
            return
            
        icon = self.status_icons[icon_name].copy()
        if is_flashing:
            icon.set_alpha(int(flash_alpha))
        surface.blit(icon, (x, y))

    def update(self, dt):
        """更新动画 / Update animation"""
        self.animation_timer += dt
        if self.animation_timer >= self.flash_duration:
            self.animation_timer = 0

    def _render_duration(self, surface, duration, x, y):
        """渲染状态持续时间 / Render status duration"""
        if duration <= 0:
            return
            
        font = pygame.font.Font(None, 20)
        duration_text = font.render(str(duration), True, (255, 255, 255))
        text_rect = duration_text.get_rect(
            bottomright=(x + self.icon_size, y + self.icon_size)
        )
        surface.blit(duration_text, text_rect)

    def trigger_flash(self, status_type, duration=1.0):
        """触发状态图标闪烁 / Trigger status icon flash"""
        self.flash_icons.add(status_type)
        # 设置定时器在duration秒后停止闪烁
        pygame.time.set_timer(
            pygame.USEREVENT + 1,  # 使用自定义事件
            int(duration * 1000),
            True  # 只触发一次
        )