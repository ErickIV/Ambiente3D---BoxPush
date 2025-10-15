"""
graphics/primitives.py
======================
Formas geométricas primitivas e otimizadas para renderização.
Inclui cubos, grama 3D com Display Lists, e outras formas básicas.
"""

import random
import math
from OpenGL.GL import *
from config import *


class Primitives:
    """Gerenciador de formas geométricas primitivas"""
    
    # Display Lists para otimização
    _grass_display_list = None
    _cube_display_list = None
    
    @staticmethod
    def draw_unit_cube():
        """Desenha um cubo unitário centrado na origem"""
        hs = 0.5
        glBegin(GL_QUADS)
        
        # Frente
        glNormal3f(0, 0, 1)
        glVertex3f(-hs, -hs, hs)
        glVertex3f(hs, -hs, hs)
        glVertex3f(hs, hs, hs)
        glVertex3f(-hs, hs, hs)
        
        # Trás
        glNormal3f(0, 0, -1)
        glVertex3f(-hs, -hs, -hs)
        glVertex3f(-hs, hs, -hs)
        glVertex3f(hs, hs, -hs)
        glVertex3f(hs, -hs, -hs)
        
        # Esquerda
        glNormal3f(-1, 0, 0)
        glVertex3f(-hs, -hs, -hs)
        glVertex3f(-hs, -hs, hs)
        glVertex3f(-hs, hs, hs)
        glVertex3f(-hs, hs, -hs)
        
        # Direita
        glNormal3f(1, 0, 0)
        glVertex3f(hs, -hs, -hs)
        glVertex3f(hs, hs, -hs)
        glVertex3f(hs, hs, hs)
        glVertex3f(hs, -hs, hs)
        
        # Topo
        glNormal3f(0, 1, 0)
        glVertex3f(-hs, hs, -hs)
        glVertex3f(-hs, hs, hs)
        glVertex3f(hs, hs, hs)
        glVertex3f(hs, hs, -hs)
        
        # Base
        glNormal3f(0, -1, 0)
        glVertex3f(-hs, -hs, -hs)
        glVertex3f(hs, -hs, -hs)
        glVertex3f(hs, -hs, hs)
        glVertex3f(-hs, -hs, hs)
        
        glEnd()
    
    @staticmethod
    def create_grass_display_list():
        """
        Cria Display List otimizada para grama 3D.
        Performance boost de ~90% comparado a renderização por frame.
        """
        if Primitives._grass_display_list is not None:
            return Primitives._grass_display_list
        
        random.seed(42)  # Seed fixo para consistência
        
        # Cria nova display list
        Primitives._grass_display_list = glGenLists(1)
        glNewList(Primitives._grass_display_list, GL_COMPILE)
        
        # Gera toda a geometria da grama
        total_blades = GRASS_AREA * GRASS_AREA * GRASS_DENSITY
        
        for i in range(total_blades):
            # Posição aleatória
            gx = random.uniform(-GRASS_AREA/2, GRASS_AREA/2)
            gz = random.uniform(-GRASS_AREA/2, GRASS_AREA/2)
            
            # Propriedades aleatórias
            height = random.uniform(GRASS_MIN_HEIGHT, GRASS_MAX_HEIGHT)
            rotation = random.uniform(0, 360)
            color_var = random.uniform(-0.3, 0.3)
            
            # Desenha folha diretamente na display list
            glPushMatrix()
            glTranslatef(gx, -1.0, gz)
            glRotatef(rotation, 0, 1, 0)
            
            # Cor verde com variação
            r = 0.1 + color_var * 0.1
            g = 0.6 + color_var * 0.3
            b = 0.1 + color_var * 0.05
            glColor3f(r, g, b)
            
            # Quad vertical (folha)
            glBegin(GL_QUADS)
            w = GRASS_BLADE_WIDTH
            
            # Frente
            glVertex3f(-w, 0, 0)
            glVertex3f(w, 0, 0)
            glVertex3f(w, height, 0)
            glVertex3f(-w, height, 0)
            
            # Trás (visível de ambos os lados)
            glVertex3f(-w, 0, 0)
            glVertex3f(-w, height, 0)
            glVertex3f(w, height, 0)
            glVertex3f(w, 0, 0)
            
            glEnd()
            glPopMatrix()
        
        glEndList()
        return Primitives._grass_display_list
    
    @staticmethod
    def draw_grass():
        """Renderiza grama usando Display List otimizada"""
        if Primitives._grass_display_list is None:
            Primitives.create_grass_display_list()
        
        if Primitives._grass_display_list is not None:
            glCallList(Primitives._grass_display_list)
    
    @staticmethod
    def draw_floor():
        """Desenha chão base com grama"""
        # Chão base verde
        glDisable(GL_LIGHTING)
        glColor3f(0.15, 0.5, 0.15)
        
        glPushMatrix()
        glTranslatef(0.0, -1.0, 0.0)
        glScalef(40.0, 0.02, 40.0)
        
        hs = 0.5
        glBegin(GL_QUADS)
        glVertex3f(-hs, hs, -hs)
        glVertex3f(-hs, hs, hs)
        glVertex3f(hs, hs, hs)
        glVertex3f(hs, hs, -hs)
        glEnd()
        
        glPopMatrix()
        
        # Grama 3D otimizada
        Primitives.draw_grass()
        
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def draw_target_marker(x, y, z):
        """
        Desenha marcador de objetivo (círculo + X).
        
        Args:
            x, y, z: Posição do objetivo
        """
        glPushMatrix()
        glTranslatef(x, y - 0.95, z)
        glDisable(GL_LIGHTING)
        
        # Círculo azul
        glColor3f(0.1, 0.7, 1.0)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius = 0.35
        
        for i in range(0, 361, 12):
            angle = math.radians(i)
            glVertex3f(math.cos(angle) * radius, 0, math.sin(angle) * radius)
        glEnd()
        
        # X vermelho
        glColor3f(1.0, 0.0, 0.0)
        glLineWidth(6.0)
        glBegin(GL_LINES)
        glVertex3f(-0.25, 0.01, -0.25)
        glVertex3f(0.25, 0.01, 0.25)
        glVertex3f(0.25, 0.01, -0.25)
        glVertex3f(-0.25, 0.01, 0.25)
        glEnd()
        glLineWidth(1.0)
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    @staticmethod
    def draw_shadow(x, y, z, size=0.4, alpha=0.3):
        """
        Desenha sombra projetada no chão.
        
        Args:
            x, y, z: Posição da sombra
            size: Tamanho da sombra
            alpha: Transparência (0-1)
        """
        glPushMatrix()
        glTranslatef(x, -0.99, z)
        glDisable(GL_LIGHTING)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, alpha)
        
        glBegin(GL_QUADS)
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, 0, size)
        glVertex3f(-size, 0, size)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    @staticmethod
    def draw_particle(x, y, z, size=0.1, color=(1.0, 1.0, 0.0)):
        """
        Desenha uma partícula de efeito visual.
        
        Args:
            x, y, z: Posição da partícula
            size: Tamanho da partícula
            color: Cor RGB
        """
        glPushMatrix()
        glTranslatef(x, y, z)
        glDisable(GL_LIGHTING)
        
        glColor3f(*color)
        glScalef(size, size, size)
        Primitives.draw_unit_cube()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    @staticmethod
    def cleanup():
        """Libera recursos de Display Lists"""
        if Primitives._grass_display_list is not None:
            glDeleteLists(Primitives._grass_display_list, 1)
            Primitives._grass_display_list = None
        
        if Primitives._cube_display_list is not None:
            glDeleteLists(Primitives._cube_display_list, 1)
            Primitives._cube_display_list = None
