#!/bin/bash
echo "Installation des dependances Mine de Teint Blog Auto..."
pip3 install requests python-dotenv
echo "Installation terminee."
echo ""
echo "=== Prochaines etapes ==="
echo "1. Lance : python3 scheduler.py  (pour voir le planning)"
echo "2. Lance : python3 generate_articles_json.py  (pour generer articles.json)"
echo "3. Lance : python3 publish.py    (pour tester la premiere publication)"
echo "4. Lance : ./cron-setup.sh       (pour automatiser)"
