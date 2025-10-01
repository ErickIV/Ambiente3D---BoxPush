# ambiente3d.py
# Ambiente 3D didático para Computação Gráfica / RV
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
import sys
glutInit(sys.argv)  # <<< inicializa GLUT cedo

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
camera_rot_x = 0.0  # pitch
camera_rot_y = 0.0  # yaw

player_x, player_y, player_z = 0.0, 0.0, 0.0

paredes = []   # lista de tuplas (x,y,z) centradas no grid
caixas = []    # idem
objetivos = [] # idem

_last_push_time = 0.0

# -----------------------------
# Utilidades de Mundo / Geometria
# -----------------------------
def grid_round(v):
    return int(round(v))

def aabb_colide_ponto(px, pz, cx, cz, half=0.5, raio=PLAYER_RAIO):
    """
    Teste simples de colisão no plano XZ entre um círculo (player) e AABB (bloco centrado em cx,cz).
    """
    # limites do AABB
    minx = cx - half
    maxx = cx + half
    minz = cz - half
    maxz = cz + half

    # clampa ponto ao AABB
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
    # Usa EXATAMENTE a mesma lógica do movimento
    yaw = math.radians(camera_rot_y)
    forward_x = math.sin(yaw)
    forward_z = -math.cos(yaw)  # mesma fórmula do movimento
    
    # Converte para direção cardinal mais próxima
    if abs(forward_x) > abs(forward_z):
        dir_x = 1 if forward_x > 0 else -1
        dir_z = 0
    else:
        dir_x = 0
        dir_z = 1 if forward_z > 0 else -1
    return dir_x, dir_z

# -----------------------------
# Cena / Mundo
# -----------------------------
def criar_mundo():
    global paredes, caixas, objetivos, player_x, player_y, player_z, camera_rot_x, camera_rot_y

    paredes = []
    caixas = []
    objetivos = []

    # bordas - "arena" quadrada de -10..10
    for i in range(-10, 11):
        paredes.append((i, 0, -10))
        paredes.append((i, 0, 10))
        paredes.append((-10, 0, i))
        paredes.append((10, 0, i))

    # algumas paredes internas
    for i in range(-6, 7):
        if i not in (-1, 0, 1):
            paredes.append((i, 0, -2))
    for i in range(-6, 7, 2):
        paredes.append((3, 0, i))
    for i in range(-4, 5):
        paredes.append((-4, 0, i))

    # caixas iniciais (em células livres)
    caixas.extend([(0, 0, 2), (2, 0, 3), (-2, 0, -1), (5, 0, 0)])

    # objetivos (alvos) onde você deve empurrar caixas
    objetivos.extend([(6, 0, 0), (-6, 0, 0), (0, 0, -6), (0, 0, 6)])

    # player spawn
    player_x, player_y, player_z = 0.0, 0.0, 0.0
    camera_rot_x, camera_rot_y = 0.0, 0.0

# -----------------------------
# Desenho (OpenGL)
# -----------------------------
def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # iluminação
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (4.0, 6.0, 3.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.25, 0.25, 0.25, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (0.85, 0.85, 0.85, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.2, 0.2, 0.2, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 8.0)

    glClearColor(0.55, 0.78, 0.95, 1.0)  # céu

def aplicar_perspectiva(w, h):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, (w / float(h)), NEAR, FAR)
    glMatrixMode(GL_MODELVIEW)

def desenhar_cubo_unitario():
    # Cubo centrado na origem, aresta 1.0
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

def desenhar_chao():
    glDisable(GL_LIGHTING)
    glColor3f(0.35, 0.55, 0.35)
    glBegin(GL_QUADS)
    s = 40.0
    glVertex3f(-s, -1.0, -s)
    glVertex3f(-s, -1.0,  s)
    glVertex3f( s, -1.0,  s)
    glVertex3f( s, -1.0, -s)
    glEnd()
    glEnable(GL_LIGHTING)

def desenhar_parede(x, y, z):
    glPushMatrix()
    glTranslatef(x, y + 0.5, z)
    glScalef(1.0, 2.0, 1.0)
    glColor3f(0.35, 0.35, 0.37)
    desenhar_cubo_unitario()
    glPopMatrix()

def desenhar_objetivo(x, y, z):
    glPushMatrix()
    glTranslatef(x, y + 0.02, z)
    glDisable(GL_LIGHTING)
    glColor3f(0.1, 0.7, 1.0)  # azul claro
    
    # Círculo azul no chão
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, -0.98, 0)
    r = 0.4
    for i in range(0, 361, 12):
        ang = math.radians(i)
        glVertex3f(math.cos(ang) * r, -0.98, math.sin(ang) * r)
    glEnd()
    
    # Desenha um "X" vermelho para marcar o objetivo
    glColor3f(1.0, 0.0, 0.0)  # vermelho
    glLineWidth(4.0)
    glBegin(GL_LINES)
    # Linha diagonal 1
    glVertex3f(-0.3, -0.96, -0.3)
    glVertex3f(0.3, -0.96, 0.3)
    # Linha diagonal 2
    glVertex3f(0.3, -0.96, -0.3)
    glVertex3f(-0.3, -0.96, 0.3)
    glEnd()
    glLineWidth(1.0)
    
    glEnable(GL_LIGHTING)
    glPopMatrix()

def desenhar_caixa(x, y, z):
    glPushMatrix()
    glTranslatef(x, y + 0.5, z)
    glScalef(1.0, 1.0, 1.0)
    
    # Verifica se esta caixa está na frente do player
    dir_x, dir_z = direcao_frente_cardinal()
    px, pz = grid_round(player_x), grid_round(player_z)
    caixa_na_frente = (px + dir_x, 0, pz + dir_z)
    
    # Define cor e material baseado no estado
    if (x, y, z) == caixa_na_frente:
        destino = (x + dir_x, y, z + dir_z)
        pode_empurrar = (destino not in caixas) and (destino not in paredes) and abs(destino[0]) < 10 and abs(destino[2]) < 10
        
        if pode_empurrar:
            # Verde empurrável
            cor = (0.2, 0.9, 0.2, 1.0)
        else:
            # Vermelho bloqueado
            cor = (0.9, 0.2, 0.2, 1.0)
    else:
        # Marrom padrão
        cor = (0.72, 0.48, 0.16, 1.0)
    
    # Configura material para refletir a cor desejada
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, cor)
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, cor)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)
    
    desenhar_cubo_unitario()
    glPopMatrix()

def desenhar_player_casco():
    # opcional: visualizar o corpo do player (útil em terceira pessoa)
    glPushMatrix()
    glTranslatef(player_x, player_y + 0.9, player_z)
    glColor3f(1.0, 0.7, 0.2)
    glutSolidSphere(0.3, 16, 16)
    glPopMatrix()

def desenhar_cena():
    desenhar_chao()
    # paredes
    for (x, y, z) in paredes:
        desenhar_parede(x, y, z)
    # objetivos (desenhados sob as caixas)
    for (x, y, z) in objetivos:
        desenhar_objetivo(x, y, z)
    # caixas
    for (x, y, z) in caixas:
        desenhar_caixa(x, y, z)

# -----------------------------
# HUD (texto 2D via GLUT)
# -----------------------------
def draw_text_2d(x, y, text, size=18):
    # usa projeção ortográfica no tamanho da tela
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

# -----------------------------
# Movimento / Entrada
# -----------------------------
def pode_mover_para(nx, nz):
    # colisão contra cada bloco sólido (paredes e caixas)
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
    # Testa colisão no destino completo
    if pode_mover_para(nx, nz):
        player_x = nx
        player_z = nz
    else:
        # Tenta mover só X
        if pode_mover_para(nx, player_z):
            player_x = nx
        # Tenta mover só Z
        elif pode_mover_para(player_x, nz):
            player_z = nz

def empurrar_caixa(t):
    global caixas, _last_push_time
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
            # segurança: não deixa empurrar contra a borda imediatamente
            if abs(destino[0]) < 10 and abs(destino[2]) < 10:
                idx = caixas.index(frente)
                caixas[idx] = destino

# -----------------------------
# Loop Principal
# -----------------------------
def main():
    global camera_rot_x, camera_rot_y
    global player_x, player_y, player_z

    pygame.init()
    pygame.display.set_caption("Ambiente 3D - CG/RV - Pygame + PyOpenGL")
    pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), DOUBLEBUF | OPENGL)
    glutInit(sys.argv)

    init_opengl()
    aplicar_perspectiva(LARGURA_TELA, ALTURA_TELA)

    criar_mundo()

    clock = pygame.time.Clock()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))

    running = True
    while running:
        # dt com clamp para evitar "saltos" em pausas/debug
        dt_ms = clock.tick(120)
        dt = min(dt_ms / 1000.0, 0.033)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_r:
                    criar_mundo()

            elif event.type == VIDEORESIZE:
                w, h = event.size
                # (opcional) adaptar para janela redimensionável

        # mouse look (relativo ao centro)
        mx, my = pygame.mouse.get_pos()
        dx = mx - (LARGURA_TELA // 2)
        dy = my - (ALTURA_TELA // 2)
        camera_rot_y += dx * MOUSE_SENS
        camera_rot_x -= dy * MOUSE_SENS
        camera_rot_x = max(-89.0, min(89.0, camera_rot_x))
        # recentraliza mouse
        pygame.mouse.set_pos((LARGURA_TELA // 2, ALTURA_TELA // 2))

        keys = pygame.key.get_pressed()
        mult = RUN_MULTIPLIER if (keys[K_LSHIFT] or keys[K_RSHIFT]) else 1.0
        speed = MOVE_SPEED * mult

        # === MOVIMENTO RELATIVO À CÂMERA (CORRIGIDO) ===
        yaw = math.radians(camera_rot_y)

        # Vetores forward/right no plano XZ (ignorando pitch)
        forward_x = math.sin(yaw)
        forward_z = -math.cos(yaw)    # <-- CORREÇÃO: -cos para alinhar com view (yaw==0 => -Z)
        right_x   = math.cos(yaw)
        right_z   = math.sin(yaw)

        # Leitura de entrada (mapear para forward/strafe)
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

        # Combina inputs em vetor world-space
        move_x = forward_x * input_forward + right_x * input_strafe
        move_z = forward_z * input_forward + right_z * input_strafe

        # Normaliza para evitar movimento diagonal mais rápido
        norm = math.hypot(move_x, move_z)
        if norm > 0.0:
            move_x = (move_x / norm) * speed   # 'speed' é MOVE_SPEED * mult
            move_z = (move_z / norm) * speed
        else:
            move_x = 0.0
            move_z = 0.0

        # Aplica movimento
        mover_player(move_x, move_z, dt)
        # === fim do bloco de movimento ===

        # empurrar caixas
        if keys[K_SPACE]:
            empurrar_caixa(pygame.time.get_ticks() / 1000.0)

        # Renderização 3D
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Câmera: primeira pessoa
        glRotatef(camera_rot_x, 1, 0, 0)
        glRotatef(camera_rot_y, 0, 1, 0)
        glTranslatef(-player_x, -PLAYER_ALTURA_Olhos, -player_z)
        desenhar_cena()

        # HUD (texto 2D)
        caixas_ok = sum([c in objetivos for c in caixas])
        draw_text_2d(20, ALTURA_TELA - 36, "WASD: mover | Mouse: olhar | Espaço: empurrar | R: reset | ESC: sair")
        draw_text_2d(20, ALTURA_TELA - 68, f"Caixas nos objetivos: {caixas_ok}/{len(caixas)}")

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()