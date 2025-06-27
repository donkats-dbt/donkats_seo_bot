from fpdf import FPDF
from datetime import datetime
import os
import re
import unicodedata

def sanitize(text):
    
    # Clean text to remove characters unsupported by FPDF core fonts."""
    
    if not isinstance(text, str):
        return text

    cleaned = (text
        .replace("❌", "[NOT FOUND]")
        .replace("⚠️", "[WARNING]")
        .replace("⚠", "[WARNING]")
        .replace("✅", "[OK]")
        .replace("–", "-")
        .replace("—", "-")
        .replace("…", "...")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("•", "-")
    )

    # Remove invisible/control characters (zero-width, BOM, etc.)
    cleaned = ''.join(
        c for c in cleaned
        if ord(c) >= 32 and (ord(c) < 127 or unicodedata.category(c)[0] != "C")
    )

    # Break up long unbroken strings (>50 chars)
    cleaned = re.sub(r'(\S{50,})', r'\1 ', cleaned)

    return cleaned
    
def create_pdf(results):
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_margins(left=10, top=10, right=10)
    pdf.set_font("Arial", "B", 24)
    pdf.image("static/logo.png", 10, 8, 33)
    
    pdf.cell(200, 10, "DonKats SEO Bot Report", ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, "Copyright © 2025 by DonKats Services, Inc. All Rights Reserved.", ln=True, align="C")


    pdf.set_font("Arial", "I", 10)
    pdf.ln(20)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    source = results.get("source", "Unknown")
    if re.match(r'https?://', source):
        domain = re.sub(r'https?://(www\.)?', '', source).split('/')[0]
        pdf.cell(0, 10, f"Analyzed Website: {domain}", ln=True)
    else:
        pdf.cell(0, 10, f"Analyzed Input: Direct Text", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.ln(5)

    if results.get("error"):
        pdf.set_text_color(220, 50, 50)
        pdf.multi_cell(0, 10, sanitize(f"Error: {results['error']}"))
        pdf.set_text_color(0, 0, 0)

    safe_width = 180
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(safe_width, 10, f"Title: {sanitize(results['title'])}")

    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(safe_width, 10, f"Meta Description: {sanitize(results['meta_desc'])}")

    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(safe_width, 10, f"Word Count: {results['word_count']}")

    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(safe_width, 10, f"Readability Score: {results['readability']:.2f}")


    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Content Preview:", ln=True)
    pdf.set_font("Arial", "", 11)
    preview = results["text"][:500] if results["text"] else "[NOT FOUND]"
    pdf.multi_cell(0, 10, sanitize(preview))

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SEO Reference Guide", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.ln(2)

    reference_lines = [
        "Title Tag:\nAppears in browser tabs and Google search results. It should be clear, concise, and include your target keywords.",
        "Meta Description:\nSummarizes the page content in search results. A well-written description improves click-through rate.",
        "Word Count:\nPages with more useful content tend to rank better, especially when the content is original and relevant.",
        "Readability Score:\nA higher Flesch Reading Ease score means your content is easier to read - important for retaining users.",
        "Body Text:\nThe main content on your page. It should be well-structured, use proper headings, and avoid keyword stuffing."
    ]

    for line in reference_lines:
        pdf.multi_cell(0, 8, sanitize(line))
        pdf.ln(1)

###################################################################

    # Extended SEO Analysis
    pdf.ln(8)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Extended SEO Analysis", ln=True)

    # Top Keywords by Frequency
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Top Keywords by Frequency", ln=True)
    pdf.set_font("Arial", "", 11)
    for kw, freq in results.get("top_keywords_freq", []):
        pdf.cell(0, 8, f"{kw}: {freq}", ln=True)

    # Top Keywords by TF-IDF
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Top Keywords by TF-IDF", ln=True)
    pdf.set_font("Arial", "", 11)
    for kw, score in results.get("top_keywords_tfidf", []):
        pdf.cell(0, 8, f"{kw}: {score:.4f}", ln=True)

    # Extracted Phrases
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Extracted Phrases", ln=True)
    pdf.set_font("Arial", "", 11)
    for phrase in results.get("noun_phrases", []):
        pdf.cell(0, 8, sanitize(phrase), ln=True)

    # SEO Recommendations
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "SEO Recommendations", ln=True)
    pdf.set_font("Arial", "", 11)
    for rec in results.get("recommendations", []):
        pdf.multi_cell(0, 8, sanitize(rec))
        pdf.ln(1)

####################  Added 6/24/2025 ##################################

# Section-Level SEO Analysis (Tabs / Panels)
    sections = results.get("sections", [])
    if sections:
#        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
#        pdf.cell(0, 10, "Section-Level SEO Analysis", ln=True)
####################  Added 6/24/2025 ##########        
        print(f"Generating PDF for {len(sections)} sections")
####################  Added 6/24/2025 ##########
        for section in sections:
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Section-Level SEO Analysis", ln=True)
####################  Added 6/24/2025 ##########        
            print(f"   Section: {section['label']}")
####################  Added 6/24/2025 ##########            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 8, f"Section: {sanitize(section['label'])}")

            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Word Count: {section['word_count']}", ln=True)
            pdf.cell(0, 8, f"Readability Score: {section['readability']:.2f}", ln=True)

            # Keywords by frequency
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, "Top Keywords:", ln=True)
            pdf.set_font("Arial", "", 11)
            for kw, freq in section.get("top_keywords", []):
                pdf.cell(0, 8, f"{kw}: {freq}", ln=True)

            # Noun Phrases
            phrases = ", ".join(section.get("noun_phrases", []))
            if phrases:
                pdf.ln(2)
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, "Noun Phrases:", ln=True)
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 8, sanitize(phrases))

            pdf.ln(4)


####################################################################

    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Generated by DonKats SEO Bot", 0, 0, "C")

    output_path = "output/donkats_seo_report.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return output_path
