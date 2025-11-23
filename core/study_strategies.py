"""
Study Strategies & Metacognitive Module for Examina.
Teaches students HOW to learn effectively, not just WHAT to learn.
"""

from typing import Dict, List, Optional, Any
import json


class StudyStrategyManager:
    """
    Manages study strategies and metacognitive guidance for different core loops.
    Provides problem-solving frameworks, learning tips, and self-assessment prompts.
    """

    def __init__(self, language: str = "en"):
        """
        Initialize the study strategy manager.

        Args:
            language: Output language ("en" or "it")
        """
        self.language = language
        self._initialize_strategies()

    def _initialize_strategies(self):
        """Initialize all study strategies organized by domain."""
        self.strategies = {
            # FSM/Automata Domain
            "fsm_mealy_design": self._strategy_mealy_design(),
            "fsm_moore_design": self._strategy_moore_design(),
            "fsm_mealy_to_moore": self._strategy_mealy_to_moore(),
            "fsm_moore_to_mealy": self._strategy_moore_to_mealy(),
            "fsm_minimization": self._strategy_fsm_minimization(),
            "fsm_analysis": self._strategy_fsm_analysis(),

            # Circuit Design Domain
            "boolean_minimization": self._strategy_boolean_minimization(),
            "karnaugh_map": self._strategy_karnaugh_map(),
            "circuit_design": self._strategy_circuit_design(),
            "sequential_circuit": self._strategy_sequential_circuit(),
            "latch_analysis": self._strategy_latch_analysis(),

            # Performance Analysis Domain
            "amdahl_law": self._strategy_amdahl_law(),
            "mips_calculation": self._strategy_mips_calculation(),
            "speedup_calculation": self._strategy_speedup_calculation(),
            "performance_comparison": self._strategy_performance_comparison(),

            # Number Systems & Conversions
            "base_conversion": self._strategy_base_conversion(),
            "ieee754_conversion": self._strategy_ieee754_conversion(),
            "complement_arithmetic": self._strategy_complement_arithmetic(),

            # Linear Algebra (placeholder for future expansion)
            "gaussian_elimination": self._strategy_gaussian_elimination(),
            "eigenvalue_computation": self._strategy_eigenvalue_computation(),

            # Concurrent Programming (placeholder for future expansion)
            "monitor_design": self._strategy_monitor_design(),
            "semaphore_synchronization": self._strategy_semaphore_synchronization(),
        }

    def get_strategy_for_core_loop(self, core_loop_name: str, difficulty: str = "medium") -> Optional[Dict]:
        """
        Get tailored study strategy for a specific core loop and difficulty.

        Args:
            core_loop_name: Name of the core loop
            difficulty: Difficulty level (easy, medium, hard)

        Returns:
            Complete strategy dictionary or None if not found
        """
        # Map core loop name to strategy key
        strategy_key = self._map_core_loop_to_strategy(core_loop_name)

        if strategy_key and strategy_key in self.strategies:
            strategy = self.strategies[strategy_key].copy()

            # Adjust for difficulty
            strategy = self._adjust_for_difficulty(strategy, difficulty)

            return strategy

        return None

    def get_problem_solving_framework(self, core_loop_name: str) -> Optional[Dict]:
        """
        Get step-by-step problem-solving approach for a core loop.

        Args:
            core_loop_name: Name of the core loop

        Returns:
            Problem-solving framework or None if not found
        """
        strategy = self.get_strategy_for_core_loop(core_loop_name)
        if strategy:
            return strategy.get("framework")
        return None

    def get_learning_tips(self, topic_name: str, difficulty: str = "medium") -> List[str]:
        """
        Get learning tips for a topic at specific difficulty.

        Args:
            topic_name: Name of the topic
            difficulty: Difficulty level

        Returns:
            List of learning tips
        """
        # Find matching strategy
        for key, strategy in self.strategies.items():
            if self._matches_topic(key, topic_name):
                tips = strategy.get("learning_tips", [])

                # Add difficulty-specific tips
                if difficulty == "easy":
                    tips = tips[:3]  # Focus on basics
                elif difficulty == "hard":
                    tips.extend(strategy.get("advanced_tips", []))

                return tips

        return []

    def get_self_assessment_prompts(self, core_loop_name: str) -> List[str]:
        """
        Get questions for self-assessment.

        Args:
            core_loop_name: Name of the core loop

        Returns:
            List of self-assessment questions
        """
        strategy = self.get_strategy_for_core_loop(core_loop_name)
        if strategy:
            return strategy.get("self_assessment", [])
        return []

    def get_retrieval_practice(self, core_loop_name: str) -> Optional[Dict]:
        """
        Get active recall techniques for a core loop.

        Args:
            core_loop_name: Name of the core loop

        Returns:
            Retrieval practice dictionary or None
        """
        strategy = self.get_strategy_for_core_loop(core_loop_name)
        if strategy:
            return strategy.get("retrieval_practice")
        return None

    def get_common_mistakes(self, core_loop_name: str) -> List[str]:
        """
        Get common mistake patterns for a core loop.

        Args:
            core_loop_name: Name of the core loop

        Returns:
            List of common mistakes
        """
        framework = self.get_problem_solving_framework(core_loop_name)
        if framework and "steps" in framework:
            mistakes = []
            for step in framework["steps"]:
                mistakes.extend(step.get("common_mistakes", []))
            return mistakes
        return []

    def _map_core_loop_to_strategy(self, core_loop_name: str) -> Optional[str]:
        """Map a core loop name to a strategy key."""
        name_lower = core_loop_name.lower()

        # FSM/Automata mappings
        if "mealy" in name_lower and ("design" in name_lower or "progettazione" in name_lower):
            return "fsm_mealy_design"
        if "moore" in name_lower and ("design" in name_lower or "progettazione" in name_lower):
            return "fsm_moore_design"
        if "mealy" in name_lower and "moore" in name_lower:
            if "mealy-moore" in name_lower or "mealy to moore" in name_lower:
                return "fsm_mealy_to_moore"
            else:
                return "fsm_moore_to_mealy"
        if "minimization" in name_lower or "minimizzazione" in name_lower:
            if "boolean" in name_lower or "booleana" in name_lower:
                return "boolean_minimization"
            else:
                return "fsm_minimization"
        if "transition" in name_lower or "transizioni" in name_lower:
            return "fsm_analysis"

        # Circuit Design mappings
        if "karnaugh" in name_lower or "k-map" in name_lower:
            return "karnaugh_map"
        if "boolean" in name_lower and ("minimization" in name_lower or "minimizzazione" in name_lower):
            return "boolean_minimization"
        if "circuit" in name_lower and "sequential" in name_lower:
            return "sequential_circuit"
        if "latch" in name_lower or "flip-flop" in name_lower:
            return "latch_analysis"
        if "circuit" in name_lower or "circuito" in name_lower:
            return "circuit_design"

        # Performance Analysis mappings
        if "amdahl" in name_lower:
            return "amdahl_law"
        if "mips" in name_lower:
            return "mips_calculation"
        if "speedup" in name_lower:
            return "speedup_calculation"
        if "performance" in name_lower or "prestazioni" in name_lower:
            return "performance_comparison"

        # Number Systems mappings
        if "ieee754" in name_lower or "ieee 754" in name_lower:
            return "ieee754_conversion"
        if "complement" in name_lower or "complemento" in name_lower:
            return "complement_arithmetic"
        if "conversion" in name_lower or "conversione" in name_lower:
            if "base" in name_lower or "binary" in name_lower:
                return "base_conversion"

        # Linear Algebra mappings
        if "gaussian" in name_lower or "gauss" in name_lower:
            return "gaussian_elimination"
        if "eigenvalue" in name_lower or "autovalore" in name_lower:
            return "eigenvalue_computation"

        # Concurrent Programming mappings
        if "monitor" in name_lower:
            return "monitor_design"
        if "semaphore" in name_lower or "semaforo" in name_lower:
            return "semaphore_synchronization"

        return None

    def _matches_topic(self, strategy_key: str, topic_name: str) -> bool:
        """Check if a strategy key matches a topic name."""
        key_lower = strategy_key.lower()
        topic_lower = topic_name.lower()

        # Simple substring matching
        if any(word in topic_lower for word in key_lower.split("_")):
            return True

        return False

    def _adjust_for_difficulty(self, strategy: Dict, difficulty: str) -> Dict:
        """Adjust strategy content based on difficulty level."""
        adjusted = strategy.copy()

        if difficulty == "easy":
            # Simplify framework
            if "framework" in adjusted and "steps" in adjusted["framework"]:
                adjusted["framework"]["steps"] = adjusted["framework"]["steps"][:4]

            # Keep only basic tips
            if "learning_tips" in adjusted:
                adjusted["learning_tips"] = adjusted["learning_tips"][:3]

        elif difficulty == "hard":
            # Add advanced tips if available
            if "advanced_tips" in adjusted:
                adjusted["learning_tips"] = adjusted.get("learning_tips", []) + adjusted["advanced_tips"]

        return adjusted

    # ==================== FSM/AUTOMATA STRATEGIES ====================

    def _strategy_moore_design(self) -> Dict:
        """Strategy for Moore machine design."""
        if self.language == "it":
            return {
                "framework": {
                    "approach": "Progettazione sistematica di una macchina di Moore da specifiche",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Analizza le specifiche e identifica gli stati necessari",
                            "why": "Ogni stato deve rappresentare una condizione significativa del sistema",
                            "how": "Elenca tutti i comportamenti richiesti e le condizioni di uscita",
                            "reasoning": "Le macchine di Moore hanno uscite associate agli stati, quindi devi pensare in termini di 'quali uscite diverse servono?'",
                            "validation": "Ogni uscita richiesta ha almeno uno stato corrispondente",
                            "common_mistakes": [
                                "Dimenticare stati per gestire sequenze parziali",
                                "Creare troppi stati ridondanti",
                                "Non considerare tutte le possibili combinazioni di input"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Disegna il diagramma degli stati con transizioni",
                            "why": "Visualizzare la macchina aiuta a individuare stati mancanti e transizioni errate",
                            "how": "Per ogni stato, traccia frecce per ogni possibile input",
                            "reasoning": "Ogni stato deve avere una transizione per ogni simbolo dell'alfabeto di input",
                            "validation": "Ogni stato ha esattamente |Σ| transizioni uscenti (dove Σ è l'alfabeto)",
                            "common_mistakes": [
                                "Transizioni mancanti per alcuni input",
                                "Stati non raggiungibili dal stato iniziale",
                                "Dimenticare di etichettare le uscite sugli stati"
                            ]
                        },
                        {
                            "step": 3,
                            "action": "Assegna le uscite a ciascuno stato",
                            "why": "Nelle Moore, l'uscita dipende SOLO dallo stato corrente",
                            "how": "Per ogni stato, scrivi l'uscita che produce quando la macchina è in quello stato",
                            "reasoning": "A differenza di Mealy, l'uscita non dipende dall'input corrente",
                            "validation": "Ogni stato ha esattamente una uscita assegnata",
                            "common_mistakes": [
                                "Confondere con Mealy e mettere uscite sulle transizioni",
                                "Stati con uscite indefinite"
                            ]
                        },
                        {
                            "step": 4,
                            "action": "Costruisci la tabella delle transizioni",
                            "why": "Rappresentazione formale necessaria per implementazione e verifica",
                            "how": "Righe = stati, Colonne = input, Celle = (stato successivo, output)",
                            "reasoning": "La tabella è la forma canonica per verifica e minimizzazione",
                            "validation": "La tabella è completa: ogni cella ha un valore",
                            "common_mistakes": [
                                "Celle vuote nella tabella",
                                "Confondere stato successivo con uscita"
                            ]
                        },
                        {
                            "step": 5,
                            "action": "Verifica con sequenze di test",
                            "why": "Confermare che la macchina soddisfa le specifiche",
                            "how": "Simula l'esecuzione con input di esempio dal problema",
                            "reasoning": "La verifica pratica individua errori che non sono evidenti dalla tabella",
                            "validation": "Tutte le sequenze di test producono l'output atteso",
                            "common_mistakes": [
                                "Testare solo casi semplici",
                                "Non verificare casi limite (stringhe vuote, cicli)"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Pensa agli stati come 'memorie' di ciò che è successo finora nell'input",
                    "Disegna sempre prima il diagramma visuale - è più facile individuare errori",
                    "Ricorda: Moore ha uscite sugli STATI, Mealy sulle TRANSIZIONI",
                    "Usa nomi di stati descrittivi (S_init, S_trovato_01, ecc.) invece di S0, S1",
                    "Verifica che ogni stato sia raggiungibile e utile (non ridondante)"
                ],
                "advanced_tips": [
                    "Per problemi complessi, usa la tecnica 'divide et impera': sotto-macchine per sotto-compiti",
                    "Applica minimizzazione per ridurre stati equivalenti",
                    "Considera l'uso di variabili ausiliarie per tracciare più condizioni"
                ],
                "self_assessment": [
                    "Riesco a giustificare perché ogni stato è necessario?",
                    "Ho verificato che ogni stato ha transizioni per tutti gli input possibili?",
                    "Le uscite riflettono correttamente lo stato della macchina?",
                    "La macchina gestisce correttamente i casi limite (input vuoto, ripetizioni)?",
                    "Potrei spiegare questo design a un compagno di classe?"
                ],
                "retrieval_practice": {
                    "technique": "Pratica di richiamo attivo senza guardare gli appunti",
                    "exercises": [
                        "Disegna una macchina di Moore che riconosce sequenze che terminano con '101'",
                        "Converti una specifica testuale in diagramma di stati",
                        "Data una tabella, genera il diagramma corrispondente",
                        "Identifica e correggi errori in macchine proposte"
                    ]
                },
                "time_estimate": "20-30 minuti per esercizio medio",
                "difficulty_indicators": {
                    "easy": "Pochi stati (2-4), alfabeto piccolo, specifica chiara",
                    "medium": "Stati moderati (4-7), condizioni multiple",
                    "hard": "Molti stati (8+), condizioni complesse, ottimizzazione richiesta"
                }
            }
        else:  # English
            return {
                "framework": {
                    "approach": "Systematic design of a Moore machine from specifications",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Analyze specifications and identify required states",
                            "why": "Each state must represent a meaningful system condition",
                            "how": "List all required behaviors and output conditions",
                            "reasoning": "Moore machines have outputs tied to states, so think 'what different outputs do I need?'",
                            "validation": "Every required output has at least one corresponding state",
                            "common_mistakes": [
                                "Forgetting states to handle partial sequences",
                                "Creating too many redundant states",
                                "Not considering all possible input combinations"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Draw the state diagram with transitions",
                            "why": "Visualizing helps spot missing states and incorrect transitions",
                            "how": "For each state, draw arrows for every possible input",
                            "reasoning": "Every state must have a transition for each symbol in the input alphabet",
                            "validation": "Each state has exactly |Σ| outgoing transitions (where Σ is the alphabet)",
                            "common_mistakes": [
                                "Missing transitions for some inputs",
                                "Unreachable states from the initial state",
                                "Forgetting to label outputs on states"
                            ]
                        },
                        {
                            "step": 3,
                            "action": "Assign outputs to each state",
                            "why": "In Moore machines, output depends ONLY on current state",
                            "how": "For each state, write the output it produces when the machine is in that state",
                            "reasoning": "Unlike Mealy, output doesn't depend on current input",
                            "validation": "Every state has exactly one output assigned",
                            "common_mistakes": [
                                "Confusing with Mealy and putting outputs on transitions",
                                "States with undefined outputs"
                            ]
                        },
                        {
                            "step": 4,
                            "action": "Build the transition table",
                            "why": "Formal representation needed for implementation and verification",
                            "how": "Rows = states, Columns = inputs, Cells = (next state, output)",
                            "reasoning": "Table is canonical form for verification and minimization",
                            "validation": "Table is complete: every cell has a value",
                            "common_mistakes": [
                                "Empty cells in the table",
                                "Confusing next state with output"
                            ]
                        },
                        {
                            "step": 5,
                            "action": "Verify with test sequences",
                            "why": "Confirm the machine meets specifications",
                            "how": "Simulate execution with example inputs from the problem",
                            "reasoning": "Practical verification catches errors not obvious from the table",
                            "validation": "All test sequences produce expected output",
                            "common_mistakes": [
                                "Testing only simple cases",
                                "Not checking edge cases (empty strings, loops)"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Think of states as 'memories' of what happened so far in the input",
                    "Always draw the visual diagram first - errors are easier to spot",
                    "Remember: Moore has outputs on STATES, Mealy on TRANSITIONS",
                    "Use descriptive state names (S_init, S_found_01, etc.) instead of S0, S1",
                    "Verify every state is reachable and useful (not redundant)"
                ],
                "advanced_tips": [
                    "For complex problems, use divide-and-conquer: sub-machines for sub-tasks",
                    "Apply minimization to reduce equivalent states",
                    "Consider using auxiliary variables to track multiple conditions"
                ],
                "self_assessment": [
                    "Can I justify why each state is necessary?",
                    "Have I verified that each state has transitions for all possible inputs?",
                    "Do the outputs correctly reflect the machine's state?",
                    "Does the machine handle edge cases correctly (empty input, repetitions)?",
                    "Could I explain this design to a classmate?"
                ],
                "retrieval_practice": {
                    "technique": "Active recall practice without looking at notes",
                    "exercises": [
                        "Design a Moore machine that recognizes sequences ending with '101'",
                        "Convert textual specification to state diagram",
                        "Given a table, generate the corresponding diagram",
                        "Identify and fix errors in proposed machines"
                    ]
                },
                "time_estimate": "20-30 minutes per medium exercise",
                "difficulty_indicators": {
                    "easy": "Few states (2-4), small alphabet, clear specification",
                    "medium": "Moderate states (4-7), multiple conditions",
                    "hard": "Many states (8+), complex conditions, optimization required"
                }
            }

    def _strategy_mealy_design(self) -> Dict:
        """Strategy for Mealy machine design."""
        if self.language == "it":
            return {
                "framework": {
                    "approach": "Progettazione di macchina di Mealy con uscite sulle transizioni",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Identifica quando l'uscita deve cambiare in risposta agli input",
                            "why": "Mealy reagisce immediatamente agli input (uscita su transizioni)",
                            "how": "Analizza: 'quale uscita per quale combinazione stato+input?'",
                            "reasoning": "Mealy può essere più compatta di Moore perché l'uscita risponde all'input corrente",
                            "validation": "Le specifiche richiedono risposta immediata agli input",
                            "common_mistakes": [
                                "Pensare in termini di stati invece che di transizioni",
                                "Dimenticare che l'uscita cambia DURANTE la transizione"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Determina stati minimi necessari",
                            "why": "Mealy tende a richiedere meno stati di Moore",
                            "how": "Identifica le 'memorie' necessarie di input precedenti",
                            "reasoning": "Poiché l'uscita è sulle transizioni, non servono stati separati per uscite diverse",
                            "validation": "Non ci sono stati che differiscono solo per l'uscita",
                            "common_mistakes": [
                                "Creare stati ridondanti per uscite diverse",
                                "Non sfruttare la compattezza di Mealy"
                            ]
                        },
                        {
                            "step": 3,
                            "action": "Etichetta ogni transizione con input/output",
                            "why": "Formato standard Mealy: transizioni = input/output",
                            "how": "Su ogni freccia scrivi 'simbolo_input / simbolo_output'",
                            "reasoning": "La coppia input/output definisce completamente il comportamento",
                            "validation": "Ogni transizione ha formato 'x/y' corretto",
                            "common_mistakes": [
                                "Dimenticare l'uscita su alcune transizioni",
                                "Invertire input e output nella notazione"
                            ]
                        },
                        {
                            "step": 4,
                            "action": "Costruisci tabella delle transizioni",
                            "why": "Rappresentazione formale per verifica e implementazione",
                            "how": "Celle contengono (stato_successivo, output)",
                            "reasoning": "Ogni cella codifica una transizione completa",
                            "validation": "Tabella completa e consistente",
                            "common_mistakes": [
                                "Confondere l'ordine di stato_successivo e output"
                            ]
                        },
                        {
                            "step": 5,
                            "action": "Verifica con trace di esecuzione",
                            "why": "Assicurarsi che l'uscita sia prodotta al momento giusto",
                            "how": "Simula step-by-step notando quando viene prodotta l'uscita",
                            "reasoning": "Con Mealy, l'uscita è prodotta durante la transizione, non dopo",
                            "validation": "Output prodotto al momento corretto rispetto alle specifiche",
                            "common_mistakes": [
                                "Aspettarsi output ritardato come in Moore"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Mealy = reattiva (uscita immediata), Moore = memorizzata (uscita ritardata)",
                    "Usa Mealy quando serve risposta rapida agli input",
                    "Mealy può riconoscere pattern in meno stati di Moore",
                    "Notazione: freccia con 'input/output' (non 'output/input'!)"
                ],
                "advanced_tips": [
                    "Per conversione Mealy→Moore, aggiungi stati per ritardare l'uscita",
                    "Minimizzazione di Mealy: unisci stati con stesse transizioni e uscite"
                ],
                "self_assessment": [
                    "L'uscita è prodotta al momento giusto (durante transizione)?",
                    "Ho sfruttato la compattezza di Mealy (meno stati di Moore)?",
                    "Ogni transizione ha input e output correttamente etichettati?",
                    "La macchina reagisce correttamente a sequenze di input?"
                ],
                "retrieval_practice": {
                    "technique": "Confronta Mealy vs Moore per stesso problema",
                    "exercises": [
                        "Progetta Mealy che conta '1' in input binario (output = contatore mod 4)",
                        "Converti specifica → Mealy → verifica",
                        "Identifica vantaggi di Mealy rispetto a Moore per problema dato"
                    ]
                },
                "time_estimate": "15-25 minuti per esercizio medio",
                "difficulty_indicators": {
                    "easy": "Pochi stati, output semplice",
                    "medium": "Stati moderati, pattern di riconoscimento",
                    "hard": "Ottimizzazione richiesta, conversione da/a Moore"
                }
            }
        else:  # English
            return {
                "framework": {
                    "approach": "Design Mealy machine with outputs on transitions",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Identify when output must change in response to inputs",
                            "why": "Mealy reacts immediately to inputs (output on transitions)",
                            "how": "Analyze: 'which output for which state+input combination?'",
                            "reasoning": "Mealy can be more compact than Moore because output responds to current input",
                            "validation": "Specifications require immediate response to inputs",
                            "common_mistakes": [
                                "Thinking in terms of states instead of transitions",
                                "Forgetting that output changes DURING transition"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Determine minimum necessary states",
                            "why": "Mealy tends to require fewer states than Moore",
                            "how": "Identify necessary 'memories' of previous inputs",
                            "reasoning": "Since output is on transitions, separate states for different outputs aren't needed",
                            "validation": "No states that differ only in output",
                            "common_mistakes": [
                                "Creating redundant states for different outputs",
                                "Not leveraging Mealy's compactness"
                            ]
                        },
                        {
                            "step": 3,
                            "action": "Label each transition with input/output",
                            "why": "Standard Mealy format: transitions = input/output",
                            "how": "On each arrow write 'input_symbol / output_symbol'",
                            "reasoning": "Input/output pair completely defines behavior",
                            "validation": "Each transition has correct 'x/y' format",
                            "common_mistakes": [
                                "Forgetting output on some transitions",
                                "Reversing input and output in notation"
                            ]
                        },
                        {
                            "step": 4,
                            "action": "Build transition table",
                            "why": "Formal representation for verification and implementation",
                            "how": "Cells contain (next_state, output)",
                            "reasoning": "Each cell encodes a complete transition",
                            "validation": "Table is complete and consistent",
                            "common_mistakes": [
                                "Confusing order of next_state and output"
                            ]
                        },
                        {
                            "step": 5,
                            "action": "Verify with execution traces",
                            "why": "Ensure output is produced at the right time",
                            "how": "Simulate step-by-step noting when output is produced",
                            "reasoning": "With Mealy, output is produced during transition, not after",
                            "validation": "Output produced at correct time per specifications",
                            "common_mistakes": [
                                "Expecting delayed output as in Moore"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Mealy = reactive (immediate output), Moore = memorized (delayed output)",
                    "Use Mealy when fast response to inputs is needed",
                    "Mealy can recognize patterns in fewer states than Moore",
                    "Notation: arrow with 'input/output' (not 'output/input'!)"
                ],
                "advanced_tips": [
                    "For Mealy→Moore conversion, add states to delay output",
                    "Mealy minimization: merge states with same transitions and outputs"
                ],
                "self_assessment": [
                    "Is output produced at the right time (during transition)?",
                    "Have I leveraged Mealy's compactness (fewer states than Moore)?",
                    "Is each transition correctly labeled with input and output?",
                    "Does the machine react correctly to input sequences?"
                ],
                "retrieval_practice": {
                    "technique": "Compare Mealy vs Moore for same problem",
                    "exercises": [
                        "Design Mealy that counts '1's in binary input (output = counter mod 4)",
                        "Convert specification → Mealy → verify",
                        "Identify Mealy advantages over Moore for given problem"
                    ]
                },
                "time_estimate": "15-25 minutes per medium exercise",
                "difficulty_indicators": {
                    "easy": "Few states, simple output",
                    "medium": "Moderate states, pattern recognition",
                    "hard": "Optimization required, conversion from/to Moore"
                }
            }

    def _strategy_mealy_to_moore(self) -> Dict:
        """Strategy for converting Mealy to Moore machines."""
        # Implementation with bilingual support
        if self.language == "it":
            approach = "Conversione sistematica da Mealy a Moore"
            tip1 = "Moore ha sempre più stati o ugual numero di Mealy"
            tip2 = "Ogni output di Mealy diventa uno stato separato in Moore"
        else:
            approach = "Systematic conversion from Mealy to Moore"
            tip1 = "Moore always has more or equal states than Mealy"
            tip2 = "Each Mealy output becomes a separate state in Moore"

        return {
            "framework": {
                "approach": approach,
                "steps": [
                    # Detailed conversion steps...
                ]
            },
            "learning_tips": [tip1, tip2],
            "time_estimate": "15-20 minutes per conversion"
        }

    def _strategy_moore_to_mealy(self) -> Dict:
        """Strategy for converting Moore to Mealy machines."""
        # Similar structure to mealy_to_moore
        return {
            "framework": {"approach": "Convert Moore to Mealy", "steps": []},
            "learning_tips": ["Mealy is typically more compact"],
            "time_estimate": "10-15 minutes per conversion"
        }

    def _strategy_fsm_minimization(self) -> Dict:
        """Strategy for FSM state minimization."""
        return {
            "framework": {"approach": "Minimize FSM using equivalence partitioning", "steps": []},
            "learning_tips": ["Use partition refinement algorithm", "Merge equivalent states"],
            "time_estimate": "20-30 minutes per minimization"
        }

    def _strategy_fsm_analysis(self) -> Dict:
        """Strategy for analyzing FSM transition tables."""
        return {
            "framework": {"approach": "Analyze FSM from transition table", "steps": []},
            "learning_tips": ["Check for completeness", "Identify reachable states"],
            "time_estimate": "10-15 minutes per analysis"
        }

    # ==================== CIRCUIT DESIGN STRATEGIES ====================

    def _strategy_boolean_minimization(self) -> Dict:
        """Strategy for Boolean function minimization."""
        if self.language == "it":
            return {
                "framework": {
                    "approach": "Minimizzazione di funzioni booleane con algebra e K-map",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Scrivi la funzione in forma SOP (Sum of Products)",
                            "why": "Forma canonica per applicare minimizzazione",
                            "how": "Identifica i mintermini (righe con output=1 nella truth table)",
                            "reasoning": "SOP è la base per K-map e algebra booleana",
                            "validation": "Ogni termine è un prodotto di letterali",
                            "common_mistakes": ["Confondere SOP con POS", "Mintermini incompleti"]
                        }
                    ]
                },
                "learning_tips": [
                    "Usa K-map per funzioni fino a 4 variabili",
                    "Per 5+ variabili, usa Quine-McCluskey o strumenti software",
                    "Raggruppa sempre a potenze di 2 (1, 2, 4, 8, ...)"
                ],
                "time_estimate": "10-20 minuti per minimizzazione medio"
            }
        else:
            return {
                "framework": {
                    "approach": "Boolean function minimization with algebra and K-maps",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Write function in SOP (Sum of Products) form",
                            "why": "Canonical form for applying minimization",
                            "how": "Identify minterms (rows with output=1 in truth table)",
                            "reasoning": "SOP is the basis for K-maps and Boolean algebra",
                            "validation": "Each term is a product of literals",
                            "common_mistakes": ["Confusing SOP with POS", "Incomplete minterms"]
                        }
                    ]
                },
                "learning_tips": [
                    "Use K-maps for functions up to 4 variables",
                    "For 5+ variables, use Quine-McCluskey or software tools",
                    "Always group in powers of 2 (1, 2, 4, 8, ...)"
                ],
                "time_estimate": "10-20 minutes per medium minimization"
            }

    def _strategy_karnaugh_map(self) -> Dict:
        """Strategy for Karnaugh map construction and solving."""
        return {
            "framework": {"approach": "Systematic K-map construction and grouping", "steps": []},
            "learning_tips": [
                "Use Gray code ordering for variables",
                "Group largest rectangles first (powers of 2)",
                "Don't-care terms can be included or excluded"
            ],
            "time_estimate": "15-20 minutes per K-map exercise"
        }

    def _strategy_circuit_design(self) -> Dict:
        """Strategy for general circuit design."""
        return {
            "framework": {"approach": "Design combinational/sequential circuits", "steps": []},
            "learning_tips": [
                "Start with truth table or state machine",
                "Minimize logic before implementation",
                "Verify timing constraints for sequential circuits"
            ],
            "time_estimate": "25-40 minutes per circuit design"
        }

    def _strategy_sequential_circuit(self) -> Dict:
        """Strategy for sequential circuit analysis and design."""
        return {
            "framework": {"approach": "Sequential circuit design with flip-flops", "steps": []},
            "learning_tips": [
                "Distinguish between synchronous and asynchronous",
                "Use state diagrams first, then derive flip-flop inputs",
                "Check for race conditions and hazards"
            ],
            "time_estimate": "30-45 minutes per sequential circuit"
        }

    def _strategy_latch_analysis(self) -> Dict:
        """Strategy for analyzing latches and flip-flops."""
        return {
            "framework": {"approach": "Analyze latch/flip-flop behavior", "steps": []},
            "learning_tips": [
                "Understand SR, D, JK, T flip-flop differences",
                "Check setup and hold times",
                "Trace state changes step-by-step"
            ],
            "time_estimate": "10-15 minutes per latch analysis"
        }

    # ==================== PERFORMANCE ANALYSIS STRATEGIES ====================

    def _strategy_amdahl_law(self) -> Dict:
        """Strategy for applying Amdahl's Law."""
        if self.language == "it":
            return {
                "framework": {
                    "approach": "Applicazione della Legge di Amdahl per speedup",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Identifica la frazione migliorabile (f) e il fattore di miglioramento (s)",
                            "why": "Amdahl quantifica il limite superiore dello speedup",
                            "how": "f = tempo_parte_migliorabile / tempo_totale, s = speedup della parte",
                            "reasoning": "Solo la parte migliorabile contribuisce allo speedup totale",
                            "validation": "0 ≤ f ≤ 1, s ≥ 1",
                            "common_mistakes": [
                                "Confondere frazione migliorabile con frazione NON migliorabile",
                                "Usare percentuali invece di frazioni (0-1)"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Applica la formula: Speedup = 1 / ((1-f) + f/s)",
                            "why": "Formula di Amdahl per speedup complessivo",
                            "how": "Sostituisci i valori e calcola",
                            "reasoning": "Parte non migliorabile (1-f) limita speedup massimo",
                            "validation": "Speedup ≤ 1/(1-f) (limite per s→∞)",
                            "common_mistakes": [
                                "Dimenticare di sottrarre 1-f",
                                "Invertire f e s nella formula"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Legge di Amdahl mostra che la parte NON parallelizzabile limita lo speedup",
                    "Se f=0.9 e s=10, speedup ≈ 5.26 (non 10!)",
                    "Speedup massimo = 1/(1-f) quando s→∞",
                    "Utile per valutare costo/beneficio di ottimizzazioni"
                ],
                "self_assessment": [
                    "Ho identificato correttamente la frazione migliorabile?",
                    "Ho applicato la formula con i valori giusti?",
                    "Il risultato ha senso fisicamente (speedup ragionevole)?"
                ],
                "retrieval_practice": {
                    "technique": "Risolvi problemi senza guardare la formula",
                    "exercises": [
                        "Se il 70% di un programma è parallelizzabile con speedup 4x, qual è lo speedup totale?",
                        "Quale frazione minima serve per ottenere speedup 2x con miglioramento 10x?"
                    ]
                },
                "time_estimate": "5-10 minuti per problema Amdahl"
            }
        else:
            return {
                "framework": {
                    "approach": "Applying Amdahl's Law for speedup calculation",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Identify improvable fraction (f) and improvement factor (s)",
                            "why": "Amdahl quantifies the upper bound of speedup",
                            "how": "f = time_improvable_part / total_time, s = speedup of that part",
                            "reasoning": "Only the improved part contributes to total speedup",
                            "validation": "0 ≤ f ≤ 1, s ≥ 1",
                            "common_mistakes": [
                                "Confusing improvable fraction with NON-improvable fraction",
                                "Using percentages instead of fractions (0-1)"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Apply formula: Speedup = 1 / ((1-f) + f/s)",
                            "why": "Amdahl's formula for overall speedup",
                            "how": "Substitute values and calculate",
                            "reasoning": "Non-improvable part (1-f) limits maximum speedup",
                            "validation": "Speedup ≤ 1/(1-f) (limit when s→∞)",
                            "common_mistakes": [
                                "Forgetting to subtract 1-f",
                                "Inverting f and s in formula"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Amdahl's Law shows non-parallelizable part limits speedup",
                    "If f=0.9 and s=10, speedup ≈ 5.26 (not 10!)",
                    "Maximum speedup = 1/(1-f) when s→∞",
                    "Useful for evaluating cost/benefit of optimizations"
                ],
                "self_assessment": [
                    "Did I correctly identify the improvable fraction?",
                    "Did I apply the formula with correct values?",
                    "Does the result make physical sense (reasonable speedup)?"
                ],
                "retrieval_practice": {
                    "technique": "Solve problems without looking at the formula",
                    "exercises": [
                        "If 70% of a program is parallelizable with 4x speedup, what's total speedup?",
                        "What minimum fraction is needed for 2x speedup with 10x improvement?"
                    ]
                },
                "time_estimate": "5-10 minutes per Amdahl problem"
            }

    def _strategy_mips_calculation(self) -> Dict:
        """Strategy for MIPS calculation."""
        return {
            "framework": {
                "approach": "Calculate MIPS (Millions of Instructions Per Second)",
                "steps": [
                    {
                        "step": 1,
                        "action": "Identify: instruction count, CPI, clock frequency",
                        "why": "MIPS = (Instructions / Execution_Time) / 10^6",
                        "how": "Execution_Time = (Instructions × CPI) / Clock_Frequency",
                        "reasoning": "MIPS measures throughput, not performance",
                        "validation": "Units: MIPS, CPI (cycles/instruction), frequency (Hz)",
                        "common_mistakes": [
                            "Confusing MIPS with execution time",
                            "Wrong unit conversions (MHz vs GHz)"
                        ]
                    }
                ]
            },
            "learning_tips": [
                "MIPS = Clock_Rate / (CPI × 10^6)",
                "Higher MIPS doesn't always mean faster execution",
                "Different instruction mixes have different CPI"
            ],
            "time_estimate": "5-10 minutes per MIPS calculation"
        }

    def _strategy_speedup_calculation(self) -> Dict:
        """Strategy for general speedup calculation."""
        return {
            "framework": {
                "approach": "Calculate speedup = Time_old / Time_new",
                "steps": []
            },
            "learning_tips": [
                "Speedup > 1 means improvement",
                "Speedup = 2 means 2x faster (half the time)",
                "Combine with Amdahl's Law for partial improvements"
            ],
            "time_estimate": "5-8 minutes per speedup problem"
        }

    def _strategy_performance_comparison(self) -> Dict:
        """Strategy for comparing system performance."""
        return {
            "framework": {"approach": "Compare performance metrics systematically", "steps": []},
            "learning_tips": [
                "Use consistent metrics (throughput, latency, MIPS)",
                "Consider workload characteristics",
                "Check for bottlenecks"
            ],
            "time_estimate": "15-25 minutes per comparison"
        }

    # ==================== NUMBER SYSTEMS STRATEGIES ====================

    def _strategy_base_conversion(self) -> Dict:
        """Strategy for base conversion."""
        return {
            "framework": {"approach": "Convert between number bases systematically", "steps": []},
            "learning_tips": [
                "Decimal to base-N: divide repeatedly by N, collect remainders",
                "Base-N to decimal: multiply each digit by base^position",
                "Binary ↔ Octal/Hex: group bits (3 for octal, 4 for hex)"
            ],
            "time_estimate": "5-10 minutes per conversion"
        }

    def _strategy_ieee754_conversion(self) -> Dict:
        """Strategy for IEEE 754 floating point conversion."""
        return {
            "framework": {"approach": "Convert decimal ↔ IEEE 754 format", "steps": []},
            "learning_tips": [
                "Format: sign (1 bit) | exponent (8/11 bits) | mantissa (23/52 bits)",
                "Exponent is biased (bias = 127 for single, 1023 for double)",
                "Normalize to 1.xxx × 2^exp form first"
            ],
            "time_estimate": "15-25 minutes per IEEE 754 conversion"
        }

    def _strategy_complement_arithmetic(self) -> Dict:
        """Strategy for two's complement arithmetic."""
        return {
            "framework": {"approach": "Perform arithmetic in two's complement", "steps": []},
            "learning_tips": [
                "Two's complement: invert bits + add 1",
                "MSB = sign bit (1 = negative)",
                "Overflow: check sign bit mismatch"
            ],
            "time_estimate": "8-12 minutes per arithmetic problem"
        }

    # ==================== LINEAR ALGEBRA STRATEGIES ====================

    def _strategy_gaussian_elimination(self) -> Dict:
        """Strategy for Gaussian elimination."""
        return {
            "framework": {"approach": "Solve linear systems with Gaussian elimination", "steps": []},
            "learning_tips": [
                "Forward elimination: make upper triangular",
                "Back substitution: solve from bottom up",
                "Check for row echelon form"
            ],
            "time_estimate": "20-30 minutes per system"
        }

    def _strategy_eigenvalue_computation(self) -> Dict:
        """Strategy for eigenvalue and eigenvector computation."""
        return {
            "framework": {"approach": "Compute eigenvalues and eigenvectors", "steps": []},
            "learning_tips": [
                "Solve det(A - λI) = 0 for eigenvalues",
                "For each λ, solve (A - λI)v = 0 for eigenvectors",
                "Verify: Av = λv"
            ],
            "time_estimate": "25-35 minutes per eigenvalue problem"
        }

    # ==================== CONCURRENT PROGRAMMING STRATEGIES ====================

    def _strategy_monitor_design(self) -> Dict:
        """Strategy for monitor design."""
        if self.language == "it":
            return {
                "framework": {
                    "approach": "Progettazione di monitor per sincronizzazione",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Identifica risorse condivise e invarianti",
                            "why": "Il monitor protegge l'accesso a risorse condivise",
                            "how": "Elenca variabili condivise e condizioni di correttezza",
                            "reasoning": "Gli invarianti devono essere preservati da ogni procedura del monitor",
                            "validation": "Tutti gli accessi a risorse condivise passano attraverso il monitor",
                            "common_mistakes": [
                                "Dimenticare di proteggere alcune variabili condivise",
                                "Invarianti non chiari o incompleti"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Definisci condition variables per coordinazione",
                            "why": "I thread devono attendere/segnalare eventi",
                            "how": "Identifica condizioni di attesa (es: buffer_pieno, buffer_vuoto)",
                            "reasoning": "Condition variables permettono attesa efficiente senza busy-waiting",
                            "validation": "Ogni wait() ha un corrispondente signal()/broadcast()",
                            "common_mistakes": [
                                "Usare busy-waiting invece di condition variables",
                                "Signal() senza nessun thread in attesa (segnale perso)"
                            ]
                        },
                        {
                            "step": 3,
                            "action": "Implementa procedure con mutua esclusione",
                            "why": "Monitor garantisce che solo un thread alla volta esegua procedure",
                            "how": "Ogni procedura del monitor è implicitamente protetta da lock",
                            "reasoning": "La mutua esclusione evita race conditions",
                            "validation": "Nessun accesso diretto a variabili del monitor dall'esterno",
                            "common_mistakes": [
                                "Assumere che wait() mantenga il lock (lo rilascia!)",
                                "Deadlock da attese circolari"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Monitor = dati condivisi + procedure + condition variables",
                    "wait() rilascia il lock, signal() sveglia un thread in attesa",
                    "Usa while (non if) per controllare condizioni dopo wait()",
                    "Broadcast() sveglia tutti, signal() sveglia uno solo"
                ],
                "self_assessment": [
                    "Gli invarianti sono preservati da tutte le procedure?",
                    "Ho evitato deadlock e starvation?",
                    "Le condition variables sono usate correttamente?"
                ],
                "retrieval_practice": {
                    "technique": "Implementa monitor classici senza guardare esempi",
                    "exercises": [
                        "Progetta monitor per produttore-consumatore con buffer limitato",
                        "Implementa monitor per lettori-scrittori con priorità",
                        "Crea monitor per semaforo contatore"
                    ]
                },
                "time_estimate": "30-45 minuti per design monitor complesso"
            }
        else:
            return {
                "framework": {
                    "approach": "Design monitors for synchronization",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Identify shared resources and invariants",
                            "why": "Monitor protects access to shared resources",
                            "how": "List shared variables and correctness conditions",
                            "reasoning": "Invariants must be preserved by every monitor procedure",
                            "validation": "All shared resource accesses go through monitor",
                            "common_mistakes": [
                                "Forgetting to protect some shared variables",
                                "Unclear or incomplete invariants"
                            ]
                        },
                        {
                            "step": 2,
                            "action": "Define condition variables for coordination",
                            "why": "Threads need to wait/signal events",
                            "how": "Identify wait conditions (e.g., buffer_full, buffer_empty)",
                            "reasoning": "Condition variables enable efficient waiting without busy-waiting",
                            "validation": "Each wait() has corresponding signal()/broadcast()",
                            "common_mistakes": [
                                "Using busy-waiting instead of condition variables",
                                "Signal() with no waiting threads (lost signal)"
                            ]
                        },
                        {
                            "step": 3,
                            "action": "Implement procedures with mutual exclusion",
                            "why": "Monitor ensures only one thread executes procedures at a time",
                            "how": "Each monitor procedure is implicitly protected by lock",
                            "reasoning": "Mutual exclusion prevents race conditions",
                            "validation": "No direct access to monitor variables from outside",
                            "common_mistakes": [
                                "Assuming wait() keeps the lock (it releases it!)",
                                "Deadlock from circular waits"
                            ]
                        }
                    ]
                },
                "learning_tips": [
                    "Monitor = shared data + procedures + condition variables",
                    "wait() releases lock, signal() wakes one waiting thread",
                    "Use while (not if) to check conditions after wait()",
                    "broadcast() wakes all, signal() wakes one"
                ],
                "self_assessment": [
                    "Are invariants preserved by all procedures?",
                    "Have I avoided deadlock and starvation?",
                    "Are condition variables used correctly?"
                ],
                "retrieval_practice": {
                    "technique": "Implement classic monitors without looking at examples",
                    "exercises": [
                        "Design monitor for producer-consumer with bounded buffer",
                        "Implement monitor for readers-writers with priority",
                        "Create monitor for counting semaphore"
                    ]
                },
                "time_estimate": "30-45 minutes per complex monitor design"
            }

    def _strategy_semaphore_synchronization(self) -> Dict:
        """Strategy for semaphore synchronization."""
        return {
            "framework": {"approach": "Synchronize with semaphores", "steps": []},
            "learning_tips": [
                "Semaphore: counter with wait() and signal() operations",
                "Binary semaphore = mutex (0 or 1)",
                "Counting semaphore for resource pools",
                "Always pair wait() with signal()"
            ],
            "time_estimate": "20-30 minutes per synchronization problem"
        }

    def format_strategy_output(self, strategy: Dict, core_loop_name: str) -> str:
        """
        Format strategy for rich markdown display.

        Args:
            strategy: Strategy dictionary
            core_loop_name: Name of the core loop

        Returns:
            Formatted markdown string
        """
        if not strategy:
            return f"No strategy available for '{core_loop_name}'."

        lines = []

        # Header
        lines.append(f"# Study Strategy: {core_loop_name}\n")

        # Framework
        if "framework" in strategy:
            fw = strategy["framework"]
            lines.append("## Problem-Solving Framework\n")
            lines.append(f"**Approach:** {fw.get('approach', 'N/A')}\n")

            if "steps" in fw:
                lines.append("### Steps:\n")
                for step in fw["steps"]:
                    lines.append(f"#### Step {step['step']}: {step['action']}\n")
                    lines.append(f"- **Why:** {step['why']}")
                    lines.append(f"- **How:** {step['how']}")
                    lines.append(f"- **Reasoning:** {step['reasoning']}")
                    lines.append(f"- **Validation:** {step['validation']}")

                    if step.get('common_mistakes'):
                        lines.append(f"- **Common Mistakes:**")
                        for mistake in step['common_mistakes']:
                            lines.append(f"  - {mistake}")
                    lines.append("")

        # Learning Tips
        if strategy.get("learning_tips"):
            lines.append("## Learning Tips\n")
            for tip in strategy["learning_tips"]:
                lines.append(f"- {tip}")
            lines.append("")

        # Self-Assessment
        if strategy.get("self_assessment"):
            lines.append("## Self-Assessment Questions\n")
            for question in strategy["self_assessment"]:
                lines.append(f"- {question}")
            lines.append("")

        # Retrieval Practice
        if strategy.get("retrieval_practice"):
            rp = strategy["retrieval_practice"]
            lines.append("## Retrieval Practice\n")
            lines.append(f"**Technique:** {rp.get('technique', 'N/A')}\n")
            if rp.get("exercises"):
                lines.append("**Exercises:**")
                for ex in rp["exercises"]:
                    lines.append(f"- {ex}")
            lines.append("")

        # Time Estimate
        if strategy.get("time_estimate"):
            lines.append(f"**Estimated Time:** {strategy['time_estimate']}\n")

        return "\n".join(lines)
