import json
import os
from typing import Dict, Any, List, Optional
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None
from datetime import datetime
from dotenv import load_dotenv

# ============================================================
# GEMINI CONFIGURATION
# ============================================================
# Load .env from current working directory and also from this file's directory
# so that starting uvicorn from parent/root still picks up the key.
load_dotenv()  # try CWD first
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
    _ENV_PATH = os.path.join(_HERE, ".env")
    if os.path.exists(_ENV_PATH):
        load_dotenv(dotenv_path=_ENV_PATH, override=False)
except Exception:
    # Non-fatal: we will still rely on existing env if present
    pass
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_ENABLED = False

def configure_gemini() -> bool:
    """Configures the Gemini API client. Falls back gracefully if unavailable."""
    global GEMINI_ENABLED
    # If package import failed, we cannot use Gemini
    if genai is None:
        GEMINI_ENABLED = False
        print("⚠️ google.generativeai not available; using local fallback generation")
        return False
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            GEMINI_ENABLED = False
            print("⚠️ GEMINI_API_KEY not set; using local fallback generation")
            return False
        genai.configure(api_key=api_key)
        GEMINI_ENABLED = True
        print("✅ Gemini API configured successfully")
        return True
    except Exception as e:
        GEMINI_ENABLED = False
        print(f"⚠️ Failed to configure Gemini API: {str(e)} — using local fallback generation")
        return False

# ============================================================
# ENHANCED HTML TEMPLATE
# ============================================================

ENHANCED_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facial Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #ffffff 0%, #ffffff 100%);
            color: #2d3748;
            min-height: 100vh;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        
        .container {{
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
            animation: fadeIn 0.6s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 3px solid #e2e8f0;
        }}
        
        header h1 {{
            color: #1a202c;
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .timestamp {{
            font-size: 0.95em;
            color: #718096;
            font-weight: 500;
        }}
        
        .image-container {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .image-container img {{
            border-radius: 16px;
            max-width: 280px;
            height: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            border: 4px solid #f7fafc;
            transition: transform 0.3s ease;
        }}
        
        .image-container img:hover {{
            transform: scale(1.05);
        }}
        
        section {{
            margin: 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 16px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
        }}
        
        section:hover {{
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
            transform: translateX(5px);
        }}
        
        section h2 {{
            color: #2d3748;
            font-size: 1.5em;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        section h2 .emoji {{
            font-size: 1.3em;
        }}
        
        section p {{
            color: #4a5568;
            font-size: 1.05em;
            line-height: 1.8;
            margin: 10px 0;
        }}
        
        ul {{
            list-style-type: none;
            padding: 0;
            margin-top: 15px;
        }}
        
        li {{
            margin: 12px 0;
            padding: 12px 15px;
            background: white;
            border-radius: 10px;
            position: relative;
            padding-left: 35px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }}
        
        li:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transform: translateX(3px);
        }}
        
        li::before {{
            content: '●';
            color: #667eea;
            font-weight: bold;
            font-size: 1.3em;
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
        }}
        
        .score-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1.2em;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .hidden {{
            display: none;
        }}
        
        #summary {{
            background: linear-gradient(135deg, #fef5e7 0%, #fdebd0 100%);
            border-left-color: #f39c12;
        }}
        
        #skincare {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left-color: #4caf50;
        }}
        
        #grooming {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left-color: #2196f3;
        }}
        
        #attractiveness {{
            background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
            border-left-color: #e91e63;
        }}
        
        #good_features {{
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-left-color: #9c27b0;
        }}
        
        #bad_features {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-left-color: #ff9800;
        }}
        
        #neutral_features {{
            background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
            border-left-color: #009688;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 25px;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
            
            section {{
                padding: 20px;
            }}
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            color: #718096;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Facial Feature & Grooming Analysis</h1>
            <div class="timestamp">Generated: {timestamp}</div>
        </header>
        
        <div class="image-container">
            <img src="{image_path}" alt="Subject Image">
        </div>

        <section id="summary">
            <h2><span class="emoji">📋</span> Executive Summary</h2>
            <p>{summary_text}</p>
        </section>

        <section id="skincare">
            <h2><span class="emoji">🧴</span> Skincare Insights</h2>
            <ul>{skincare_list}</ul>
        </section>

        <section id="grooming">
            <h2><span class="emoji">💈</span> Grooming & Hair Insights</h2>
            <ul>{grooming_list}</ul>
        </section>

        <section id="attractiveness" class="{attractiveness_class}">
            <h2><span class="emoji">🌟</span> Attractiveness Analysis</h2>
            <div class="score-badge">Score: {attractive_score}/10</div>
            <p>{attractiveness_comment}</p>
        </section>

        <section id="good_features">
            <h2><span class="emoji">👍</span> Standout Features</h2>
            <ul>{good_features_list}</ul>
        </section>

        <section id="bad_features">
            <h2><span class="emoji">⚠️</span> Areas for Enhancement</h2>
            <ul>{bad_features_list}</ul>
        </section>

        <section id="neutral_features">
            <h2><span class="emoji">ℹ️</span> Additional Observations</h2>
            <ul>{neutral_features_list}</ul>
        </section>
        
        <div class="footer">
            <p>This report is generated using AI analysis and is for informational purposes only.</p>
        </div>
    </div>
</body>
</html>
"""

# ============================================================
# IMPROVED PROMPT TEMPLATES
# ============================================================

GEMINI_SUMMARY_PROMPT = """
You are a professional facial analysis expert. Your task is to create an engaging executive summary based on facial feature analysis data.

CONTEXT:
You will receive JSON data containing facial analysis results including:
- Demographic information (gender)
- Facial features (eyes, nose, lips, jawline, etc.)
- Hair characteristics
- Skin attributes
- Various probability scores for different facial features

YOUR TASK:
Write a comprehensive yet concise summary (80-120 words) that:
1. Describes the user's key demographic characteristics
2. Highlights the most prominent facial features detected
3. Mentions notable hair and skin characteristics
4. Uses warm, professional, and positive language
5. Avoids using raw percentages or probability numbers
6. Focuses on qualitative descriptions rather than quantitative data

STYLE GUIDELINES:
- Use engaging, natural language
- Be descriptive but professional
- Maintain a positive, constructive tone
- Write in complete sentences, not bullet points
- Make it sound like an expert's professional assessment

- You are giving feedback , reply to him in human language

## MOST IMPORTANT:
- Do NOT include raw data, percentages, or technical jargon
- Talk about features in a way that is easy to understand
- Don't use phrases like "The user has dark circle" instead use "You have signs of dark circles"
FACIAL ANALYSIS DATA:
{data_str}

Generate the summary now:
"""

GEMINI_CONTENT_PROMPT = """
You are an expert facial aesthetics and grooming consultant. You will analyze facial feature data and generate personalized insights.

CONTEXT:
You have two sources of information:
1. FACIAL ANALYSIS DATA: Contains probabilities and classifications for various facial features
2. FEATURE DESCRIPTIONS: Contains detailed explanations of what each feature means

YOUR TASK:
Generate content for different sections of a facial analysis report. You MUST return your response as a valid JSON object with this EXACT structure:

{{{{
  "skincare_list": ["insight 1", "insight 2", "insight 3"],
  "grooming_list": ["insight 1", "insight 2", "insight 3"],
  "attractiveness_comment": "detailed comment here or empty string",
  "positive_features_list": ["feature 1", "feature 2", "feature 3"],
  "features_to_improve_list": ["suggestion 1", "suggestion 2"],
  "other_observations_list": ["observation 1", "observation 2"]
}}}}

SECTION GUIDELINES:

1. skincare_list:
   - Analyze skin-related features (skin tone, texture, complexion)
   - Provide 2-4 specific skincare recommendations
   - Be constructive and actionable
   - Example: "Consider using a moisturizer with SPF to maintain healthy skin tone"

2. grooming_list:
   - Focus on hair, facial hair, eyebrows, and overall grooming
   - Provide 2-4 specific grooming suggestions
   - Be practical and achievable
   - Example: "A trim to clean up the eyebrow shape could enhance facial symmetry"

3. attractiveness_comment:
   - ONLY generate if the attractiveness probability is > 0.7
   - If probability ≤ 0.7, return an empty string ""
   - If generating, write 2-3 sentences highlighting what makes the person attractive
   - Be genuine, specific, and professional

4. positive_features_list:
   - List 3-5 strongest/most attractive facial features
   - Reference features with high probability scores
   - Be specific (e.g., "Well-defined jawline" not just "nice face")
   - Use positive, descriptive language

5. features_to_improve_list:
   - List 2-4 features that could be enhanced
   - Frame as opportunities, not criticisms
   - Provide actionable suggestions when possible
   - Be gentle and constructive

6. other_observations_list:
   - Include 2-3 neutral observations
   - Mention unique or distinctive features
   - Provide context or additional information
   - Keep it informative and interesting

CRITICAL RULES:
- Return ONLY valid JSON, no additional text
- Use proper JSON escaping for quotes within strings
- Each list item should be a complete sentence or phrase
- If a section has no content, use an empty list [] or empty string ""
- Do NOT include HTML tags or markdown in the content
- Be professional, empathetic, and constructive throughout
- Avoid overly technical jargon

FACIAL ANALYSIS DATA:
{json_data}

FEATURE DESCRIPTIONS:
{feature_descriptions}

Generate the JSON response now:
"""

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def load_json_file(json_path: str) -> Dict[str, Any]:
    """Loads a JSON file with comprehensive error handling."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Successfully loaded JSON from: {json_path}")
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {json_path}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading JSON file {json_path}: {str(e)}")

def clean_json_response(response_text: str) -> str:
    """Cleans Gemini response to extract valid JSON."""
    # Remove markdown code blocks if present
    response_text = response_text.strip()
    
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    return response_text.strip()

def _local_summary(data: Dict[str, Any]) -> str:
    # Construct a lightweight, human-friendly summary from available fields
    try:
        attrs = []
        getp = lambda k: data.get(k, {}).get("predicted") if isinstance(data.get(k), dict) else data.get(k)
        if getp("male") is True:
            attrs.append("male")
        elif getp("male") is False:
            attrs.append("female")
        if getp("attractive") is True:
            attrs.append("attractive features")
        if getp("sharp_jawline") is True:
            attrs.append("a defined jawline")
        if getp("high_cheekbones") is True:
            attrs.append("high cheekbones")
        if getp("big_eyes") is True:
            attrs.append("expressive eyes")
        if getp("sharp_nose") is True:
            attrs.append("a sharp nose")
        if getp("well_groomed") is True:
            attrs.append("well-groomed appearance")
        bits = ", ".join(attrs[:-1]) + (" and " + attrs[-1] if attrs else "")
        core = f"You appear {bits}." if bits else "Your image has been analyzed for key facial attributes."
        extras = []
        if getp("oily_skin") is True:
            extras.append("Consider oil-control skincare for balance.")
        if getp("curly_hair") is True:
            extras.append("Curl-enhancing care can improve definition.")
        tail = " ".join(extras)
        return (core + " " + tail).strip()
    except Exception:
        return "Your facial attributes have been analyzed and summarized."

def generate_summary(data: Dict[str, Any]) -> str:
    """Generates a short summary; uses Gemini if available, else local fallback."""
    if GEMINI_ENABLED and genai is not None:
        try:
            data_str = json.dumps(data, indent=2)
            prompt = GEMINI_SUMMARY_PROMPT.format(data_str=data_str)
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            summary = response.text.strip()
            print(f"✅ Generated summary ({len(summary)} characters)")
            return summary
        except Exception as e:
            print(f"⚠️ Warning: Gemini summary failed: {str(e)}; using local fallback")
    return _local_summary(data)

def _local_content(data: Dict[str, Any]) -> Dict[str, Any]:
    def pred(k):
        v = data.get(k)
        if isinstance(v, dict):
            return bool(v.get("predicted"))
        return bool(v)
    skincare = []
    grooming = []
    positives = []
    improve = []
    other = []
    if pred("oily_skin"):
        skincare.append("Use an oil-free cleanser and non-comedogenic moisturizer.")
    if pred("dark_circles"):
        skincare.append("Consider eye cream with caffeine and ensure proper sleep.")
    if pred("curly_hair"):
        grooming.append("Use sulfate-free shampoo and a curl-defining leave-in.")
    if pred("has_beard"):
        grooming.append("Apply beard oil and maintain regular trims for shape.")
    if pred("sharp_jawline"):
        positives.append("Well-defined jawline enhances facial structure.")
    if pred("big_eyes"):
        positives.append("Expressive eyes draw positive attention.")
    if pred("attractive"):
        positives.append("Overall attractive facial balance.")
    if pred("patchy_beard"):
        improve.append("Even growth can improve with regular grooming and patience.")
    if pred("receeding_hairline"):
        improve.append("Consult a specialist and consider volumizing hairstyles.")
    other.append("Recommendations are informational and not medical advice.")
    return {
        "skincare_list": skincare[:4] or ["Maintain a consistent, gentle skincare routine."],
        "grooming_list": grooming[:4] or ["Keep a regular grooming routine aligned with your hair type."],
        "attractiveness_comment": "",
        "positive_features_list": positives[:5] or ["Multiple strengths observed across features."],
        "features_to_improve_list": improve[:4] or ["No major areas of improvement identified."],
        "other_observations_list": other[:3]
    }

def generate_content(data: Dict[str, Any], feature_descriptions: Dict[str, Any]) -> Dict[str, Any]:
    """Generates content; uses Gemini if available, else a local rules-based fallback."""
    if GEMINI_ENABLED and genai is not None:
        try:
            prompt = GEMINI_CONTENT_PROMPT.format(
                json_data=json.dumps(data, indent=2),
                feature_descriptions=json.dumps(feature_descriptions, indent=2)
            )
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            raw_response = response.text.strip()
            print("📝 Raw Gemini response received")
            cleaned_response = clean_json_response(raw_response)
            content = json.loads(cleaned_response)
            required_keys = [
                "skincare_list", "grooming_list", "attractiveness_comment",
                "positive_features_list", "features_to_improve_list", "other_observations_list"
            ]
            for key in required_keys:
                if key not in content:
                    if key.endswith("_list"):
                        content[key] = []
                    else:
                        content[key] = ""
            print("✅ Content validation successful")
            return content
        except Exception as e:
            print(f"⚠️ Warning: Gemini content failed: {str(e)}; using local fallback")
    return _local_content(data)

def format_list_items(items: List[str]) -> str:
    """Formats a list of items into HTML <li> tags with validation."""
    if not items or len(items) == 0:
        return "<li>No specific recommendations at this time</li>"
    
    formatted_items = []
    for item in items:
        # Clean and validate each item
        cleaned_item = str(item).strip()
        if cleaned_item:
            formatted_items.append(f"<li>{cleaned_item}</li>")
    
    return "\n".join(formatted_items) if formatted_items else "<li>No specific recommendations at this time</li>"

def get_formatted_timestamp() -> str:
    """Returns current timestamp in a nice format."""
    return datetime.now().strftime("%B %d, %Y, %I:%M %p IST")

def generate_html_report(
    data: Dict[str, Any],
    summary: str,
    content: Dict[str, Any],
    image_path: str
) -> str:
    """Generates HTML report by injecting text into the enhanced template."""
    try:
        # Extract attractiveness data safely
        attractive_prob = data.get("attractive", {}).get("probability", 0)
        attractiveness_class = "hidden" if attractive_prob <= 0.7 else ""
        attractive_score = round(attractive_prob * 10, 2)
        attractiveness_comment = content.get("attractiveness_comment", "") if attractive_prob > 0.7 else ""
        
        # Generate timestamp
        timestamp = get_formatted_timestamp()
        
        # Generate HTML
        html_report = ENHANCED_HTML_TEMPLATE.format(
            timestamp=timestamp,
            image_path=image_path,
            summary_text=summary,
            skincare_list=format_list_items(content.get("skincare_list", [])),
            grooming_list=format_list_items(content.get("grooming_list", [])),
            attractiveness_class=attractiveness_class,
            attractive_score=attractive_score,
            attractiveness_comment=attractiveness_comment,
            good_features_list=format_list_items(content.get("positive_features_list", [])),
            bad_features_list=format_list_items(content.get("features_to_improve_list", [])),
            neutral_features_list=format_list_items(content.get("other_observations_list", []))
        )
        
        print("✅ HTML report generated successfully")
        return html_report
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate HTML report: {str(e)}")

# ============================================================
# MAIN EXECUTION FUNCTION
# ============================================================

def main(json_path: str, feature_json_path: str, image_path: str, output_html: str) -> None:
    """Main process to generate full HTML facial analysis report with comprehensive error handling."""
    print("\n" + "="*60)
    print("FACIAL ANALYSIS REPORT GENERATOR")
    print("="*60 + "\n")
    
    try:
        # Step 1: Configure Gemini
        print("Step 1: Configuring Gemini API...")
        configure_gemini()
        
        # Step 2: Load JSON files
        print("\nStep 2: Loading data files...")
        data = load_json_file(json_path)
        feature_descriptions = load_json_file(feature_json_path)
        
        # Step 3: Validate image path
        print("\nStep 3: Validating image path...")
        if not os.path.exists(image_path):
            print(f"⚠️ Warning: Image file not found at {image_path}")
            print("   HTML will be generated but image won't display")
        else:
            print(f"✅ Image found: {image_path}")
        
        # Step 4: Generate summary
        print("\nStep 4: Generating executive summary...")
        summary = generate_summary(data)
        
        # Step 5: Generate content
        print("\nStep 5: Generating detailed content sections...")
        content = generate_content(data, feature_descriptions)
        
        # Step 6: Generate HTML
        print("\nStep 6: Compiling HTML report...")
        html_report = generate_html_report(data, summary, content, image_path)
        
        # Step 7: Save file
        print("\nStep 7: Saving HTML file...")
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"\n📄 HTML report saved at:\n   {os.path.abspath(output_html)}")
        print(f"\n📊 Report Statistics:")
        print(f"   - Summary length: {len(summary)} characters")
        print(f"   - Skincare insights: {len(content.get('skincare_list', []))} items")
        print(f"   - Grooming tips: {len(content.get('grooming_list', []))} items")
        print(f"   - Positive features: {len(content.get('positive_features_list', []))} items")
        print("\n" + "="*60 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ FILE ERROR: {str(e)}")
        print("   Please check that all file paths are correct.")
    except ValueError as e:
        print(f"\n❌ DATA ERROR: {str(e)}")
        print("   Please check that your JSON files are properly formatted.")
    except RuntimeError as e:
        print(f"\n❌ PROCESSING ERROR: {str(e)}")
        print("   There was an error generating the report.")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        print("   An unexpected error occurred during processing.")

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    # File paths - UPDATE THESE TO MATCH YOUR SYSTEM
    json_path = "./example_predictions.json" # model output
    feature_json_path = "./attribute_mapping.json" # attribute_mapping
    image_path = "./Aamir_Khan_001.jpg"
    output_html = "./final_facial_report.html"
    
    main(json_path, feature_json_path, image_path, output_html)