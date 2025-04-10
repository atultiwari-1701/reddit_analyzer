import requests
import pandas as pd
import io
import re
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from transformers import pipeline
from .models import AnalysisResult


# Load sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis")

# Global variable to store analyzed data before exporting
analyzed_data_list = []


# Function to extract comments recursively
def extract_comments(comment_data, all_comments):
    for comment in comment_data:
        if "body" in comment["data"]:
            comment_text = comment["data"]["body"]
            all_comments.append(comment_text)

        if "replies" in comment["data"] and isinstance(comment["data"]["replies"], dict):
            extract_comments(comment["data"]["replies"]["data"]["children"], all_comments)

LPU_KEYWORDS = set(["lpu", "lovely professional", "lovely professional university", "lovely uni", "punjab college", "phagwara", "lpu campus", "lpu university", "lpu wale", "yeh college", "this college", "apna college", "tera college", "mera college", "lp wala", "hostel at lpu", "hostel in lpu", "placement at lpu", "campus life lpu", "college in punjab", "college at punjab", "punjab wale college", "collage in punjab", "lpu ki", "lpu ka", "lpu mein", "punjab university", "lpu students", "lpu student", "lpu crowd", "lpu ke", "college crowd", "lpu fee", "lpu course", "punjab private college", "btech lpu", "mca lpu", "bca lpu", "mba lpu", "hostel facility lpu", "lpu fest", "lpu fests", "one india lpu", "youth vibe lpu", "lp university", "lpu infra", "lpu infrastructure", "mera lpu", "my college lpu", "placement season lpu", "campus tour lpu", "hostel room lpu", "college fest lpu", "internship lpu", "faculty lpu", "lpu staff", "college life lpu", "lpu food", "canteen lpu", "wifi lpu", "lpu crowd", "lpu gate", "lpu entry", "jalandhar lpu", "delhi to lpu", "lpu train", "lpu ka scene", "punjab wale", "university lpu", "private university lpu", "private uni lpu", "collage lpu", "colg lpu", "collg lpu", "collage wala", "lpu wale", "campus placement lpu", "lpu review", "lpu opinions", "lpu student review", "is lpu good", "is lpu bad", "review of lpu", "how is lpu", "about lpu", "lpu experience", "lpu journey", "main lpu", "in lpu", "lp ka collg", "punjab collg", "punjab ka collg", "collage mein lpu", "clg lpu", "meri university lpu", "private collg lpu", "jee and lpu", "neet and lpu", "cutoff lpu", "placement lpu", "admission lpu", "entrance lpu", "lpu hai", "collage ka naam lpu", "mera campus lpu", "college placement", "college review", "campus life", "lpu vibes", "lpu ke baare mein", "lpu worth", "worth it lpu", "lpu admission", "collage info lpu", "college feedback lpu", "lpu private", "university info lpu", "college wale", "mera collage", "lp wale log", "mera clg", "mera collg", "about college lpu", "about lpu campus", "infrastructure lpu", "fees lpu", "lp clg", "mera lp", "mera lp clg", "lp wala clg", "lp ka collg", "clg in punjab", "main clg", "mera collg kaisa h", "mera collg ka review", "collg mein kya hai", "college wala experience", "campus mein kya hota", "lpu ka hostel", "lpu me admission", "clg me life", "campus ke log", "lpu interview", "campus drive lpu", "lpu ka placement", "festivals in lpu", "lpu seminars", "lpu education", "lp clg reviews", "mera feedback lpu", "campus ki life", "student feedback lpu", "student lpu", "fresher lpu", "seniors lpu", "college crowd lpu", "juniors lpu", "main waha padh rha", "mera bhai waha padh rha", "meri behan lpu", "friend lpu", "mera dost lpu", "yeh college sahi h", "college ka scene", "college ka truth", "reality of lpu", "campus life at lpu", "inside lpu", "about lpu placement", "inside story lpu", "truth about lpu", "lpu main kya hota", "college rules", "lpu hostel rules", "lpu ke canteen", "college mein kya hota", "placement ka scene", "yeh college kaisa h", "mera review on lpu", "mera experience", "mera college", "mera view", "lp wale students", "campus inside", "mera opinion", "lpu ke andar", "placement wala", "campus life", "lpu girl", "lpu boys", "hostel life lpu"
])  # paste 200+ LPU relevance keywords here
POSITIVE_KEYWORDS = set(["good placement", "nice faculty", "amazing college", "great exposure", "top infrastructure", "worth it", "value for money", "international exposure", "best college", "great crowd", "supportive staff", "peaceful campus", "modern classrooms", "fast wifi", "top-notch infra", "good fests", "vibe is great", "clean hostel", "beautiful campus", "cultural fest", "fun college", "good teachers", "motivated students", "great mentorship", "lpu rocks", "awesome place", "very nice", "amazing life", "best memories", "chill place", "genuine support", "good experience", "value education", "helpful seniors", "superb place", "positive vibes", "growth oriented", "tech friendly", "modern learning", "huge campus", "good canteen", "food is tasty", "well managed", "top rated", "well equipped", "5 star", "amazing friends", "placement hai", "good placement", "average accha", "badiya placement", "nice rooms", "nice lab", "well organized", "top placement", "top 10 college", "top 100", "global connect", "foreign exposure", "amazing workshops", "cool environment", "amazing faculty", "teachers are nice", "seniors help", "good in everything", "sab kuch sahi", "hostel awesome", "canteen good", "staff good", "rules ok", "modern feel", "naya campus", "nai facilities", "achi placement", "sahi hai", "paisa vasool", "mast crowd", "bhai mast hai", "fun crowd", "good sessions", "webinars nice", "free wifi", "coding culture", "tech community", "internship opportunity", "supportive team", "placement scene accha", "mein toh khush", "satisfied", "placements decent", "overall nice", "no ragging", "safe environment", "girls safe", "friendly people", "peaceful life", "sahi college", "top private college", "college achha", "recommend karunga", "best private", "punjab best", "mera best time", "best years", "positive experience", "kaafi acha", "acha hi h", "sahi scene", "bhot badiya", "life changing", "top placement", "sab sahi", "everything fine", "feel good", "top ranking", "amazing review", "rating acchi", "good rating", "sab safe", "top recruiter", "big companies", "amazon lpu", "google lpu", "wipro lpu", "infosys lpu", "placement mila", "offer mila", "amazing talk", "free certifications", "placements are good", "off campus bhi help", "full support", "job laga", "placement package", "package mila", "job mila", "career ban gaya", "career path", "teachers support", "no issues", "maza aaya", "best vibe", "good track", "campus drive sahi", "offering courses", "cool people", "career secure", "very supportive", "positive environment", "modern campus", "badiya teachers", "staff supportive", "punjab ka best", "hostel accha", "feel like home", "hostel sahi", "collg badiya", "environment friendly", "kuch bhi bura nahi", "bhot achha", "college of dreams", "meri college awesome", "study environment", "peaceful life", "campus is fun", "life at campus", "modern hostel", "food quality", "hostel rooms clean", "net fast", "clean and green", "lpu is wow", "accommodation is fine", "student friendly", "crowd helpful", "full support", "tech support", "tech learning", "kaafi supportive", "saare help karte", "cultural programs", "fests awesome", "youth vibe amazing", "internship acchi", "placement guarantee", "security best", "kaafi good", "teachers help", "sab help karte", "pehle se better", "bhot maza aaya", "kaafi mast", "campus tour", "feel great", "worth college", "hostel life nice", "acha clg", "collg bdiya", "infra good", "neat campus", "ac facilities", "wifi fast", "positive growth", "placements increase", "higher package", "personal growth", "college help", "full satisfied", "collg best", "private best", "meri journey best"

])  # paste 200+ positive keywords here
NEGATIVE_KEYWORDS = set(["bad placement", "fraud college", "fake promises", "no job", "zero placement", "overhyped", "only marketing", "nothing inside", "waste of money", "expensive and useless", "hostel dirty", "bathroom dirty", "worst experience", "bad crowd", "useless faculty", "not helpful", "too expensive", "loot liya", "scam college", "placement fake", "low salary", "bad package", "3 lakh package", "worst teachers", "no support", "no help", "faculty rude", "rude staff", "poor hostel", "bad rules", "weird rules", "not allowed", "strict rules", "laptop not allowed", "boys girls problem", "no freedom", "scam", "money minded", "only business", "college for profit", "profit motive", "money machine", "no coding", "no tech", "poor labs", "fake lab", "no resources", "internship not real", "placement nahi mila", "nahi mila job", "sirf dhong", "dhong clg", "bekar", "bekar college", "bakwas", "faltu college", "bakwas college", "bekar padhai", "faltu rules", "faltu fee", "no value", "placement farzi", "paisa barbaad", "ruined my life", "poor teaching", "very poor", "staff rude", "canteen dirty", "tasteless food", "no facilities", "wifi slow", "wifi not working", "ac not working", "no power backup", "load shedding", "hostel dirty", "rat in hostel", "bugs in room", "no internship", "hostel mein dikkat", "placement nahi", "placement fake", "job nahi mila", "no recruiter", "0 package", "bad experience", "worst crowd", "bad behavior", "poor management", "worst campus", "nothing to learn", "waste of time", "money loss", "value nahi", "not worth", "overpriced", "low quality", "placement story fake", "salary low", "3lpa only", "poor infra", "zero infra", "broken classroom", "classroom dirty", "no attention", "no mentorship", "negative vibes", "lpu sux", "lpu sucks", "lpu worst", "hate lpu", "disappointed", "fees too high", "no output", "output nahi", "fail clg", "not recommended", "never join", "career ruined", "dream broken", "regret joining", "never again", "bad reviews", "worst feedback", "kuch nahi milta", "waste of time", "no friends", "lonely college", "no crowd", "no enjoyment", "boring college", "boring clg", "fests bakwas", "one india boring", "no fest", "youth vibe is fake", "crowd useless", "bad hostel food", "worst security", "fight in hostel", "violence", "strict environment", "over controlling", "discipline issues", "rude teachers", "biased staff", "favoritism", "corruption", "badtameezi", "seniors rude", "no ragging help", "college not safe", "unsafe", "scared in hostel", "lonely", "no counselor", "mental pressure", "mental stress", "college se bore", "no placement cell", "clg staff rude", "lpu zero", "bad management", "not punctual", "late classes", "random schedule", "no timetable", "confusing system", "career down", "downfall", "lpu ke baad nothing", "placement sirf naam", "kuch bhi nahi", "naam ka college", "name only", "baap ka paisa waste", "kuch sikha nahi", "no value education", "bura time", "kharab time", "worst decision", "never suggest", "bad atmosphere", "strict for no reason", "closed minded", "no growth", "rejected offer", "fake job", "poor security", "staff not trained", "food poisoning", "dirty water", "drain water", "fees scam", "security issue", "network issues", "hate experience", "rude management"
    "10k-20k",
    "20k/mo internship",
    "CTC upto 4lakh",
    "company cut",
    "college takes cut",
    "herd of 20k",
    "same position try",
    "no proper placement",
    "fake placement",
    "off campus the",
    "scope khud ke bharose",
    "majdooro wala haal",
    "Zomato swiggy salary",
    "salary itna hi milega",
    "placement ka sach",
    "no job support",
    "average 5-6 he",
    "real placement me kuch nahi",
    "no help in placements",

    # 💸 Fees vs Value Complaints
    "fees in Lakhs",
    "not worth fees",
    "expensive and no return",
    "paise barbaad",
    "waste of money",
    "loot macha rakha hai",
    "high fees low return",
    "overpriced education",
    "fees kaafi high",

    # 🧑‍🏫 Management, Faculty, and Academic Criticism
    "management bhot bakwas",
    "brain dead people",
    "worst management",
    "faculty biased",
    "8 cgpa nahi degi",
    "no 8 cgpa",
    "scholarship nahi milega",
    "partial grading",
    "marks cut karte hain",
    "admin doesn't care",
    "zero academic support",
    "bakwas system",
    "no real learning",
    "paper checking unfair",

    # ❌ Negative College Reputation
    "ekdam 2/10",
    "bohot shitty",
    "worst college",
    "will not recommend",
    "not recommend to enemy",
    "absolute waste of time",
    "overhyped he bohot",
    "overhype reality",
    "bad college experience",
    "yeh college bakwas",
    "not good college",
    "avoid this college",

    # ❗ Doubts & Concerns (context-sensitive but negative tone)
    "how much in lpunest",
    "don't know if I will get cse",
    "admission waghera kaise",
    "anything about ragging",
    "concerned about ragging",
    "safe for freshers?",
    "ragging scene",
    "confused about admission",
    "worried about lpu"
])  # paste 200+ negative keywords here

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text

def is_lpu_related(comment):
    comment = preprocess(comment)
    return any(keyword in comment for keyword in LPU_KEYWORDS)

def get_sentiment(comment):
    comment = preprocess(comment)
    positive_score = sum(1 for kw in POSITIVE_KEYWORDS if kw in comment)
    negative_score = sum(1 for kw in NEGATIVE_KEYWORDS if kw in comment)

    if positive_score > negative_score:
        return "POSITIVE"
    elif negative_score > positive_score:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


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
        else:
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
        print("Data fetched from Reddit API:")
        post_data = data[0]["data"]["children"][0]["data"]
        print(post_data)

        title = post_data["title"]
        upvotes = post_data["ups"]
        comments_count = post_data["num_comments"]

        # ✅ Updated this to unpack lists instead of just counts
        positive_comments, negative_comments, neutral_comments, _ = analyze_comments(data)

        # ✅ Construct the response using list lengths and actual comments
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

        # Save to session (optional for export)
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
        return redirect("/")  # Or return an error if you want

    # Limit the data to specific columns
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
    
    # Get filename from query parameter or use default
    filename = request.GET.get("filename", "reddit_analysis") + ".xlsx"

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    df.to_excel(response, index=False)
    return response








LPU_KEYWORDS = set([
    "lpu", "lovely professional", "lovely professional university", "punjab college",
    "apna college", "this college", "yeh college", "hamara college", "tera college",
    "mera college", "is college", "college in punjab", "phagwara college", "lpu punjab",
    "my college", "your college", "their college", "our college", "that college",
    "fake college", "scam college", "placement college", "lovely uni", "fraud college"
])

POSITIVE_KEYWORDS = set([
    "good placement", "nice faculty", "amazing college", "great exposure", "top infrastructure",
    "helpful teachers", "supportive staff", "well maintained", "good experience", "high package",
    "placement offers", "internship opportunities", "peaceful campus", "excellent college"
])

NEGATIVE_KEYWORDS = set([
    "bad placement", "fraud college", "fake promises", "no job", "zero placement",
    "scam", "bakwaas", "worst college", "waste of money", "useless college",
    "not worth it", "teachers are bad", "no support", "fake reviews", "placement is fake",
    
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