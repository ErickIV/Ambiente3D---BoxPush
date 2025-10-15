"""
game/level.py
=============
Gerenciamento de níveis do jogo.
Carrega, valida e manipula dados dos níveis.

RESPONSABILIDADES:
-----------------
1. Carregamento de dados de níveis (levels_data.py)
2. Validação de spawn points e geometria
3. Lógica de empurrar caixas (push mechanics)
4. Detecção de colisões caixa-parede e caixa-caixa
5. Verificação de condições de vitória
6. Sistema de partículas para feedback visual
7. Estatísticas (movimentos, caixas no objetivo)

MECÂNICA DE EMPURRAR:
--------------------
- Verifica posição do jogador e direção olhada
- Calcula posição da caixa na frente
- Valida se destino está livre (sem paredes/caixas)
- Verifica limites do mundo
- Atualiza estado e dispara efeitos sonoros/visuais

SISTEMA DE GRID:
---------------
- Posições discretas (inteiros) para lógica
- Posições contínuas (floats) para renderização
- Conversão através de Physics.grid_round()
"""

from .levels_data import LEVELS, get_level, get_level_count
from .physics import Physics
from utils.sound import get_sound_manager
from graphics.clouds import CloudSystem


class Level:
    """Gerenciador de um nível do jogo"""
    
    def __init__(self):
        """Inicializa gerenciador de nível vazio"""
        self.current_level_index = 0
        self.walls = []
        self.boxes = []
        self.objectives = []
        self.spawn_position = (0.0, 0.0, 0.0)
        self.move_count = 0
        self.particles = []  # Lista de (x, y, z, start_time)
        self.clouds = None  # Sistema de nuvens
        
        # Dados do nível atual
        self.level_name = ""
        self.level_difficulty = ""
    
    def load_level(self, level_index):
        """
        Carrega um nível específico.
        
        Args:
            level_index (int): Índice do nível (0-based)
            
        Returns:
            bool: True se carregou com sucesso
        """
        level_data = get_level(level_index)
        
        if level_data is None:
            return False
        
        self.current_level_index = level_index
        
        # Copia dados do nível
        self.walls = level_data['paredes'][:]
        self.boxes = level_data['caixas'][:]
        self.objectives = level_data['objetivos'][:]
        self.spawn_position = level_data['spawn']
        
        # Validação: Verifica se spawn não está dentro de parede
        spawn_grid = (
            int(round(self.spawn_position[0])),
            int(round(self.spawn_position[1])),
            int(round(self.spawn_position[2]))
        )
        if spawn_grid in self.walls:
            # Ajusta spawn automaticamente movendo 2 unidades para frente
            self.spawn_position = (
                self.spawn_position[0],
                self.spawn_position[1],
                self.spawn_position[2] + 2.0
            )
        
        # Metadados
        self.level_name = level_data.get('name', f'Nível {level_index + 1}')
        self.level_difficulty = level_data.get('difficulty', 'Normal')
        
        # Reseta estado
        self.move_count = 0
        self.particles = []
        
        # Inicializa sistema de nuvens (distribuídas em 360°)
        if self.clouds:
            self.clouds.cleanup()  # Limpa nuvens antigas
        self.clouds = CloudSystem(num_clouds=15, wind_speed=0.8)
        
        return True
    
    def reload_current_level(self):
        """Recarrega o nível atual (reset)"""
        return self.load_level(self.current_level_index)
    
    def get_next_level_index(self):
        """Retorna índice do próximo nível ou None se é o último"""
        next_index = self.current_level_index + 1
        if next_index < get_level_count():
            return next_index
        return None
    
    def is_last_level(self):
        """Verifica se é o último nível"""
        return self.current_level_index >= get_level_count() - 1
    
    def check_victory(self):
        """
        Verifica se o jogador completou o nível.
        
        Returns:
            bool: True se todas as caixas estão nos objetivos
        """
        if len(self.boxes) != len(self.objectives):
            return False
        
        # Conta caixas nos objetivos corretos
        boxes_on_targets = sum(1 for box in self.boxes if box in self.objectives)
        
        return boxes_on_targets == len(self.objectives)
    
    def can_push_box(self, player_x, player_z, direction_x, direction_z):
        """
        Verifica se pode empurrar uma caixa.
        
        Args:
            player_x, player_z: Posição do jogador
            direction_x, direction_z: Direção do empurrão
            
        Returns:
            tuple: (pode_empurrar, box_position, destination) ou (False, None, None)
        """
        px = Physics.grid_round(player_x)
        pz = Physics.grid_round(player_z)
        
        # Posição da caixa na frente do jogador
        box_pos = (px + direction_x, 0, pz + direction_z)
        
        # Verifica se há uma caixa
        if box_pos not in self.boxes:
            return False, None, None
        
        # Posição de destino da caixa
        dest_pos = (box_pos[0] + direction_x, 0, box_pos[2] + direction_z)
        
        # Verifica se destino está livre
        if dest_pos in self.boxes or dest_pos in self.walls:
            return False, box_pos, dest_pos
        
        # Verifica limites do mundo
        if abs(dest_pos[0]) >= 100 or abs(dest_pos[2]) >= 100:
            return False, box_pos, dest_pos
        
        return True, box_pos, dest_pos
    
    def push_box(self, player_x, player_z, direction_x, direction_z, current_time):
        """
        Empurra uma caixa se possível.
        
        Args:
            player_x, player_z: Posição do jogador
            direction_x, direction_z: Direção do empurrão
            current_time: Tempo atual para partículas
            
        Returns:
            bool: True se empurrou com sucesso
        """
        can_push, box_pos, dest_pos = self.can_push_box(
            player_x, player_z, direction_x, direction_z
        )
        
        if not can_push:
            # Som de bloqueio
            get_sound_manager().play('blocked')
            return False
        
        # Move a caixa
        idx = self.boxes.index(box_pos)
        self.boxes[idx] = dest_pos
        self.move_count += 1
        
        # Som de empurrar
        get_sound_manager().play('push')
        
        # Cria partículas e som se atingiu objetivo
        if dest_pos in self.objectives:
            self.particles.append((dest_pos[0], dest_pos[1], dest_pos[2], current_time))
            get_sound_manager().play('box_on_target')
        
        return True
    
    def get_box_status(self, box_position, player_x, player_z):
        """
        Retorna status de uma caixa para renderização.
        
        Args:
            box_position: Posição da caixa
            player_x, player_z: Posição do jogador
            
        Returns:
            str: 'on_target', 'pushable', 'blocked', ou 'normal'
        """
        # Caixa no objetivo
        if box_position in self.objectives:
            return 'on_target'
        
        # Verifica se está na frente do jogador
        dir_x, dir_z = 0, 0  # Precisaria da direção da câmera
        px = Physics.grid_round(player_x)
        pz = Physics.grid_round(player_z)
        
        # Esta função seria chamada do renderer com a direção
        return 'normal'
    
    def update_particles(self, current_time, max_lifetime=2.0):
        """
        Atualiza lista de partículas, removendo as antigas.
        
        Args:
            current_time: Tempo atual
            max_lifetime: Tempo máximo de vida das partículas
        """
        self.particles = [
            p for p in self.particles 
            if (current_time - p[3]) < max_lifetime
        ]
    
    def get_progress_stats(self):
        """
        Retorna estatísticas de progresso do nível.
        
        Returns:
            dict: {'boxes_on_target', 'total_boxes', 'move_count', 'completion_percent'}
        """
        boxes_on_target = sum(1 for box in self.boxes if box in self.objectives)
        total_boxes = len(self.objectives)
        completion = (boxes_on_target / total_boxes * 100) if total_boxes > 0 else 0
        
        return {
            'boxes_on_target': boxes_on_target,
            'total_boxes': total_boxes,
            'move_count': self.move_count,
            'completion_percent': completion
        }
