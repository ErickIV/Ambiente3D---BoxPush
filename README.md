# 🎮 BoxPush 3D - Sokoban Game

Um jogo Sokoban 3D moderno desenvolvido com **Pygame + PyOpenGL** para a disciplina de Computação Gráfica e Realidade Virtual.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyOpenGL](https://img.shields.io/badge/PyOpenGL-3D_Graphics-green.svg)
![Pygame](https://img.shields.io/badge/Pygame-Game_Engine-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Características Principais

### 🎨 Visual e Gráficos
- **Renderização 3D completa** com OpenGL
- **Texturas realistas**: Paredes de concreto com variações procedurais
- **Chão de grama 3D**: 3200 folhas individuais renderizadas dinamicamente
- **Sistema de iluminação**: Iluminação ambiente e direcional
- **Efeitos visuais**: Partículas de sucesso e animações
- **Crosshair** para orientação do jogador

### 🎯 Jogabilidade
- **5 níveis progressivos** com dificuldade crescente
- **Sistema de colisão preciso** para movimento e empurrão de caixas
- **Contador de movimentos** para desafio adicional
- **Tela de vitória final épica** com troféu e animações
- **Menu principal 3D** com preview do jogo

### 🕹️ Controles Intuitivos
- **WASD**: Movimentação do jogador
- **SHIFT**: Correr
- **Mouse**: Rotação da câmera (mouse look)
- **ESPAÇO**: Empurrar caixas
- **R**: Reiniciar nível atual
- **ESC**: Sair/voltar ao menu
- **ENTER**: Confirmar/próximo nível

## 🚀 Instalação e Execução

### Pré-requisitos
```bash
Python 3.8 ou superior
```

### Instalação das Dependências
```bash
# Clone o repositório
git clone https://github.com/ErickIV/Ambiente3D---BoxPush.git
cd Ambiente3D---BoxPush

# Instale as dependências
pip install pygame PyOpenGL
```

### Executar o Jogo
```bash
python Ambiente3D_BoxPush.py
```

## 🎮 Como Jogar

### Objetivo
Empurre todas as **caixas marrons** para os **objetivos vermelhos (X)** para completar cada nível.

### Regras
- ✅ Você só pode **empurrar** caixas, não puxar
- ✅ Não é possível empurrar duas caixas ao mesmo tempo
- ✅ Caixas não podem ser empurradas através de paredes
- ✅ Complete todos os 5 níveis para ver a tela de vitória especial

### Progressão dos Níveis
1. **Nível 1 - Tutorial**: Introdução básica aos controles
2. **Nível 2 - Intermediário**: Obstáculos e múltiplas caixas
3. **Nível 3 - Labirinto**: Navegação em labirinto com passagens estratégicas
4. **Nível 4 - Quebra-cabeça**: Design em cruz com planejamento necessário
5. **Nível 5 - Grande Desafio**: Labirinto complexo final

## 🏗️ Arquitetura Técnica

### Tecnologias Utilizadas
- **Python 3.8+**: Linguagem principal
- **Pygame**: Engine de jogo e input handling
- **PyOpenGL**: Renderização 3D e shaders
- **NumPy**: Cálculos matemáticos otimizados
- **GLUT**: Renderização de texto

### Estrutura do Código
```
├── Ambiente3D_BoxPush.py    # Arquivo principal
├── README.md                # Documentação
└── .gitignore              # Arquivos ignorados
```

### Features Técnicas
- **Sistema de materiais OpenGL** para texturas realistas
- **Geração procedural** de grama 3D
- **Sistema de grid** para movimentação precisa
- **Gerenciamento de estados** (Menu, Jogo, Vitória)
- **Sistema de câmera FPS** com mouse look
- **Renderização 2D overlay** para HUD e menus

## 🎯 Níveis de Dificuldade

| Nível | Nome | Descrição | Caixas | Objetivos |
|-------|------|-----------|---------|-----------|
| 1 | Tutorial | Básico para aprender | 2 | 2 |
| 2 | Intermediário | Obstáculos simples | 4 | 4 |
| 3 | Labirinto | Navegação complexa | 5 | 5 |
| 4 | Quebra-cabeça | Design em cruz | 6 | 6 |
| 5 | Grande Desafio | Labirinto final | 7 | 7 |

## 🎨 Screenshots

### Menu Principal
- Interface 3D com preview do jogo
- Controles claramente indicados
- Cena de demonstração animada

### Gameplay
- Visão em primeira pessoa
- HUD informativo com progresso
- Feedback visual para objetivos

### Tela de Vitória Final
- Animações de celebração
- Troféu ASCII animado
- Estatísticas de conclusão

## 🔧 Desenvolvimento

### Estrutura de Classes Principais
- **Gerenciamento de Estados**: Menu, Jogo, Vitória
- **Sistema de Níveis**: Carregamento dinâmico de fases
- **Renderização 3D**: Objetos, terreno, iluminação
- **Input Management**: Teclado e mouse
- **Sistema de Colisão**: Grid-based para precisão

### Design Patterns Utilizados
- **State Pattern**: Gerenciamento de estados do jogo
- **Component System**: Separação de responsabilidades
- **Factory Pattern**: Criação de partículas e objetos

## 🎓 Contexto Educacional

Este projeto foi desenvolvido como material didático para:
- **Computação Gráfica**: Renderização 3D, iluminação, texturas
- **Realidade Virtual**: Navegação 3D, interação espacial
- **Desenvolvimento de Jogos**: Game loops, estados, input handling
- **Programação Python**: Orientação a objetos, bibliotecas gráficas

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- **ErickIV** - *Desenvolvimento inicial* - [ErickIV](https://github.com/ErickIV)

## 🙏 Agradecimentos

- Disciplina de Computação Gráfica e Realidade Virtual
- Comunidade PyOpenGL e Pygame
- Inspiração no clássico jogo Sokoban

---

**🎮 Divirta-se jogando BoxPush 3D!** 🎉
