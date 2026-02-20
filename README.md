# Mine de Teint — Blog Auto

Publication automatique de 100 articles SEO sur Shopify via Claude.
Planning intelligent avec horaires aleatoires pour un profil de publication naturel.

## Planning de publication

### Phase 1 — Articles 1 a 30 (lancement intensif)
- **Frequence** : 1 article par jour
- **Jours** : lundi au vendredi
- **Horaire** : aleatoire entre 7h35 et 10h17
- **Duree** : ~6 semaines

### Phase 2 — Articles 31 a 100 (rythme de croisiere)
- **Frequence** : tous les 2 jours
- **Jours** : lundi au samedi (pas le dimanche)
- **Alternance** : semaine A (lun-mer-ven) / semaine B (mar-jeu-sam)
- **Horaire** : aleatoire entre 7h35 et 10h17
- **Duree** : ~7 semaines

**Duree totale : ~13 semaines pour 100 articles.**

## Installation

1. **Installe les dependances**
   ```bash
   chmod +x install.sh && ./install.sh
   ```

2. **Genere le planning et verifie-le**
   ```bash
   python3 scheduler.py
   ```

3. **Genere articles.json**
   ```bash
   python3 generate_articles_json.py
   ```

4. **Teste une premiere publication**
   ```bash
   python3 publish.py
   ```

5. **Active le cron pour l'automatisation complete**
   ```bash
   chmod +x cron-setup.sh && ./cron-setup.sh
   ```

## Fichiers

| Fichier | Role |
|---------|------|
| `publish.py` | Script principal — genere et publie l'article du |
| `scheduler.py` | Genere le planning avec dates et heures aleatoires |
| `generate_articles_json.py` | Cree articles.json avec le planning pre-calcule |
| `articles.json` | Liste des 100 articles avec planning |
| `.env` | Cles API (ne jamais partager) |
| `logs.txt` | Journal de toutes les publications |
| `cron-setup.sh` | Active la verification automatique toutes les 20 min |

## Comment ca marche

1. `scheduler.py` pre-calcule les 100 dates et heures de publication
2. Le cron lance `publish.py` toutes les 20 minutes (7h30-10h20, lun-sam)
3. `publish.py` obtient un token Shopify frais (renouvellement automatique)
4. Si un article est du : genere via Claude -> publie sur Shopify -> marque comme publie
5. Si aucun article du : ne fait rien, attend le prochain check

## Token Shopify

Le token est obtenu automatiquement via le flux client credentials.
Il se renouvelle a chaque execution (expire toutes les 24h).
Aucune intervention manuelle requise.
