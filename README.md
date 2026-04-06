# 🌿 KODA - Inteligência Artificial de Apoio Emocional

O **KODA** (do nativo americano: *"companheiro"*) é uma aplicação de Inteligência Artificial desenhada com uma interface *Mobile-First* de altíssimo nível, focada em UX Emocional. Seu propósito é oferecer acolhimento psicológico informal, escuta ativa e clareza mental para usuários em momentos de ansiedade ou confusão.

---

## ✨ Filosofia do Projeto

O KODA não é um chatbot genérico. Ele foi construído sobre princípios de psicologia humanista e Terapia Cognitivo-Comportamental (TCC) básica, operando sob uma **Engenharia de Prompt Avançada**. 

Ele une a empatia incondicional de um conselheiro com a capacidade de organização visual de uma máquina, formatando textos complexos em tópicos digeríveis para mentes sobrecarregadas.

> **⚠️ Isenção de Responsabilidade Médica:**
> O KODA é um experimento de tecnologia e suporte emocional. Ele **NÃO** substitui psicólogos, psiquiatras ou ajuda médica profissional. Em caso de crise aguda, o sistema possui protocolos para redirecionamento imediato a serviços de prevenção à vida.

---

## 🚀 Principais Funcionalidades

- 🧠 **Adaptação Cognitiva:** O KODA lê a intenção do usuário (desabafo, pedido de conselho ou autossabotagem) e muda seu modo de resposta para se adaptar.
- 🛡️ **Escudo de Crise (`crisis.py`):** Um algoritmo interceptador backend que avalia gatilhos de risco de vida via Regex. Caso detecte perigo, ele sobrepõe a IA e encaminha o usuário imediatamente para o CVV (188).
- 🎨 **UX/UI Emocional:** Interface minimalista e terapêutica. Utiliza paleta de cores *Sage & Sand* (Sálvia e Areia), bordas arredondadas e ausência de contrastes agressivos para evitar fadiga ocular e ansiedade.
- 📱 **Mobile-First App:** Design fluído, perfeitamente adaptado para leitura e toque em telas de smartphones.
- 🔄 **Barra de Ações (Copiar, Editar, Refazer):** Botões em formato SVG minimalista que permitem ao usuário corrigir suas mensagens antigas ou solicitar uma nova formatação de resposta à IA.

---

## 🛠️ Stack Tecnológica

O projeto foi dividido em uma arquitetura limpa, separando a lógica de inteligência da camada de apresentação visual.

**Backend:**
- **Python 3+**
- **FastAPI** (Roteamento ágil e servimento de arquivos estáticos)
- **OpenAI SDK / Google Gemini API** (Comunicação LLM via OpenRouter)

**Frontend:**
- **HTML5, CSS3, JavaScript (Vanilla)**
- **Marked.js** (Renderização de Markdown dinâmico)
- Arquitetura de arquivos separados (`index.html`, `estilo.css`, `script.js`) para fácil manutenção.

---

## 📦 Como rodar o KODA localmente

### 1. Clone o repositório e acesse a pasta
```bash
git clone [[https://github.com/seu-usuario/projeto-koda.git](https://github.com/seu-usuario/projeto-koda.git)](https://github.com/guilhermesolagarcia/projeto-koda.git)
cd projeto-koda
