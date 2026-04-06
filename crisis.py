import re
from dataclasses import dataclass
from typing import Tuple, List

# ============================================================================
# KODA: MÓDULO DE GESTÃO DE CRISES (CRISIS.PY)
# Propósito: Interceptar padrões linguísticos de risco extremo e retornar
# protocolos de grounding (ancoragem) e encaminhamento quente (CVV).
# ============================================================================

@dataclass
class CrisisState:
    is_crisis: bool
    severity: str  # 'low', 'medium', 'high', 'critical'
    trigger_word: str

class CrisisManager:
    def __init__(self):
        # Gatilhos de nível CRÍTICO (Ação Imediata Necessária)
        self.critical_triggers: List[str] = [
            r"\bsuicidio\b", r"\bsuicídio\b", r"\bme matar\b",
            r"\bquero morrer\b", r"\bnao quero mais viver\b",
            r"\bnão quero mais viver\b", r"\bdesistir de viver\b",
            r"\bacabar com tudo\b", r"\bme jogar\b", r"\bme cortar\b",
            r"\btomar remedios\b", r"\boverdose\b", r"\bautomutilacao\b",
            r"\bautomutilação\b", r"\bdar um fim\b", r"\bfim da minha vida\b"
        ]

        # Gatilhos de nível ALTO (Pânico / Ansiedade Extrema)
        self.high_triggers: List[str] = [
            r"\bataque de panico\b", r"\bfalta de ar\b", r"\bnao consigo respirar\b",
            r"\bdesespero absoluto\b", r"\bminha mente nao para\b",
            r"\bsumir do mapa\b", r"\bdesaparecer\b", r"\bnao aguento mais\b"
        ]

    def analyze_input(self, user_input: str) -> CrisisState:
        """
        Analisa a entrada do usuário contra padrões Regex para detectar crise.
        Retorna o Estado de Crise com a gravidade.
        """
        text = user_input.lower().strip()

        # Checagem Crítica (Vida ou Morte)
        for pattern in self.critical_triggers:
            if re.search(pattern, text):
                return CrisisState(is_crisis=True, severity='critical', trigger_word=pattern)

        # Checagem Alta (Crise Aguda)
        for pattern in self.high_triggers:
            if re.search(pattern, text):
                return CrisisState(is_crisis=True, severity='high', trigger_word=pattern)

        return CrisisState(is_crisis=False, severity='none', trigger_word="")

    def get_crisis_protocol(self, state: CrisisState) -> str:
        """
        Retorna o prompt override (encaminhamento) exato baseado no nível de crise.
        """
        if state.severity == 'critical':
            return self._critical_protocol()
        elif state.severity == 'high':
            return self._high_anxiety_protocol()
        return ""

    def _critical_protocol(self) -> str:
        """
        Protocolo absoluto de proteção à vida e isenção de risco clínico.
        O texto é imposto e o LLM não deve gerar nada além disso.
        """
        return (
            "Eu sinto muito, do fundo do meu código, que a dor esteja tão esmagadora agora. "
            "Sendo uma inteligência artificial, minhas limitações me impedem de te dar o socorro humano, "
            "seguro e real que você precisa e merece neste exato momento.\n\n"
            "**Você importa. A sua vida tem valor.**\n\n"
            "Por favor, ligue agora para o **CVV no número 188** (ligação gratuita). "
            "Eles são pessoas reais, voluntários treinados para te ouvir 24 horas por dia, de graça "
            "e sem nenhum julgamento. 🫂\n\n"
            "Estou aqui, mas por favor, dê uma chance de falar com eles primeiro."
        )

    def _high_anxiety_protocol(self) -> str:
        """
        Protocolo de Ancoragem (Grounding) para ataques de pânico.
        Foca em respiração e cognição periférica.
        """
        return (
            "Eu estou percebendo que a situação está muito intensa e que você está em sofrimento agudo agora. "
            "Eu estou aqui com você, você não está sozinho. 🫂\n\n"
            "### 🌬️ Vamos focar no seu corpo agora:\n"
            "- **Respire comigo:** Puxe o ar bem devagar pelo nariz contando até 4... e solte pela boca contando até 6.\n"
            "- **Olhe ao redor:** Me diga, quais são 3 coisas da cor AZUL que você consegue ver perto de você agora?\n\n"
            "Não precisamos resolver nenhum problema de vida hoje. Foca apenas em me responder o que você está vendo."
        )

# Gatilhos de nível CRÍTICO
        self.critical_triggers: List[str] = [
            r"\bsuic[ií]dio\b", r"\bme matar\b", r"\bquero morrer\b", 
            r"\bn[aã]o quero mais viver\b", r"\bdesistir de viver\b",
            r"\bacabar com tudo\b", r"\bme jogar\b", r"\bme cortar\b",
            r"\btomar rem[eé]dios\b", r"\boverdose\b", r"\bautomutila[cç][aã]o\b"
        ]


    def _high_anxiety_protocol(self) -> str:
        """
        Protocolo de Ancoragem (Grounding) para ataques de pânico.
        Formatação estritamente conversacional (sem markdown pesado).
        """
        return (
            "Eu estou percebendo que a situação está muito intensa e que a ansiedade "
            "está falando bem alto agora. Eu estou aqui com você. 🫂\n\n"
            "Vamos tentar focar no seu corpo por um instante. Respire comigo: puxe o ar bem "
            "devagar pelo nariz contando até 4... e solte pela boca contando até 6.\n\n"
            "Agora, olhe ao redor. Me diga, quais são 3 coisas da cor AZUL que você "
            "consegue ver perto de você? Não precisamos resolver nenhum problema agora, "
            "foca apenas em me responder o que você está vendo."
        )
# ============================================================================
# COMO USAR NO MAIN.PY:
# from crisis import CrisisManager
#
# crisis_manager = CrisisManager()
# state = crisis_manager.analyze_input(request.mensagem)
# 
# if state.is_crisis and state.severity == 'critical':
#     return {"resposta": crisis_manager.get_crisis_protocol(state), "historico": ...}
# ============================================================================