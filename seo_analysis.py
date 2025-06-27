import requests
from bs4 import BeautifulSoup
import textstat
from readability import Document
from collections import Counter
#from stopwords import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from playwright.sync_api import sync_playwright
import re
import spacy
nlp = spacy.load("en_core_web_sm")

def get_top_freq_words(text, top_n=10):
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return Counter(words).most_common(top_n)

#def get_top_freq_words(text, top_n=10): 
#    words = re.findall(r'\b[a-z]{3,}\b', text.lower()) 
#    filtered = [word for word in words if word not in stopwords] 
#    return Counter(filtered).most_common(top_n)

def extract_tfidf_keywords(text, top_n=10):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf = vectorizer.fit_transform([text])
    terms = vectorizer.get_feature_names_out()
    scores = tfidf.toarray()[0]
    top_indices = scores.argsort()[-top_n:][::-1]
    return [(terms[i], scores[i]) for i in top_indices]
    
def extract_noun_phrases(text, top_n=10):
    doc = nlp(text)
    phrases = [chunk.text.lower().strip() for chunk in doc.noun_chunks]
    # Remove duplicates and short generic phrases
    cleaned = [p for p in set(phrases) if len(p.split()) > 1 and len(p) > 4]
    return cleaned[:top_n]
    
def generate_recommendations(result):
    recommendations = []
    if result.get("word_count", 0) < 300:
        recommendations.append("Increase word count to at least 300 for SEO effectiveness.")
    if result.get("readability", 100) < 50:
        recommendations.append("Improve readability by simplifying sentence structure.")
    if "not found" in result.get("meta_desc", "").lower():
        recommendations.append("Add a relevant meta description including target keywords.")
    if len(result.get("top_keywords_freq", [])) < 5:
        recommendations.append("Add more keyword-rich content to improve relevance.")
    if "not found" in result.get("title", "").lower():
        recommendations.append("Add a unique, keyword-rich title tag.")
    return recommendations
   
def extract_tab_sections(rendered_html):

    soup = BeautifulSoup(rendered_html, "html.parser")
    sections = []

    # Target dynamic tab containers, accordions, panels, etc.
    tab_containers = soup.select(
        ".tab-content > div, .elementor-tab-content, .accordion-body, .panel-body, .tab-pane, section"
    )
 
    for i, tab in enumerate(tab_containers):
        aria_id = tab.get("aria-labelledby")
        label_element = soup.find(id=aria_id) if aria_id else None
        label = label_element.get_text(strip=True) if label_element else f"Section {i+1}"
 
        text = tab.get_text(separator=" ", strip=True)

        if text and len(text.split()) > 20:
############################################################################           
            print(f" Section found: {label} ({len(text.split())} words)")
############################################################################            
            sections.append({
                "label": label,
                "text": text
            })
 
    return sections 
    
def analyze_url_or_text(user_input, input_type):
    result = {
        "title": "❌ Not found",
        "meta_desc": "❌ Not found",
        "readability": 0,
        "word_count": 0,
        "text": "❌ No readable content found.",
        "error": None,
        "source": user_input,  # for tracking in the PDF
        "top_keywords_freq": [],  # ✅ explicitly initialized
        "top_keywords_tfidf": [],  # ✅ explicitly initialized
        "noun_phrases": [], # ✅ explicitly initialized
        "recommendations": [] # ✅ explicitly initialized

    }

    try:
        if input_type == "url":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1", 
                "Referer": user_input
            }

            response = requests.get(user_input, headers=headers, timeout=10)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Title tag
            if soup.title and soup.title.string:
                result["title"] = soup.title.string.strip()

            # Meta description: standard + Open Graph fallback
            meta = soup.find("meta", attrs={"name": "description"})
            og_meta = soup.find("meta", attrs={"property": "og:description"})
            if meta and meta.get("content"):
                result["meta_desc"] = meta["content"].strip()
            elif og_meta and og_meta.get("content"):
                result["meta_desc"] = og_meta["content"].strip()

            # Main content: readability first, fallback to <p> tags
            try:
                doc = Document(html)
                body_html = doc.summary()
                text = BeautifulSoup(body_html, "html.parser").get_text()
            except Exception:
                paragraphs = soup.find_all("p")
                text = "\n".join(p.get_text() for p in paragraphs)

            tab_sections = extract_tab_sections(html)

            result["sections"] = []

            if text.strip():
                result["text"] = text.strip()
                result["word_count"] = len(text.split())
                result["readability"] = textstat.flesch_reading_ease(text)
                result["top_keywords_freq"] = get_top_freq_words(text)
                result["top_keywords_tfidf"] = extract_tfidf_keywords(text)
                result["noun_phrases"] = extract_noun_phrases(text)
                result["recommendations"] = generate_recommendations(result)

                for sec in tab_sections:
                    sec_result = {
                    "label": sec["label"],
                    "word_count": len(sec["text"].split()),
                    "readability": textstat.flesch_reading_ease(sec["text"]),
                    "top_keywords": get_top_freq_words(sec["text"]),
                    "tfidf": extract_tfidf_keywords(sec["text"]),
                    "noun_phrases": extract_noun_phrases(sec["text"]),
                    }
                    result["sections"].append(sec_result)
        else:  # Plain text input
            result["title"] = "Untitled"
            result["meta_desc"] = "No meta description"
            result["text"] = user_input.strip()
            result["word_count"] = len(user_input.split())
            result["readability"] = textstat.flesch_reading_ease(user_input)
            result["top_keywords_freq"] = get_top_freq_words(user_input)
            result["top_keywords_tfidf"] = extract_tfidf_keywords(user_input)
            result["noun_phrases"] = extract_noun_phrases(user_input)
            result["recommendations"] = generate_recommendations(result)

    except Exception as e:
        print("SEO Analysis Error:", e)
        result["error"] = "Website could not be found."
            
    return result
