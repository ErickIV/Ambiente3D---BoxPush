"""
graphics/materials.py
=====================
Definições de materiais e sistema de iluminação profissional.
Implementa materiais PBR-like para paredes, chão, caixas e objetivos.
"""

from OpenGL.GL import *


class Materials:
    """Gerenciador de materiais do jogo"""
    
    @staticmethod
    def apply_wall_material_varied(x, z):
        """
        Material de parede com variações procedurais baseadas na posição.
        Simula concreto com irregularidades naturais.
        
        Args:
            x (float): Posição X da parede
            z (float): Posição Z da parede
        """
        variation = (abs(x * 0.1) + abs(z * 0.1)) % 0.3 - 0.15
        base_color = 0.6 + variation * 0.1
        
        # Cores com variação sutil
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, 
                    (0.15, 0.15, 0.16 + variation * 0.02, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, 
                    (base_color, base_color, base_color + variation * 0.02, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, 
                    (0.1, 0.1, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 
                   4.0 + variation * 2.0)
    
    @staticmethod
    def apply_wall_material():
        """Material padrão para paredes (concreto)"""
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.15, 0.15, 0.16, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.62, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 4.0)
    
    @staticmethod
    def apply_floor_material():
        """Material para o chão (grama realista)"""
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.4, 0.1, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.2, 0.8, 0.2, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.3, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 16.0)
    
    @staticmethod
    def apply_box_material(color, shininess=32.0):
        """
        Material para caixas com cor personalizável.
        
        Args:
            color (tuple): Cor RGBA da caixa
            shininess (float): Brilho especular
        """
        # Ambient mais escuro para melhor contraste
        ambient = [c * 0.5 for c in color[:3]] + [1.0]
        
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)


class Lighting:
    """Sistema de iluminação profissional com 3 luzes"""
    
    @staticmethod
    def setup():
        """
        Configura sistema de iluminação de 3 pontos profissional:
        - Key Light (Luz Principal): Sol
        - Fill Light (Luz de Preenchimento): Ilumina sombras
        - Rim Light (Luz de Contorno): Adiciona profundidade
        """
        # Habilita iluminação
        glEnable(GL_LIGHTING)
        
        # Configuração global de iluminação
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.25, 0.25, 0.30, 1.0))
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        
        # === LUZ PRINCIPAL (Sol) - LIGHT0 ===
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (15.0, 20.0, 10.0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.22, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.85, 1.0))  # Amarelo suave
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.8, 0.8, 0.7, 1.0))
        
        # Atenuação realista
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.5)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.01)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.001)
        
        # === LUZ DE PREENCHIMENTO - LIGHT1 ===
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (-10.0, 12.0, -8.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.15, 0.15, 0.18, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.45, 0.55, 1.0))  # Azul suave
        glLightfv(GL_LIGHT1, GL_SPECULAR, (0.2, 0.2, 0.3, 1.0))
        
        # === LUZ DE CONTORNO - LIGHT2 ===
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, (0.0, 8.0, -15.0, 1.0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (0.1, 0.1, 0.12, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.3, 0.35, 0.4, 1.0))
        glLightfv(GL_LIGHT2, GL_SPECULAR, (0.4, 0.4, 0.5, 1.0))
