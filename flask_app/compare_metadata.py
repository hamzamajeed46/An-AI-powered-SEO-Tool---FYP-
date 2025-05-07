from groq import Groq
from config import Config
import markdown
import os
from backlinks import get_db_connection
from metadata_analysis import fetch_metadata


db = get_db_connection()  
coll = db["metadata"]  


# Initialize LLM
client = Groq(
    api_key=os.getenv("LLM_API"),
)

def compare_metadata2(url1, url2, keyword=None):
    try:
        if keyword:
            metadata1, keyword_data1, body_text1 = fetch_metadata(url1, keyword)
            metadata2, keyword_data2, body_text2 = fetch_metadata(url2, keyword)
        else:
            metadata1, keyword_data1, body_text1 = fetch_metadata(url1)
            metadata2, keyword_data2, body_text2 = fetch_metadata(url2)

        

        results = {
            "site1": {
                "url": url1,
                "metadata": metadata1,
                "keyword_data": keyword_data1,
                "body_text": body_text1
            },
            "site2": {
                "url": url2,
                "metadata": metadata2,
                "keyword_data": keyword_data2,
                "body_text": body_text2
            }
        }

        

        
        return results

    except Exception as e:
        return {"error": f"Failed to compare metadata: {str(e)}"}


def generate_comparison_recommendations(compare_result):
    try:
        site1_data = compare_result.get("site1", {})
        site2_data = compare_result.get("site2", {})


        prompt = (
            "You are an expert SEO consultant.\n"
            "The client provided the following metadata and keyword analysis from two websites.\n"
            "Analyze them and give actionable SEO recommendations for the client to improve their site.\n\n"
            "===  Client Website Metadata ===\n"
            f"{site1_data.get('metadata', {})}\n"
            "Keyword Analysis:\n"
            f"{site1_data.get('keyword_data', {})}\n\n"
            "=== Competitor Website Metadata ===\n"
            f"{site2_data.get('metadata', {})}\n"
            "Keyword Analysis:\n"
            f"{site2_data.get('keyword_data', {})}\n\n"
            "Focus only on actionable improvements. Give detailed strategies that can improve SEO."
        )


        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            stream=True,
        )
        # Prepare a prompt for the LLM


        # Send to LLM
        response = chat_completion.choices[0].message.content

        if response:
            recommendations_html = markdown.markdown(response.content)
            # First, find the latest document (if needed)
            latest_document = coll.find_one({"url": site1_data["url"]}, sort=[("_id", -1)])

            # Then, perform the update on the latest document
            if latest_document:
                coll.update_one(
                    {"_id": latest_document["_id"]},
                    {"$set": {"recommendations": recommendations_html}}
                )

            return recommendations_html
        else:
            return "No recommendations were generated."
        
    except Exception as e:
        return f"Failed to generate comparison recommendations: {str(e)}"
