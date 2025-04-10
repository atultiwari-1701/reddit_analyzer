import requests
import pandas as pd
import io
import re
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import AnalysisResult
import openai
# Enhanced LPU-related keywords
LPU_KEYWORDS = set([
    "lpu", "lovely professional", "lovely professional university", "punjab college",
    "apna college", "this college", "yeh college", "hamara college", "tera college",
    "mera college", "is college", "college in punjab", "phagwara college", "lpu punjab",
    "my college", "your college", "their college", "our college", "that college",
    "fake college", "scam college", "placement college", "lovely uni", "fraud college"
        "lpu", "lovely professional", "lovely professional university", "punjab college",
    "apna college", "this college", "yeh college", "hamara college", "tera college",
    "mera college", "is college", "college in punjab", "phagwara college", "lpu punjab",
    "my college", "your college", "their college", "our college", "that college",
    "fake college", "scam college", "placement college", "lovely uni", "fraud college",
    "lpu campus", "lpu admission", "lpu hostel", "lpu fest", "lpu placement",
    "lpu ke placements", "lpu ki fest", "lpu ka hostel", "lpu ka admission",
    "lpu main kya hota hai", "lpu fees", "lpu mein admission kaise le",
    "punjab university", "punjab mein college", "punjab ka top college",
    "lpu event", "lpu function", "lpu group", "lpu friend circle",
    "lpu classroom", "lpu ka campus", "lpu rules", "lpu reviews",
    "lpu students", "lpu seniors", "lpu juniors", "lpu crowd", "lpu mess",
    "lpu library", "lpu wifi", "lpu net", "lpu timing", "lpu crowd",
    "phagwara lpu", "phagwara university", "lpu official", "lpu student life",
    "lpu professors", "lpu education", "lpu degree", "lpu ki degree",
    "punjab engineering college", "btech in lpu", "mba in lpu", "mtech in lpu",
    "ba in lpu", "bca in lpu", "lpu alumni", "lpu engineer", "lpu ka student",
    "main lpu mein hoon", "main lpu ka hoon", "main lpu mein padhta hoon",
    "main lpu se hoon", "lpu se padha hai", "lpu ke student", "lpu se graduate",
    "mera bhai lpu mein hai", "meri behan lpu mein", "mere friend lpu mein",
    "lpu ke result", "lpu placement drive", "lpu ke fest", "lpu ka function",
    "lovely pro university", "lovely prof. uni", "lovely pro.", "lpu topper",
    "lpu student review", "lpu management", "lpu exam", "lpu scholarship",
    "lpu ka result", "lpu form", "lpu admission form", "lpu brochure",
    "lpu website", "lpu student portal", "lpu contact", "lpu helpline",
    "lpu ka food", "lpu mein khana", "lpu canteen", "lpu se job", "lpu mein job",
    "lpu ke log", "lpu ka placement report", "lpu mein padhai",
    "lpu ka system", "lpu faculty", "lpu mein exam", "lpu internal",
    "lpu external", "lpu online", "lpu offline", "lpu mein kya hai",
    "lpu ke seniors", "lpu ka dress code", "lpu mein ragging", "lpu mein strict",
    "lpu mein masti", "lpu culture", "lpu ki padhai", "lpu ki policy",
    "lpu mein rules", "lpu admin", "lpu helpline number", "lpu whatsapp group",
    "lpu ke professors", "lpu ka management", "lpu student group",
    "lpu discussion", "lpu complaints", "lpu reviews hindi", "punjab university review",
    "lpu kya sahi hai", "lpu kaisa hai", "lpu kaisa dikhta hai",
    "lpu mein kya sikhaya jata hai", "lpu full form", "lpu ki details",
    "lpu se kya career banega", "lpu worth it", "lpu ke paper",
    "lpu mein subjects", "lpu ka prospectus", "lpu mein ragging hoti hai?",
    "lpu fest photos", "lpu crowd kaise hai", "lpu girls ratio",
    "lpu boys hostel", "lpu girls hostel", "lpu campus map", "lpu location",
    "lpu admission process", "lpu mein entry", "lpu degree valuable?",
    "lpu mein placements fake hain kya", "lpu fake", "lpu scam", "lpu safe hai?",
    "lpu mein discipline", "lpu mein strictness", "lpu mein growth",
    "lpu mein industry exposure", "lpu mein kya sikha", "lpu best or worst",
    "lpu mein admission lena chahiye", "lpu career prospects"
])

POSITIVE_KEYWORDS = set(["good placement", "nice faculty", "amazing college", "great exposure", "top infrastructure",
    "helpful teachers", "supportive staff", "well maintained", "good experience", "high package",
    "placement offers", "internship opportunities", "peaceful campus", "excellent college",
    "achha placement", "mast faculty", "top college", "accha infrastructure", "faculty supportive hai",
    "bhot acchi jagah", "safe campus", "career bana diya", "teachers ache hain",
    "learning environment", "study friendly", "internship mil gaya", "job lag gayi",
    "placement achha mila", "achha atmosphere", "positive vibes", "supportive seniors",
    "best college in punjab", "no ragging", "friendly teachers", "helpful seniors",
    "career boost", "growth opportunities", "nice infrastructure", "clean campus",
    "modern facilities", "technology advanced", "labs achhe hain", "placement training",
    "interview help", "achhe professors", "experienced faculty", "foreign exposure",
    "international tie-ups", "industry connect", "coding culture", "hackathons",
    "project support", "startup culture", "entrepreneurship support", "peaceful environment",
    "hostel is good", "mess food acha hai", "discipline maintained", "value for money",
    "friendly crowd", "diversity in students", "multi cultural", "good crowd",
    "co-curricular active", "fest awesome tha", "management acha hai", "events mast hote hain",
    "achhi life", "best memories", "placement ke chances high hain", "training sessions",
    "campus recruitment", "top MNCs aaye the", "Google placement", "Amazon aaya tha",
    "Infosys, Wipro hire", "campus drive", "CV banane mein madad", "interview skills groomed",
    "skill based learning", "value added courses", "certification courses", "LinkedIn profile boost",
    "placement oriented", "coding classes", "mock interview", "resume building help",
    "career counseling", "positive feedback", "no ragging issue", "bhot secure campus",
    "faculty guidance", "career mentorship", "alumni support", "project showcase",
    "internship compulsory", "company visits", "practical training", "live project",
    "industrial exposure", "motivating teachers", "placement ke liye tayar karte hain",
    "test series for placement", "job milti hai", "campus se direct job", "baap college",
    "bahut acha institute", "college ka naam hai", "naam suna hoga", "brand value",
    "achha naam", "top ranking", "higher studies support", "GRE coaching", "GATE coaching",
    "IELTS support", "foreign admission support", "startup se support", "mentorship milta hai",
    "yeh college best hai", "placement ke liye best", "achhi facilities", "learning ka mahaul",
    "dost ache mile", "team work sikha", "real life sikha", "achhi environment",
    "job oriented curriculum", "soft skill training", "resume help", "counseling sessions",
    "student support", "skill development", "interactive classes", "online learning",
    "e-learning platform", "wifi campus", "digital classrooms", "smart boards",
    "library achhi hai", "books available", "notes milte hain", "support system",
    "good feedback", "students happy", "acche seniors", "hostel staff helpful",
    "warden cooperative", "hostel safe", "sports facilities", "sports fest",
    "technical fest", "cultural fest", "fashion show", "fun campus", "dancing singing fest",
    "achhi memories", "yaadgar time", "college ke din yaad aate hain", "achha waqt tha",
    "best decision", "kisi ne bola join karo", "no regret", "satisfied student",
    "parents bhi khush", "career ban gaya", "education quality top", "standards maintained",
    "value education", "discipline bhi hai", "time ka respect", "quality crowd",
    "meri pehli job yahin se", "meri zindagi change kar di", "pehla salary slip",
    "mentors amazing", "supportive environment", "kamaal ka placement", "placement ki tayyari",
    "mock GD PI", "interview guidance", "coding environment", "development environment",
    "open source culture", "active community", "college life best thi", "full support",
    "bina issue ke degree", "sahi time pe complete", "marks transparency", "management cooperation",
    "always available teachers", "online portal helpful", "query solve hoti hai",
    "koi problem nahi", "smart classes", "labs modern", "wifi fast", "well-connected",
    "accessibility", "hostel me AC", "good food", "campus me CCD", "Dominos", "Food court",
    "campus green", "clean campus", "neat and tidy", "hygiene maintained",
    "medical support", "health center", "ambulance ready", "safety guards", "CCTV security",
    "night security", "female friendly", "no harassment", "strict rules",
    "career success", "achievements", "reputation maintained", "placement figures genuine",
    "positive environment", "feedback culture", "faculty listens", "student council",
    "polls for decision", "open feedback", "freedom of thought", "encouragement",
    "talent support", "creative freedom", "innovation driven", "r&d opportunities",
    "research opportunities", "funding available", "lab access", "placement chart",
    "website updated", "ERP portal useful", "college ka ERP", "students ka care",
    "attention milta hai", "staff listens", "help desk", "response time fast",
    "feedback ka response milta hai", "development environment", "upskilling",
    "future ready", "college ka vision acha hai", "mission driven", "good values",
    "cultural values", "Indian values", "global exposure", "achha guidance",
    "proper process", "everything is streamlined", "policy transparent", "college growth"

])

NEGATIVE_KEYWORDS = set([
    "bad placement", "fraud college", "fake promises", "no job", "zero placement",
    "scam", "bakwaas", "worst college", "waste of money", "useless college",
    "not worth it", "teachers are bad", "no support", "fake reviews", "placement is fake",
    "kaam ka nahi", "paisa barbaad", "no exposure", "fake degree", "zero opportunity",
    "ragging", "waste of time", "herd of people", "classroom bound", "strict", 
    "zero opportunities", "policies made by brain dead people", "no scope", 
    "one of the worst", "mess it up", "bad infrastructure", "not recommend", 
    "hate", "regret", "fake promises", "cheating", "last se last wala college", 
    "brain dead", "no support", "marks biased", "bakwas", "overhyped", 
    "horrible", "nightmare", "bad experience", "bad review", "shitty", "2/10", 
    "cut of the money", "10k-20k salary", "internship only", "job cut", 
    "delivery boy salary", "majdoor wala haal", "9–5 slave", "companies take cut", 
    "not placed", "fake placements", "off-campus only", "low CTC", 
    "no job security", "struggle for job", "CTC manipulation", "disappointment", 
    "expensive", "no scholarship", "lakhs fees", "not worth it", "not affordable", 
    "took cut", "bhot mehenga", "paisa barbaad", "high fees low return", 
    "looting", "fraud",
    "no placements", "false promises", "money minded", "poor management", 
    "unprofessional staff", "low quality education", "no practical exposure", 
    "overcrowded", "lack of facilities", "poor infrastructure", "money grabbers", 
    "no career growth", "unethical practices", "no value for money", 
    "misleading advertisements", "poor teaching quality", "no industry exposure", 
    "high dropout rate", "no innovation", "lack of research", "poor alumni network", 
    "no extracurricular activities", "unresponsive administration", 
    "lack of transparency", "biased grading", "no personal attention", 
    "poor hostel facilities", "unhygienic conditions", "no safety measures", 
    "lack of discipline", "no student support", "poor placement assistance"
      "sirf paisa kamaane wale", "faltu college", "sirf naam ka", "bas paisa chahiye", 
    "ekdum third class", "pura time barbaad", "yeh college mat lena", 
    "iss se achha ghar baith jao", "ghanta padhai", "padhai zero", 
    "paisa leke kuch nahi sikhate", "na job milti hai na internship", 
    "sab jhooth bolte hai", "placement ka dhong", "placement jhootha", 
    "degree bekaar hai", "resume mein kuch nahi", "resume kaam ka nahi", 
    "course outdated hai", "na koi tech stack", "teacher kuch nahi sikhata", 
    "faltu gyaan dete hai", "bina matlab ke rules", "discipline sirf naam ka", 
    "hostel jail jaise", "canteen mein khana bakwas", "kharcha zyada output zero", 
    "fraud ke alawa kuch nahi", "students ka future barbaad", 
    "koi bhi company nahi aati", "career khatam", "sirf formality ka internship", 
    "bina placement passout", "placement ke naam pe joke", "100% placement jhooth", 
    "placement milta hi nahi", "achhe students bhi fail ho jate", 
    "marks milte setting se", "padhai pe focus nahi", "faltu ka pressure", 
    "management sunta nahi", "student ki koi value nahi", "bina bataye fine", 
    "useless faculty", "time waste karte hai", "padhai ka standard low hai", 
    "bina plan ke syllabus", "curriculum old hai", "placements fixed nahi hote", 
    "degree lene ke baad regret", "koi help nahi milta", "kisi ko farak nahi padta", 
    "na admin sunta hai", "har semester mein paise looto", "no support system", 
    "teacher partiality karte hai", "sab politics hai", "teacher biased hai", 
    "placement cell kuch nahi karta", "sab setting se hota hai", "connection chahiye", 
    "merit kaam nahi karta", "fail hone ka darr", "unfair marking", "no feedback", 
    "koi student welfare nahi", "grievance sunte nahi", "na internship milti hai", 
    "IT infra bekaar", "WiFi nahi chalta", "labs kharab", "software outdated", 
    "hardware purana", "project mein help nahi", "cheating allow karte hai", 
    "strict for no reason", "discipline aur jail mein farak nahi", 
    "na koi fest hota", "culture dull hai", "creativity nahi hai", 
    "kuch bhi organize nahi hota", "events sirf naam ke", "achhe log demotivate hote", 
    "rattal lagwani padti hai", "research zero", "koi innovation nahi", 
    "useless course curriculum", "teachers koi training nahi lete", 
    "internship ke liye khud dhoondho", "placement sirf top 5 ko", 
    "baaki students bhool jao", "na koi mentorship", "career ka satyanaash", 
    "admin unresponsive", "support ticket ka reply nahi", "safety zero", 
    "ragging control nahi", "late night issues", "hostel unsafe", "no CCTV", 
    "staff careless", "bina kaam ke fine lagta hai", "discipline mein harassment", 
    "bina wajah trouble", "khana kharab", "unhygienic hostel", 
    "water problem", "AC kaam nahi karta", "fan kharab", "garmi mein maar jaoge", 
    "no cooling system", "faltu ka syllabus", "notes nahi milta", 
    "lecture time pe nahi hota", "recorded lectures bekaar", 
    "doubt solve nahi hota", "student ka opinion ignore", "attendance ka jhanjhat", 
    "forcefully attend karna padta", "no freedom", "kaam ka pressure zyada", 
    "exam pattern bekaar", "kya padhna hai samajh nahi aata", 
    "padhai se jyada formality", "academic pressure without guidance", 
    "chhutti nahi milti", "exam ke beech mein lecture", "fekne ke liye padhai", 
    "review fake hai", "alumni ka feedback negative", "ranking bhi fake hai"
])

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text

def is_lpu_related(comment):
    comment = preprocess(comment)
    for keyword in LPU_KEYWORDS:
        if keyword in comment:
            print(f"[LPU-MATCH] Matched keyword: {keyword} in comment: {comment}")
            return True
    print(f"[NOT LPU] {comment}")
    return False

def contains_keyword(comment, keyword_list):
    comment = comment.lower()
    return any(re.search(rf"\b{re.escape(kw)}\b", comment) for kw in keyword_list)
def get_sentiment(comment):
    comment = preprocess(comment)
    positive_score = sum(1 for kw in POSITIVE_KEYWORDS if kw in comment)
    negative_score = sum(1 for kw in NEGATIVE_KEYWORDS if kw in comment)

    print(f"\nAnalyzing Comment: {comment}")
    print(f"Positive Matches: {positive_score}, Negative Matches: {negative_score}")

    if negative_score > positive_score:
        return "NEGATIVE"
    elif positive_score > negative_score:
        return "POSITIVE"
    else:
        return "NEUTRAL"

def extract_comments(comment_data, all_comments):
    for comment in comment_data:
        if "body" in comment["data"]:
            comment_text = comment["data"]["body"]
            all_comments.append(comment_text)

        if "replies" in comment["data"] and isinstance(comment["data"]["replies"], dict):
            extract_comments(comment["data"]["replies"]["data"]["children"], all_comments)

def analyze_comments(data):
    comments_data = data[1]["data"]["children"]
    all_comments = []
    extract_comments(comments_data, all_comments)

    positive_comments = []
    negative_comments = []
    neutral_comments = []

    for comment_text in all_comments:
        if is_lpu_related(comment_text):
            sentiment = get_sentiment(comment_text)
        else:
            sentiment = "NEUTRAL"

        if sentiment == "POSITIVE":
            positive_comments.append(comment_text)
        elif sentiment == "NEGATIVE":
            negative_comments.append(comment_text)
        elif sentiment == "NEUTRAL" and comment_text not in positive_comments and comment_text not in negative_comments:
            # Ensure neutral comments do not overlap with positive or negative
            neutral_comments.append(comment_text)

    return positive_comments, negative_comments, neutral_comments, len(all_comments)

def analyze_reddit_post(request):
    if request.method == "POST":
        post_url = request.POST.get("post_url")
        if not post_url:
            return JsonResponse({"error": "Please provide a valid URL."}, status=400)

        json_url = post_url if post_url.endswith(".json") else post_url + ".json"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(json_url, headers=headers)

        if response.status_code != 200:
            return JsonResponse({"error": f"Unable to fetch data. Status code: {response.status_code}"}, status=500)

        data = response.json()
        post_data = data[0]["data"]["children"][0]["data"]

        title = post_data["title"]
        upvotes = post_data["ups"]
        comments_count = post_data["num_comments"]

        positive_comments, negative_comments, neutral_comments, _ = analyze_comments(data)

        new_data = {
            "Title": title,
            "URL": post_url,
            "Upvotes": upvotes,
            "Comments Count": comments_count,
            "Positive Sentiments": len(positive_comments),
            "Negative Sentiments": len(negative_comments),
            "Neutral Sentiments": len(neutral_comments),
            "Positive Comments": positive_comments,
            "Negative Comments": negative_comments,
            "Neutral Comments": neutral_comments
        }

        if "analyzed_data" not in request.session:
            request.session["analyzed_data"] = []

        analyzed_data = request.session["analyzed_data"]
        analyzed_data.append(new_data)
        request.session["analyzed_data"] = analyzed_data

        return JsonResponse(new_data)

    return render(request, "index.html")

def export_to_excel(request):
    analyzed_data = request.session.get("analyzed_data", [])

    if not analyzed_data:
        return redirect("/")

    filtered_data = [
        {
            "Title": item["Title"],
            "URL": item["URL"],
            "Upvotes": item["Upvotes"],
            "Comments Count": item["Comments Count"],
            "Positive Sentiments": item["Positive Sentiments"],
            "Negative Sentiments": item["Negative Sentiments"],
            "Neutral Sentiments": item["Neutral Sentiments"],
        }
        for item in analyzed_data
    ]

    df = pd.DataFrame(filtered_data)

    filename = request.GET.get("filename", "reddit_analysis") + ".xlsx"

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    df.to_excel(response, index=False)
    return response
