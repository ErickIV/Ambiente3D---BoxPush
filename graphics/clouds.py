"""
graphics/clouds.py
==================
Sistema de nuvens procedurais para ambiente 3D.
Implementa nuvens animadas leves e eficientes usando técnicas de computação gráfica.

ARQUITETURA:
-----------
- Cloud: Classe individual representando uma nuvem com posição e movimento
- CloudSystem: Gerenciador de todas as nuvens com textura compartilhada

TÉCNICAS GRÁFICAS:
-----------------
1. Billboard Rendering: Quads 2D que sempre rotacionam para encarar a câmera
   - Calcula ângulo entre câmera e nuvem usando atan2
   - Aplica rotação no eixo Y para manter orientação frontal
   
2. Textura Procedimental: Geração algorítmica sem arquivos externos
   - Gradiente radial baseado em distância euclidiana do centro
   - Ruído pseudo-aleatório usando funções trigonométricas
   - Alpha channel para transparência suave nas bordas
   
3. Sistema de Animação: Movimento orgânico baseado em funções senoidais
   - Movimento principal no eixo X (sin)
   - Deriva lateral no eixo Z (cos)
   - Time offset para dessincronizar cada nuvem
   
4. Distribuição Espacial: Anel uniforme ao redor do jogador
   - 360° de cobertura usando coordenadas polares
   - Raio variável para profundidade visual
   
5. Alpha Blending: Transparência com mistura de cores
   - glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
   - Desabilita depth write para evitar oclusão entre nuvens

OTIMIZAÇÕES:
-----------
- Textura única compartilhada por todas as nuvens
- Geometria simples (1 quad por nuvem)
- Sem sombras dinâmicas (mantém performance)
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math


class Cloud:
    """Representa uma nuvem individual no céu"""
    
    def __init__(self, x, y, z, size, speed):
        """
        Inicializa uma nuvem
        
        Args:
            x, y, z: Posição inicial
            size: Tamanho da nuvem (escala)
            speed: Velocidade de movimento
        """
        self.initial_x = x
        self.initial_z = z
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.speed = speed
        self.time_offset = random.uniform(0, 100)  # Offset de tempo aleatório
    
    def update(self, dt, wind_speed=1.0, total_time=0.0):
        """
        Atualiza posição da nuvem (movimento do vento)
        
        Args:
            dt: Delta time (tempo desde último frame)
            wind_speed: Multiplicador de velocidade do vento
            total_time: Tempo total desde início
        """
        # Movimento em órbita circular lenta + deslocamento linear
        t = (total_time + self.time_offset) * self.speed * wind_speed * 0.1
        
        # Movimento em X (vento principal)
        self.x = self.initial_x + math.sin(t) * 10
        
        # Movimento em Z (deriva lateral)
        self.z = self.initial_z + math.cos(t) * 5


class CloudSystem:
    """Sistema de gerenciamento de nuvens"""
    
    def __init__(self, num_clouds=12, wind_speed=0.5):
        """
        Inicializa o sistema de nuvens
        
        Args:
            num_clouds: Quantidade de nuvens no céu
            wind_speed: Velocidade base do vento
        """
        self.clouds = []
        self.wind_speed = wind_speed
        self.texture_id = None
        self.total_time = 0.0  # Tempo acumulado para animação
        
        # Gera nuvens distribuídas em círculo (360°)
        for i in range(num_clouds):
            # Distribuição em anel ao redor do jogador
            angle = (i / num_clouds) * 2 * math.pi
            radius = random.uniform(25, 40)  # Distância do centro
            
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            y = random.uniform(12, 18)  # Altura no céu
            
            size = random.uniform(4, 8)
            speed = random.uniform(0.5, 1.2)
            
            self.clouds.append(Cloud(x, y, z, size, speed))
        
        # Cria textura procedimental
        self._create_cloud_texture()
    
    def _create_cloud_texture(self):
        """
        Cria uma textura procedimental para as nuvens
        Usa gradiente radial com ruído para aparência orgânica
        """
        size = 128
        texture_data = []
        
        for y in range(size):
            for x in range(size):
                # Coordenadas normalizadas (-1 a 1)
                nx = (x / size) * 2 - 1
                ny = (y / size) * 2 - 1
                
                # Distância do centro (gradiente radial)
                dist = math.sqrt(nx*nx + ny*ny)
                
                # Adiciona ruído pseudo-aleatório
                noise = math.sin(x * 0.1) * math.cos(y * 0.1) * 0.2
                
                # Alpha baseado na distância (fade nas bordas)
                alpha = max(0.0, min(1.0, 1.0 - dist + noise))
                alpha = int(alpha * 255)
                
                # Cor branca com alpha variável
                texture_data.extend([255, 255, 255, alpha])
        
        # Cria textura OpenGL
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Parâmetros da textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        # Upload da textura para GPU
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, bytes(texture_data)
        )
    
    def update(self, dt):
        """
        Atualiza todas as nuvens
        
        Args:
            dt: Delta time
        """
        self.total_time += dt
        for cloud in self.clouds:
            cloud.update(dt, self.wind_speed, self.total_time)
    
    def render(self, camera_pos):
        """
        Renderiza todas as nuvens (billboards de frente para câmera)
        
        Args:
            camera_pos: Posição da câmera (para billboard)
        """
        # Habilita blending para transparência
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Desabilita depth write (nuvens não devem bloquear outras nuvens)
        glDepthMask(GL_FALSE)
        
        # Habilita textura
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Material das nuvens (branco brilhante)
        glColor4f(1.0, 1.0, 1.0, 0.8)
        
        for cloud in self.clouds:
            glPushMatrix()
            
            # Posição da nuvem (já atualizada com movimento)
            pos_x = cloud.x
            pos_y = cloud.y
            pos_z = cloud.z
            
            glTranslatef(pos_x, pos_y, pos_z)
            
            # Billboard: calcula vetor da câmera para a nuvem
            dx = camera_pos[0] - pos_x
            dz = camera_pos[2] - pos_z
            angle = math.degrees(math.atan2(dx, dz))
            
            # Rotaciona para encarar a câmera
            glRotatef(angle, 0, 1, 0)
            
            # Escala
            s = cloud.size
            
            # Desenha quad (plano retangular)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex3f(-s, -s*0.5, 0)
            glTexCoord2f(1, 0); glVertex3f( s, -s*0.5, 0)
            glTexCoord2f(1, 1); glVertex3f( s,  s*0.5, 0)
            glTexCoord2f(0, 1); glVertex3f(-s,  s*0.5, 0)
            glEnd()
            
            glPopMatrix()
        
        # Restaura estados OpenGL
        glDisable(GL_TEXTURE_2D)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
    
    def cleanup(self):
        """Libera recursos da GPU"""
        if self.texture_id:
            glDeleteTextures([self.texture_id])
