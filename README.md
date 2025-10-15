# 🎮 BoxPush 3D - Sokoban Game

Um jogo Sokoban 3D desenvolvido com **Pygame + PyOpenGL** utilizando **arquitetura modular** e **boas práticas de programação**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyOpenGL](https://img.shields.io/badge/PyOpenGL-3D_Graphics-green.svg)
![Pygame](https://img.shields.io/badge/Pygame-Game_Engine-red.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📁 Estrutura do Projeto (Arquitetura Profissional)

```
Ambiente3D---BoxPush/
│
├── main.py                    # 🎮 Ponto de entrada do jogo
├── config.py                  # ⚙️ Configurações centralizadas
│
├── graphics/                  # 🎨 Módulo de Renderização
│   ├── __init__.py
│   ├── materials.py           # Materiais PBR e iluminação 3-pontos
│   ├── primitives.py          # Formas 3D + Display Lists otimizadas
│   ├── renderer.py            # Pipeline de renderização completa
│   ├── clouds.py              # Sistema de nuvens procedurais animadas
│   └── ui.py                  # HUD, menus e interface
│
├── game/                      # 🎯 Lógica do Jogo
│   ├── __init__.py
│   ├── levels_data.py         # Definição dos 5 níveis
│   ├── level.py               # Gerenciamento de níveis
│   ├── player.py              # Jogador e câmera
│   └── physics.py             # Sistema de física e colisões
│
└── utils/                     # 🔧 Utilitários
    ├── __init__.py
    └── sound.py               # Sistema de áudio procedimental (Singleton)
```

## 🌟 Características Principais

### 🏗️ Arquitetura
- ✅ **Código Modular**: Separação clara de responsabilidades
- ✅ **Alta Manutenibilidade**: Fácil localizar e corrigir bugs
- ✅ **Escalabilidade**: Adicionar features sem complicações
- ✅ **Reutilização**: Componentes podem ser usados em outros projetos
- ✅ **Testabilidade**: Cada módulo pode ser testado independentemente
- ✅ **Clean Code**: Seguindo boas práticas da indústria

### 🎨 Gráficos Avançados
- **Display Lists**: Otimização de ~90% na renderização de grama
- **Iluminação 3-Pontos**: Key Light + Fill Light + Rim Light
- **Materiais PBR-like**: Paredes, caixas e chão com materiais realistas
- **3200+ folhas de grama**: Renderizadas dinamicamente
- **Sistema de partículas**: Efeitos visuais ao completar objetivos
- **Nuvens procedurais animadas**: 15 nuvens com movimento senoidal em 360°
- **Billboard rendering**: Nuvens sempre de frente para a câmera
- **Crosshair dinâmica**: Orientação visual
- **Sombras projetadas**: Profundidade e realismo

### 🎵 Sistema de Áudio Completo
- **Síntese procedimental**: Todos os sons gerados por código (sem arquivos WAV)
- **7 efeitos sonoros**: Push, blocked, box_on_target, victory, footsteps, etc.
- **6 músicas 8-bit**: 5 trilhas de nível + 1 tema de menu (estilo Mario clássico)
- **ADSR envelope**: Ataque/decay/sustain/release para qualidade profissional
- **Controles independentes**: M (música) e N (efeitos sonoros)
- **Padrão Singleton**: Gerenciador único de áudio
- **HUD de status**: Indicadores visuais de música/sons ON/OFF

### 🎮 Jogabilidade
- **5 níveis progressivos**: Do tutorial ao desafio final
- **Física precisa**: Sistema AABB de colisões
- **Feedback visual**: Caixas mudam de cor (normal/empurrável/bloqueada/no objetivo)
- **Contador de movimentos**: Desafio adicional
- **Mouse look**: Câmera em primeira pessoa
- **Movimento suave**: Com sliding em paredes

### 🎯 Sistema de Níveis
- **Metadados**: Nome, dificuldade e estatísticas
- **Validação**: Verificação de vitória automática
- **Progressão**: Sistema de avanço de níveis
- **Reset rápido**: Tecla R para reiniciar

## 🚀 Instalação e Execução

### Pré-requisitos
```bash
Python 3.8 ou superior
```

### Instalação das Dependências
```bash
# No diretório do projeto
pip install pygame PyOpenGL PyOpenGL_accelerate numpy
```

### Executar o Jogo
```bash
# Usando o novo arquivo principal modular
python main.py
```

## 🕹️ Controles

| Ação | Tecla/Mouse |
|------|------------|
| Mover | `W` `A` `S` `D` |
| Correr | `SHIFT` |
| Olhar | `Mouse` |
| Empurrar Caixa | `ESPAÇO` |
| Reiniciar Nível | `R` |
| **Música ON/OFF** | `M` 🎵 |
| **Sons ON/OFF** | `N` 🔊 |
| **Teleporte de Emergência** | `T` ⚡ |
| Avançar/Iniciar | `ENTER` |
| Sair | `ESC` |

## 📦 Módulos Detalhados

### `config.py`
Centraliza todas as configurações do jogo:
- Parâmetros de janela e câmera
- Velocidades e física
- Configurações de renderização
- Estados do jogo

### `graphics/materials.py`
Sistema de materiais e iluminação:
- **Materials**: Gerenciador de materiais PBR-like
- **Lighting**: Sistema de iluminação profissional de 3 pontos

### `graphics/primitives.py`
Formas geométricas primitivas:
- Cubo unitário
- Grama 3D com Display Lists
- Marcadores de objetivo
- Sombras e partículas

### `graphics/renderer.py`
Pipeline completa de renderização:
- Configuração OpenGL
- Renderização de cena
- Efeitos visuais
- Integração com UI

### `graphics/ui.py`
Interface do usuário:
- HUD durante jogo
- Menus (principal, vitória, final)
- Crosshair
- Texto 2D
- Indicadores de áudio

### `graphics/clouds.py`
Sistema de nuvens procedurais:
- Billboard rendering (sempre de frente para câmera)
- Textura procedimental com gradiente radial + ruído
- Movimento senoidal orgânico (X + Z)
- Distribuição 360° em anel
- Alpha blending para transparência

### `utils/sound.py`
Sistema de áudio completo:
- Síntese procedimental (ondas senoidais + quadradas)
- ADSR envelope para qualidade profissional
- Padrão Singleton (instância única)
- 7 efeitos sonoros + 6 músicas 8-bit
- Controles independentes (música/SFX)
- Buffer management para evitar garbage collection

### `game/levels_data.py`
Definição dos 5 níveis:
- Estrutura de dados padronizada
- Metadados (nome, dificuldade)
- Funções de acesso

### `game/level.py`
Gerenciamento de níveis:
- Carregamento e validação
- Sistema de partículas
- Verificação de vitória
- Estatísticas de progresso

### `game/player.py`
Jogador e câmera:
- Posicionamento
- Rotação de câmera
- Vetores de movimento
- Integração com física

### `game/physics.py`
Sistema de física:
- Colisões AABB
- Detecção de obstáculos
- Movimento suave com sliding
- Direções cardinais

### `main.py`
Ponto de entrada e loop principal:
- Inicialização do jogo
- Gerenciamento de estados
- Loop de jogo
- Tratamento de eventos

## 🎓 Conceitos de Programação Aplicados

### Design Patterns
- **Singleton Pattern**: Configurações centralizadas
- **State Pattern**: GameState para gerenciar estados
- **Strategy Pattern**: Diferentes modos de renderização

### Princípios SOLID
- **Single Responsibility**: Cada módulo tem uma responsabilidade única
- **Open/Closed**: Fácil adicionar níveis sem modificar código base
- **Dependency Inversion**: Módulos dependem de abstrações

### Clean Code
- **Nomes Descritivos**: Variáveis e funções com nomes claros
- **Funções Pequenas**: Cada função faz uma coisa bem
- **Comentários Úteis**: Documentação clara do propósito
- **DRY**: Sem duplicação de código

## 🔧 Otimizações Implementadas

### Performance
1. **Display Lists**: Grama pré-compilada (boost de ~90%)
2. **Culling**: Face culling para não renderizar faces invisíveis
3. **Minimal State Changes**: Agrupa mudanças de estado OpenGL
4. **Efficient Collision**: AABB ao invés de testes pixel-perfect

### Física Melhorada (v1.1)
- **Sistema de Sliding Aprimorado**: Previne travamento em cantos
- **Redução de velocidade**: 70% da velocidade normal ao deslizar
- **Teleporte de Emergência**: Tecla **T** para voltar ao spawn se ficar preso
- **Movimento mais suave**: Menos chance de ficar travado em paredes

### Memória
- Reutilização de objetos
- Limpeza de partículas antigas
- Gerenciamento eficiente de listas

## 📊 Estatísticas do Projeto

- **Linhas de Código**: ~3000+ linhas
- **Módulos**: 14 arquivos Python
- **Funções**: 100+ funções
- **Classes**: 12 classes
- **Níveis**: 5 níveis completos
- **Efeitos Sonoros**: 7 sons procedurais
- **Músicas**: 6 trilhas 8-bit
- **Nuvens**: 15 nuvens animadas
- **Performance**: 120 FPS estáveis

## 🎯 Níveis Disponíveis

1. **Tutorial** - Fácil: Aprenda os controles básicos
2. **Corredor** - Médio: Primeiro desafio real
3. **Labirinto** - Médio: Navegue pelo labirinto
4. **Cruz** - Difícil: Quebra-cabeça complexo
5. **Grande Labirinto** - Muito Difícil: Desafio final épico

## 🐛 Debugging e Desenvolvimento

### Adicionar Novo Nível
1. Edite `game/levels_data.py`
2. Adicione dict com estrutura padrão
3. O jogo detecta automaticamente

### Modificar Iluminação
1. Edite `graphics/materials.py`
2. Ajuste parâmetros em `Lighting.setup()`
3. Teste visualmente

### Ajustar Física
1. Edite `config.py` para parâmetros globais
2. Edite `game/physics.py` para algoritmos

## 📝 Licença

MIT License - Veja LICENSE para detalhes

## 👨‍💻 Desenvolvimento

Desenvolvido como projeto acadêmico para a disciplina de Computação Gráfica e Realidade Virtual, demonstrando:
- Renderização 3D em tempo real
- Sistemas de iluminação
- Otimizações gráficas
- Arquitetura de software profissional
- Boas práticas de programação

---

**🎮 Divirta-se jogando BoxPush 3D!**

Para dúvidas ou sugestões, abra uma issue no GitHub.

