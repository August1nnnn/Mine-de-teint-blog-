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
    """Genere un slug SEO optimise a partir du titre."""
    slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    slug = slug.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    slug = slug[:60].rstrip('-')
    return slug


def generate_seo_tags(title, keywords):
    """Genere des tags SEO complets pour Shopify."""
    base_tags = [
        "masque-led",
        "luminotherapie",
        "luminotherapie-led",
        "soin-visage",
        "soin-visage-led",
        "mine-de-teint",
        "masque-led-pro",
        "photobiomodulation",
        "beaute",
        "anti-age",
        "skincare",
        "led-visage"
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


def extract_meta_and_content(raw_response):
    """Separe la meta description du contenu HTML."""
    lines = raw_response.strip().split("\n")
    meta_description = ""
    html_start = 0

    for i, line in enumerate(lines):
        if line.strip().startswith("META_DESCRIPTION:"):
            meta_description = line.replace("META_DESCRIPTION:", "").strip()
            html_start = i + 1
            break

    # Sauter les lignes vides apres META_DESCRIPTION
    while html_start < len(lines) and lines[html_start].strip() == "":
        html_start += 1

    html_content = "\n".join(lines[html_start:]).strip()
    return meta_description, html_content


def generate_article(title, keywords, scheduled_date, slug):
    log(f"Generation de l'article : {title}")

    prompt = f"""Redige un article de blog complet en HTML pour le site minedeteint.com.

TITRE : {title}
MOTS-CLES CIBLES : {keywords}
SLUG URL : {slug}
DATE DE PUBLICATION : {scheduled_date}

AVANT de commencer le HTML de l'article, ecris sur la premiere ligne :
META_DESCRIPTION: [ta meta description ici, 145-155 caracteres, contenant le mot-cle principal, donnant envie de cliquer, sans guillemets ni caracteres speciaux]

Puis saute une ligne et commence le HTML.

REGLES SEO ON-PAGE STRICTES :

TITRES ET STRUCTURE :
- Le H1 contient le mot-cle principal exact
- Chaque H2 cible une variante longue traine ou une question que les gens posent sur Google
- Les H3 approfondissent les H2 avec des sous-themes specifiques
- Maximum 300 mots entre deux sous-titres (H2 ou H3)
- La structure doit repondre a l'intention de recherche

TABLE DES MATIERES :
- Ajouter en debut d'article une table des matieres HTML avec ancres :
<nav aria-label="Table des matieres">
  <h2>Sommaire</h2>
  <ol>
    <li><a href="#section-1">[Titre section 1]</a></li>
    <li><a href="#section-2">[Titre section 2]</a></li>
  </ol>
</nav>
- Chaque H2 doit avoir un id correspondant : <h2 id="section-1">...</h2>

MAILLAGE INTERNE :
- Ajoute 3 a 5 liens internes vers d'autres articles du blog quand c'est pertinent
- Format : <a href="https://minedeteint.com/blogs/journal/[slug-article-lie]">[ancre naturelle]</a>
- Les ancres doivent etre descriptives (jamais "cliquez ici")

CONTENU OPTIMISE POUR LES FEATURED SNIPPETS :
- Inclure au moins un paragraphe de definition directe (format "X est..." au debut d'une section)
- Inclure au moins une liste a puces resumant les points cles
- Inclure au moins un tableau comparatif ou recapitulatif si pertinent
- Utiliser des phrases courtes et directes qui repondent aux questions Google

CONTENU OPTIMISE POUR LES LLMs (GEO) :
- Ecrire des phrases factuelles claires que les LLMs peuvent citer directement
- Inclure des statistiques sourcees et des chiffres precis
- Structurer les reponses en format "question implicite -> reponse directe"
- Utiliser le pattern Entity-Attribute-Value : "Le Masque LED Pro Mine de Teint utilise 5 longueurs d'onde dont le 1064nm infrarouge profond exclusif"
- Mentionner le nom complet du produit et de la marque au moins 5 fois dans l'article
- Inclure des affirmations d'expertise : "Selon les etudes cliniques...", "Les dermatologues recommandent..."

BALISES SEMANTIQUES HTML :
- Utiliser <strong> pour les mots-cles importants (2-3 fois par section, pas plus)
- Utiliser <em> pour les nuances et termes techniques
- Utiliser <blockquote> pour les citations d'experts ou donnees cles
- Utiliser <mark> pour les chiffres cles (ex: <mark>99% des utilisatrices</mark>)
- Utiliser <abbr title="..."> pour les acronymes techniques (LED, nm, CE, FCC)
- Utiliser <time datetime="..."> pour les durees et dates mentionnees

IMAGES (emplacements a preparer) :
- Ajouter 2 a 3 emplacements d'images par article :
<figure>
  <img src="" alt="[description riche en mots-cles, 8-12 mots]" loading="lazy" width="800" height="500">
  <figcaption>[legende descriptive]</figcaption>
</figure>

LONGUEUR ET PROFONDEUR :
- Minimum 3000 mots, idealement 3500-4000
- Chaque section H2 doit faire 400-600 mots minimum
- L'article doit etre plus complet que tout ce qui existe sur le sujet en francais

STRUCTURE FINALE :
- Intro engageante (200-300 mots)
- Table des matieres
- 5 a 6 sections H2 avec sous-sections H3
- Section FAQ avec 3-5 questions/reponses
- Conclusion avec CTA vers : https://minedeteint.com/products/masque-led-luminotherapie-visage-pro
- Donnees structurees JSON-LD : Article, FAQPage, Product, et HowTo si pertinent
  - Dans le schema Article, utilise le slug "{slug}" et la date "{scheduled_date}"
  - Dans le schema FAQPage, reprends les questions de la section FAQ

Ne pas inclure html, head, body — uniquement le contenu de l'article.
Reponds avec META_DESCRIPTION sur la premiere ligne puis le HTML complet."""

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


def publish_to_shopify(title, html_content, keywords, meta_description, slug, shopify_token):
    log(f"Publication sur Shopify : {title}")

    tags = generate_seo_tags(title, keywords)

    article_data = {
        "article": {
            "title": title,
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
                    "value": title,
                    "type": "single_line_text_field"
                }
            ]
        }
    }

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
    log(f"Article publie avec succes — ID Shopify : {article_id}")
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

    slug = generate_slug(article["title"])

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

        # Extraire meta description et HTML
        meta_description, html_content = extract_meta_and_content(raw_content)
        log(f"Article genere — {len(html_content)} caracteres")
        if meta_description:
            log(f"Meta description : {meta_description[:80]}...")
        else:
            log("ATTENTION : Pas de meta description detectee")

        time.sleep(2)

        # Publier sur Shopify
        publish_to_shopify(
            article["title"],
            html_content,
            article["keywords"],
            meta_description,
            slug,
            shopify_token
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
