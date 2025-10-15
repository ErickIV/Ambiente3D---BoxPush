"""
graphics/renderer.py
====================
Sistema central de renderização do jogo.
Gerencia toda a pipeline de renderização 3D.
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *
from .materials import Materials, Lighting
from .primitives import Primitives
from .ui import UI


class Renderer:
    """Gerenciador de renderização 3D"""
    
    @staticmethod
    def init_opengl():
        """Inicializa OpenGL com todas as configurações"""
        # Depth test e culling
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Suavização
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        # Blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Sistema de iluminação profissional
        Lighting.setup()
        
        # Material padrão
        Materials.apply_wall_material()
        
        # Cor de fundo (céu)
        glClearColor(*SKY_COLOR)
    
    @staticmethod
    def set_perspective(width, height):
        """
        Configura matriz de projeção perspectiva.
        
        Args:
            width, height: Dimensões da janela
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, width / float(height), NEAR_PLANE, FAR_PLANE)
        glMatrixMode(GL_MODELVIEW)
    
    @staticmethod
    def setup_camera(player):
        """
        Configura câmera em primeira pessoa.
        
        Args:
            player: Objeto Player com posição e rotação
        """
        glLoadIdentity()
        
        # Rotação da câmera
        glRotatef(player.camera_pitch, 1, 0, 0)
        glRotatef(player.camera_yaw, 0, 1, 0)
        
        # Posição da câmera (inverte pois é a câmera que move)
        glTranslatef(-player.x, -PLAYER_EYE_HEIGHT, -player.z)
    
    @staticmethod
    def draw_wall(x, y, z):
        """
        Desenha uma parede.
        
        Args:
            x, y, z: Posição da parede
        """
        Materials.apply_wall_material_varied(x, z)
        glPushMatrix()
        glTranslatef(x, y + 0.0, z)
        glScalef(1.0, 2.0, 1.0)
        Primitives.draw_unit_cube()
        glPopMatrix()
    
    @staticmethod
    def draw_box(x, y, z, status='normal'):
        """
        Desenha uma caixa com cor baseada no status.
        
        Args:
            x, y, z: Posição da caixa
            status: 'normal', 'on_target', 'pushable', 'blocked'
        """
        glPushMatrix()
        glTranslatef(x, y - 0.5, z)
        glScalef(1.0, 1.0, 1.0)
        
        # Define cor baseada no status
        if status == 'on_target':
            color = (1.0, 0.84, 0.0, 1.0)  # Dourado
            shininess = 64.0
        elif status == 'pushable':
            color = (0.2, 0.9, 0.2, 1.0)  # Verde
            shininess = 32.0
        elif status == 'blocked':
            color = (0.9, 0.2, 0.2, 1.0)  # Vermelho
            shininess = 32.0
        else:  # normal
            color = (0.72, 0.48, 0.16, 1.0)  # Marrom
            shininess = 32.0
        
        Materials.apply_box_material(color, shininess)
        Primitives.draw_unit_cube()
        
        # Restaura material padrão
        Materials.apply_wall_material()
        
        glPopMatrix()
    
    @staticmethod
    def get_box_status(box_pos, objectives, player, level):
        """
        Determina status visual de uma caixa.
        CORRIGIDO: Detecção mais precisa e confiável.
        
        Args:
            box_pos: Posição da caixa (tupla (x, y, z))
            objectives: Lista de objetivos
            player: Objeto Player
            level: Objeto Level
            
        Returns:
            str: Status da caixa ('normal', 'on_target', 'pushable', 'blocked')
        """
        # Caixa no objetivo (prioridade máxima)
        if box_pos in objectives:
            return 'on_target'
        
        # Obtém posição do jogador no grid
        from game.physics import Physics
        px = Physics.grid_round(player.x)
        pz = Physics.grid_round(player.z)
        
        # Obtém direção que o jogador está olhando
        dir_x, dir_z = player.get_facing_direction()
        
        # Calcula posição da caixa na frente do jogador
        box_in_front_x = px + dir_x
        box_in_front_z = pz + dir_z
        
        # Verifica se ESTA caixa está na frente do jogador
        # Compara apenas X e Z (ignora Y que é sempre 0)
        if box_pos[0] == box_in_front_x and box_pos[2] == box_in_front_z:
            # Verifica distância para evitar detecção de longe
            dist_x = abs(player.x - box_pos[0])
            dist_z = abs(player.z - box_pos[2])
            max_dist = max(dist_x, dist_z)
            
            # Só considera se estiver próximo (até 2.5 unidades)
            if max_dist <= 2.5:
                # Verifica se pode empurrar nesta direção
                can_push, _, _ = level.can_push_box(player.x, player.z, dir_x, dir_z)
                return 'pushable' if can_push else 'blocked'
        
        return 'normal'
    
    @staticmethod
    def draw_particles(particles, current_time):
        """
        Desenha partículas de efeito.
        
        Args:
            particles: Lista de (x, y, z, start_time)
            current_time: Tempo atual
        """
        glDisable(GL_LIGHTING)
        
        for (x, y, z, start_t) in particles:
            elapsed = current_time - start_t
            
            if elapsed < PARTICLE_LIFETIME:
                # Animação de partículas em espiral
                for i in range(PARTICLE_COUNT):
                    angle = (i / PARTICLE_COUNT) * 2 * math.pi
                    offset = elapsed * 2.0
                    
                    px = x + math.cos(angle + elapsed * 3) * offset
                    pz = z + math.sin(angle + elapsed * 3) * offset
                    py = y - 0.2 + math.sin(elapsed * 5) * 0.3 + 0.3
                    
                    # Cor amarela brilhante
                    Primitives.draw_particle(px, py, pz, 0.1, (1.0, 1.0, 0.0))
        
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def render_game_scene(level, player, current_time):
        """
        Renderiza cena principal do jogo.
        
        Args:
            level: Objeto Level
            player: Objeto Player
            current_time: Tempo atual
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configura câmera
        Renderer.setup_camera(player)
        
        # Desenha chão
        Primitives.draw_floor()
        
        # Desenha paredes
        for (x, y, z) in level.walls:
            Renderer.draw_wall(x, y, z)
        
        # Desenha objetivos
        for (x, y, z) in level.objectives:
            Primitives.draw_target_marker(x, y, z)
        
        # Desenha caixas com sombras
        for (x, y, z) in level.boxes:
            status = Renderer.get_box_status((x, y, z), level.objectives, player, level)
            Renderer.draw_box(x, y, z, status)
            Primitives.draw_shadow(x, y, z)
        
        # Desenha partículas
        Renderer.draw_particles(level.particles, current_time)
        
        # Desenha HUD
        stats = level.get_progress_stats()
        UI.draw_hud(level.current_level_index, stats)
        UI.draw_crosshair()
    
    @staticmethod
    def render_menu_background():
        """Renderiza fundo 3D para o menu"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Câmera fixa para o menu
        glRotatef(-20, 1, 0, 0)
        glRotatef(30, 0, 1, 0)
        glTranslatef(-2, -1, -8)
        
        glEnable(GL_LIGHTING)
        
        # Chão de demonstração
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.7, 0.2)
        glPushMatrix()
        glTranslatef(0, -1, 0)
        glScalef(8, 0.02, 6)
        
        hs = 0.5
        glBegin(GL_QUADS)
        glVertex3f(-hs, hs, -hs)
        glVertex3f(-hs, hs, hs)
        glVertex3f(hs, hs, hs)
        glVertex3f(hs, hs, -hs)
        glEnd()
        glPopMatrix()
        
        glEnable(GL_LIGHTING)
        
        # Parede de demonstração
        Materials.apply_wall_material_varied(1, 1)
        glPushMatrix()
        glTranslatef(2, 0, 0)
        glScalef(1, 2, 1)
        Primitives.draw_unit_cube()
        glPopMatrix()
        
        # Caixa de demonstração
        glPushMatrix()
        glTranslatef(0, -0.5, 0)
        Materials.apply_box_material((0.72, 0.48, 0.16, 1.0), 32.0)
        Primitives.draw_unit_cube()
        glPopMatrix()
        
        # Objetivo de demonstração
        Primitives.draw_target_marker(-1, 0, 0)
    
    @staticmethod
    def render_menu():
        """Renderiza menu principal completo"""
        Renderer.render_menu_background()
        UI.draw_menu()
    
    @staticmethod
    def render_victory(level, player, current_time):
        """
        Renderiza tela de vitória de nível.
        
        Args:
            level: Objeto Level
            player: Objeto Player
            current_time: Tempo atual
        """
        # Renderiza cena de fundo
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        Renderer.setup_camera(player)
        
        Primitives.draw_floor()
        
        for (x, y, z) in level.walls:
            Renderer.draw_wall(x, y, z)
        
        for (x, y, z) in level.objectives:
            Primitives.draw_target_marker(x, y, z)
        
        for (x, y, z) in level.boxes:
            Renderer.draw_box(x, y, z, 'on_target')
            Primitives.draw_shadow(x, y, z)
        
        Renderer.draw_particles(level.particles, current_time)
        
        # Overlay de vitória
        UI.draw_victory_screen(level.move_count)
    
    @staticmethod
    def render_final_victory():
        """Renderiza tela de vitória final"""
        UI.draw_final_victory_screen()
    
    @staticmethod
    def cleanup():
        """Limpa recursos de renderização"""
        Primitives.cleanup()
