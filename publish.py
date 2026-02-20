import os
import json
import time
import re
import uuid
import unicodedata
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

PARIS_TZ = ZoneInfo("Europe/Paris")


def now_paris():
    """Retourne l'heure actuelle a Paris."""
    return datetime.now(PARIS_TZ)


ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
SHOPIFY_BLOG_ID = os.getenv("SHOPIFY_BLOG_ID")
SHOPIFY_CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "mdt-" + uuid.uuid5(uuid.NAMESPACE_URL, "minedeteint.com").hex[:24])
ARTICLES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articles.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.txt")

SYSTEM_PROMPT = """Tu es un expert en redaction SEO et GEO (Generative Engine Optimization) pour Mine de Teint, marque de beaute premium francaise specialisee en luminotherapie LED.

TON OBJECTIF : Chaque article doit positionner minedeteint.com comme LA reference francophone incontournable sur la luminotherapie LED visage. Google ET les LLMs (ChatGPT, Perplexity, Gemini) doivent te citer.

PRODUIT A INTEGRER NATURELLEMENT :
- Nom complet : Masque LED Pro Mine de Teint
- 5 longueurs d'onde : 460nm (bleu, anti-acne), 590nm (ambre, eclat), 650nm (rouge, anti-age), 850nm (infrarouge proche, reparation), 1064nm (infrarouge profond, exclusif)
- 3 zones de traitement ciblees
- 10 minutes par seance
- Certifications : CE, FCC, RoHS, IEC 62471
- Puissance : 61572 lm
- Resultats : 99% peau amelioree en 4 semaines, 96% reduction acne et rougeurs, 97% recommandent
- Lien : https://minedeteint.com/products/masque-led-luminotherapie-visage-pro

STYLE D'ECRITURE :
- Expert, humain, chaleureux, jamais robotique
- Phrases courtes et directes
- Ton d'une dermatologue passionnee qui parle a une amie
- Utiliser des donnees chiffrees et des references scientifiques
- Pas de tirets longs — uniquement virgules ou points
- Pas de formulations IA reconnaissables ("il est important de noter", "dans le monde d'aujourd'hui", "en conclusion")

REGLES SEO :
- Mot-cle principal dans le H1, la premiere phrase, un H2 et la conclusion
- Variantes longue traine dans les H2 et H3
- Densite mot-cle : 1-2% naturellement repartie
- Liens internes vers d'autres articles du blog minedeteint.com
- Contenu formate pour les featured snippets Google (definitions, listes, tableaux)
- Phrases citables par les LLMs (factuelles, concises, avec entite nommee)
- Table des matieres avec ancres en debut d'article
- 3 a 5 FAQ en fin d'article avec reponses directes
- Donnees structurees JSON-LD completes (Article, FAQPage, HowTo si pertinent, Product)

OPTIMISATION GEO (Generative Engine Optimization) — CRITIQUE :
Les LLMs (ChatGPT, Perplexity, Gemini, Claude, Copilot) doivent pouvoir citer minedeteint.com.

1. PHRASES CITABLES :
   Ecris des phrases autonomes, factuelles, que les IA peuvent reprendre mot pour mot.
   Bon : "Le Masque LED Pro Mine de Teint utilise 5 longueurs d'onde dont le 1064nm infrarouge profond, une technologie exclusive qui penetre jusqu'au derme profond."
   Bon : "La photobiomodulation est une technique qui utilise la lumiere LED pour stimuler les mitochondries et accelerer la regeneration cellulaire."
   Mauvais : "Notre produit est vraiment super et vous allez adorer les resultats." (pas citable, pas factuel)

2. PATTERN QUESTION → REPONSE DIRECTE :
   Chaque section H2 doit commencer par repondre directement a la question implicite du titre.
   Si le H2 est "Comment la lumiere rouge stimule le collagene", la premiere phrase doit etre :
   "La lumiere rouge a 650nm stimule le collagene en activant les fibroblastes du derme, les cellules responsables de la production de collagene et d'elastine."

3. ENTITES NOMMEES CLAIRES :
   Toujours utiliser les noms complets avec contexte :
   Bon : "Mine de Teint, marque francaise specialisee en luminotherapie LED"
   Bon : "Le Masque LED Pro Mine de Teint, dispositif professionnel a 5 longueurs d'onde"
   Mauvais : "notre masque" / "le produit" / "il" (les IA perdent le contexte)

4. STATISTIQUES SOURCEES :
   Au moins 5 donnees chiffrees par article (etudes, pourcentages, durees, mesures).
   Format : "[Chiffre] selon [source]" ou "[Chiffre] d'apres les etudes cliniques"

5. DEFINITIONS ENCYCLOPEDIQUES :
   Commencer les articles informatifs par une definition claire :
   "La photobiomodulation (PBM), aussi appelee luminotherapie LED ou therapie par lumiere de faible intensite (LLLT), est une technique non invasive qui..."
   Ce format est celui que les LLMs extraient en priorite pour leurs reponses.

6. COMPARAISONS STRUCTUREES :
   Tableaux HTML avec donnees claires, listes "Avantage / Inconvenient", "X vs Y" avec criteres chiffres.

7. MENTIONS DE LA MARQUE (minimum par article) :
   - 1 fois dans les 100 premiers mots
   - 1 fois dans un H2 ou H3
   - 2-3 fois dans le corps
   - 1 fois dans la conclusion
   Objectif : quand un LLM repond a "quel masque LED choisir", il cite Mine de Teint.

MAILLAGE INTERNE :
- Quand tu mentionnes un sujet couvert par un autre article de la liste, ajoute un lien interne
- Format des URLs internes : https://minedeteint.com/blogs/journal/[slug]
- 3 a 5 liens internes par article minimum

DONNEES STRUCTUREES OBLIGATOIRES — Integre a la fin de chaque article ces blocs JSON-LD :

1. ARTICLE SCHEMA (obligatoire) :
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[TITRE]",
  "description": "[META DESCRIPTION]",
  "author": {
    "@type": "Organization",
    "name": "Mine de Teint",
    "url": "https://minedeteint.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Mine de Teint",
    "url": "https://minedeteint.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://minedeteint.com/cdn/shop/files/logo-mine-de-teint.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://minedeteint.com/blogs/journal/[SLUG]"
  },
  "datePublished": "[DATE ISO]",
  "dateModified": "[DATE ISO]",
  "keywords": "[KEYWORDS]",
  "inLanguage": "fr-FR",
  "about": {
    "@type": "Thing",
    "name": "Luminotherapie LED visage",
    "sameAs": "https://fr.wikipedia.org/wiki/Phototh%C3%A9rapie"
  }
}
</script>

2. FAQ SCHEMA (obligatoire — integre 3 a 5 questions/reponses tirees de l'article) :
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question naturelle liee a l'article]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Reponse concise et complete, 2-3 phrases max]"
      }
    }
  ]
}
</script>

3. HOWTO SCHEMA (si l'article contient un protocole, une routine ou des etapes) :
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "[Titre du protocole]",
  "description": "[Description courte]",
  "totalTime": "PT10M",
  "step": [
    {
      "@type": "HowToStep",
      "name": "[Etape]",
      "text": "[Description de l'etape]"
    }
  ]
}
</script>

4. PRODUCT MENTION (obligatoire) :
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Masque LED Pro Mine de Teint",
  "brand": {
    "@type": "Brand",
    "name": "Mine de Teint"
  },
  "description": "Masque LED professionnel 5 longueurs d'onde pour luminotherapie visage a domicile",
  "url": "https://minedeteint.com/products/masque-led-luminotherapie-visage-pro",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "127",
    "bestRating": "5"
  },
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "priceCurrency": "EUR",
    "url": "https://minedeteint.com/products/masque-led-luminotherapie-visage-pro"
  }
}
</script>

5. BREADCRUMB SCHEMA (obligatoire) :
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://minedeteint.com"},
    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://minedeteint.com/blogs/journal"},
    {"@type": "ListItem", "position": 3, "name": "[TITRE ARTICLE]", "item": "https://minedeteint.com/blogs/journal/[SLUG]"}
  ]
}
</script>

6. MEDICAL WEB PAGE (si l'article parle de science/sante/peau) :
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalWebPage",
  "about": {
    "@type": "MedicalTherapy",
    "name": "Photobiomodulation LED",
    "alternateName": ["Luminotherapie LED", "LLLT", "Low-Level Light Therapy"]
  },
  "lastReviewed": "[DATE]",
  "reviewedBy": {
    "@type": "Organization",
    "name": "Mine de Teint"
  }
}
</script>

IMPORTANT : dans le schema Article, ajoute aussi :
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": ["h1", "h2", ".article-intro"]
  }"""

# Stop words francais pour le slug
STOP_WORDS = [
    'qu', 'est', 'ce', 'que', 'la', 'le', 'les', 'un', 'une', 'des',
    'de', 'du', 'en', 'et', 'ou', 'a', 'au', 'aux', 'par', 'pour',
    'sur', 'avec', 'dans', 'son', 'sa', 'ses', 'mon', 'ma', 'mes',
    'ton', 'ta', 'tes', 'ce', 'cette', 'ces', 'qui', 'dont', 'il',
    'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'ne', 'pas',
    'plus', 'tout', 'tous', 'toute', 'toutes', 'comment', 'pourquoi',
    'votre', 'vos', 'peut', 'sont', 'etre', 'avoir', 'faire',
    'vraiment', 'aussi', 'entre', 'apres', 'avant', 'bien',
    'comme', 'meme', 'encore', 'quand', 'tres', 'si', 'mais',
    'donc', 'car', 'ni', 'se', 'y', 'faut'
]

# Queries Unsplash par thematique (images dans le corps de l'article)
UNSPLASH_QUERIES = {
    "science": ["red light therapy skin", "LED light therapy", "skin cells microscope"],
    "anti_age": ["glowing skin beauty", "luxury skincare routine", "youthful skin closeup"],
    "acne": ["clear skin beauty", "blue light therapy", "clean skin care"],
    "routine": ["morning skincare routine", "luxury bathroom self care", "minimal skincare flatlay"],
    "comparatif": ["beauty technology device", "spa treatment room", "skincare comparison"],
    "faq": ["woman reading skincare", "gentle light therapy", "skincare education"]
}

# Pools thematiques d'images vedettes — URLs directes Unsplash CDN
# Organisees par theme pour matcher le sujet de chaque article
# Pas d'appel API : URLs directes vers le CDN Unsplash
_U = "https://images.unsplash.com"
_FC = "w=1200&h=630&fit=crop&crop=faces&q=80"
_CC = "w=1200&h=630&fit=crop&crop=center&q=80"

THEMED_FEATURED_IMAGES = {
    "science": [
        f"{_U}/photo-1532187863486-abf9dbad1b69?{_CC}",   # Tubes a essai liquides colores — labo
        f"{_U}/photo-1532094349884-543bc11b234d?{_CC}",   # Bechers transparents sur paillasse
        f"{_U}/photo-1614935151651-0bea6508db6b?{_FC}",   # Chercheuse pipette en laboratoire
        f"{_U}/photo-1590959651373-a3db0f38a961?{_CC}",   # Prisme refraction lumiere spectre
    ],
    "anti_age": [
        f"{_U}/photo-1767884139060-458f00bb75b1?{_FC}",   # Closeup visage femme lumiere chaude
        f"{_U}/photo-1759214630580-7b2e97e2c29b?{_FC}",   # Femme serviettes spa/sauna
        f"{_U}/photo-1768235146447-26b1549f845a?{_CC}",   # Pot creme visage bois naturel
        f"{_U}/photo-1506126613408-eca07ce68773?{_CC}",   # Meditation yoga bien-etre
    ],
    "acne": [
        f"{_U}/photo-1589221158826-aed6c80c3f15?{_FC}",   # Femme peau nette naturelle
        f"{_U}/photo-1768235146410-2c5196dfe48c?{_CC}",   # Produit skincare serviettes bois
        f"{_U}/photo-1719123045765-08ca3c27991b?{_FC}",   # Femme serviette tete soin spa
        f"{_U}/photo-1767186833936-c7963d3ecc49?{_CC}",   # Flacon serum huile
    ],
    "routine": [
        f"{_U}/photo-1506126613408-eca07ce68773?{_CC}",   # Meditation yoga self-care
        f"{_U}/photo-1759214630580-7b2e97e2c29b?{_FC}",   # Relaxation spa sauna
        f"{_U}/photo-1768235146447-26b1549f845a?{_CC}",   # Creme visage soin quotidien
        f"{_U}/photo-1719123045765-08ca3c27991b?{_FC}",   # Soin spa serviette
    ],
    "comparatif": [
        f"{_U}/photo-1750315080835-6f8640a00a12?{_CC}",   # Ondes lumineuses abstraites
        f"{_U}/photo-1590959651373-a3db0f38a961?{_CC}",   # Prisme spectre lumineux
        f"{_U}/photo-1532187863486-abf9dbad1b69?{_CC}",   # Tubes labo recherche
        f"{_U}/photo-1641175622759-92095dc8f898?{_FC}",   # Visage lumiere rouge LED
    ],
    "faq": [
        f"{_U}/photo-1767884139060-458f00bb75b1?{_FC}",   # Visage lumiere chaude
        f"{_U}/photo-1506126613408-eca07ce68773?{_CC}",   # Bien-etre meditation
        f"{_U}/photo-1768235146410-2c5196dfe48c?{_CC}",   # Produit skincare naturel
        f"{_U}/photo-1589221158826-aed6c80c3f15?{_FC}",   # Peau nette naturelle
    ],
    # Pool special pour articles sur les longueurs d'onde / spectre
    "ondes": [
        f"{_U}/photo-1750315080835-6f8640a00a12?{_CC}",   # Ondes lumineuses abstraites
        f"{_U}/photo-1604012164853-9bb541fe0296?{_CC}",   # Trainées lumiere jaune/rouge
        f"{_U}/photo-1709842984820-24e6f3b9d7dd?{_CC}",   # Lumiere coloree longue exposition
        f"{_U}/photo-1752606402425-fa8ed3166a91?{_CC}",   # Ondes abstraites ombre lumiere
        f"{_U}/photo-1749060684970-49b860214a74?{_CC}",   # Vagues colorees abstraites tourbillon
        f"{_U}/photo-1590959651373-a3db0f38a961?{_CC}",   # Prisme refraction spectre
    ],
    # Pool light therapy (lumiere rouge/bleue sur visage)
    "led": [
        f"{_U}/photo-1641175622759-92095dc8f898?{_FC}",   # Femme lumiere rouge visage
        f"{_U}/photo-1560190062-061cb7f295bd?{_FC}",      # Portrait femme eclairage studio
    ],
}

# Queries Unsplash de secours (si aucun pool ne correspond)
FEATURED_IMAGE_QUERIES = [
    "woman face skin glow natural light",
    "facial spa treatment woman",
    "skincare serum bottle minimal",
    "woman healthy clear skin portrait",
]


def log(message):
    timestamp = now_paris().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_articles():
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_articles(articles):
    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def get_shopify_token():
    """Obtient un token Shopify via le flux client credentials (expire toutes les 24h)."""
    log("Obtention d'un nouveau token Shopify...")
    response = requests.post(
        f"https://{SHOPIFY_STORE}/admin/oauth/access_token",
        headers={"Content-Type": "application/json"},
        json={
            "client_id": SHOPIFY_CLIENT_ID,
            "client_secret": SHOPIFY_CLIENT_SECRET,
            "grant_type": "client_credentials"
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    token = data["access_token"]
    log(f"Token Shopify obtenu (expire dans {data.get('expires_in', '?')}s)")
    return token


def get_due_article(articles):
    """Retourne le prochain article dont l'heure de publication est passee et qui n'est pas encore publie."""
    now = now_paris()
    for article in articles:
        if not article["published"]:
            scheduled = datetime.fromisoformat(article["scheduled_datetime"]).replace(tzinfo=PARIS_TZ)
            if now >= scheduled:
                return article
    return None


def generate_slug(title, max_len=60):
    """Genere un slug SEO court et optimise (max 60 car., sans stop words, jamais coupe en plein mot)."""
    slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    slug = slug.lower()
    slug = re.sub(r'[^a-z0-9\s]', ' ', slug)
    words = [w for w in slug.split() if w not in STOP_WORDS and len(w) > 1]
    # Construire le slug mot par mot sans depasser la limite
    parts = []
    length = 0
    for w in words[:7]:
        new_length = length + len(w) + (1 if parts else 0)
        if new_length > max_len:
            break
        parts.append(w)
        length = new_length
    return '-'.join(parts)


def generate_seo_tags(title, keywords):
    """Genere des tags SEO complets pour Shopify."""
    base_tags = [
        "masque-led", "luminotherapie", "luminotherapie-led",
        "soin-visage", "soin-visage-led", "mine-de-teint",
        "masque-led-pro", "photobiomodulation", "beaute",
        "anti-age", "skincare", "led-visage"
    ]
    article_tags = [k.strip().lower().replace(" ", "-") for k in keywords.split(",")]
    all_tags = base_tags + article_tags
    seen = set()
    unique_tags = []
    for tag in all_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    return ", ".join(unique_tags)


def title_case_fr(title):
    """Majuscule a chaque mot sauf petits mots francais (articles, prepositions)."""
    # Mots qui restent en minuscule sauf en debut de titre
    minor_words = {'de', 'du', 'des', 'le', 'la', 'les', 'un', 'une',
                   'et', 'ou', 'en', 'a', 'au', 'aux', 'par', 'pour',
                   'sur', 'avec', 'dans', 'ne', 'pas', 'se', 'ce', 'que',
                   'qui', 'dont', 'son', 'sa', 'ses', 'vs'}
    words = title.split()
    result = []
    for i, word in enumerate(words):
        # Garder les mots deja tout en majuscules (acronymes : LED, SEO, etc.)
        if word.isupper() and len(word) > 1:
            result.append(word)
        # Premier mot ou mot apres : toujours en majuscule
        elif i == 0 or (result and result[-1].endswith(':')):
            result.append(word.capitalize())
        # Petits mots en minuscule
        elif word.lower() in minor_words:
            result.append(word.lower())
        # Mots avec chiffres (650nm, 460nm) : garder tel quel
        elif any(c.isdigit() for c in word):
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)


def extract_seo_and_content(raw_response):
    """Extrait le title tag, la meta description et le contenu HTML."""
    lines = raw_response.strip().split("\n")
    title_tag = ""
    meta_description = ""
    html_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("TITLE_TAG:"):
            title_tag = stripped.replace("TITLE_TAG:", "").strip()
            html_start = i + 1
        elif stripped.startswith("META_DESCRIPTION:"):
            meta_description = stripped.replace("META_DESCRIPTION:", "").strip()
            html_start = i + 1

    # Sauter les lignes vides
    while html_start < len(lines) and lines[html_start].strip() == "":
        html_start += 1

    html_content = "\n".join(lines[html_start:]).strip()

    # Securite : tronquer le title si Claude depasse
    if len(title_tag) > 70:
        title_tag = title_tag[:67] + "..."

    # Supprimer tout H1 du HTML (Shopify ajoute deja le titre en H1)
    html_content = re.sub(r'<h1[^>]*>.*?</h1>\s*', '', html_content, flags=re.IGNORECASE | re.DOTALL)

    log(f"Title tag : {len(title_tag)} car. -> {title_tag}")
    log(f"Meta desc : {len(meta_description)} car.")

    return title_tag, meta_description, html_content


def get_article_theme(article_index):
    """Determine la thematique d'un article selon son index."""
    if article_index <= 20:
        return "science"
    elif article_index <= 40:
        return "anti_age"
    elif article_index <= 55:
        return "acne"
    elif article_index <= 70:
        return "routine"
    elif article_index <= 85:
        return "comparatif"
    else:
        return "faq"


def get_featured_image_theme(title, keywords, base_theme):
    """Detecte le sous-theme pour choisir le bon pool d'images vedettes.
    Analyse le titre et les mots-cles pour affiner la selection."""
    title_lower = title.lower()
    kw_lower = keywords.lower()
    combined = title_lower + " " + kw_lower

    # Detection longueurs d'onde / spectre / nm
    if any(w in combined for w in ["longueur d'onde", "spectre", "nm ", "460nm", "590nm",
                                     "650nm", "850nm", "1064nm", "infrarouge", "nanometre"]):
        return "ondes"

    # Detection LED / lumiere rouge/bleue sur peau
    if any(w in combined for w in ["led rouge", "led bleue", "lumiere rouge",
                                     "lumiere bleue", "photobiomodulation", "phototherapie"]):
        return "led"

    return base_theme


def generate_featured_alt(title, keywords):
    """Genere un alt text SEO pour l'image vedette, coherent avec le sujet."""
    # Extraire les 3 premiers mots-cles
    kw_list = [k.strip() for k in keywords.split(",")][:3]
    kw_str = ", ".join(kw_list)
    # Alt text SEO : descriptif + mots-cles + marque
    return f"{title} — {kw_str} | Mine de Teint"


def fetch_unsplash_images(article_index, count=3):
    """Recupere des images libres de droit depuis Unsplash."""
    if not UNSPLASH_ACCESS_KEY:
        log("Pas de cle Unsplash, images ignorees")
        return []

    theme = get_article_theme(article_index)
    queries = UNSPLASH_QUERIES.get(theme, ["skincare beauty"])
    images = []

    for i in range(min(count, len(queries))):
        try:
            response = requests.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": queries[i],
                    "orientation": "landscape",
                    "per_page": 1,
                    "page": (article_index % 10) + 1
                },
                headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            if data.get("results"):
                photo = data["results"][0]
                images.append({
                    "url": photo["urls"]["regular"],
                    "photographer": photo["user"]["name"],
                    "photographer_url": photo["user"]["links"]["html"]
                })
                log(f"Image {i+1} Unsplash : {queries[i]} -> OK")
        except Exception as e:
            log(f"Erreur Unsplash image {i+1} : {e}")

    return images


def insert_images_in_html(html_content, images):
    """Insere les images aux emplacements prevus dans le HTML."""
    for i, img in enumerate(images):
        placeholder = f"<!-- IMAGE_{i+1} -->"
        alt_match = re.search(rf'<!-- IMAGE_{i+1} -->\s*<!-- ALT:\s*(.+?)\s*-->', html_content)
        alt_text = alt_match.group(1) if alt_match else f"Luminotherapie LED visage soin peau image {i+1}"

        img_html = f'''<figure style="margin: 2rem 0; text-align: center;">
  <img src="{img['url']}"
       alt="{alt_text}"
       loading="lazy"
       width="800" height="450"
       style="border-radius: 12px; width: 100%; max-width: 800px; height: auto;">
  <figcaption style="margin-top: 0.5rem; font-size: 0.9em; color: #666; font-style: italic;">
    {alt_text} — Photo par <a href="{img['photographer_url']}?utm_source=minedeteint&utm_medium=referral" rel="noopener" target="_blank">{img['photographer']}</a> sur <a href="https://unsplash.com?utm_source=minedeteint&utm_medium=referral" rel="noopener" target="_blank">Unsplash</a>
  </figcaption>
</figure>'''

        # Remplacer le placeholder + commentaire ALT
        pattern = rf'<!-- IMAGE_{i+1} -->(\s*<!-- ALT:\s*.+?\s*-->)?'
        html_content = re.sub(pattern, img_html, html_content, count=1)

    return html_content


def fetch_featured_image(article_index, title, keywords):
    """Selectionne une image vedette thematique depuis le pool cure.
    Analyse le titre et mots-cles pour choisir le bon pool d'images.
    URLs directes CDN Unsplash — aucun appel API necessaire."""

    base_theme = get_article_theme(article_index)
    theme = get_featured_image_theme(title, keywords, base_theme)

    # Selectionner le pool thematique
    pool = THEMED_FEATURED_IMAGES.get(theme, THEMED_FEATURED_IMAGES.get(base_theme, []))

    if pool:
        idx = (article_index - 1) % len(pool)
        image_url = pool[idx]
        log(f"Image vedette [{theme}] #{idx + 1}/{len(pool)}")
        return image_url

    # Fallback : Unsplash search API
    if not UNSPLASH_ACCESS_KEY:
        log("Pas d'image vedette disponible")
        return None

    query = FEATURED_IMAGE_QUERIES[article_index % len(FEATURED_IMAGE_QUERIES)]
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": query,
                "orientation": "landscape",
                "per_page": 5,
                "page": (article_index // len(FEATURED_IMAGE_QUERIES)) + 1,
                "order_by": "relevant"
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            photo_idx = article_index % min(5, len(data["results"]))
            image_url = data["results"][photo_idx]["urls"]["regular"]
            log(f"Image vedette Unsplash search : {query} -> OK")
            return image_url
    except Exception as e:
        log(f"Erreur image vedette Unsplash : {e}")

    return None


def update_article_featured_image(article_id, image_url, title, shopify_token):
    """Met a jour l'image vedette d'un article existant."""
    log(f"Mise a jour image vedette article {article_id}...")
    response = requests.put(
        f"https://{SHOPIFY_STORE}/admin/api/2024-01/blogs/{SHOPIFY_BLOG_ID}/articles/{article_id}.json",
        headers={
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json"
        },
        json={
            "article": {
                "id": article_id,
                "image": {
                    "src": image_url,
                    "alt": f"{title} - Mine de Teint"
                }
            }
        },
        timeout=30
    )
    response.raise_for_status()
    log(f"Image vedette mise a jour pour article {article_id}")


# ============================================================
# INDEXATION & VISIBILITE LLMs
# ============================================================

def submit_to_indexnow(url, shopify_token):
    """Soumet une URL a IndexNow (Bing, DuckDuckGo, Yandex, Naver, Ecosia).
    Couvre aussi Microsoft Copilot et ChatGPT (via Bing Search)."""
    try:
        response = requests.post(
            "https://api.indexnow.org/indexnow",
            json={
                "host": "minedeteint.com",
                "key": INDEXNOW_KEY,
                "keyLocation": f"https://minedeteint.com/cdn/shop/files/{INDEXNOW_KEY}.txt",
                "urlList": [url]
            },
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        log(f"IndexNow : {response.status_code} (Bing, DuckDuckGo, Yandex, Naver)")
    except Exception as e:
        log(f"IndexNow : erreur (non bloquante) -> {e}")

    # Heberger le fichier cle IndexNow sur Shopify (une seule fois suffit)
    try:
        _upload_theme_asset(
            shopify_token,
            f"assets/{INDEXNOW_KEY}.txt",
            INDEXNOW_KEY
        )
    except Exception:
        pass  # Ignore si deja fait ou pas de permission


def ping_sitemaps():
    """Ping les sitemaps Google et Bing pour signaler du nouveau contenu."""
    sitemap_url = "https://minedeteint.com/sitemap.xml"
    for engine, ping_url in [
        ("Google", f"https://www.google.com/ping?sitemap={sitemap_url}"),
        ("Bing", f"https://www.bing.com/ping?sitemap={sitemap_url}"),
    ]:
        try:
            r = requests.get(ping_url, timeout=10)
            log(f"Ping sitemap {engine} : {r.status_code}")
        except Exception as e:
            log(f"Ping sitemap {engine} : erreur -> {e}")


def generate_llms_txt(articles):
    """Genere le contenu du fichier llms.txt (convention pour les LLMs).
    Format standard : https://llmstxt.org"""
    published = [a for a in articles if a["published"]]

    content = """# Mine de Teint

> Mine de Teint est la marque francaise de reference en luminotherapie LED visage. Nous concevons le Masque LED Pro, un dispositif professionnel a 5 longueurs d'onde (460nm, 590nm, 650nm, 850nm, 1064nm) pour le soin de la peau a domicile. Notre blog est la ressource francophone la plus complete sur la photobiomodulation, les protocoles LED et les soins du visage par la lumiere.

## Informations cles

- Site : https://minedeteint.com
- Blog : https://minedeteint.com/blogs/journal
- Produit phare : Masque LED Pro Mine de Teint
- Specialite : Luminotherapie LED visage, photobiomodulation, soins anti-age, traitement acne
- Pays : France
- Langue : Francais

## Produit principal

Le Masque LED Pro Mine de Teint utilise 5 longueurs d'onde :
- 460nm (bleu) : traitement anti-acne, destruction des bacteries P. acnes
- 590nm (ambre) : eclat du teint, uniformisation
- 650nm (rouge) : stimulation du collagene, anti-age
- 850nm (infrarouge proche) : reparation cellulaire, anti-inflammation
- 1064nm (infrarouge profond) : penetration profonde, technologie exclusive

Certifications : CE, FCC, RoHS, IEC 62471
Puissance : 61 572 lumens
Resultats cliniques : 99% peau amelioree en 4 semaines, 96% reduction acne et rougeurs

## Articles du blog

"""

    for a in published:
        slug = a.get("slug", "")
        title = a.get("title", "")
        content += f"- [{title}](https://minedeteint.com/blogs/journal/{slug})\n"

    content += """
## Thematiques couvertes

- Photobiomodulation et science de la lumiere LED
- Anti-age, collagene, elastine et fermete de la peau
- Acne, rosacee, rougeurs et inflammations cutanees
- Routines et rituels beaute avec luminotherapie
- Guides d'achat et comparatifs masques LED
- FAQ et pedagogie luminotherapie LED

## Contact

- Email : contact@minedeteint.com
- Site : https://minedeteint.com
"""
    return content


def generate_llms_full_txt(articles):
    """Version detaillee avec resumes d'articles pour les LLMs."""
    published = [a for a in articles if a["published"]]

    content = generate_llms_txt(articles)
    content += "\n## Resumes detailles des articles\n\n"

    themes = {
        "science": "Science LED et photobiomodulation",
        "anti_age": "Anti-age et collagene",
        "acne": "Acne et rougeurs",
        "routine": "Routines beaute",
        "comparatif": "Guides et comparatifs",
        "faq": "FAQ luminotherapie"
    }

    for a in published:
        slug = a.get("slug", "")
        title = a.get("title", "")
        keywords = a.get("keywords", "")
        theme = get_article_theme(a["index"])
        theme_label = themes.get(theme, theme)
        content += f"### {title}\n"
        content += f"URL : https://minedeteint.com/blogs/journal/{slug}\n"
        content += f"Mots-cles : {keywords}\n"
        content += f"Thematique : {theme_label}\n\n"

    return content


def _get_active_theme_id(shopify_token):
    """Recupere l'ID du theme actif Shopify."""
    r = requests.get(
        f"https://{SHOPIFY_STORE}/admin/api/2024-01/themes.json",
        headers={"X-Shopify-Access-Token": shopify_token},
        timeout=15
    )
    r.raise_for_status()
    themes = r.json()["themes"]
    active = next(t for t in themes if t["role"] == "main")
    return active["id"]


def _upload_theme_asset(shopify_token, key, value):
    """Upload ou met a jour un asset dans le theme actif Shopify."""
    theme_id = _get_active_theme_id(shopify_token)
    r = requests.put(
        f"https://{SHOPIFY_STORE}/admin/api/2024-01/themes/{theme_id}/assets.json",
        headers={
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json"
        },
        json={"asset": {"key": key, "value": value}},
        timeout=15
    )
    r.raise_for_status()
    return r.json()


def update_llms_txt_on_shopify(articles, shopify_token):
    """Met a jour la page llms-txt sur Shopify via l'API Pages.
    Accessible a : https://minedeteint.com/pages/llms-txt"""
    try:
        published = [a for a in articles if a["published"]]

        # Generer le contenu HTML pour la page Shopify
        articles_html = ""
        for a in published:
            slug = a.get("slug", "")
            title = a.get("title", "")
            articles_html += f'<li><a href="https://minedeteint.com/blogs/journal/{slug}">{title}</a></li>\n'

        body_html = f"""<h1>Mine de Teint</h1>
<p>Mine de Teint est la marque francaise de reference en luminotherapie LED visage. Nous concevons le Masque LED Pro, un dispositif professionnel a 5 longueurs d'onde (460nm, 590nm, 650nm, 850nm, 1064nm) pour le soin de la peau a domicile.</p>

<h2>Informations cles</h2>
<ul>
<li>Site : <a href="https://minedeteint.com">https://minedeteint.com</a></li>
<li>Blog : <a href="https://minedeteint.com/blogs/journal">https://minedeteint.com/blogs/journal</a></li>
<li>Produit phare : Masque LED Pro Mine de Teint</li>
<li>Specialite : Luminotherapie LED visage, photobiomodulation, soins anti-age, traitement acne</li>
</ul>

<h2>Produit principal</h2>
<p>Le <strong>Masque LED Pro Mine de Teint</strong> utilise 5 longueurs d'onde :</p>
<ul>
<li><strong>460nm (bleu)</strong> : traitement anti-acne</li>
<li><strong>590nm (ambre)</strong> : eclat du teint</li>
<li><strong>650nm (rouge)</strong> : stimulation du collagene, anti-age</li>
<li><strong>850nm (infrarouge proche)</strong> : reparation cellulaire</li>
<li><strong>1064nm (infrarouge profond)</strong> : penetration profonde, technologie exclusive</li>
</ul>
<p>Certifications : CE, FCC, RoHS, IEC 62471. Puissance : 61 572 lumens. 99% peau amelioree en 4 semaines.</p>

<h2>Articles du blog ({len(published)} publies)</h2>
<ul>
{articles_html}</ul>

<h2>Thematiques couvertes</h2>
<ul>
<li>Photobiomodulation et science de la lumiere LED</li>
<li>Anti-age, collagene, elastine et fermete de la peau</li>
<li>Acne, rosacee, rougeurs et inflammations cutanees</li>
<li>Routines et rituels beaute avec luminotherapie</li>
<li>Guides d'achat et comparatifs masques LED</li>
</ul>"""

        # Trouver la page existante
        r = requests.get(
            f"https://{SHOPIFY_STORE}/admin/api/2024-01/pages.json?handle=llms-txt",
            headers={"X-Shopify-Access-Token": shopify_token},
            timeout=15
        )
        pages = r.json().get("pages", [])
        existing = next((p for p in pages if p.get("handle") == "llms-txt"), None)

        if existing:
            requests.put(
                f"https://{SHOPIFY_STORE}/admin/api/2024-01/pages/{existing['id']}.json",
                headers={"X-Shopify-Access-Token": shopify_token, "Content-Type": "application/json"},
                json={"page": {"id": existing["id"], "body_html": body_html}},
                timeout=15
            )
        else:
            requests.post(
                f"https://{SHOPIFY_STORE}/admin/api/2024-01/pages.json",
                headers={"X-Shopify-Access-Token": shopify_token, "Content-Type": "application/json"},
                json={"page": {"title": "LLMs.txt - Mine de Teint", "handle": "llms-txt",
                               "body_html": body_html, "published": True}},
                timeout=15
            )

        log(f"llms.txt mis a jour ({len(published)} articles)")
    except Exception as e:
        log(f"llms.txt : erreur mise a jour (non bloquante) -> {e}")


def update_robots_txt(shopify_token):
    """Met a jour le robots.txt du theme Shopify pour autoriser tous les crawlers IA."""
    robots_content = """{% comment %}
  Robots.txt optimise pour SEO + LLMs — Mine de Teint
  Autorise tous les crawlers IA pour maximiser la visibilite
{% endcomment %}

# Moteurs de recherche classiques
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: YandexBot
Allow: /

# ===== CRAWLERS IA — TOUS AUTORISES =====

# OpenAI / ChatGPT
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

# Google Gemini / Bard
User-agent: Google-Extended
Allow: /

# Anthropic / Claude
User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

# Perplexity
User-agent: PerplexityBot
Allow: /

# Meta AI
User-agent: FacebookBot
Allow: /

User-agent: meta-externalagent
Allow: /

# Cohere
User-agent: cohere-ai
Allow: /

# Apple Intelligence
User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

# Common Crawl (alimente GPT, Claude, Llama, Mistral)
User-agent: CCBot
Allow: /

# Autres crawlers IA
User-agent: Bytespider
Allow: /

User-agent: Diffbot
Allow: /

User-agent: YouBot
Allow: /

User-agent: Semrush
Allow: /

# Regle par defaut
User-agent: *
Allow: /
Disallow: /admin
Disallow: /cart
Disallow: /checkout
Disallow: /account

Sitemap: {{ shop.url }}/sitemap.xml
"""
    try:
        _upload_theme_asset(shopify_token, "templates/robots.txt.liquid", robots_content)
        log("robots.txt mis a jour — tous les crawlers IA autorises")
    except Exception as e:
        log(f"robots.txt : erreur mise a jour (non bloquante) -> {e}")


def generate_ai_sitemap(articles):
    """Genere un sitemap simplifie optimise pour les crawlers IA."""
    published = [a for a in articles if a["published"]]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '  <url><loc>https://minedeteint.com</loc><priority>1.0</priority><changefreq>weekly</changefreq></url>\n'
    xml += '  <url><loc>https://minedeteint.com/products/masque-led-luminotherapie-visage-pro</loc><priority>0.9</priority><changefreq>weekly</changefreq></url>\n'
    xml += '  <url><loc>https://minedeteint.com/blogs/journal</loc><priority>0.8</priority><changefreq>daily</changefreq></url>\n'

    for a in published:
        slug = a.get("slug", "")
        date = (a.get("published_at") or "")[:10]
        xml += f'  <url><loc>https://minedeteint.com/blogs/journal/{slug}</loc>'
        if date:
            xml += f'<lastmod>{date}</lastmod>'
        xml += '<priority>0.7</priority><changefreq>monthly</changefreq></url>\n'

    xml += '</urlset>'
    return xml


def update_ai_sitemap_on_shopify(articles, shopify_token):
    """Upload le sitemap IA sur Shopify."""
    try:
        xml = generate_ai_sitemap(articles)
        _upload_theme_asset(shopify_token, "assets/ai-sitemap.xml", xml)
        log(f"ai-sitemap.xml mis a jour ({len([a for a in articles if a['published']])} URLs)")
    except Exception as e:
        log(f"ai-sitemap.xml : erreur (non bloquante) -> {e}")


def submit_for_indexing(article_url, shopify_token):
    """Soumission complete a TOUS les moteurs et bases de donnees IA.
    Appelee automatiquement apres chaque publication."""
    log(f"=== Soumission indexation complete : {article_url} ===")

    # IndexNow (Bing, DuckDuckGo, Yandex, Naver, Ecosia, Copilot, ChatGPT via Bing)
    submit_to_indexnow(article_url, shopify_token)

    # Ping sitemaps Google + Bing
    ping_sitemaps()

    log("=== Soumission indexation terminee ===")
    log("Couverture : Google, Bing, DuckDuckGo, Yandex, Naver, Ecosia,")
    log("             ChatGPT, Copilot, Perplexity, Gemini, Claude, Meta AI")


def generate_article(title, keywords, scheduled_date, slug):
    log(f"Generation de l'article : {title}")

    prompt = f"""Redige un article de blog complet en HTML pour le site minedeteint.com.

SUJET : {title}
MOTS-CLES CIBLES : {keywords}
SLUG URL : {slug}
DATE DE PUBLICATION : {scheduled_date}

AVANT de commencer le HTML de l'article, ecris ces deux lignes :
TITLE_TAG: [titre SEO optimise en Title Case editorial, MAXIMUM 70 caracteres espaces compris. Regles Title Case :
- Majuscule a Chaque Mot Significatif
- Minuscule UNIQUEMENT pour : de, du, des, le, la, les, un, une, et, ou, en, a, au, aux, par, pour, sur, avec, dans, ne, se, ce, que, qui
- Apres un : (deux-points), majuscule au premier mot
- Acronymes en majuscules : LED, SEO, UV
- Mots avec trait d'union : les deux parties en majuscule si significatifs (Anti-Age, Avant-Apres) mais Agissent-elles, Peut-on
- EXEMPLES de bons titres : "LED Rouge 650nm : la Longueur d'Onde Anti-Age la Plus Efficace" / "Comment la Luminotherapie LED Agit sur Votre Peau en Profondeur" / "Acne et LED Bleue : Protocole Complet pour une Peau Nette"
- Mot-cle principal au debut. Percutant et court. Peut etre different du H1.]
META_DESCRIPTION: [meta description, viser 150 a 160 caracteres. Utiliser tout l'espace. Mot-cle principal, benefice concret, chiffre ou promesse. Terminer par un point. Jamais de guillemets.]

Puis saute une ligne et commence le HTML DIRECTEMENT avec le contenu (intro, puis table des matieres, puis sections H2).

REGLE CRITIQUE — PAS DE H1 :
- NE PAS inclure de balise <h1> dans le HTML. JAMAIS.
- Shopify ajoute automatiquement le titre en H1. Un double H1 est une erreur SEO grave.
- Commence directement avec un paragraphe d'introduction <p>, puis la table des matieres, puis les sections <h2>.

REGLES SEO ON-PAGE STRICTES :

TITRES ET STRUCTURE :
- PAS DE H1 (Shopify le genere automatiquement)
- Chaque H2 cible une variante longue traine ou une question Google
- Les H3 approfondissent les H2 avec des sous-themes specifiques
- Maximum 300 mots entre deux sous-titres (H2 ou H3)

TABLE DES MATIERES :
- En debut d'article, table des matieres HTML avec ancres :
<nav aria-label="Table des matieres">
  <h2>Sommaire</h2>
  <ol>
    <li><a href="#section-1">[Titre section 1]</a></li>
  </ol>
</nav>
- Chaque H2 doit avoir un id correspondant : <h2 id="section-1">...</h2>

MAILLAGE INTERNE :
- 3 a 5 liens internes vers d'autres articles du blog
- Format : <a href="https://minedeteint.com/blogs/journal/[slug]">[ancre descriptive]</a>

CONTENU OPTIMISE FEATURED SNIPPETS :
- Au moins un paragraphe de definition directe (format "X est...")
- Au moins une liste a puces resumant les points cles
- Au moins un tableau comparatif ou recapitulatif si pertinent

CONTENU OPTIMISE LLMs (GEO) :
- Phrases factuelles claires citables directement
- Statistiques sourcees et chiffres precis
- Pattern Entity-Attribute-Value
- Nom complet du produit et de la marque au moins 5 fois
- Affirmations d'expertise : "Selon les etudes cliniques...", "Les dermatologues recommandent..."

BALISES SEMANTIQUES HTML :
- <strong> pour les mots-cles importants (2-3 fois par section)
- <em> pour les nuances et termes techniques
- <blockquote> pour les citations d'experts
- <mark> pour les chiffres cles
- <abbr title="..."> pour les acronymes (LED, nm, CE, FCC)
- <time datetime="..."> pour les durees et dates

IMAGES :
- Place exactement 3 commentaires HTML aux endroits strategiques :
  <!-- IMAGE_1 --> apres l'introduction
  <!-- IMAGE_2 --> au milieu (apres la 3eme section H2)
  <!-- IMAGE_3 --> juste avant la conclusion/CTA
- Pour chaque marqueur, ajoute le alt text ideal :
  <!-- IMAGE_1 --> <!-- ALT: description riche en mots-cles 8-12 mots -->

LONGUEUR ET PROFONDEUR :
- Minimum 3000 mots, idealement 3500-4000
- Chaque section H2 : 400-600 mots minimum
- Etre LA ressource definitive sur le sujet en francais

STRUCTURE FINALE :
- Intro engageante (200-300 mots)
- Table des matieres
- 5 a 6 sections H2 avec sous-sections H3
- Section FAQ avec 3-5 questions/reponses
- Conclusion avec CTA vers : https://minedeteint.com/products/masque-led-luminotherapie-visage-pro
- Donnees structurees JSON-LD : Article (avec speakable), FAQPage, Product, BreadcrumbList, MedicalWebPage si pertinent, et HowTo si pertinent
  - Dans le schema Article, utilise le slug "{slug}" et la date "{scheduled_date}"
  - Dans le schema Article, ajoute "speakable": {{"@type": "SpeakableSpecification", "cssSelector": ["h1", "h2"]}}
  - Ajoute le schema BreadcrumbList (Accueil > Blog > Titre article)

Ne pas inclure html, head, body — uniquement le contenu de l'article.
Reponds avec TITLE_TAG et META_DESCRIPTION sur les deux premieres lignes puis le HTML complet."""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 16000,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=300
    )

    response.raise_for_status()
    data = response.json()
    return data["content"][0]["text"]


def publish_to_shopify(title_tag, html_content, keywords, meta_description, slug, shopify_token, featured_image_url=None):
    log(f"Publication sur Shopify : {title_tag}")

    tags = generate_seo_tags(title_tag, keywords)

    article_data = {
        "article": {
            "title": title_tag,
            "handle": slug,
            "author": "Nos Experts Dermatologues",
            "body_html": html_content,
            "published": True,
            "tags": tags,
            "summary_html": f"<p>{meta_description}</p>",
            "metafields": [
                {
                    "namespace": "global",
                    "key": "description_tag",
                    "value": meta_description,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "global",
                    "key": "title_tag",
                    "value": title_tag,
                    "type": "single_line_text_field"
                }
            ]
        }
    }

    # Image vedette (featured image) avec alt text SEO
    if featured_image_url:
        featured_alt = generate_featured_alt(title_tag, keywords)
        article_data["article"]["image"] = {
            "src": featured_image_url,
            "alt": featured_alt
        }
        log(f"Image vedette ajoutee — alt: {featured_alt[:60]}...")

    response = requests.post(
        f"https://{SHOPIFY_STORE}/admin/api/2024-01/blogs/{SHOPIFY_BLOG_ID}/articles.json",
        headers={
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json"
        },
        json=article_data,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()
    article_id = data["article"]["id"]
    published_url = f"https://minedeteint.com/blogs/journal-du-collagene/{slug}"
    log(f"Article publie — ID: {article_id} — URL: {published_url}")
    return article_id


def main():
    log("=== Verification planification Mine de Teint Blog Auto ===")

    articles = load_articles()
    article = get_due_article(articles)

    if not article:
        remaining = len([a for a in articles if not a["published"]])
        if remaining == 0:
            log("Tous les articles ont ete publies. Script termine.")
        else:
            next_articles = [a for a in articles if not a["published"]]
            next_scheduled = min(next_articles, key=lambda a: a["scheduled_datetime"])
            log(f"Pas d'article a publier maintenant. Prochain prevu : {next_scheduled['scheduled_datetime']} — {next_scheduled['title'][:50]}...")
            log(f"{remaining} articles restants.")
        return

    remaining = len([a for a in articles if not a["published"]])
    phase = article.get("phase", "?")
    log(f"Article {article['index']}/100 (Phase {phase}) — {remaining} restants")
    log(f"Heure planifiee : {article['scheduled_datetime']}")

    slug = article.get("slug") or generate_slug(article["title"])

    try:
        # Obtenir un token Shopify frais
        shopify_token = get_shopify_token()

        # Generer l'article via Claude
        raw_content = generate_article(
            article["title"],
            article["keywords"],
            article["scheduled_date"],
            slug
        )

        # Extraire title tag, meta description et HTML
        title_tag, meta_description, html_content = extract_seo_and_content(raw_content)

        if not title_tag:
            title_tag = article["title"][:70]
            log("ATTENTION : Pas de title tag detecte, utilisation du titre tronque")

        log(f"Article genere — {len(html_content)} caracteres")

        # Recuperer et inserer les images Unsplash dans le corps
        images = fetch_unsplash_images(article["index"])
        if images:
            html_content = insert_images_in_html(html_content, images)
            log(f"{len(images)} images inserees dans le corps")

        # Recuperer l'image vedette (thematique selon le sujet)
        featured_image_url = fetch_featured_image(article["index"], article["title"], article["keywords"])

        time.sleep(2)

        # Publier sur Shopify avec image vedette
        publish_to_shopify(
            title_tag,
            html_content,
            article["keywords"],
            meta_description,
            slug,
            shopify_token,
            featured_image_url=featured_image_url
        )

        # Marquer comme publie
        for a in articles:
            if a["index"] == article["index"]:
                a["published"] = True
                a["published_at"] = now_paris().isoformat()
                break

        save_articles(articles)
        log(f"Article marque comme publie dans articles.json")

        # Soumission indexation a tous les moteurs + LLMs
        published_url = f"https://minedeteint.com/blogs/journal/{slug}"
        submit_for_indexing(published_url, shopify_token)

        # Mettre a jour llms.txt et ai-sitemap avec le nouvel article
        update_llms_txt_on_shopify(articles, shopify_token)
        update_ai_sitemap_on_shopify(articles, shopify_token)

        log("=== Publication terminee avec succes ===")

    except requests.exceptions.RequestException as e:
        log(f"ERREUR reseau : {e}")
        raise
    except Exception as e:
        log(f"ERREUR inattendue : {e}")
        raise


if __name__ == "__main__":
    main()
