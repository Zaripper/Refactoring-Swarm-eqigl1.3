# Synthèse des Exigences du TP - The Refactoring Swarm

## Objectif Scientifique
Construire un système multi-agents capable de prendre en entrée un dossier contenant du code Python "mal fait" (buggy, non documenté, non testé) et de délivrer en sortie une version propre, fonctionnelle et validée par des tests.

## Architecture du Système (3 Agents Spécialisés)
1. **The Auditor** : Lit le code, effectue une analyse statique et produit un plan de refactoring.
2. **The Fixer** : Lit le plan, modifie les fichiers de code un par un pour corriger les erreurs.
3. **The Judge** : Exécute les tests unitaires.
   - Si échec : Renvoie au Fixer avec les logs d'erreur (Boucle d'auto-correction).
   - Si succès : Confirme la fin de la mission.

## Rôles de l'Équipe (4 Rôles)
1. **L'Orchestrateur (Lead Dev)** : Conçoit le graphe d'exécution (LangGraph, CrewAI ou AutoGen), gère la logique de passage de relais et `main.py`.
2. **The Toolsmith** : Développe les fonctions Python appelées par les agents (API interne), gère la sécurité (limitation au dossier "sandbox") et les interfaces avec `pylint` et `pytest`.
3. **The Prompt Engineer** : Écrit et versionne les prompts système, optimise pour minimiser les hallucinations et les coûts.
4. **The Quality & Data Manager** : Responsable de la télémétrie, s'assure que chaque action est enregistrée dans `logs/experiment_data.json`.

## Contraintes Techniques
- **Python** : 3.10 ou 3.11 (3.12+ non supporté).
- **API** : Google Gemini.
- **Logging** : Utilisation obligatoire de `src/utils/logger.py`. Chaque interaction LLM doit être enregistrée avec `input_prompt` et `output_response`.
- **Point d'entrée** : `python main.py --target_dir "./sandbox/dataset_inconnu"`.
- **Git** : Commits fréquents et messages clairs.

## Critères d'Évaluation
- **Performance (40%)** : Tests unitaires réussis, score Pylint augmenté.
- **Robustesse Technique (30%)** : Pas de crash, pas de boucle infinie (max 10 itérations), respect de l'argument `--target_dir`.
- **Qualité des Données (30%)** : Fichier `experiment_data.json` valide et complet.
