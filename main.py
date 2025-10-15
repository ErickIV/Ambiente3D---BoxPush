"""
main.py
=======
BoxPush 3D - Jogo Sokoban em 3D
Ponto de entrada principal do jogo.

ARQUITETURA DO PROJETO:
-----------------------
- main.py: Loop principal, gerenciamento de estados e eventos
- game/: Lógica do jogo (níveis, física, jogador)
- graphics/: Sistema de renderização 3D (OpenGL)
- utils/: Utilitários (sistema de som procedural)
- config.py: Constantes e configurações

PADRÕES DE PROJETO UTILIZADOS:
------------------------------
- MVC (Model-View-Controller): Separação entre lógica e renderização
- Singleton: Gerenciador de som com instância única
- State Pattern: Estados do jogo (menu, jogando, vitória)

TECNOLOGIAS:
-----------
- Pygame: Janela, eventos e áudio
- PyOpenGL: Renderização 3D com pipeline OpenGL
- NumPy: Geração procedural de sons

Controles:
- WASD: Movimento
- SHIFT: Correr
- Mouse: Olhar ao redor
- ESPAÇO: Empurrar caixa
- R: Reiniciar nível
- M: Música ON/OFF
- N: Sons ON/OFF
- T: Teleporte de emergência
- ESC: Sair/Menu
- ENTER: Avançar nível/Iniciar
"""

import sys
import pygame
from pygame.locals import *
from OpenGL.GLUT import glutInit

# Importa módulos do jogo
from config import *
from graphics.renderer import Renderer
from game.player import Player
from game.level import Level
from game.levels_data import get_level_count
from utils.sound import get_sound_manager


class GameState:
    """Gerenciador de estados do jogo"""
    
    def __init__(self):
        self.state = GAME_STATE_MENU
        self.last_push_time = 0.0
        self.victory_time = 0.0
    
    def is_menu(self):
        return self.state == GAME_STATE_MENU
    
    def is_playing(self):
        return self.state == GAME_STATE_PLAYING
    
    def is_victory(self):
        return self.state == GAME_STATE_WIN
    
    def is_final_victory(self):
        return self.state == GAME_STATE_FINAL_VICTORY
    
    def set_menu(self):
        self.state = GAME_STATE_MENU
    
    def set_playing(self):
        self.state = GAME_STATE_PLAYING
    
    def set_victory(self, current_time):
        self.state = GAME_STATE_WIN
        self.victory_time = current_time
    
    def set_final_victory(self):
        self.state = GAME_STATE_FINAL_VICTORY


class Game:
    """Classe principal do jogo"""
    
    def __init__(self):
        """Inicializa o jogo"""
        # Inicializa Pygame
        pygame.init()
        glutInit(sys.argv)
        
        # Inicializa sistema de som
        self.sound = get_sound_manager()
        
        # Cria janela
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_mode(
            (self.window_width, self.window_height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )
        
        # Inicializa OpenGL
        Renderer.init_opengl()
        Renderer.set_perspective(self.window_width, self.window_height)
        
        # Objetos do jogo
        self.player = Player()
        self.level = Level()
        self.game_state = GameState()
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Mouse
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        
        # Inicia música do menu
        self.sound.play_music('menu', is_menu=True)
    
    def handle_events(self):
        """Processa eventos do Pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                # ESC sempre sai
                if event.key == K_ESCAPE:
                    return False
                
                # R: Reset nível (apenas durante jogo)
                elif event.key == K_r and self.game_state.is_playing():
                    self.level.reload_current_level()
                    self.player.set_position(*self.level.spawn_position)
                    self.player.reset_camera()
                    # Reinicia música da fase atual
                    self.sound.play_music(self.level.current_level_index)
                
                # T: Teleporte de emergência (caso fique preso na parede)
                elif event.key == K_t and self.game_state.is_playing():
                    self.player.set_position(*self.level.spawn_position)
                    self.player.reset_camera()
                
                # M: Toggle música de fundo
                elif event.key == K_m:
                    self.sound.toggle_music()
                
                # N: Toggle sons de efeito
                elif event.key == K_n:
                    self.sound.toggle_sfx()
                
                # ENTER: Controle de fluxo
                elif event.key == K_RETURN:
                    self.sound.play('menu_select')
                    if self.game_state.is_menu():
                        # Inicia jogo
                        self.level.load_level(0)
                        self.player.set_position(*self.level.spawn_position)
                        self.player.reset_camera()
                        self.game_state.set_playing()
                        self.sound.play('level_start')
                        self.sound.play_music(0)  # Música da fase 1
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos(
                            (self.window_width // 2, self.window_height // 2)
                        )
                    
                    elif self.game_state.is_victory():
                        # Próximo nível ou menu
                        next_index = self.level.get_next_level_index()
                        if next_index is not None:
                            self.level.load_level(next_index)
                            self.player.set_position(*self.level.spawn_position)
                            self.player.reset_camera()
                            self.game_state.set_playing()
                            self.sound.play('level_start')
                            self.sound.play_music(next_index)  # Música da próxima fase
                        else:
                            self.game_state.set_menu()
                            self.sound.stop_music()
                            self.sound.play_music('menu', is_menu=True)  # Volta música do menu
                        
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos(
                            (self.window_width // 2, self.window_height // 2)
                        )
                    
                    elif self.game_state.is_final_victory():
                        # Volta ao menu
                        self.game_state.set_menu()
                        self.sound.stop_music()
                        self.sound.play_music('menu', is_menu=True)  # Volta música do menu
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
            
            elif event.type == VIDEORESIZE:
                # Redimensionamento de janela
                self.window_width, self.window_height = event.size
                pygame.display.set_mode(
                    (self.window_width, self.window_height),
                    DOUBLEBUF | OPENGL | RESIZABLE
                )
                Renderer.set_perspective(self.window_width, self.window_height)
        
        return True
    
    def update_playing(self, dt, current_time):
        """Atualiza lógica durante o jogo"""
        # Mouse look
        mx, my = pygame.mouse.get_pos()
        dx = mx - (self.window_width // 2)
        dy = my - (self.window_height // 2)
        self.player.update_camera_rotation(dx, dy)
        pygame.mouse.set_pos((self.window_width // 2, self.window_height // 2))
        
        # Atualiza nuvens
        if self.level.clouds:
            self.level.clouds.update(dt)
        
        # Input de movimento
        keys = pygame.key.get_pressed()
        
        input_forward = 0.0
        input_strafe = 0.0
        
        if keys[K_w]:
            input_forward += 1.0
        if keys[K_s]:
            input_forward -= 1.0
        if keys[K_d]:
            input_strafe += 1.0
        if keys[K_a]:
            input_strafe -= 1.0
        
        # Movimento
        is_running = keys[K_LSHIFT] or keys[K_RSHIFT]
        self.player.move(
            input_forward, input_strafe, dt,
            self.level.walls, self.level.boxes,
            is_running, current_time
        )
        
        # Empurrar caixa
        if keys[K_SPACE]:
            if (current_time - self.game_state.last_push_time) >= PUSH_COOLDOWN:
                dir_x, dir_z = self.player.get_facing_direction()
                
                if self.level.push_box(
                    self.player.x, self.player.z,
                    dir_x, dir_z, current_time
                ):
                    self.game_state.last_push_time = current_time
                    
                    # Verifica vitória
                    if self.level.check_victory():
                        self.sound.play('victory')
                        if self.level.is_last_level():
                            self.game_state.set_final_victory()
                        else:
                            self.game_state.set_victory(current_time)
                        
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
        
        # Atualiza partículas
        self.level.update_particles(current_time, PARTICLE_LIFETIME)
    
    def render(self, current_time):
        """Renderiza frame atual"""
        if self.game_state.is_menu():
            Renderer.render_menu(self.sound)
        
        elif self.game_state.is_playing():
            Renderer.render_game_scene(self.level, self.player, current_time, self.sound)
        
        elif self.game_state.is_victory():
            Renderer.render_victory(self.level, self.player, current_time)
        
        elif self.game_state.is_final_victory():
            Renderer.render_final_victory()
        
        pygame.display.flip()
    
    def run(self):
        """Loop principal do jogo"""
        running = True
        
        while running:
            # Tempo
            dt_ms = self.clock.tick(TARGET_FPS)
            dt = min(dt_ms / 1000.0, MAX_FRAME_TIME)
            current_time = pygame.time.get_ticks() / 1000.0
            
            # Eventos
            running = self.handle_events()
            
            # Atualização
            if self.game_state.is_playing():
                self.update_playing(dt, current_time)
            
            # Renderização
            self.render(current_time)
        
        # Limpeza
        Renderer.cleanup()
        pygame.quit()


def main():
    """Função principal"""
    print("=" * 60)
    print("🎮 BOXPUSH 3D - Sokoban Game")
    print("=" * 60)
    print(f"📦 {get_level_count()} níveis disponíveis")
    print("🎯 Empurre todas as caixas para os objetivos!")
    print()
    print("Controles:")
    print("  WASD      - Mover")
    print("  SHIFT     - Correr")
    print("  Mouse     - Olhar")
    print("  ESPAÇO    - Empurrar caixa")
    print("  R         - Reiniciar nível")
    print("  M         - Música ON/OFF")
    print("  N         - Sons ON/OFF")
    print("  ENTER     - Avançar/Iniciar")
    print("  ESC       - Sair")
    print("=" * 60)
    print()
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
