# import requests
# import pandas as pd
# import re
# from django.shortcuts import render, redirect
# from django.http import JsonResponse, HttpResponse
# from .models import AnalysisResult
# import openai

# openai.api_key = "OPENAI_API_KEY"

# def preprocess(text):
#     text = text.lower()
#     text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
#     return text

# def is_lpu_related(comment):
#     # Basic logic to filter comments related to LPU
#     comment = preprocess(comment)
#     return "lpu" in comment or "lovely professional" in comment or "lovely professional university" in comment

# def get_sentiment_chatgpt(comment):
#     try:
#         system_message = {
#             "role": "system",
#             "content": (
#                 "You are a sentiment classifier for Reddit comments about Lovely Professional University (LPU). "
#                 "You must reply ONLY with one of the following words: POSITIVE, NEGATIVE, or NEUTRAL. "
#                 "Do not explain or add anything else."
#             )
#         }

#         user_message = {
#             "role": "user",
#             "content": f"Classify the sentiment of this comment: {comment}"
#         }

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[system_message, user_message],
#             max_tokens=5,
#             temperature=0
#         )

#         # Extract and normalize sentiment
#         content = response.choices[0].message["content"].strip().upper()
#         print(f"[ChatGPT Response] {content}")

#         # Use regex to extract one of the valid labels
#         match = re.search(r"\b(POSITIVE|NEGATIVE|NEUTRAL)\b", content)
#         if match:
#             return match.group(1)
#         else:
#             return "NEUTRAL"

#     except Exception as e:
#         print(f"[ERROR in ChatGPT call] {e}")
#         return "NEUTRAL"


# def extract_comments(comment_data, all_comments):
#     for comment in comment_data:
#         if "body" in comment["data"]:
#             comment_text = comment["data"]["body"]
#             all_comments.append(comment_text)

#         if "replies" in comment["data"] and isinstance(comment["data"]["replies"], dict):
#             extract_comments(comment["data"]["replies"]["data"]["children"], all_comments)

# def analyze_comments(data):
#     comments_data = data[1]["data"]["children"]
#     all_comments = []
#     extract_comments(comments_data, all_comments)

#     positive_comments = []
#     negative_comments = []
#     neutral_comments = []

#     for comment_text in all_comments:
#         if is_lpu_related(comment_text):
#             sentiment = get_sentiment_chatgpt(comment_text)

#             if sentiment == "POSITIVE":
#                 positive_comments.append(comment_text)
#             elif sentiment == "NEGATIVE":
#                 negative_comments.append(comment_text)
#             else:
#                 neutral_comments.append(comment_text)

#     return positive_comments, negative_comments, neutral_comments, len(all_comments)

# def analyze_reddit_post(request):
#     if request.method == "POST":
#         post_url = request.POST.get("post_url")
#         if not post_url:
#             return JsonResponse({"error": "Please provide a valid URL."}, status=400)

#         json_url = post_url.rstrip("/") + ".json"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         try:
#             response = requests.get(json_url, headers=headers, timeout=10)
#             response.raise_for_status()
#         except requests.RequestException as e:
#             return JsonResponse({"error": f"Failed to fetch Reddit post: {e}"}, status=500)

#         data = response.json()
#         post_data = data[0]["data"]["children"][0]["data"]

#         title = post_data["title"]
#         upvotes = post_data["ups"]
#         comments_count = post_data["num_comments"]

#         positive_comments, negative_comments, neutral_comments, total_comments = analyze_comments(data)

#         new_data = {
#             "Title": title,
#             "URL": post_url,
#             "Upvotes": upvotes,
#             "Comments Count": comments_count,
#             "Positive Sentiments": len(positive_comments),
#             "Negative Sentiments": len(negative_comments),
#             "Neutral Sentiments": len(neutral_comments),
#             "Positive Comments": neutral_comments,
#             "Negative Comments": negative_comments,
#             "Neutral Comments": positive_comments
#         }

#         if "analyzed_data" not in request.session:
#             request.session["analyzed_data"] = []

#         request.session["analyzed_data"].append(new_data)
#         request.session.modified = True

#         return JsonResponse(new_data)

#     return render(request, "index.html")

# def export_to_excel(request):
#     analyzed_data = request.session.get("analyzed_data", [])
#     if not analyzed_data:
#         return redirect("/")

#     filtered_data = [
#         {
#             "Title": item["Title"],
#             "URL": item["URL"],
#             "Upvotes": item["Upvotes"],
#             "Comments Count": item["Comments Count"],
#             "Positive Sentiments": item["Positive Sentiments"],
#             "Negative Sentiments": item["Negative Sentiments"],
#             "Neutral Sentiments": item["Neutral Sentiments"],
#         }
#         for item in analyzed_data
#     ]

#     df = pd.DataFrame(filtered_data)
#     filename = request.GET.get("filename", "reddit_analysis") + ".xlsx"

#     response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'

#     df.to_excel(response, index=False)
#     return response
