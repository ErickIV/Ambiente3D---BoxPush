"""
game/player.py
==============
Gerenciamento do jogador, câmera e controles.

CÂMERA PRIMEIRA PESSOA:
----------------------
- Pitch (rotação vertical): Limitado a ±89° para evitar gimbal lock
- Yaw (rotação horizontal): Livre 360°
- Sensibilidade configurável via config.py

SISTEMA DE MOVIMENTO:
--------------------
1. Captura input WASD + direção da câmera
2. Calcula vetores forward e right baseados no yaw
3. Normaliza movimento diagonal
4. Aplica velocidade (normal ou corrida)
5. Física suave através de Physics.smooth_move()
6. Sistema de sons de passos com intervalo temporal

CARACTERÍSTICAS:
---------------
- Movimento relativo à direção da câmera
- Suporte a corrida (multiplicador de velocidade)
- Detecção de colisões com paredes e caixas
- Sons de passos adaptativos (mais rápidos ao correr)
- Teleporte de emergência para spawn
"""

import math
from config import *
from .physics import Physics
from utils.sound import get_sound_manager


class Player:
    """Classe que representa o jogador e sua câmera"""
    
    def __init__(self):
        """Inicializa jogador na posição padrão"""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        
        # Rotação da câmera
        self.camera_pitch = 0.0  # Rotação vertical (X)
        self.camera_yaw = 0.0    # Rotação horizontal (Y)
        
        # Estado
        self.is_running = False
        
        # Controle de som de passos
        self.last_step_time = 0.0
        self.step_interval = 0.35  # Intervalo entre sons de passo (segundos)
    
    def set_position(self, x, y, z):
        """
        Define posição do jogador.
        
        Args:
            x, y, z: Nova posição
        """
        self.x = x
        self.y = y
        self.z = z
    
    def get_position(self):
        """Retorna posição atual"""
        return (self.x, self.y, self.z)
    
    def get_grid_position(self):
        """Retorna posição arredondada para o grid"""
        return (
            Physics.grid_round(self.x),
            Physics.grid_round(self.y),
            Physics.grid_round(self.z)
        )
    
    def update_camera_rotation(self, dx, dy):
        """
        Atualiza rotação da câmera baseado no movimento do mouse.
        
        Args:
            dx: Movimento horizontal do mouse
            dy: Movimento vertical do mouse
        """
        self.camera_yaw += dx * MOUSE_SENSITIVITY
        self.camera_pitch -= dy * MOUSE_SENSITIVITY
        
        # Limita pitch para evitar gimbal lock
        self.camera_pitch = max(-89.0, min(89.0, self.camera_pitch))
    
    def get_camera_vectors(self):
        """
        Calcula vetores de direção da câmera.
        
        Returns:
            tuple: (forward_x, forward_z, right_x, right_z)
        """
        yaw = math.radians(self.camera_yaw)
        
        forward_x = math.sin(yaw)
        forward_z = -math.cos(yaw)
        right_x = math.cos(yaw)
        right_z = math.sin(yaw)
        
        return forward_x, forward_z, right_x, right_z
    
    def get_facing_direction(self):
        """
        Retorna direção cardinal que o jogador está olhando.
        
        Returns:
            tuple: (dir_x, dir_z) em valores -1, 0 ou 1
        """
        return Physics.get_cardinal_direction(self.camera_yaw)
    
    def move(self, input_forward, input_strafe, dt, walls, boxes, run=False, current_time=0.0):
        """
        Move o jogador baseado em input.
        
        Args:
            input_forward: Input frente/trás (-1 a 1)
            input_strafe: Input esquerda/direita (-1 a 1)
            dt: Delta time
            walls: Lista de paredes
            boxes: Lista de caixas
            run: Se está correndo
            current_time: Tempo atual para som de passos
            
        Returns:
            bool: True se moveu
        """
        # Calcula vetores de movimento
        forward_x, forward_z, right_x, right_z = self.get_camera_vectors()
        
        # Combina inputs
        move_x = forward_x * input_forward + right_x * input_strafe
        move_z = forward_z * input_forward + right_z * input_strafe
        
        # Normaliza movimento diagonal
        norm = math.hypot(move_x, move_z)
        if norm > 0.0:
            move_x /= norm
            move_z /= norm
        else:
            return False
        
        # Aplica velocidade
        speed = MOVE_SPEED
        if run:
            speed *= RUN_MULTIPLIER
            step_multiplier = 0.7  # Passos mais rápidos ao correr
        else:
            step_multiplier = 1.0
        
        move_x *= speed
        move_z *= speed
        
        # Move com física
        new_x, new_z, moved = Physics.smooth_move(
            self.x, self.z,
            self.x + move_x * dt, self.z + move_z * dt,
            walls, boxes, dt, speed
        )
        
        self.x = new_x
        self.z = new_z
        
        # Som de passos se moveu
        if moved and current_time - self.last_step_time >= self.step_interval * step_multiplier:
            get_sound_manager().play('step')
            self.last_step_time = current_time
        
        return moved
    
    def reset_camera(self):
        """Reseta rotação da câmera"""
        self.camera_pitch = 0.0
        self.camera_yaw = 0.0
