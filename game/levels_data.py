"""
game/levels_data.py
===================
Definição de todos os níveis do jogo.
Cada nível contém: paredes, caixas, objetivos e posição inicial.
"""

LEVELS = [
    # ========================================
    # LEVEL 1: Tutorial Simples
    # ========================================
    {
        'name': 'Tutorial',
        'difficulty': 'Fácil',
        'paredes': [
            (i, 0, -5) for i in range(-5, 6)
        ] + [
            (i, 0, 5) for i in range(-5, 6)
        ] + [
            (-5, 0, i) for i in range(-4, 5)
        ] + [
            (5, 0, i) for i in range(-4, 5)
        ] + [
            (-1, 0, 0)
        ],
        'caixas': [(0, 0, 1), (1, 0, 1)],
        'objetivos': [(3, 0, 3), (-3, 0, -3)],
        'spawn': (0.0, 0.0, -3.0)
    },
    
    # ========================================
    # LEVEL 2: Intermediário
    # ========================================
    {
        'name': 'Corredor',
        'difficulty': 'Médio',
        'paredes': [
            (i, 0, -8) for i in range(-8, 9)
        ] + [
            (i, 0, 8) for i in range(-8, 9)
        ] + [
            (-8, 0, i) for i in range(-7, 8)
        ] + [
            (8, 0, i) for i in range(-7, 8)
        ] + [
            (i, 0, 0) for i in range(-5, 6) if i not in (-1, 0, 1)
        ] + [
            (3, 0, i) for i in range(-5, 5)
        ],
        'caixas': [(-6, 0, -6), (6, 0, 6), (0, 0, 6), (-6, 0, 6)],
        'objetivos': [(-4, 0, -4), (4, 0, 4), (4, 0, -4), (-4, 0, 4)],
        'spawn': (0.0, 0.0, -6.0)
    },
    
    # ========================================
    # LEVEL 3: Labirinto
    # ========================================
    {
        'name': 'Labirinto',
        'difficulty': 'Médio',
        'paredes': [
            (i, 0, -10) for i in range(-10, 11)
        ] + [
            (i, 0, 10) for i in range(-10, 11)
        ] + [
            (-10, 0, i) for i in range(-9, 10)
        ] + [
            (10, 0, i) for i in range(-9, 10)
        ] + [
            (i, 0, -6) for i in range(-6, 7) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, 6) for i in range(-6, 7) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (-6, 0, i) for i in range(-5, 6) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (6, 0, i) for i in range(-5, 6) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (-4, 0, -4), (4, 0, -4)
        ],
        'caixas': [(-2, 0, -2), (2, 0, -2), (-2, 0, 2), (2, 0, 2), (0, 0, -3)],
        'objetivos': [(-8, 0, -8), (8, 0, -8), (-8, 0, 8), (8, 0, 8), (0, 0, -8)],
        'spawn': (0.0, 0.0, 7.0)
    },
    
    # ========================================
    # LEVEL 4: Quebra-Cabeça Complexo
    # ========================================
    {
        'name': 'Cruz',
        'difficulty': 'Difícil',
        'paredes': [
            (i, 0, -12) for i in range(-12, 13)
        ] + [
            (i, 0, 12) for i in range(-12, 13)
        ] + [
            (-12, 0, i) for i in range(-11, 12)
        ] + [
            (12, 0, i) for i in range(-11, 12)
        ] + [
            (0, 0, i) for i in range(-8, 9) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, 0) for i in range(-8, 9) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (-7, 0, -7), (7, 0, -7), (-7, 0, 7), (7, 0, 7)
        ],
        'caixas': [(-3, 0, -6), (3, 0, -6), (-6, 0, -3), (6, 0, -3), (-1, 0, -1), (1, 0, 1)],
        'objetivos': [(-10, 0, -10), (10, 0, -10), (-10, 0, 10), (10, 0, 10), (0, 0, -10), (0, 0, 10)],
        'spawn': (0.0, 0.0, -2.0)
    },
    
    # ========================================
    # LEVEL 5: Desafio Final - "O Grande Labirinto"
    # ========================================
    {
        'name': 'Grande Labirinto',
        'difficulty': 'Muito Difícil',
        'paredes': [
            (i, 0, -15) for i in range(-15, 16)
        ] + [
            (i, 0, 15) for i in range(-15, 16)
        ] + [
            (-15, 0, i) for i in range(-14, 15)
        ] + [
            (15, 0, i) for i in range(-14, 15)
        ] + [
            (i, 0, -12) for i in range(-12, 13) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, 12) for i in range(-12, 13) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (-12, 0, i) for i in range(-11, 12) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (12, 0, i) for i in range(-11, 12) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, -9) for i in range(-9, 10) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (i, 0, 9) for i in range(-9, 10) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (-9, 0, i) for i in range(-8, 9) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (9, 0, i) for i in range(-8, 9) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (i, 0, -6) for i in range(-6, 7) if i not in (-1, 0, 1)
        ] + [
            (i, 0, 6) for i in range(-6, 7) if i not in (-1, 0, 1)
        ] + [
            (-5, 0, -5), (5, 0, -5), (-5, 0, 5), (5, 0, 5)
        ],
        'caixas': [(-4, 0, -4), (4, 0, -4), (-4, 0, 4), (4, 0, 4), (-2, 0, 0), (2, 0, 0), (0, 0, -2)],
        'objetivos': [(-13, 0, -13), (13, 0, -13), (-13, 0, 13), (13, 0, 13), (0, 0, -13), (0, 0, 13), (13, 0, 0)],
        'spawn': (-11.0, 0.0, 0.0)
    }
]


def get_level_count():
    """Retorna o número total de níveis"""
    return len(LEVELS)


def get_level(index):
    """
    Retorna dados de um nível específico.
    
    Args:
        index (int): Índice do nível (0-based)
        
    Returns:
        dict: Dados do nível ou None se inválido
    """
    if 0 <= index < len(LEVELS):
        return LEVELS[index]
    return None
