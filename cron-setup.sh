#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cron toutes les 20 min entre 7h30 et 10h20, du lundi au samedi
# Le script publish.py verifie si un article doit etre publie a ce moment precis
CRON_CMD="*/20 7-10 * * 1-6 cd $SCRIPT_DIR && /usr/bin/python3 publish.py >> $SCRIPT_DIR/logs.txt 2>&1"

(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "Cron job installe avec succes."
echo ""
echo "Fonctionnement :"
echo "  -> Le cron verifie toutes les 20 min entre 7h30 et 10h20"
echo "  -> Du lundi au samedi"
echo "  -> Le script publie uniquement si l'heure planifiee est passee"
echo ""
echo "Planning de publication :"
echo "  -> Articles 1-30  : lundi-vendredi, 1/jour, heure aleatoire 7h35-10h17"
echo "  -> Articles 31-100 : tous les 2 jours lun-sam, alternance semaine A/B"
echo ""
echo "Pour verifier : crontab -l"
echo "Pour supprimer : crontab -e"
echo "Pour voir le planning : python3 scheduler.py"
