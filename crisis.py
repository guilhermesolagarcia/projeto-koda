import re
from dataclasses import dataclass
from typing import Tuple, List

# ============================================================================
# KODA: MÓDULO DE GESTÃO DE CRISES E GROUNDING (CRISIS.PY) v2.0
# Propósito: Interceptar padrões linguísticos de risco extremo e retornar
# protocolos de ancoragem ou encaminhamento quente (CVV) IMEDIATAMENTE.
# ============================================================================

@dataclass
class CrisisState:
    is_crisis: bool
    severity: str  # 'none', 'high', 'critical'
    trigger_word: str

class CrisisManager:
    def __init__(self):
        # Gatilhos de nível CRÍTICO (Ação Imediata Necessária - Módulo 10)
        # Expandido para capturar o "Vazio Absoluto" do Módulo 9.12
        self.critical_triggers: List[str] = [
            r"\bsuic[ií]dio\b", r"\bme matar\b", r"\bquero morrer\b", 
            r"\bn[aã]o quero mais viver\b", r"\bdesistir de viver\b",
            r"\bacabar com tudo\b", r"\bme jogar\b", r"\bme cortar\b",
            r"\btomar rem[eé]dios\b", r"\boverdose\b", r"\bautomutila[cç][aã]o\b",
            r"\bdar um fim\b", r"\bfim da minha vida\b", r"\bnada mais importa\b",
            r"\bmelhor se eu n[aã]o existisse\b", r"\bqueria dormir pra sempre\b",
            r"\bme despedir\b", r"\bn[aã]o vejo mais sa[ií]da\b"
        ]

        # Gatilhos de nível ALTO (Pânico / Ansiedade Extrema Aguda)
        self.high_triggers: List[str] = [
            r"\bataque de p[aâ]nico\b", r"\bfalta de ar\b", r"\bn[aã]o consigo respirar\b",
            r"\bdesespero absoluto\b", r"\bminha mente n[aã]o para\b",
            r"\bme tira daqui\b", r"\bn[aã]o aguento mais\b"
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

        # Checagem Alta (Crise Aguda de Pânico)
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
        Texto imposto; o LLM não deve gerar nada além disso.
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