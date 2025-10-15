# 🎮 BoxPush 3D - Sokoban Game (Refatorado)

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
    └── __init__.py
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
- **Crosshair dinâmica**: Orientação visual
- **Sombras projetadas**: Profundidade e realismo

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
pip install pygame PyOpenGL PyOpenGL_accelerate
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

- **Linhas de Código**: ~2000+ linhas
- **Módulos**: 12 arquivos Python
- **Funções**: 80+ funções
- **Classes**: 8 classes
- **Níveis**: 5 níveis completos
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
