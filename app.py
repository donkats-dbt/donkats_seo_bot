from flask import Flask, render_template, request, send_file, session
from seo_analysis import analyze_url_or_text
from generate_pdf import create_pdf
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "fallback-if-missing")

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        input_type = request.form.get("input_type")
        user_input = request.form.get("user_input")

        results = analyze_url_or_text(user_input, input_type)

        pdf_path = create_pdf(results)

        return render_template("results.html", results=results, pdf_path=pdf_path)

    return render_template("form.html")
    
@app.route("/")
def landing():
    return render_template("landing.html")    
    
@app.route("/pay")
def pay():
    return render_template("pay.html")
    
# added start
@app.route("/session_completed")
def session_completed():
    return render_template("session_completed.html")
# added end     

@app.route("/download")
def download():
    return send_file("output/donkats_seo_report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
