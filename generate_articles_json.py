import json
from scheduler import generate_schedule

ARTICLES_DATA = [
    # === LUMINOTHERAPIE & SCIENCE (20 articles) ===
    {"title": "Qu'est-ce que la photobiomodulation ? La science derriere la luminotherapie LED", "keywords": "photobiomodulation, luminotherapie LED, science LED peau"},
    {"title": "Comment les longueurs d'onde LED agissent sur votre peau en profondeur", "keywords": "longueurs d'onde LED, action LED peau, penetration lumiere peau"},
    {"title": "LED rouge 650nm : pourquoi c'est la longueur d'onde anti-age la plus efficace", "keywords": "LED rouge 650nm, anti-age LED, lumiere rouge peau"},
    {"title": "LED bleue 460nm : comment elle detruit les bacteries responsables de l'acne", "keywords": "LED bleue 460nm, acne LED bleue, bacteries acne lumiere"},
    {"title": "Infrarouge proche 850nm : la lumiere invisible qui transforme votre peau", "keywords": "infrarouge proche 850nm, LED infrarouge peau, lumiere invisible soin"},
    {"title": "1064nm infrarouge profond : la technologie exclusive du Masque LED Pro Mine de Teint", "keywords": "1064nm infrarouge profond, masque LED pro, technologie exclusive LED"},
    {"title": "Luminotherapie LED vs laser : quelles differences pour votre peau ?", "keywords": "luminotherapie vs laser, LED ou laser peau, difference LED laser"},
    {"title": "Les etudes cliniques qui prouvent l'efficacite de la luminotherapie LED", "keywords": "etudes cliniques LED, preuves scientifiques luminotherapie, efficacite LED prouvee"},
    {"title": "Comment fonctionne la stimulation du collagene par la lumiere rouge ?", "keywords": "stimulation collagene LED, lumiere rouge collagene, production collagene LED"},
    {"title": "Securite de la luminotherapie LED : tout ce que vous devez savoir", "keywords": "securite luminotherapie LED, LED dangereuse, risques masque LED"},
    {"title": "La chronobiologie de la peau : pourquoi le soir est le meilleur moment pour la LED", "keywords": "chronobiologie peau, meilleur moment LED, soin LED soir"},
    {"title": "Mitochondries et LED : comment la lumiere produit de l'energie dans vos cellules", "keywords": "mitochondries LED, energie cellulaire lumiere, ATP luminotherapie"},
    {"title": "Pourquoi la regularite est plus importante que l'intensite en luminotherapie", "keywords": "regularite luminotherapie, frequence soin LED, routine LED reguliere"},
    {"title": "LED ambree 590nm : le secret d'un teint lumineux et uniforme", "keywords": "LED ambree 590nm, teint lumineux LED, lumiere ambree peau"},
    {"title": "3 zones de traitement du masque LED : visage, cuir chevelu et traitement profond", "keywords": "zones traitement masque LED, LED visage cuir chevelu, masque LED 3 zones"},
    {"title": "Photobiomodulation et cicatrisation : comment la LED accelere la reparation cutanee", "keywords": "photobiomodulation cicatrisation, LED reparation peau, cicatrisation lumiere"},
    {"title": "Les certifications CE, FCC et IEC 62471 expliquees pour votre masque LED", "keywords": "certification CE FCC masque LED, IEC 62471, normes securite LED"},
    {"title": "Flux lumineux et puissance : comment evaluer l'efficacite d'un masque LED", "keywords": "flux lumineux masque LED, puissance LED, evaluer efficacite masque"},
    {"title": "La difference entre luminotherapie grand public et traitement medical", "keywords": "luminotherapie grand public vs medical, LED domicile vs clinique, soin LED professionnel"},
    {"title": "Histoire de la phototherapie : des hopitaux a votre salle de bain", "keywords": "histoire phototherapie, origines luminotherapie, evolution LED soin"},

    # === ANTI-AGE & COLLAGENE (20 articles) ===
    {"title": "Collagene et elastine : comment les booster naturellement avec la lumiere LED", "keywords": "collagene elastine LED, booster collagene naturellement, lumiere LED anti-age"},
    {"title": "Rides d'expression vs rides profondes : quelle lumiere LED pour chaque type ?", "keywords": "rides expression LED, rides profondes traitement, lumiere LED rides"},
    {"title": "Perte de fermete apres 40 ans : comment la LED peut renverser la tendance", "keywords": "fermete peau 40 ans, LED anti-relachement, raffermissement LED"},
    {"title": "Taches brunes et hyperpigmentation : le protocole LED pour un teint uniforme", "keywords": "taches brunes LED, hyperpigmentation luminotherapie, teint uniforme LED"},
    {"title": "Cernes et poches sous les yeux : la LED peut-elle vraiment aider ?", "keywords": "cernes LED, poches yeux luminotherapie, contour yeux LED"},
    {"title": "Le protocole anti-age complet : combiner LED et soins topiques", "keywords": "protocole anti-age LED, combiner LED soins, routine anti-age complete"},
    {"title": "Avant / apres masque LED : a quoi ressemblent vraiment les resultats apres 12 semaines", "keywords": "avant apres masque LED, resultats LED 12 semaines, transformation LED"},
    {"title": "Menopause et peau : comment la luminotherapie LED compense la chute d'oestrogenes", "keywords": "menopause peau LED, oestrogenes luminotherapie, soin peau menopause"},
    {"title": "Peau terne et fatiguee : retrouver l'eclat en 10 minutes par jour", "keywords": "peau terne LED, eclat visage luminotherapie, teint fatigue solution"},
    {"title": "Ovale du visage relache : comment la LED aide a sculpter naturellement", "keywords": "ovale visage relache LED, sculpter visage lumiere, raffermissement ovale LED"},
    {"title": "Soin anti-age a domicile : pourquoi la LED surpasse les cremes seules", "keywords": "soin anti-age domicile, LED vs cremes, efficacite LED anti-age"},
    {"title": "La routine beaute des femmes qui ne vieillissent pas : leur secret LED", "keywords": "routine beaute anti-age, secret jeunesse LED, femmes qui ne vieillissent pas"},
    {"title": "Peaux matures : comment adapter son utilisation du masque LED", "keywords": "peaux matures masque LED, LED peau agee, adaptation soin LED"},
    {"title": "Cou et decollete : etendre son soin LED au-dela du visage", "keywords": "cou decollete LED, soin LED corps, luminotherapie cou"},
    {"title": "Stress oxydatif et vieillissement cutane : comment la LED neutralise les radicaux libres", "keywords": "stress oxydatif LED, radicaux libres luminotherapie, anti-oxydant LED"},
    {"title": "Micro-circulation et LED : comment ameliorer l'oxygenation de votre peau", "keywords": "micro-circulation LED, oxygenation peau lumiere, circulation sanguine LED"},
    {"title": "Acide hyaluronique et LED : le duo parfait pour une peau repulpee", "keywords": "acide hyaluronique LED, peau repulpee, duo soin LED"},
    {"title": "Peptides et lumiere rouge : l'association qui multiplie les resultats", "keywords": "peptides lumiere rouge, association soins LED, synergie peptides LED"},
    {"title": "Comment la LED prepare la peau a mieux absorber vos soins", "keywords": "LED absorption soins, preparer peau LED, penetration soins luminotherapie"},
    {"title": "10 minutes de LED par jour : le bilan apres 6 mois d'utilisation", "keywords": "bilan LED 6 mois, resultats long terme LED, 10 minutes LED par jour"},

    # === ACNE, ROUGEURS, ROSACEE (15 articles) ===
    {"title": "Acne adulte : pourquoi ca arrive et comment la LED bleue la traite en profondeur", "keywords": "acne adulte LED bleue, traitement acne lumiere, LED anti-acne"},
    {"title": "Rosacee : la luminotherapie LED peut-elle calmer les rougeurs chroniques ?", "keywords": "rosacee luminotherapie, rougeurs chroniques LED, calmer rosacee lumiere"},
    {"title": "Peau sensible et LED : tout ce que vous devez savoir avant de commencer", "keywords": "peau sensible LED, luminotherapie peau reactive, precautions LED sensible"},
    {"title": "Cicatrices d'acne : comment la LED reduit les marques residuelles", "keywords": "cicatrices acne LED, marques acne luminotherapie, reduire cicatrices LED"},
    {"title": "Boutons hormonaux : le protocole LED adapte au cycle menstruel", "keywords": "boutons hormonaux LED, acne cycle menstruel, protocole LED hormonal"},
    {"title": "Couperose et LED : apaiser les vaisseaux dilates naturellement", "keywords": "couperose LED, vaisseaux dilates luminotherapie, apaiser couperose lumiere"},
    {"title": "Points noirs et pores dilates : la LED peut-elle vraiment aider ?", "keywords": "points noirs LED, pores dilates luminotherapie, resserrer pores LED"},
    {"title": "Peau grasse et LED : reguler le sebum sans dessecher", "keywords": "peau grasse LED, reguler sebum lumiere, equilibrer peau grasse LED"},
    {"title": "Eczema et psoriasis : les limites et benefices de la luminotherapie", "keywords": "eczema LED, psoriasis luminotherapie, limites LED dermatologie"},
    {"title": "Post-acne : reconstruire une peau nette avec la photobiomodulation", "keywords": "post-acne photobiomodulation, reconstruire peau LED, peau nette apres acne"},
    {"title": "Inflammation cutanee : comment l'infrarouge 850nm calme les reactions", "keywords": "inflammation cutanee infrarouge, 850nm anti-inflammatoire, calmer peau LED"},
    {"title": "Maskne : soigner l'acne causee par le port du masque avec la LED", "keywords": "maskne LED, acne masque traitement, soigner maskne luminotherapie"},
    {"title": "Dermatite et LED : une approche complementaire validee par la science", "keywords": "dermatite LED, approche complementaire luminotherapie, dermatite traitement lumiere"},
    {"title": "Peaux reactives : construire une tolerance avec la luminotherapie douce", "keywords": "peaux reactives LED, tolerance luminotherapie, luminotherapie douce sensible"},
    {"title": "Soleil et rougeurs : reparer les degats UV avec la lumiere LED", "keywords": "degats UV LED, rougeurs soleil luminotherapie, reparer peau soleil LED"},

    # === ROUTINES & RITUELS (15 articles) ===
    {"title": "La routine beaute minimaliste qui maximise les resultats : LED et 3 soins", "keywords": "routine minimaliste LED, beaute minimaliste efficace, 3 soins LED"},
    {"title": "Matin ou soir : quel est le meilleur moment pour utiliser son masque LED ?", "keywords": "meilleur moment masque LED, LED matin ou soir, quand utiliser LED"},
    {"title": "Comment preparer sa peau avant une seance de luminotherapie LED", "keywords": "preparer peau LED, avant seance luminotherapie, preparation soin LED"},
    {"title": "Les soins a appliquer apres une seance LED pour decupler les effets", "keywords": "soins apres LED, decupler effets luminotherapie, apres seance LED"},
    {"title": "Masque LED et grossesse : ce qu'il faut savoir", "keywords": "masque LED grossesse, luminotherapie enceinte, LED femme enceinte"},
    {"title": "Voyager avec son masque LED : conseils pratiques et reglementation avion", "keywords": "voyager masque LED, LED avion reglementation, transport masque LED"},
    {"title": "Combiner masque LED et gua sha : les deux se completent-ils ?", "keywords": "masque LED gua sha, combiner LED gua sha, synergie LED massage"},
    {"title": "LED et Botox : peut-on utiliser son masque apres une injection ?", "keywords": "LED apres Botox, masque LED injection, luminotherapie post-Botox"},
    {"title": "Masque LED et autobronzant : les precautions a prendre", "keywords": "masque LED autobronzant, LED et bronzage, precautions LED autobronzant"},
    {"title": "La routine beaute anti-stress : comment la LED agit sur le cortisol cutane", "keywords": "LED anti-stress, cortisol cutane luminotherapie, beaute anti-stress LED"},
    {"title": "Rituel bien-etre : transformer ses 10 minutes LED en moment de meditation", "keywords": "rituel LED meditation, bien-etre luminotherapie, relaxation masque LED"},
    {"title": "Demaquillage optimal avant LED : les erreurs a eviter absolument", "keywords": "demaquillage avant LED, erreurs LED, preparer peau demaquillage LED"},
    {"title": "Masque LED et retinol : comment les associer sans irriter la peau", "keywords": "masque LED retinol, LED et retinol irritation, associer LED retinol"},
    {"title": "Entretien de votre masque LED : nettoyage et duree de vie", "keywords": "entretien masque LED, nettoyage LED, duree vie masque LED"},
    {"title": "4 semaines de defi LED : journal de bord semaine par semaine", "keywords": "defi LED 4 semaines, journal LED, challenge luminotherapie"},

    # === COMPARATIFS & GUIDES D'ACHAT (15 articles) ===
    {"title": "Masque LED vs seance en institut : le comparatif honnete", "keywords": "masque LED vs institut, comparatif LED domicile institut, LED maison ou salon"},
    {"title": "Comment choisir son masque LED : les 8 criteres indispensables", "keywords": "choisir masque LED, criteres masque LED, guide achat LED"},
    {"title": "Masque LED 5 longueurs d'onde vs 3 longueurs d'onde : quelle difference ?", "keywords": "5 longueurs onde vs 3, masque LED multionde, comparatif longueurs onde"},
    {"title": "Certifications CE, FCC, RoHS : pourquoi elles sont non negociables", "keywords": "certifications masque LED, CE FCC RoHS LED, securite certifications LED"},
    {"title": "Le vrai cout d'un masque LED sur 2 ans vs les soins en institut", "keywords": "cout masque LED 2 ans, LED vs institut prix, economie masque LED"},
    {"title": "Masque LED souple vs rigide : avantages et inconvenients", "keywords": "masque LED souple rigide, comparatif LED flexible, LED souple vs dur"},
    {"title": "Les arnaques du marche des masques LED : comment les reconnaitre", "keywords": "arnaques masque LED, faux masque LED, reconnaitre arnaque LED"},
    {"title": "Masque LED professionnel a domicile : mythe ou realite ?", "keywords": "masque LED professionnel domicile, LED pro maison, qualite pro LED"},
    {"title": "Guide d'achat masque LED 2026 : tout ce qu'il faut savoir avant d'acheter", "keywords": "guide achat masque LED 2026, acheter masque LED, meilleur masque LED"},
    {"title": "Flux lumineux et densite de puissance : les chiffres qui comptent vraiment", "keywords": "flux lumineux LED, densite puissance masque, chiffres efficacite LED"},
    {"title": "Retours d'experience : ce que disent vraiment les utilisatrices apres 3 mois", "keywords": "retours experience masque LED, avis utilisatrices LED, temoignages LED 3 mois"},
    {"title": "Masque LED et prise en charge : mutuelles et remboursement possible ?", "keywords": "masque LED mutuelle, remboursement LED, prise en charge luminotherapie"},
    {"title": "Les 5 questions a poser avant d'acheter un masque LED", "keywords": "questions achat masque LED, avant acheter LED, guide questions LED"},
    {"title": "Masque LED Pro Mine de Teint : test et avis complet apres 90 jours", "keywords": "test masque LED Pro, avis Mine de Teint, masque LED 90 jours"},
    {"title": "Pourquoi le Masque LED Pro est different des autres masques du marche", "keywords": "masque LED Pro difference, Mine de Teint unique, avantages masque LED Pro"},

    # === FAQ & PEDAGOGIE (15 articles) ===
    {"title": "La luminotherapie LED est-elle dangereuse pour les yeux ?", "keywords": "luminotherapie LED yeux, danger LED yeux, protection oculaire LED"},
    {"title": "Peut-on utiliser un masque LED tous les jours ? La reponse des experts", "keywords": "masque LED tous les jours, frequence utilisation LED, LED quotidien"},
    {"title": "Masque LED et medicaments photosensibilisants : les precautions a prendre", "keywords": "LED medicaments photosensibilisants, precautions LED medicaments, photosensibilite LED"},
    {"title": "Pourquoi mon masque LED ne semble pas fonctionner : 5 raisons possibles", "keywords": "masque LED ne fonctionne pas, problemes LED, LED pas de resultats"},
    {"title": "LED et cancer de la peau : la lumiere rouge est-elle un risque ?", "keywords": "LED cancer peau, lumiere rouge risque cancer, securite LED cancer"},
    {"title": "Masque LED et peaux noires et metissees : est-ce adapte ?", "keywords": "masque LED peaux noires, LED peau metissee, luminotherapie peau foncee"},
    {"title": "Combien de seances faut-il pour voir des resultats avec un masque LED ?", "keywords": "nombre seances LED resultats, combien temps LED, resultats LED combien seances"},
    {"title": "La chaleur du masque LED est-elle normale ? Ce qu'il faut savoir", "keywords": "chaleur masque LED, masque LED chauffe, temperature LED normale"},
    {"title": "Masque LED et peaux tatouees : peut-on l'utiliser sans risque ?", "keywords": "masque LED tatouage, LED peau tatouee, luminotherapie tattoo"},
    {"title": "Pourquoi la luminotherapie LED ne fonctionne pas pareil pour tout le monde", "keywords": "LED resultats differents, luminotherapie personnalisee, variation resultats LED"},
    {"title": "Masque LED pendant les regles : faut-il adapter son protocole ?", "keywords": "masque LED regles, LED menstruation, protocole LED cycle"},
    {"title": "Les effets secondaires possibles de la luminotherapie LED", "keywords": "effets secondaires LED, risques luminotherapie, effets indesirables masque LED"},
    {"title": "Luminotherapie LED et immunite cutanee : ce que la science dit", "keywords": "LED immunite cutanee, luminotherapie defense peau, science LED immunite"},
    {"title": "Masque LED apres exposition solaire : bonnes pratiques", "keywords": "masque LED apres soleil, LED exposition solaire, soin LED post-soleil"},
    {"title": "10 idees recues sur la luminotherapie LED enfin demystifiees", "keywords": "idees recues LED, mythes luminotherapie, demystifier LED"},
]


def generate_articles_json():
    schedule = generate_schedule()
    articles = []

    for i, (article_info, pub_datetime) in enumerate(zip(ARTICLES_DATA, schedule), 1):
        articles.append({
            "index": i,
            "title": article_info["title"],
            "keywords": article_info["keywords"],
            "phase": 1 if i <= 30 else 2,
            "scheduled_date": pub_datetime.strftime("%Y-%m-%d"),
            "scheduled_time": pub_datetime.strftime("%H:%M"),
            "scheduled_datetime": pub_datetime.isoformat(),
            "published": False,
            "published_at": None
        })

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"articles.json genere avec {len(articles)} articles")
    print(f"   Phase 1 : articles 1-30 (lun-ven, quotidien)")
    print(f"   Phase 2 : articles 31-100 (lun-sam, tous les 2 jours, alternance)")
    print(f"   Premiere publication : {schedule[0].strftime('%d/%m/%Y a %Hh%M')}")
    print(f"   Derniere publication : {schedule[-1].strftime('%d/%m/%Y a %Hh%M')}")


if __name__ == "__main__":
    generate_articles_json()
