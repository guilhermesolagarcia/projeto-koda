# KODA v2 — Design

Data: 2026-10-08 · Status: aguardando revisão

## Objetivo

Reescrever o KODA (IA de apoio emocional, PT-BR) como projeto de **portfólio**. Ele **roda localmente** no PC (sem hospedagem), tem que subir com um comando só, responder rápido, ter contas, guardar histórico de conversas e ter um visual moderno. O custo deve ser zero.

**Pronto quando:** com o app rodando no PC, alguém abre no navegador (ou no celular, pela rede local), conversa sem criar conta, vê a resposta aparecendo em streaming, cria uma conta depois sem perder as conversas, volta outro dia e encontra o histórico. Também deve conseguir conversar por voz.

## Decisões tomadas

| Tema | Decisão |
|---|---|
| Público | Portfólio / estudo. Prioridade: custo zero. |
| Stack | Next.js (App Router, TypeScript) + Tailwind v4 + shadcn/ui. **Sem hospedagem:** roda local (`npm run build && npm start`). O Supabase continua na nuvem (plano grátis), porque é serviço, não hospedagem. |
| Backend de dados | Supabase (Auth + Postgres com RLS) |
| Login | E-mail + senha, link mágico por e-mail e modo anônimo (anônimo → conta sem perder dados) |
| IA | OpenRouter com modelos **grátis** e fila de reserva. Lista na env `KODA_MODELS`. |
| Nome | KODA |
| Visual | "Aurora": minimal escuro, fundo quase preto com luz azul-petróleo no topo, efeito de vidro e destaques em azul |
| Voz | Ditado (🎤) + modo voz completo na v1, com APIs grátis do navegador |

## Visual — Aurora

Tokens (CSS variables / tema Tailwind):

```
--bg:      #05070c   (fundo)
--fg:      #e6eef7   (texto)
--muted:   #8292a8   (texto secundário)
--line:    rgba(255,255,255,.06)   --line-2: rgba(255,255,255,.10)
--accent:  #8cc8ff
--grad:    linear-gradient(135deg, #8fd3e8, #6f86ff)   (botão enviar, avatar fallback)
--user-bubble: rgba(140,200,255,.12) + borda rgba(140,200,255,.18)
glow de fundo: radial-gradient(80% 45% at 20% 0%, rgba(54,120,170,.42), transparent 70%)
               + radial-gradient(50% 35% at 100% 25%, rgba(90,90,210,.22), transparent 70%)
voz: ouvindo #8cc8ff · pensando #b3a2ff · falando #8fe3e8
```

- Fonte: Geist (sans) e Geist Mono (timer do modo voz).
- Só tema escuro na v1.
- Mensagem do usuário em balão. Resposta do KODA sem balão, como texto corrido com a esfera ao lado.
- Mockups aprovados: `.superpowers/brainstorm/587-1791424992/content/` (`azul-calmo.html` opção 2, `app-completo.html`, `elementos.html`).

### Componentes vindos das referências (`refss/`)

| Referência | Uso |
|---|---|
| `estilodeia` → `ai-blob-warp.tsx` | Avatar do KODA. O shader Warp usa cores Aurora `["#8fd3e8","#6f86ff","#a58cff","#4fb3d9"]`. A velocidade sobe enquanto ele está gerando. Já pausa fora da tela e respeita `prefers-reduced-motion`. |
| `estilocaisa` → `ai-prompt-box.tsx` | Base da caixa de texto: autosize, Enter envia, botão ■ para a geração, 🎤 dita. **Remover:** Search/Think/Canvas, upload de imagem e a injeção de `<style>` no nível do módulo (quebra no SSR; mover pro CSS global). Trocar `framer-motion` por `motion`. |
| vídeo `…0222…mp4` | Texto **"Criando sua resposta…"** com brilho passando (CSS `background-clip:text` + gradiente animado). Aparece até chegar o 1º token. |
| vídeo `…0221…mp4` | Modo voz com estados Ouvindo / Pensando / Falando, esfera grande, ondas e timer, nas cores Aurora. |

## Arquitetura

```
Navegador (Next.js / React)
  ├─ useChat (AI SDK)  ── POST /api/chat ──►  Route Handler (servidor)
  │                                            ├─ Supabase server client (sessão do cookie)
  │                                            ├─ carrega histórico do banco
  │                                            ├─ detectCrisis()
  │                                            ├─ streamText() via OpenRouter (fila KODA_MODELS)
  │                                            └─ onFinish: salva resposta
  └─ Supabase browser client (auth, lista de conversas)
```

Estrutura de pastas proposta:

```
app/
  layout.tsx, globals.css
  page.tsx                  → redireciona pra nova conversa
  c/[id]/page.tsx           → tela de chat
  entrar/page.tsx           → login / criar conta
  api/chat/route.ts
  auth/callback/route.ts    → retorno do link mágico / confirmação
components/
  ui/ (shadcn + ai-blob-warp + prompt-box)
  chat/ (message-list, message, generating-text, sidebar, voice-mode)
lib/
  persona.ts                → prompt (vindo do persona.py)
  crisis.ts (+ crisis.test.ts)
  models.ts                 → fila de modelos + fallback
  supabase/ (client.ts, server.ts, middleware.ts)
supabase/migrations/0001_init.sql
```

## Banco de dados

```sql
create table conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade default auth.uid(),
  title text not null default 'Nova conversa',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations on delete cascade,
  user_id uuid not null references auth.users on delete cascade default auth.uid(),
  role text not null check (role in ('user','assistant')),
  content text not null check (char_length(content) <= 8000),
  created_at timestamptz not null default now()
);
create index on messages (conversation_id, created_at);
create index on conversations (user_id, updated_at desc);

alter table conversations enable row level security;
alter table messages enable row level security;
create policy "dono" on conversations for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "dono" on messages for all using (user_id = auth.uid()) with check (user_id = auth.uid());
```

- O papel `system` **não existe** no banco. O prompt é sempre injetado pelo servidor.
- **Título:** primeiros ~40 caracteres da 1ª mensagem, cortados na palavra.

## Autenticação

- **1º acesso sem sessão:** `signInAnonymously()`. A pessoa já pode conversar, e as conversas ficam no banco ligadas ao usuário anônimo.
- **Criar conta (anônimo → permanente):** `updateUser({ email })` dispara o e-mail de confirmação. Depois de confirmar, `updateUser({ password })` define a senha. O usuário é o mesmo, então o histórico continua.
- **Entrar numa conta existente:** `signInWithPassword` ou `signInWithOtp` (link mágico). Limitação conhecida: as conversas anônimas daquele aparelho **não** são mescladas. A tela avisa isso se houver conversas anônimas.
- **Supabase dashboard:** ativar "Anonymous sign-ins" e configurar a URL de redirect (`/auth/callback`).
- O middleware do `@supabase/ssr` renova a sessão em toda requisição.

## Fluxo do `/api/chat`

1. Recebe `{ conversationId, message }`. Valida com zod: a mensagem tem de 1 a 4000 caracteres e o `conversationId` é um uuid. O cliente **não** envia histórico.
2. Pega o usuário da sessão. Sem usuário, responde 401.
3. Se a conversa não existe, cria (com título). Se existe e não é do usuário, o RLS bloqueia e a rota responde 404.
4. Salva a mensagem do usuário.
5. Roda `detectCrisis(message)`. Se der `critical`, responde com `CRISIS_RESPONSE` (texto fixo, em formato de stream pra UI tratar igual), salva como assistant, marca `crisis: true` no metadata (a UI mostra o banner CVV) e encerra.
6. Carrega as últimas **30** mensagens da conversa. Monta `[system: KODA_SYSTEM_PROMPT, ...historico]`.
7. Chama `streamText` com o 1º modelo de `KODA_MODELS`. Se der erro **antes do 1º token**, tenta o próximo. Se todos falharem, responde com a mensagem amigável de instabilidade (sem salvar).
8. No `onFinish`, salva a resposta e atualiza `conversations.updated_at`.
9. No **Refazer**, apaga a última resposta do assistant e gera de novo a partir da última mensagem do usuário (mesma rota, flag `regenerate: true`).

## Filtro de crise (`lib/crisis.ts`)

Estratégia: **o regex só pega o inequívoco**. Os casos ambíguos vão para o modelo, que tem os módulos 9.12 e 10.0 no prompt.

- Normalizar: minúsculas, sem acento (`normalize('NFD')`) e espaços colapsados.
- **`critical`** (resposta fixa, sem chamar o modelo): suicídio/suicidar, me matar, quero/vou morrer, tirar (a) minha (própria) vida, não quero (mais) viver, desistir de viver, acabar com a minha vida, fim da minha vida, me cortar, automutilação, overdose, tomar todos os remédios, melhor se eu não existisse, dormir pra sempre e não acordar.
- **Removidos de `critical`** por falso positivo: "me jogar" (sozinho), "acabar com tudo" (sozinho), "nada mais importa", "me despedir".
- **`high`** (pânico): não bloqueia o modelo. Só envia `crisis: 'high'` para a UI mostrar o banner CVV discreto. O prompt já cobre o acolhimento.
- **Texto de crise único:** `CRISIS_RESPONSE`, usado no `crisis.ts`. As seções F e 10.0 do prompt passam a citar o mesmo texto.
- **Testes obrigatórios (vitest):**

| Entrada | Esperado |
|---|---|
| quero me matar | critical |
| Quero Morrer | critical |
| pensando em tirar minha vida | critical |
| nao quero mais viver | critical |
| vou me jogar no trabalho | none |
| acabar com tudo isso de prova | none |
| me despedir da minha mãe no aeroporto | none |
| nada mais importa pra mim nessa série | none |
| queria sumir pra sempre | none (módulo 6.7, não é crise) |
| tô tendo um ataque de pânico | high |

## Persona (`lib/persona.ts`)

- Conteúdo integral do `persona.py`, exportado como string.
- **Correções:** (1) seção C proíbe `###`, mas o MODO 2 manda usar. Fica: no MODO 2 pode usar tópicos `-` e negrito, mas **sem** títulos `###`. (2) Renumerar as seções (A, B, C, D, E, F; o "C.5" vira "E"). (3) Um único texto de crise.
- Tamanho atual: ~20k tokens. Mantido na v1. Se os modelos grátis reclamarem de contexto, a primeira saída é encurtar os exemplos.

## Interface

- **Desktop:** sidebar de 250px com "Nova conversa", grupos Hoje / Ontem / Últimos 7 dias / Mais antigas, item ativo destacado e, embaixo, a conta ("Criar conta" se for anônimo, "Sair" se tiver conta). Ao lado, a conversa com largura máxima de ~640px.
- **Mobile:** a sidebar vira uma gaveta (Sheet do shadcn) aberta pelo ☰.
- **Tela vazia:** "Boa noite. *Como você está, de verdade?*" (a saudação muda com a hora) + chips: Preciso desabafar / Tô ansioso / Só quero companhia / Quero um conselho.
- **Gerando:** esfera acelerada + "Criando sua resposta…" com brilho até o 1º token. Depois, streaming com cursor. O botão de enviar vira ■.
- **Ações na resposta:** copiar e refazer (só na última). Na conversa (menu ⋯): apagar, com confirmação num Dialog do shadcn (não `confirm()`).
- **Markdown:** `react-markdown`, sem `rehype-raw` (HTML não renderiza, o que resolve o XSS).
- **Aviso fixo** abaixo da caixa: "O KODA não substitui ajuda profissional. Em crise, ligue 188 (CVV)." O banner CVV em destaque aparece quando vem `crisis` no metadata.
- **Erros:** falha de rede ou 5xx mostra um toast (sonner) + "Tentar de novo" na mensagem. A mensagem do usuário não se perde.
- **PWA:** `app/manifest.ts` + ícones em `public/` (`logo-verde.png` até haver logo nova).
- **Acessibilidade:** sem `user-scalable=no`, foco visível e `aria-label` nos botões de ícone.

## Voz

Recursos do navegador, sem custo. Se `SpeechRecognition`/`webkitSpeechRecognition` não existir, os botões de voz **não aparecem**.

- **🎤 Ditar** (na caixa): `lang='pt-BR'`, `interimResults`. O texto vai entrando na caixa e a pessoa revisa antes de enviar.
- **Modo voz** (botão 🎧, tela cheia por cima do chat, mesma conversa):
  1. **Ouvindo** (`#8cc8ff`): esfera grande respirando, ondas, timer e transcrição ao vivo. Uma pausa de ~1,5s na fala envia a mensagem.
  2. **Pensando** (`#b3a2ff`): esfera acelerada e linha pontilhada.
  3. **Falando** (`#8fe3e8`): `speechSynthesis` com voz pt-BR (prefere voz "Google"/"Microsoft" pt-BR se existir). O texto aparece embaixo. O markdown é removido antes de falar. A fala começa **por frase**, conforme o stream chega.
  4. Ao terminar de falar, volta pra **Ouvindo**. Botões: ⌨ (volta pro texto) e ✕ (encerra).
- Tudo fica salvo no histórico normal da conversa.
- **Celular pela rede local:** o navegador só libera o microfone em `localhost` ou HTTPS. Acessando por `http://IP-do-PC:3000`, **a voz não funciona no celular**. No PC funciona normal. Se precisar no celular: `next dev --experimental-https` (certificado local, o celular mostra um aviso uma vez).
- **Limitações conhecidas:** a voz é robótica, e o reconhecimento é instável no iOS Safari. Voz natural (TTS pago) fica fora do escopo.

## Variáveis de ambiente

```
OPENROUTER_API_KEY=...            (já existe no .env atual)
KODA_MODELS=modelo1:free,modelo2:free,...   (sem openrouter/auto — não é grátis)
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

Os IDs de modelos grátis do OpenRouter mudam com frequência. Na fase 1, consultar `https://openrouter.ai/api/v1/models`, escolher 3–4 com sufixo `:free` e suporte a contexto ≥ 32k (o prompt tem ~20k tokens), e colocar em `KODA_MODELS`.

`.env.local` no `.gitignore`.

## Fases de implementação

Cada fase termina com algo funcionando e com um commit. Recomendado: uma sessão nova por fase, usando Sonnet.

1. **Base + chat:** criar o app Next.js na raiz (remover os arquivos Python, que ficam no histórico do git), `persona.ts`, `crisis.ts` com os testes passando, `models.ts` com fallback, `/api/chat` com streaming **ainda sem banco** (histórico em memória no cliente) e uma tela simples.
   *Pronto quando:* `npm test` passa e o chat responde em streaming no `localhost`.
2. **Supabase** (antes, o usuário cria um projeto grátis em supabase.com): migration, clients, middleware, login anônimo, `/api/chat` lendo e salvando no banco, sidebar com histórico, tela `/entrar` (senha + link mágico + criar conta a partir do anônimo) e apagar conversa.
   *Pronto quando:* recarregar a página mantém a conversa, criar conta mantém o histórico e um usuário não vê dados de outro (testar com 2 contas).
3. **Visual Aurora:** tokens, glow, `ai-blob-warp`, prompt-box adaptado, "Criando sua resposta…", gaveta mobile, banner CVV, toasts e PWA.
   *Pronto quando:* bate com os mockups aprovados no celular (390px) e no desktop.
4. **Voz:** ditado + modo voz com os 3 estados.
   *Pronto quando:* uma conversa completa por voz funciona no Chrome (desktop e Android).
5. **Rodar fácil + README:** `iniciar.bat` na raiz (instala as dependências se faltar, faz o build se preciso e roda `next start -H 0.0.0.0`, abrindo o navegador). README novo com prints, passo a passo do Supabase e `.env.example`.
   *Pronto quando:* clicar duas vezes no `iniciar.bat` abre o KODA funcionando, e o celular na mesma rede acessa pelo IP do PC.

## Fora do escopo da v1

Limite de mensagens por usuário, captcha no login anônimo, título gerado por IA, editar mensagens antigas, mesclar conversas anônimas ao entrar numa conta existente, voz natural paga, tema claro, upload de imagem e login com Google.
