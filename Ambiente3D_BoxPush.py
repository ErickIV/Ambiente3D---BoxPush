# ambiente3d_sokoban.py
# Ambiente 3D didático para Computação Gráfica / RV - Jogo Sokoban
# Pygame + PyOpenGL (GL + GLUT + GLU)
# Controles: WASD = mover | Mouse = olhar | Espaço = empurrar | R = reset | ESC = sair
# 5 Níveis progressivos + Tela de vitória final especial

import math
import sys
import time
from math import sin, cos
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

# Inicializa GLUT cedo para evitar problemas com Pygame/PyOpenGL
glutInit(sys.argv)

# -----------------------------
# Definições de Materiais
# -----------------------------
# Corrigido: Removidas as funções duplicadas e aninhadas.

def aplicar_material_parede_variado(x, z):
    # Material com aspecto de concreto com variações baseadas na posição
    variacao = (abs(x * 0.1) + abs(z * 0.1)) % 0.3 - 0.15
    base_cor = 0.6 + variacao * 0.1
    
    # Cores ligeiramente diferentes para simular irregularidades do concreto
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.15, 0.15, 0.16 + variacao * 0.02, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (base_cor, base_cor, base_cor + variacao * 0.02, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 4.0 + variacao * 2.0)

def aplicar_material_parede():
    # Material com aspecto de concreto mais realista (função de backup)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.15, 0.15, 0.16, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.62, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 4.0)

def aplicar_material_chao():
    # Chão com aspecto de grama mais realista
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.08, 0.25, 0.08, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.2, 0.7, 0.2, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.05, 0.15, 0.05, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 12.0)

# -----------------------------
# Configurações de Janela/Camera
# -----------------------------
LARGURA_TELA = 1280
ALTURA_TELA = 720
FOV = 70.0
NEAR = 0.1
FAR = 200.0

# -----------------------------
# Parâmetros de Jogabilidade
# -----------------------------
PLAYER_ALTURA_Olhos = 0.8
PLAYER_RAIO = 0.35       # raio de colisão no plano XZ
MOVE_SPEED = 3.0         # m/s
RUN_MULTIPLIER = 1.65    # segurar SHIFT para correr
MOUSE_SENS = 0.12        # sensibilidade em deg/pixel
PUSH_COOLDOWN = 0.18     # seg de intervalo entre empurrões
GRID_SIZE = 1.0          # mundo em grade unitária

# -----------------------------
# Estado Global do Jogo
# -----------------------------
# Novas variáveis de estado
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_WIN = 2
GAME_STATE_FINAL_VICTORY = 3  # Nova tela de vitória final
game_state = GAME_STATE_MENU

current_level = 0
movimento_count = 0
_last_push_time = 0.0
_victory_time = 0.0

# Variáveis de câmera e player existentes
camera_rot_x = 0.0  # pitch
camera_rot_y = 0.0  # yaw
player_x, player_y, player_z = 0.0, 0.0, 0.0

paredes = []   # lista de tuplas (x,y,z) centradas no grid
caixas = []    # idem
objetivos = [] # idem

# Partículas (para o efeito de sucesso)
particulas_sucesso = [] # lista de (x, y, z, start_time)


# -----------------------------
# Definição de Níveis (NOVO)
# -----------------------------
LEVELS = [
    # Level 1: Simples - Tutorial
    {
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
    # Level 2: Intermediário 
    {
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
    # Level 3: Labirinto
    {
        'paredes': [
            (i, 0, -10) for i in range(-10, 11)
        ] + [
            (i, 0, 10) for i in range(-10, 11)
        ] + [
            (-10, 0, i) for i in range(-9, 10)
        ] + [
            (10, 0, i) for i in range(-9, 10)
        ] + [
            # Labirinto interno - com passagens largas para facilitar movimento
            (i, 0, -6) for i in range(-6, 7) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, 6) for i in range(-6, 7) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (-6, 0, i) for i in range(-5, 6) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (6, 0, i) for i in range(-5, 6) if i not in (-2, -1, 0, 1, 2)
        ] + [
            # Apenas algumas paredes estratégicas para criar desafio sem bloquear
            (-4, 0, -4), (4, 0, -4)
        ],
        'caixas': [(-2, 0, -2), (2, 0, -2), (-2, 0, 2), (2, 0, 2), (0, 0, -3)],
        'objetivos': [(-8, 0, -8), (8, 0, -8), (-8, 0, 8), (8, 0, 8), (0, 0, -8)],
        'spawn': (0.0, 0.0, 7.0)
    },
    # Level 4: Quebra-cabeça complexo
    {
        'paredes': [
            (i, 0, -12) for i in range(-12, 13)
        ] + [
            (i, 0, 12) for i in range(-12, 13)
        ] + [
            (-12, 0, i) for i in range(-11, 12)
        ] + [
            (12, 0, i) for i in range(-11, 12)
        ] + [
            # Estrutura em cruz mais simples - evitando conflitos com spawn
            (0, 0, i) for i in range(-8, 9) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, 0) for i in range(-8, 9) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            # Obstáculos estratégicos mas não nos cantos
            (-7, 0, -7), (7, 0, -7), (-7, 0, 7), (7, 0, 7)
        ],
        'caixas': [(-3, 0, -6), (3, 0, -6), (-6, 0, -3), (6, 0, -3), (-1, 0, -1), (1, 0, 1)],
        'objetivos': [(-10, 0, -10), (10, 0, -10), (-10, 0, 10), (10, 0, 10), (0, 0, -10), (0, 0, 10)],
        'spawn': (0.0, 0.0, -5.0)
    },
    # Level 5: Desafio Final - "O Grande Labirinto"
    {
        'paredes': [
            (i, 0, -15) for i in range(-15, 16)
        ] + [
            (i, 0, 15) for i in range(-15, 16)
        ] + [
            (-15, 0, i) for i in range(-14, 15)
        ] + [
            (15, 0, i) for i in range(-14, 15)
        ] + [
            # Labirinto complexo em espiral - mais espaçoso
            (i, 0, -12) for i in range(-12, 13) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (i, 0, 12) for i in range(-12, 13) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (-12, 0, i) for i in range(-11, 12) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            (12, 0, i) for i in range(-11, 12) if i not in (-4, -3, -2, -1, 0, 1, 2, 3, 4)
        ] + [
            # Espiral interna - passagens amplas
            (i, 0, -9) for i in range(-9, 10) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (i, 0, 9) for i in range(-9, 10) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (-9, 0, i) for i in range(-8, 9) if i not in (-2, -1, 0, 1, 2)
        ] + [
            (9, 0, i) for i in range(-8, 9) if i not in (-2, -1, 0, 1, 2)
        ] + [
            # Centro do labirinto - mais aberto
            (i, 0, -6) for i in range(-6, 7) if i not in (-1, 0, 1)
        ] + [
            (i, 0, 6) for i in range(-6, 7) if i not in (-1, 0, 1)
        ] + [
            # Obstáculos estratégicos - evitando cantos
            (-5, 0, -5), (5, 0, -5), (-5, 0, 5), (5, 0, 5)
        ],
        'caixas': [(-4, 0, -4), (4, 0, -4), (-4, 0, 4), (4, 0, 4), (-2, 0, 0), (2, 0, 0), (0, 0, -2)],
        'objetivos': [(-13, 0, -13), (13, 0, -13), (-13, 0, 13), (13, 0, 13), (0, 0, -13), (0, 0, 13), (13, 0, 0)],
        'spawn': (-11.0, 0.0, 0.0)
    }
]

# -----------------------------
# Utilidades de Mundo / Geometria
# (Mantidas como estavam)
# -----------------------------
def grid_round(v):
    return int(round(v))

def aabb_colide_ponto(px, pz, cx, cz, half=0.5, raio=PLAYER_RAIO):
    # ... (código mantido) ...
    minx = cx - half
    maxx = cx + half
    minz = cz - half
    maxz = cz + half
    closest_x = max(minx, min(px, maxx))
    closest_z = max(minz, min(pz, maxz))
    dx = px - closest_x
    dz = pz - closest_z
    return (dx*dx + dz*dz) < (raio*raio)

def existe_bloco_em(lista, x, y, z):
    return (x, y, z) in lista

def pos_livre(x, y, z):
    g = (grid_round(x), grid_round(y), grid_round(z))
    return (g not in paredes) and (g not in caixas)

def direcao_frente_cardinal():
    yaw = math.radians(camera_rot_y)
    forward_x = math.sin(yaw)
    forward_z = -math.cos(yaw)
    
    if abs(forward_x) > abs(forward_z):
        dir_x = 1 if forward_x > 0 else -1
        dir_z = 0
    else:
        dir_x = 0
        dir_z = 1 if forward_z > 0 else -1
    return dir_x, dir_z

# -----------------------------
# Lógica do Jogo / Nível (NOVO/MODIFICADO)
# -----------------------------
def carregar_level(nivel):
    global paredes, caixas, objetivos, player_x, player_z, movimento_count, particulas_sucesso, _victory_time
    
    if nivel < 0 or nivel >= len(LEVELS):
        print("Fim do jogo!")
        # Implementar tela final ou ciclo de níveis
        return

    level_data = LEVELS[nivel]
    
    # Copia as listas do level (para não modificar a lista original)
    paredes = level_data['paredes'][:]
    caixas = level_data['caixas'][:]
    objetivos = level_data['objetivos'][:]
    
    player_x, player_z = level_data['spawn'][:2]
    
    # Reseta estados específicos do jogo
    movimento_count = 0
    particulas_sucesso = []
    _victory_time = 0.0
    
    # Reseta a câmera
    global camera_rot_x, camera_rot_y
    camera_rot_x, camera_rot_y = 0.0, 0.0

def criar_mundo():
    # A função original "criar_mundo" foi substituída por carregar_level
    carregar_level(current_level)

def verificar_vitoria():
    caixas_corretas = sum([c in objetivos for c in caixas])
    return caixas_corretas == len(objetivos) and len(caixas) == len(objetivos)


# -----------------------------
# Desenho (OpenGL)
# -----------------------------
def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # Iluminação Avançada (NOVO)
    glEnable(GL_LIGHTING)
    
    # Luz principal (sol) - LIGHT0
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (10.0, 15.0, 5.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.7, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    
    # Luz ambiente suave - LIGHT1
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, (0.0, 10.0, 0.0, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.3, 0.3, 0.4, 1.0))
    glLightfv(GL_LIGHT1, GL_AMBIENT, (0.2, 0.2, 0.3, 1.0)) # Esta luz define o ambiente
    
    # Material padrão inicial
    aplicar_material_parede()

    glClearColor(0.55, 0.78, 0.95, 1.0)  # céu

def aplicar_perspectiva(w, h):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, (w / float(h)), NEAR, FAR)
    glMatrixMode(GL_MODELVIEW)

# ... (função desenhar_cubo_unitario mantida) ...
def desenhar_cubo_unitario():
    hs = 0.5
    glBegin(GL_QUADS)
    # Frente
    glNormal3f(0,0,1)
    glVertex3f(-hs,-hs, hs)
    glVertex3f( hs,-hs, hs)
    glVertex3f( hs, hs, hs)
    glVertex3f(-hs, hs, hs)
    # Trás
    glNormal3f(0,0,-1)
    glVertex3f(-hs,-hs,-hs)
    glVertex3f(-hs, hs,-hs)
    glVertex3f( hs, hs,-hs)
    glVertex3f( hs,-hs,-hs)
    # Esquerda
    glNormal3f(-1,0,0)
    glVertex3f(-hs,-hs,-hs)
    glVertex3f(-hs,-hs, hs)
    glVertex3f(-hs, hs, hs)
    glVertex3f(-hs, hs,-hs)
    # Direita
    glNormal3f(1,0,0)
    glVertex3f( hs,-hs,-hs)
    glVertex3f( hs, hs,-hs)
    glVertex3f( hs, hs, hs)
    glVertex3f( hs,-hs, hs)
    # Topo
    glNormal3f(0,1,0)
    glVertex3f(-hs, hs,-hs)
    glVertex3f(-hs, hs, hs)
    glVertex3f( hs, hs, hs)
    glVertex3f( hs, hs,-hs)
    # Base
    glNormal3f(0,-1,0)
    glVertex3f(-hs,-hs,-hs)
    glVertex3f( hs,-hs,-hs)
    glVertex3f( hs,-hs, hs)
    glVertex3f(-hs,-hs, hs)
    glEnd()
# -----------------------------

def aplicar_material_chao():
    # Chão com aspecto de grama bem verde e visível
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.4, 0.1, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.2, 0.8, 0.2, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.3, 0.1, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 16.0)

def desenhar_folha_grama(x, z, altura, rotacao, cor_variacao):
    """Desenha uma folha individual de grama"""
    glPushMatrix()
    glTranslatef(x, -1.0, z)
    glRotatef(rotacao, 0, 1, 0)  # Rotação aleatória
    
    # Cor verde com variação
    verde_r = 0.1 + cor_variacao * 0.1
    verde_g = 0.6 + cor_variacao * 0.3
    verde_b = 0.1 + cor_variacao * 0.05
    glColor3f(verde_r, verde_g, verde_b)
    
    # Desenha uma folha como um quad vertical bem fino
    glBegin(GL_QUADS)
    largura = 0.02
    # Frente da folha
    glVertex3f(-largura, 0, 0)
    glVertex3f(largura, 0, 0)
    glVertex3f(largura, altura, 0)
    glVertex3f(-largura, altura, 0)
    # Trás da folha (para ser visível de ambos os lados)
    glVertex3f(-largura, 0, 0)
    glVertex3f(-largura, altura, 0)
    glVertex3f(largura, altura, 0)
    glVertex3f(largura, 0, 0)
    glEnd()
    
    glPopMatrix()

def desenhar_chao():
    # Desenha o chão base verde
    glDisable(GL_LIGHTING)
    glColor3f(0.15, 0.5, 0.15)  # Verde escuro como base
    
    glPushMatrix()
    glTranslatef(0.0, -1.0, 0.0)
    glScalef(40.0, 0.02, 40.0)
    
    # Chão base simples
    hs = 0.5
    glBegin(GL_QUADS)
    glVertex3f(-hs, hs,-hs)
    glVertex3f(-hs, hs, hs)
    glVertex3f( hs, hs, hs)
    glVertex3f( hs, hs,-hs)
    glEnd()
    
    glPopMatrix()
    
    # Agora adiciona a grama 3D por cima
    densidade_grama = 8  # Folhas por unidade quadrada
    area_grama = 20  # Área de cobertura da grama
    
    import random
    random.seed(42)  # Seed fixo para consistência
    
    for i in range(area_grama * area_grama * densidade_grama):
        # Posição aleatória dentro da área
        grama_x = random.uniform(-area_grama/2, area_grama/2)
        grama_z = random.uniform(-area_grama/2, area_grama/2)
        
        # Não desenha grama onde há paredes ou caixas
        grid_x, grid_z = int(round(grama_x)), int(round(grama_z))
        if (grid_x, 0, grid_z) in paredes or (grid_x, 0, grid_z) in caixas:
            continue
            
        # Propriedades aleatórias da folha
        altura = random.uniform(0.05, 0.15)  # Altura variada
        rotacao = random.uniform(0, 360)     # Rotação aleatória
        cor_variacao = random.uniform(-0.3, 0.3)  # Variação de cor
        
        desenhar_folha_grama(grama_x, grama_z, altura, rotacao, cor_variacao)
    
    glEnable(GL_LIGHTING)

def desenhar_parede(x, y, z):
    aplicar_material_parede_variado(x, z)
    glPushMatrix()
    # Posiciona a parede apoiada no chão (chão está em y = -1.0)
    glTranslatef(x, y + 0.0, z)  # Base da parede em y = 0, centro em y = 1.0
    glScalef(1.0, 2.0, 1.0)
    desenhar_cubo_unitario()
    glPopMatrix()

def desenhar_caixa(x, y, z):
    glPushMatrix()
    # Posiciona a caixa apoiada no chão (chão está em y = -1.0)
    glTranslatef(x, y - 0.5, z)  # Base da caixa em y = -0.5, centro em y = 0
    glScalef(1.0, 1.0, 1.0)
    
    pos_caixa = (x, y, z)
    
    # 1. Checa se a caixa está em um objetivo (Melhoria Visual)
    if pos_caixa in objetivos:
        # Material para caixa no objetivo (Amarelo Dourado)
        cor = (1.0, 0.84, 0.0, 1.0)
        brilho = 64.0
    else:
        # 2. Checa se está na frente e pode ser empurrada (Highlight)
        dir_x, dir_z = direcao_frente_cardinal()
        px, pz = grid_round(player_x), grid_round(player_z)
        caixa_na_frente = (px + dir_x, 0, pz + dir_z)
        
        if pos_caixa == caixa_na_frente:
            destino = (x + dir_x, y, z + dir_z)
            # Verifica se o destino está livre e dentro dos limites
            pode_empurrar = (destino not in caixas) and (destino not in paredes) and abs(destino[0]) < 100 and abs(destino[2]) < 100
            
            if pode_empurrar:
                # Verde empurrável
                cor = (0.2, 0.9, 0.2, 1.0)
            else:
                # Vermelho bloqueado
                cor = (0.9, 0.2, 0.2, 1.0)
        else:
            # Marrom padrão
            cor = (0.72, 0.48, 0.16, 1.0)
            
        brilho = 32.0
    
    # Configura material para refletir a cor desejada
    # Usando o Ambient um pouco mais escuro para melhor contraste
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [c * 0.5 for c in cor[:3]] + [1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, cor)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, brilho)
    
    desenhar_cubo_unitario()
    
    # Restaura o material padrão (paredes) para os próximos objetos
    aplicar_material_parede()
    
    glPopMatrix()

def desenhar_objetivo(x, y, z):
    # Objetivos devem sempre ser visíveis no Sokoban, mas respeitando a geometria
    
    # Verifica se não há uma parede NA MESMA posição do objetivo
    if (x, y, z) in paredes:
        return  # Não desenha se há uma parede exatamente aqui
    
    glPushMatrix()
    # Posiciona o objetivo DENTRO do chão para evitar sobreposição com paredes
    glTranslatef(x, y - 0.95, z)  # Bem dentro do chão, mas ainda visível
    
    # Usa depth test normal - sem forçar renderização
    glDisable(GL_LIGHTING)
    
    # Círculo azul embutido no chão
    glColor3f(0.1, 0.7, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)  # No nível do chão
    r = 0.35  # Ligeiramente menor
    for i in range(0, 361, 12):
        ang = math.radians(i)
        glVertex3f(math.cos(ang) * r, 0, math.sin(ang) * r)
    glEnd()
    
    # Desenha um "X" vermelho embutido no chão
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(6.0)
    glBegin(GL_LINES)
    # X vermelho no mesmo nível do chão
    glVertex3f(-0.25, 0.01, -0.25)  # Ligeiramente acima do chão
    glVertex3f(0.25, 0.01, 0.25)
    glVertex3f(0.25, 0.01, -0.25)
    glVertex3f(-0.25, 0.01, 0.25)
    glEnd()
    glLineWidth(1.0)
    
    glEnable(GL_LIGHTING)
    glPopMatrix()

def desenhar_sombra_caixa(x, y, z):
    # Sombra no nível correto do chão
    glPushMatrix()
    glTranslatef(x, -0.99, z)  # Bem próximo ao topo do chão em y = -1.0
    glDisable(GL_LIGHTING)
    glColor4f(0.0, 0.0, 0.0, 0.3)  # sombra semi-transparente
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Quadrado da sombra
    s = 0.4
    glBegin(GL_QUADS)
    glVertex3f(-s, 0, -s)
    glVertex3f( s, 0, -s)
    glVertex3f( s, 0,  s)
    glVertex3f(-s, 0,  s)
    glEnd()
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def desenhar_particulas_sucesso(x, y, z, tempo):
    # Partículas de sucesso ajustadas para o novo sistema de coordenadas
    if tempo < 2.0:  # partículas por 2 segundos
        glPushMatrix()
        glTranslatef(x, y - 0.2, z)  # Altura mais baixa para ficar próxima das caixas
        glDisable(GL_LIGHTING)
        
        for i in range(8):
            ang = (i / 8.0) * 2 * math.pi
            offset = tempo * 2.0
            px = math.cos(ang + tempo * 3) * offset
            pz = math.sin(ang + tempo * 3) * offset
            py = math.sin(tempo * 5) * 0.3 + 0.3  # Oscilação mais baixa
            
            glColor3f(1.0, 1.0, 0.0)  # amarelo brilhante
            glPushMatrix()
            glTranslatef(px, py, pz)
            
            # Partículas como pequenos cubos brilhantes
            glScalef(0.1, 0.1, 0.1)
            desenhar_cubo_unitario()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()

def desenhar_tela_vitoria():
    # Implementação de Tela de Vitória (Sua sugestão B)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Overlay verde de vitória
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, LARGURA_TELA, 0, ALTURA_TELA)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Tela semi-transparente
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.8, 0.0, 0.7)
    
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(LARGURA_TELA, 0)
    glVertex2f(LARGURA_TELA, ALTURA_TELA)
    glVertex2f(0, ALTURA_TELA)
    glEnd()
    
    draw_text_2d(LARGURA_TELA//2 - 100, ALTURA_TELA//2 + 50, "PARABÉNS! LEVEL COMPLETO!", 24)
    draw_text_2d(LARGURA_TELA//2 - 140, ALTURA_TELA//2 - 10, f"Movimentos: {movimento_count}")
    draw_text_2d(LARGURA_TELA//2 - 180, ALTURA_TELA//2 - 60, "Pressione ENTER para o Próximo Level / ESC para sair", 18)
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def desenhar_menu_principal():
    # Menu Principal Aprimorado com elementos visuais 3D
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Renderiza uma cena 3D de fundo com alguns elementos do jogo
    glLoadIdentity()
    
    # Câmera fixa para o menu
    glRotatef(-20, 1, 0, 0)  # Olha ligeiramente para baixo
    glRotatef(30, 0, 1, 0)   # Rotação para dar perspectiva
    glTranslatef(-2, -1, -8)  # Posiciona a câmera
    
    # Desenha alguns elementos 3D de demonstração
    glEnable(GL_LIGHTING)
    
    # Chão de demonstração
    glDisable(GL_LIGHTING)
    glColor3f(0.2, 0.7, 0.2)  # Verde grama
    glPushMatrix()
    glTranslatef(0, -1, 0)
    glScalef(8, 0.02, 6)
    hs = 0.5
    glBegin(GL_QUADS)
    glVertex3f(-hs, hs,-hs)
    glVertex3f(-hs, hs, hs)
    glVertex3f( hs, hs, hs)
    glVertex3f( hs, hs,-hs)
    glEnd()
    glPopMatrix()
    
    # Algumas folhas de grama para ambientar
    import random
    random.seed(123)  # Seed fixo para o menu
    for i in range(50):
        gx = random.uniform(-3, 3)
        gz = random.uniform(-2, 2)
        altura = random.uniform(0.05, 0.12)
        rot = random.uniform(0, 360)
        cor_var = random.uniform(-0.2, 0.2)
        
        glPushMatrix()
        glTranslatef(gx, -1.0, gz)
        glRotatef(rot, 0, 1, 0)
        
        verde_r = 0.1 + cor_var * 0.1
        verde_g = 0.6 + cor_var * 0.2
        verde_b = 0.1 + cor_var * 0.05
        glColor3f(verde_r, verde_g, verde_b)
        
        largura = 0.02
        glBegin(GL_QUADS)
        glVertex3f(-largura, 0, 0)
        glVertex3f(largura, 0, 0)
        glVertex3f(largura, altura, 0)
        glVertex3f(-largura, altura, 0)
        glEnd()
        glPopMatrix()
    
    glEnable(GL_LIGHTING)
    
    # Parede de demonstração
    aplicar_material_parede_variado(1, 1)
    glPushMatrix()
    glTranslatef(2, 0, 0)
    glScalef(1, 2, 1)
    desenhar_cubo_unitario()
    glPopMatrix()
    
    # Caixa de demonstração
    glPushMatrix()
    glTranslatef(0, -0.5, 0)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.36, 0.24, 0.08, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.72, 0.48, 0.16, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)
    desenhar_cubo_unitario()
    glPopMatrix()
    
    # Objetivo de demonstração
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(-1, -0.95, 0)
    glColor3f(0.1, 0.7, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    r = 0.35
    for i in range(0, 361, 12):
        ang = math.radians(i)
        glVertex3f(math.cos(ang) * r, 0, math.sin(ang) * r)
    glEnd()
    
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex3f(-0.2, 0.01, -0.2)
    glVertex3f(0.2, 0.01, 0.2)
    glVertex3f(0.2, 0.01, -0.2)
    glVertex3f(-0.2, 0.01, 0.2)
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)
    
    # Overlay para o texto do menu
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Fundo semi-transparente para o texto
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, LARGURA_TELA, 0, ALTURA_TELA)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.6)  # Fundo escuro semi-transparente
    
    glBegin(GL_QUADS)
    glVertex2f(0, ALTURA_TELA//2 + 150)
    glVertex2f(LARGURA_TELA, ALTURA_TELA//2 + 150)
    glVertex2f(LARGURA_TELA, ALTURA_TELA//2 - 100)
    glVertex2f(0, ALTURA_TELA//2 - 100)
    glEnd()
    
    glDisable(GL_BLEND)
    
    # Texto do menu com cores e tamanhos variados
    # Título principal
    draw_text_2d(LARGURA_TELA//2 - 160, ALTURA_TELA//2 + 80, "🎮 BOXPUSH 3D SOKOBAN 🎮", 24)
    
    # Subtítulo
    draw_text_2d(LARGURA_TELA//2 - 120, ALTURA_TELA//2 + 40, "Empurre as caixas para os objetivos!", 18)
    
    # Informação dos níveis
    draw_text_2d(LARGURA_TELA//2 - 80, ALTURA_TELA//2 + 10, "🎯 5 NÍVEIS DESAFIADORES 🎯", 16)
    
    # Instruções principais
    draw_text_2d(LARGURA_TELA//2 - 100, ALTURA_TELA//2 - 20, "⏎ ENTER - Começar Jogo", 18)
    draw_text_2d(LARGURA_TELA//2 - 60, ALTURA_TELA//2 - 50, "⎋ ESC - Sair", 18)
    
    # Controles
    draw_text_2d(LARGURA_TELA//2 - 160, ALTURA_TELA//2 - 90, "Controles: WASD=Mover | SHIFT=Correr | Mouse=Olhar | Espaço=Empurrar", 16)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def desenhar_cena(t):
    desenhar_chao()
    
    # paredes
    for (x, y, z) in paredes:
        desenhar_parede(x, y, z)
        
    # objetivos
    for (x, y, z) in objetivos:
        desenhar_objetivo(x, y, z)
        
    # caixas e sombras
    for (x, y, z) in caixas:
        desenhar_caixa(x, y, z)
        desenhar_sombra_caixa(x, y, z)
        
    # partículas de sucesso
    for (x, y, z, start_t) in particulas_sucesso:
        desenhar_particulas_sucesso(x, y, z, t - start_t)

# -----------------------------
# HUD (texto 2D via GLUT)
# -----------------------------
def draw_text_2d(x, y, text, size=18):
    # ... (código mantido) ...
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()    
    glLoadIdentity()
    gluOrtho2D(0, LARGURA_TELA, 0, ALTURA_TELA)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x+1, y-1)
    font = GLUT_BITMAP_HELVETICA_18 if size >= 18 else GLUT_BITMAP_8_BY_13
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def desenhar_tela_vitoria_final():
    """Desenha a tela de parabéns por completar todos os níveis"""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Configurar projeção 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, LARGURA_TELA, 0, ALTURA_TELA, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Fundo escuro com gradiente
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.05, 0.2)  # Roxo escuro
    glVertex2f(0, 0)
    glVertex2f(LARGURA_TELA, 0)
    glColor3f(0.2, 0.1, 0.4)  # Roxo mais claro no topo
    glVertex2f(LARGURA_TELA, ALTURA_TELA)
    glVertex2f(0, ALTURA_TELA)
    glEnd()
    
    # Efeito de estrelas cintilantes
    import random
    random.seed(42)  # Seed fixo para posições consistentes
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for i in range(100):
        x = random.randint(50, LARGURA_TELA - 50)
        y = random.randint(50, ALTURA_TELA - 50)
        brilho = 0.5 + 0.5 * abs(math.sin(time.time() * 3 + i * 0.1))
        glColor3f(brilho, brilho, brilho)
        glVertex2f(x, y)
    glEnd()
    
    # Título principal
    glColor3f(1.0, 0.8, 0.0)  # Dourado
    draw_text_2d(LARGURA_TELA // 2 - 120, ALTURA_TELA - 100, "PARABÉNS!", 36)
    
    # Subtítulo
    glColor3f(0.9, 0.9, 0.9)
    draw_text_2d(LARGURA_TELA // 2 - 200, ALTURA_TELA - 150, "VOCÊ CONQUISTOU TODOS OS DESAFIOS!", 20)
    
    # Estatísticas
    nivel_count = len(LEVELS)
    total_movimentos = sum(movimento_count for movimento_count in [0])  # Simplificado para exemplo
    
    glColor3f(0.7, 1.0, 0.7)  # Verde claro
    draw_text_2d(LARGURA_TELA // 2 - 120, ALTURA_TELA - 220, f"✓ {nivel_count} NÍVEIS COMPLETADOS", 16)
    
    # Mensagem especial
    glColor3f(1.0, 0.6, 1.0)  # Rosa
    draw_text_2d(LARGURA_TELA // 2 - 180, ALTURA_TELA - 280, "Você demonstrou excelente habilidade de", 14)
    draw_text_2d(LARGURA_TELA // 2 - 190, ALTURA_TELA - 300, "resolução de problemas e pensamento lógico!", 14)
    
    # Caixa decorativa ao redor do troféu
    cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2 - 50
    tamanho = 80
    
    # Desenhar troféu ASCII
    glColor3f(1.0, 0.8, 0.0)  # Dourado
    linhas_trofeu = [
        "    🏆",
        "  ╔═══╗",
        "  ║ ★ ║",
        "  ╚═══╝",
        "   ███",
        "  ╔═══╗",
        "  ╚═══╝"
    ]
    
    for i, linha in enumerate(linhas_trofeu):
        draw_text_2d(cx - 30, cy + (len(linhas_trofeu) - i - 1) * 20, linha, 14)
    
    # Instruções
    glColor3f(0.8, 0.8, 0.8)
    draw_text_2d(LARGURA_TELA // 2 - 150, 120, "Pressione ENTER para voltar ao menu", 14)
    draw_text_2d(LARGURA_TELA // 2 - 60, 100, "ou ESC para sair", 14)
    
    # Efeito de partículas de celebração
    tempo_atual = time.time()
    for i in range(50):
        angulo = (tempo_atual * 50 + i * 7.2) % 360
        raio = 150 + 50 * math.sin(tempo_atual * 2 + i)
        x = cx + raio * math.cos(math.radians(angulo))
        y = cy + raio * math.sin(math.radians(angulo)) * 0.5
        
        if 50 < x < LARGURA_TELA - 50 and 50 < y < ALTURA_TELA - 50:
            cor_particula = (math.sin(tempo_atual * 3 + i) + 1) / 2
            glColor3f(cor_particula, 1.0 - cor_particula, 0.8)
            glPointSize(3.0)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()
    
    # Restaurar matrizes
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def desenhar_crosshair():
    """Desenha uma crosshair simples no centro da tela para orientação"""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Configuração da projeção 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, LARGURA_TELA, 0, ALTURA_TELA)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Posição central
    center_x = LARGURA_TELA // 2
    center_y = ALTURA_TELA // 2
    
    # Tamanho da crosshair
    size = 12
    thickness = 2
    
    # Cor da crosshair com transparência
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 1.0, 1.0, 0.8)  # Branco semi-transparente
    
    # Linha horizontal
    glBegin(GL_QUADS)
    glVertex2f(center_x - size, center_y - thickness//2)
    glVertex2f(center_x + size, center_y - thickness//2)
    glVertex2f(center_x + size, center_y + thickness//2)
    glVertex2f(center_x - size, center_y + thickness//2)
    glEnd()
    
    # Linha vertical
    glBegin(GL_QUADS)
    glVertex2f(center_x - thickness//2, center_y - size)
    glVertex2f(center_x + thickness//2, center_y - size)
    glVertex2f(center_x + thickness//2, center_y + size)
    glVertex2f(center_x - thickness//2, center_y + size)
    glEnd()
    
    # Ponto central (opcional, mais sutil)
    glColor4f(1.0, 1.0, 1.0, 0.6)
    glBegin(GL_QUADS)
    dot_size = 1
    glVertex2f(center_x - dot_size, center_y - dot_size)
    glVertex2f(center_x + dot_size, center_y - dot_size)
    glVertex2f(center_x + dot_size, center_y + dot_size)
    glVertex2f(center_x - dot_size, center_y + dot_size)
    glEnd()
    
    glDisable(GL_BLEND)
    
    # Restaura configurações
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def desenhar_hud_completo():
    # Implementação do HUD Completo (Sua sugestão B)
    caixas_ok = sum([c in objetivos for c in caixas])
    
    # Status do jogo
    draw_text_2d(20, ALTURA_TELA - 36, "WASD: mover | SHIFT: correr | Mouse: olhar | Espaço: empurrar | R: reset | ESC: sair")
    draw_text_2d(20, ALTURA_TELA - 68, f"Level {current_level + 1} | Caixas: {caixas_ok}/{len(objetivos)}")
    
    # Contador de movimentos
    draw_text_2d(20, ALTURA_TELA - 100, f"Movimentos: {movimento_count}")
    
    # Dicas
    if caixas_ok == 0:
        draw_text_2d(20, ALTURA_TELA - 132, "Dica: Empurre as caixas para os X vermelhos!")
    elif caixas_ok < len(objetivos):
        draw_text_2d(20, ALTURA_TELA - 132, "Continue empurrando as caixas restantes!")

# -----------------------------
# Movimento / Entrada
# -----------------------------
def pode_mover_para(nx, nz):
    # ... (código mantido) ...
    for (x, y, z) in paredes:
        if aabb_colide_ponto(nx, nz, x, z, half=0.5, raio=PLAYER_RAIO):
            return False
    for (x, y, z) in caixas:
        if aabb_colide_ponto(nx, nz, x, z, half=0.5, raio=PLAYER_RAIO):
            return False
    return True

def mover_player(dx, dz, dt):
    global player_x, player_z
    nx = player_x + dx * dt
    nz = player_z + dz * dt
    
    moved = False
    
    if pode_mover_para(nx, nz):
        player_x = nx
        player_z = nz
        moved = True
    else:
        # Tenta mover só X
        if pode_mover_para(nx, player_z):
            player_x = nx
            moved = True
        # Tenta mover só Z
        elif pode_mover_para(player_x, nz):
            player_z = nz
            moved = True
            
    return moved

def empurrar_caixa(t):
    global caixas, _last_push_time, movimento_count, particulas_sucesso, game_state, _victory_time, current_level
    
    if (t - _last_push_time) < PUSH_COOLDOWN:
        return
    _last_push_time = t

    dir_x, dir_z = direcao_frente_cardinal()
    px, pz = grid_round(player_x), grid_round(player_z)
    frente = (px + dir_x, 0, pz + dir_z)
    destino = (frente[0] + dir_x, 0, frente[2] + dir_z)

    if frente in caixas:
        # não empurra se destino bloqueado
        if (destino not in caixas) and (destino not in paredes):
            # segurança: não deixa empurrar contra a borda (usando um limite grande, já que as paredes devem limitar)
            if abs(destino[0]) < 100 and abs(destino[2]) < 100:
                idx = caixas.index(frente)
                caixas[idx] = destino
                movimento_count += 1 # Conta o movimento!
                
                # Gera partículas se atingir um objetivo
                if destino in objetivos:
                    particulas_sucesso.append((destino[0], destino[1], destino[2], t))
                    
                # Checa vitória após o movimento
                if verificar_vitoria():
                    _victory_time = t # Registra o tempo da vitória
                    
                    # Verificar se é o último nível
                    if current_level >= len(LEVELS) - 1:
                        # Completou todos os níveis!
                        game_state = GAME_STATE_FINAL_VICTORY
                    else:
                        # Ainda há mais níveis
                        game_state = GAME_STATE_WIN

# -----------------------------
# Loop Principal
# -----------------------------
def main():
    global camera_rot_x, camera_rot_y, player_x, player_y, player_z
    global game_state, current_level, LARGURA_TELA, ALTURA_TELA
    global particulas_sucesso, movimento_count, _last_push_time, _victory_time  # Adicione todas as variáveis globais modificadas

    pygame.init()
    pygame.display.set_caption("BOXPUSH 3D - Sokoban Pygame + PyOpenGL")
    pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), DOUBLEBUF | OPENGL | RESIZABLE)

    init_opengl()
    aplicar_perspectiva(LARGURA_TELA, ALTURA_TELA)

    clock = pygame.time.Clock()
    
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)

    running = True
    while running:
        t = pygame.time.get_ticks() / 1000.0
        dt_ms = clock.tick(120)
        dt = min(dt_ms / 1000.0, 0.033)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if game_state == GAME_STATE_PLAYING:
                        running = False 
                    elif game_state == GAME_STATE_MENU:
                        running = False
                    elif game_state == GAME_STATE_WIN:
                        running = False
                    elif game_state == GAME_STATE_FINAL_VICTORY:
                        running = False

                if event.key == K_r and game_state == GAME_STATE_PLAYING:
                    carregar_level(current_level)
                
                if event.key == K_RETURN:
                    if game_state == GAME_STATE_MENU:
                        current_level = 0
                        carregar_level(current_level)
                        game_state = GAME_STATE_PLAYING
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))
                    
                    elif game_state == GAME_STATE_WIN:
                        if current_level + 1 < len(LEVELS):
                            current_level += 1
                            carregar_level(current_level)
                            game_state = GAME_STATE_PLAYING
                        else:
                            game_state = GAME_STATE_MENU
                        
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))
                    
                    elif game_state == GAME_STATE_FINAL_VICTORY:
                        # Voltar ao menu após completar todos os níveis
                        game_state = GAME_STATE_MENU
                        current_level = 0
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)

                if event.key == K_r and game_state == GAME_STATE_PLAYING:
                    carregar_level(current_level)
                
                if event.key == K_RETURN:
                    if game_state == GAME_STATE_MENU:
                        current_level = 0
                        carregar_level(current_level)
                        game_state = GAME_STATE_PLAYING
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))
                    
                    elif game_state == GAME_STATE_WIN:
                        if current_level + 1 < len(LEVELS):
                            current_level += 1
                            carregar_level(current_level)
                            game_state = GAME_STATE_PLAYING
                        else:
                            game_state = GAME_STATE_MENU
                        
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))

            elif event.type == VIDEORESIZE:
                w, h = event.size
                # REMOVA a declaração global daqui
                LARGURA_TELA, ALTURA_TELA = w, h
                pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), DOUBLEBUF | OPENGL | RESIZABLE)
                aplicar_perspectiva(LARGURA_TELA, ALTURA_TELA)

        if game_state == GAME_STATE_PLAYING:
            
            # === Lógica de Mouse Look ===
            mx, my = pygame.mouse.get_pos()
            dx = mx - (LARGURA_TELA // 2)
            dy = my - (ALTURA_TELA // 2)
            camera_rot_y += dx * MOUSE_SENS
            camera_rot_x -= dy * MOUSE_SENS
            camera_rot_x = max(-89.0, min(89.0, camera_rot_x))
            pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))

            keys = pygame.key.get_pressed()
            mult = RUN_MULTIPLIER if (keys[K_LSHIFT] or keys[K_RSHIFT]) else 1.0
            speed = MOVE_SPEED * mult

            # === MOVIMENTO RELATIVO À CÂMERA ===
            yaw = math.radians(camera_rot_y)

            forward_x = math.sin(yaw)
            forward_z = -math.cos(yaw)
            right_x   = math.cos(yaw)
            right_z   = math.sin(yaw)

            input_forward = 0.0
            input_strafe  = 0.0
            if keys[K_w]:
                input_forward += 1.0
            if keys[K_s]:
                input_forward -= 1.0
            if keys[K_d]:
                input_strafe += 1.0
            if keys[K_a]:
                input_strafe -= 1.0

            move_x = forward_x * input_forward + right_x * input_strafe
            move_z = forward_z * input_forward + right_z * input_strafe

            norm = math.hypot(move_x, move_z)
            if norm > 0.0:
                move_x = (move_x / norm) * speed
                move_z = (move_z / norm) * speed
            else:
                move_x, move_z = 0.0, 0.0

            # Aplica movimento (e conta movimentos se necessário - embora o Sokoban tradicional só conte empurrões)
            mover_player(move_x, move_z, dt)

            # empurrar caixas
            if keys[K_SPACE]:
                empurrar_caixa(t)
            
            # Limpa partículas antigas
            particulas_sucesso = [p for p in particulas_sucesso if (t - p[3]) < 2.0]

            # Renderização 3D e HUD
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Câmera: primeira pessoa
            glRotatef(camera_rot_x, 1, 0, 0)
            glRotatef(camera_rot_y, 0, 1, 0)
            glTranslatef(-player_x, -PLAYER_ALTURA_Olhos, -player_z)
            
            desenhar_cena(t)
            desenhar_hud_completo()
            desenhar_crosshair()  # Adiciona a crosshair
            
            
        elif game_state == GAME_STATE_WIN:
            # Renderização de Vitória
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glRotatef(camera_rot_x, 1, 0, 0)
            glRotatef(camera_rot_y, 0, 1, 0)
            glTranslatef(-player_x, -PLAYER_ALTURA_Olhos, -player_z)
            
            desenhar_cena(t) # Desenha a cena final
            desenhar_tela_vitoria()

            # Desativa mouse look
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)

        elif game_state == GAME_STATE_FINAL_VICTORY:
            # Estado de vitória final (todos os níveis completos)
            desenhar_tela_vitoria_final()

            # Desativa mouse look
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)

        elif game_state == GAME_STATE_MENU:
            # Renderização do Menu
            desenhar_menu_principal()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()