"""
utils/sound.py
==============
Sistema de som sintetizado para o jogo.
Gera sons proceduralmente sem necessidade de arquivos de áudio.

TÉCNICAS DE SÍNTESE DE ÁUDIO:
-----------------------------
1. Ondas Senoidais: Sons suaves para efeitos básicos
2. Ondas Quadradas: Sons 8-bit retro para músicas
3. Envelope ADSR: Controle de ataque/decaimento/sustain/release
4. Sequenciamento de Notas: Sistema de composição musical procedural

CARACTERÍSTICAS:
---------------
- Padrão Singleton para instância única global
- Geração em tempo de inicialização (não runtime)
- Sistema de buffers para prevenir garbage collection
- Controles independentes para música e efeitos sonoros
- Músicas únicas por fase + menu

SONS IMPLEMENTADOS:
------------------
- Efeitos: push, step, blocked, box_on_target, victory, menu_select, level_start
- Músicas: 5 trilhas de fase + 1 trilha de menu (estilo 8-bit)
"""

import numpy as np
import pygame


class SoundManager:
    """Gerenciador de sons sintetizados"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Garante que existe apenas uma instância (Singleton)"""
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o sistema de som"""
        # Evita re-inicialização
        if SoundManager._initialized:
            return
        
        self.enabled = False
        self.sounds = {}
        self._sound_buffers = []  # Mantém referências aos arrays numpy
        self.music_tracks = {}  # Músicas de fundo
        self.current_music = None
        self.current_music_key = None  # Armazena qual música está tocando
        self.current_music_volume = 0.2  # Volume atual da música
        
        # Controles de áudio
        self.music_enabled = True
        self.sfx_enabled = True
        
        try:
            # Verifica se pygame já foi inicializado
            if not pygame.get_init():
                pygame.init()
            
            # Reinicializa mixer com configurações específicas
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            self._generate_all_sounds()
            self._generate_music_tracks()
            self.enabled = True
            SoundManager._initialized = True
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _generate_tone(self, frequency, duration, volume=0.3):
        """
        Gera um tom simples.
        
        Args:
            frequency: Frequência em Hz
            duration: Duração em segundos
            volume: Volume (0.0 a 1.0)
            
        Returns:
            pygame.Sound ou None
        """
        try:
            sample_rate = 22050
            n_samples = int(duration * sample_rate)
            
            # Gera onda senoidal
            buf = np.sin(2 * np.pi * frequency * np.linspace(0, duration, n_samples))
            
            # Aplica envelope ADSR simples para evitar clicks
            attack = int(n_samples * 0.1)
            release = int(n_samples * 0.2)
            
            for i in range(attack):
                buf[i] *= i / attack
            for i in range(release):
                buf[-(i+1)] *= i / release
            
            # Converte para int16 e aplica volume
            buf = (buf * volume * 32767).astype(np.int16)
            
            # Cria som estéreo
            buf_stereo = np.column_stack((buf, buf))
            
            sound = pygame.sndarray.make_sound(buf_stereo)
            # Mantém referência ao buffer para evitar garbage collection
            self._sound_buffers.append(buf_stereo)
            
            return sound
        except Exception as e:
            return None
    
    def _generate_push_sound(self):
        """Gera som de empurrar caixa"""
        return self._generate_tone(200, 0.1, 0.4)
    
    def _generate_step_sound(self):
        """Gera som de passo"""
        return self._generate_tone(150, 0.05, 0.2)
    
    def _generate_box_on_target_sound(self):
        """Gera som de caixa no objetivo"""
        # Tom ascendente
        sample_rate = 22050
        duration = 0.3
        n_samples = int(duration * sample_rate)
        
        # Frequências crescentes
        freq_start = 400
        freq_end = 800
        frequencies = np.linspace(freq_start, freq_end, n_samples)
        
        buf = np.sin(2 * np.pi * frequencies * np.linspace(0, duration, n_samples))
        
        # Envelope
        envelope = np.linspace(1.0, 0.0, n_samples)
        buf *= envelope
        
        buf = (buf * 0.3 * 32767).astype(np.int16)
        buf_stereo = np.column_stack((buf, buf))
        
        sound = pygame.sndarray.make_sound(buf_stereo)
        self._sound_buffers.append(buf_stereo)
        return sound
    
    def _generate_victory_sound(self):
        """Gera som de vitória"""
        # Acorde maior (C-E-G)
        sample_rate = 22050
        duration = 0.5
        n_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, n_samples)
        
        # Três notas do acorde
        note1 = np.sin(2 * np.pi * 523 * t)  # C5
        note2 = np.sin(2 * np.pi * 659 * t)  # E5
        note3 = np.sin(2 * np.pi * 784 * t)  # G5
        
        buf = (note1 + note2 + note3) / 3
        
        # Envelope de saída
        envelope = np.linspace(1.0, 0.0, n_samples)
        buf *= envelope
        
        buf = (buf * 0.4 * 32767).astype(np.int16)
        buf_stereo = np.column_stack((buf, buf))
        
        sound = pygame.sndarray.make_sound(buf_stereo)
        self._sound_buffers.append(buf_stereo)
        return sound
    
    def _generate_blocked_sound(self):
        """Gera som de bloqueio"""
        return self._generate_tone(100, 0.15, 0.3)
    
    def _generate_menu_select_sound(self):
        """Gera som de seleção de menu"""
        return self._generate_tone(600, 0.05, 0.2)
    
    def _generate_level_start_sound(self):
        """Gera som de início de nível"""
        return self._generate_tone(440, 0.2, 0.3)
    
    def _generate_all_sounds(self):
        """Gera todos os sons do jogo"""
        self.sounds['push'] = self._generate_push_sound()
        self.sounds['step'] = self._generate_step_sound()
        self.sounds['box_on_target'] = self._generate_box_on_target_sound()
        self.sounds['victory'] = self._generate_victory_sound()
        self.sounds['blocked'] = self._generate_blocked_sound()
        self.sounds['menu_select'] = self._generate_menu_select_sound()
        self.sounds['level_start'] = self._generate_level_start_sound()
    
    def _generate_music_note_sequence(self, notes, tempo=120):
        """
        Gera sequência de notas musicais estilo 8-bit.
        
        Args:
            notes: Lista de tuplas (frequência_Hz, duração_beats) ou None para pausa
            tempo: BPM (batidas por minuto)
            
        Returns:
            pygame.Sound
        """
        sample_rate = 22050
        beat_duration = 60.0 / tempo  # Duração de uma batida em segundos
        
        all_samples = []
        
        for note in notes:
            if note is None or note[0] is None:
                # Pausa
                duration = beat_duration * (note[1] if note else 0.25)
                n_samples = int(duration * sample_rate)
                samples = np.zeros(n_samples, dtype=np.int16)
            else:
                freq, beats = note
                duration = beat_duration * beats
                n_samples = int(duration * sample_rate)
                
                # Onda quadrada para som 8-bit
                t = np.linspace(0, duration, n_samples)
                wave = np.sign(np.sin(2 * np.pi * freq * t))
                
                # Envelope simples
                envelope = np.ones(n_samples)
                fade_samples = int(0.01 * sample_rate)  # 10ms fade
                envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
                
                samples = (wave * envelope * 0.15 * 32767).astype(np.int16)
            
            all_samples.append(samples)
        
        # Concatena todas as notas
        full_wave = np.concatenate(all_samples)
        buf_stereo = np.column_stack((full_wave, full_wave))
        
        sound = pygame.sndarray.make_sound(buf_stereo)
        self._sound_buffers.append(buf_stereo)
        return sound
    
    def _generate_music_tracks(self):
        """Gera músicas de fundo estilo 8-bit para cada fase"""
        # Frequências das notas (em Hz)
        C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
        C5, D5, E5, F5, G5 = 523.25, 587.33, 659.25, 698.46, 783.99
        
        # Fase 1: Melodia alegre e simples
        track1 = [
            (C4, 0.5), (E4, 0.5), (G4, 0.5), (C5, 0.5),
            (E5, 0.25), (G4, 0.25), (C5, 0.5), (G4, 0.5),
            (C4, 0.5), (E4, 0.5), (G4, 0.5), (E4, 0.5),
            (C4, 1.0), (None, 0.5),
        ]
        
        # Fase 2: Mais rápida e energética
        track2 = [
            (G4, 0.25), (A4, 0.25), (B4, 0.25), (C5, 0.25),
            (D5, 0.5), (C5, 0.25), (B4, 0.25),
            (A4, 0.5), (G4, 0.5),
            (E4, 0.25), (G4, 0.25), (C5, 0.5),
            (G4, 1.0), (None, 0.5),
        ]
        
        # Fase 3: Misteriosa
        track3 = [
            (A4, 0.5), (None, 0.25), (A4, 0.25),
            (G4, 0.5), (F4, 0.5),
            (E4, 0.75), (None, 0.25),
            (D4, 0.5), (E4, 0.5),
            (F4, 1.0), (None, 0.5),
        ]
        
        # Fase 4: Desafiadora
        track4 = [
            (C5, 0.25), (B4, 0.25), (A4, 0.25), (G4, 0.25),
            (A4, 0.5), (C5, 0.5),
            (E5, 0.25), (D5, 0.25), (C5, 0.5),
            (G4, 0.75), (None, 0.25),
            (F4, 0.5), (E4, 0.5),
            (D4, 1.0), (None, 0.5),
        ]
        
        # Fase 5 (final): Épica
        track5 = [
            (C5, 0.5), (G4, 0.25), (C5, 0.25),
            (E5, 0.5), (D5, 0.5),
            (C5, 0.25), (D5, 0.25), (E5, 0.25), (F5, 0.25),
            (G5, 1.0),
            (E5, 0.5), (C5, 0.5),
            (G4, 1.0), (None, 0.5),
        ]
        
        # Gera todas as músicas
        self.music_tracks[0] = self._generate_music_note_sequence(track1, tempo=140)
        self.music_tracks[1] = self._generate_music_note_sequence(track2, tempo=160)
        self.music_tracks[2] = self._generate_music_note_sequence(track3, tempo=120)
        self.music_tracks[3] = self._generate_music_note_sequence(track4, tempo=150)
        self.music_tracks[4] = self._generate_music_note_sequence(track5, tempo=130)
        
        # Música do menu: Cativante e chamativa
        menu_track = [
            (C5, 0.5), (E5, 0.5), (G5, 0.5), (E5, 0.5),
            (D5, 0.5), (F5, 0.5), (A4, 0.5), (D5, 0.5),
            (C5, 0.5), (E5, 0.5), (G5, 1.0),
            (None, 0.5),
            (G4, 0.25), (A4, 0.25), (B4, 0.25), (C5, 0.25),
            (D5, 0.5), (C5, 0.5), (B4, 0.5), (A4, 0.5),
            (G4, 1.5),
            (None, 0.5),
        ]
        self.music_tracks['menu'] = self._generate_music_note_sequence(menu_track, tempo=150)
    
    def play_music(self, level_index, is_menu=False):
        """
        Toca música de fundo para uma fase específica ou menu.
        
        Args:
            level_index: Índice da fase (0-based) ou 'menu'
            is_menu: Se True, toca música do menu com volume maior
        """
        if not self.enabled:
            return
        
        if is_menu or level_index == 'menu':
            # Música do menu
            music = self.music_tracks.get('menu')
            volume = 0.4  # 40% para o menu (mais alta)
            music_key = 'menu'
        else:
            # Usa módulo para repetir músicas se houver mais fases que músicas
            track_index = level_index % 5  # 5 músicas de fases
            music = self.music_tracks.get(track_index)
            volume = 0.2  # 20% para as fases (baixinha)
            music_key = track_index
        
        if music:
            try:
                # Para música atual se houver
                if self.current_music:
                    self.current_music.stop()
                
                # Armazena qual música está tocando
                self.current_music_key = music_key
                self.current_music_volume = volume
                
                # Só toca se música estiver habilitada
                if self.music_enabled:
                    music.set_volume(volume)
                    music.play(loops=-1)  # -1 = loop infinito
                    self.current_music = music
                else:
                    self.current_music = music  # Armazena mas não toca
            except Exception as e:
                print(f"⚠️ Erro ao tocar música: {e}")
    
    def stop_music(self):
        """Para a música de fundo"""
        if self.enabled and self.current_music:
            try:
                self.current_music.stop()
                self.current_music = None
            except Exception as e:
                pass
    
    def set_music_volume(self, volume):
        """
        Define volume da música.
        
        Args:
            volume: Volume de 0.0 a 1.0
        """
        if self.enabled and self.current_music:
            try:
                self.current_music.set_volume(volume)
            except Exception as e:
                pass
    
    def play(self, sound_name):
        """
        Toca um som.
        
        Args:
            sound_name: Nome do som a tocar
        """
        if not self.enabled or not self.sfx_enabled:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                pass
    
    def toggle_music(self):
        """Liga/desliga música de fundo"""
        if not self.enabled:
            return False
        
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            # Religa música
            if self.current_music:
                try:
                    self.current_music.set_volume(self.current_music_volume)
                    self.current_music.play(loops=-1)
                except:
                    pass
        else:
            # Desliga música
            if self.current_music:
                try:
                    self.current_music.stop()
                except:
                    pass
        
        return self.music_enabled
    
    def toggle_sfx(self):
        """Liga/desliga sons de efeito"""
        if not self.enabled:
            return False
        
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled
    
    def stop_all(self):
        """Para todos os sons"""
        if self.enabled:
            pygame.mixer.stop()
    
    def set_volume(self, volume):
        """
        Define volume global.
        
        Args:
            volume: Volume de 0.0 a 1.0
        """
        if self.enabled:
            pygame.mixer.music.set_volume(volume)


# Instância global
_sound_manager = None


def get_sound_manager():
    """Retorna instância global do gerenciador de som"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager
