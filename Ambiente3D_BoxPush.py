# ambiente3d_sokoban.py
# Ambiente 3D didático para Computação Gráfica / RV - Jogo Sokoban
# Pygame + PyOpenGL (GL + GLUT + GLU)
# Controles: WASD = mover | Mouse = olhar | Espaço = empurrar | R = reset | ESC = sair

import math
import sys
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

def aplicar_material_parede():
    # Material com aspecto de concreto
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.2, 0.2, 0.22, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.4, 0.4, 0.44, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.05, 0.05, 0.05, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 2.0)

def aplicar_material_chao():
    # Chão com aspecto de grama
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.3, 0.1, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.3, 0.6, 0.3, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 8.0)

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
PLAYER_ALTURA_Olhos = 1.8
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
    # Level 1: Simples
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
    # Level 2: Mais complexo
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

def desenhar_chao():
    aplicar_material_chao() # Usa o material definido
    glPushMatrix()
    glTranslatef(0.0, -1.0, 0.0)
    glScalef(40.0, 0.02, 40.0) # Cubo unitário achatado
    desenhar_cubo_unitario()
    glPopMatrix()
    aplicar_material_parede() # Restaura o material padrão (paredes)

def desenhar_parede(x, y, z):
    aplicar_material_parede()
    glPushMatrix()
    # Corrigido: posiciona a parede no chão (y = 0 significa base em y = -0.5)
    glTranslatef(x, y + 1.0, z)  # Mudou de y + 0.5 para y + 1.0
    glScalef(1.0, 2.0, 1.0)
    desenhar_cubo_unitario()
    glPopMatrix()

def desenhar_caixa(x, y, z):
    glPushMatrix()
    # Corrigido: posiciona a caixa no chão (y = 0 significa base em y = 0)
    glTranslatef(x, y + 1.0, z)  # Mudou de y + 0.5 para y + 1.0
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
    glPushMatrix()
    # Corrigido: mantém no nível do chão
    glTranslatef(x, y + 0.02, z)  # Mantém ligeiramente acima do chão
    glDisable(GL_LIGHTING)
    
    # Círculo azul no chão (ajustado para o nível correto)
    glColor3f(0.1, 0.7, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, -0.98, 0)  # Mantém próximo ao chão em y = -1.0
    r = 0.4
    for i in range(0, 361, 12):
        ang = math.radians(i)
        glVertex3f(math.cos(ang) * r, -0.98, math.sin(ang) * r)
    glEnd()
    
    # Desenha um "X" vermelho (mantido no mesmo nível)
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex3f(-0.3, -0.96, -0.3)
    glVertex3f(0.3, -0.96, 0.3)
    glVertex3f(0.3, -0.96, -0.3)
    glVertex3f(-0.3, -0.96, 0.3)
    glEnd()
    glLineWidth(1.0)
    
    glEnable(GL_LIGHTING)
    glPopMatrix()

def desenhar_sombra_caixa(x, y, z):
    # Corrigido: sombra no nível do chão
    glPushMatrix()
    glTranslatef(x, -0.98, z)  # Mudou de -0.99 para -0.98 (mais próximo do chão)
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
    # Corrigido: partículas começam do nível do chão
    if tempo < 2.0:  # partículas por 2 segundos
        glPushMatrix()
        glTranslatef(x, y + 2.0, z)  # Mudou de y + 1.0 para y + 2.0 (mais alto)
        glDisable(GL_LIGHTING)
        
        for i in range(8):
            ang = (i / 8.0) * 2 * math.pi
            offset = tempo * 2.0
            px = math.cos(ang + tempo * 3) * offset
            pz = math.sin(ang + tempo * 3) * offset
            py = math.sin(tempo * 5) * 0.5
            
            glColor3f(1.0, 1.0, 0.0)  # amarelo brilhante
            glPushMatrix()
            glTranslatef(px, py, pz)
            
            # Substitui glutSolidSphere por cubo pequeno para evitar o erro
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
    # Implementação do Menu Principal (Sua sugestão A)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    # Título
    draw_text_2d(LARGURA_TELA//2 - 140, ALTURA_TELA//2 + 100, "BOXPUSH 3D SOKOBAN", 24)
    draw_text_2d(LARGURA_TELA//2 - 100, ALTURA_TELA//2 + 50, "Pressione ENTER para jogar (Level 1)")
    draw_text_2d(LARGURA_TELA//2 - 80, ALTURA_TELA//2, "ESC para sair")

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

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

def desenhar_hud_completo():
    # Implementação do HUD Completo (Sua sugestão B)
    caixas_ok = sum([c in objetivos for c in caixas])
    
    # Status do jogo
    draw_text_2d(20, ALTURA_TELA - 36, "WASD: mover | Mouse: olhar | Espaço: empurrar | R: reset | ESC: sair")
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
    global caixas, _last_push_time, movimento_count, particulas_sucesso, game_state, _victory_time
    
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
                    game_state = GAME_STATE_WIN
                    _victory_time = t # Registra o tempo da vitória

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

        elif game_state == GAME_STATE_MENU:
            # Renderização do Menu
            desenhar_menu_principal()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()