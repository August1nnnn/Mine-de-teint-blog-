import os
import json
import time
import re
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
</script>"""

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

# Queries image vedette — DA corporate skincare lisse et coherente
FEATURED_IMAGE_QUERIES = [
    "luxury skincare routine soft light minimal",
    "clean beauty product aesthetic white",
    "skincare flatlay minimal white background",
    "gentle face care routine morning light",
    "beauty wellness self care soft pastel",
    "glowing skin beauty natural light portrait",
    "facial treatment spa clean minimal luxury",
    "skin care beauty routine editorial soft",
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


def generate_slug(title):
    """Genere un slug SEO court et optimise (max 50 car., sans stop words)."""
    slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    slug = slug.lower()
    slug = re.sub(r'[^a-z0-9\s]', ' ', slug)
    words = [w for w in slug.split() if w not in STOP_WORDS and len(w) > 1]
    slug = '-'.join(words[:6])
    return slug[:50].rstrip('-')


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


def fetch_featured_image(article_index):
    """Recupere une image vedette depuis Unsplash avec DA corporate skincare coherente."""
    if not UNSPLASH_ACCESS_KEY:
        log("Pas de cle Unsplash, image vedette ignoree")
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
            photo = data["results"][photo_idx]
            image_url = photo["urls"]["regular"]
            log(f"Image vedette Unsplash : {query} -> OK")
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
- Donnees structurees JSON-LD : Article, FAQPage, Product, et HowTo si pertinent
  - Dans le schema Article, utilise le slug "{slug}" et la date "{scheduled_date}"

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

    # Image vedette (featured image)
    if featured_image_url:
        article_data["article"]["image"] = {
            "src": featured_image_url,
            "alt": f"{title_tag} - Mine de Teint"
        }
        log(f"Image vedette ajoutee")

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

        # Recuperer l'image vedette (featured image)
        featured_image_url = fetch_featured_image(article["index"])

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
        log("=== Publication terminee avec succes ===")

    except requests.exceptions.RequestException as e:
        log(f"ERREUR reseau : {e}")
        raise
    except Exception as e:
        log(f"ERREUR inattendue : {e}")
        raise


if __name__ == "__main__":
    main()
