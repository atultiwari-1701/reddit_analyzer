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

LPU_KEYWORDS = set([
    "lpu", "lovely professional", "lovely professional university", "punjab college"
   
])  # paste 200+ LPU relevance keywords here
POSITIVE_KEYWORDS = set(["good placement", "nice faculty", "amazing college", "great exposure", "top infrastructure", "worth it", ])  # paste 200+ positive keywords here
NEGATIVE_KEYWORDS = set(["bad placement", "fraud college", "fake promises", "no job"    
])  # paste 200+ negative keywords here

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)  # Replace punctuation with space
    text = re.sub(r"\s+", " ", text).strip()     # Normalize whitespace
    return text

def is_lpu_related(comment):
    comment = preprocess(comment)
    for keyword in LPU_KEYWORDS:
        if keyword in comment:
            print(f"[LPU-MATCH] '{keyword}' matched in comment: {comment}")
            return True
    print(f"[NOT LPU] {comment}")
    return False

def phrase_in_comment(phrase):
    return phrase in comment

def phrase_in_comment(phrase):
    return all(word in comment_words for word in phrase.split())

def get_sentiment(comment):
    comment = preprocess(comment)
    comment_words = set(comment.split())

    def phrase_in_comment(phrase):
        return all(word in comment_words for word in phrase.split())

    matched_positive = [kw for kw in POSITIVE_KEYWORDS if phrase_in_comment(kw)]
    matched_negative = [kw for kw in NEGATIVE_KEYWORDS if phrase_in_comment(kw)]


    print(f"\nComment: {comment}")
    print(f"Matched Positive: {matched_positive}")
    print(f"Matched Negative: {matched_negative}")

    if matched_negative and not matched_positive:
        return "NEGATIVE"
    elif matched_positive and not matched_negative:
        return "POSITIVE"
    elif matched_positive and matched_negative:
        return "NEGATIVE"  # prioritize negative
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