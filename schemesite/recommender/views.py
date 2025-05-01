from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import SchemeRequest
import json
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import mysql.connector


import os
from dotenv import load_dotenv



def dashboard(request):
    my_requests = SchemeRequest.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'recommender/dashboard.html', {'requests': my_requests})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('dashboard'))  # 🔁 Redirect to dashboard
    else:
        form = UserCreationForm()
    return render(request, 'recommender/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(reverse('dashboard'))  # 🔁 Redirect to dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'recommender/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import mysql.connector
import openai
import os
import json
from dotenv import load_dotenv

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import mysql.connector
import openai
import os
import json
from dotenv import load_dotenv

def all_schemes(request):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="student@172005",
            database="schemes"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schemes")
        schemes = cursor.fetchall()

        # Extract unique values
        ministries = sorted(set(s['ministry'] for s in schemes if s['ministry']))
        sectors = sorted(set(s['sector'] for s in schemes if s['sector']))
        years = sorted(set(str(s['launch_year']) for s in schemes if s['launch_year']))
        cs_types = sorted(set(s['cs_css'] for s in schemes if s['cs_css']))

        return render(request, 'recommender/all_schemes.html', {
            'schemes': schemes,
            'ministries': ministries,
            'sectors': sectors,
            'years': years,
            'cs_types': cs_types,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


import joblib
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def predict_scheme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            age = int(data.get("age"))
            income = int(data.get("income"))
            occupation = data.get("occupation").lower()

            # Load model and encoder
            base_dir = os.path.dirname(__file__)
            model = joblib.load(os.path.join(base_dir, 'model/scheme_model.pkl'))
            encoder = joblib.load(os.path.join(base_dir, 'model/occupation_encoder.pkl'))

            # Encode occupation
            occupation_encoded = encoder.transform([occupation])[0]

            # Prepare input
            X_test = [[age, age, income, income, occupation_encoded]]

            # Predict
            prediction = model.predict(X_test)

            return JsonResponse({"recommended_scheme": prediction[0]})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST method allowed"}, status=400)


def recommend_scheme_page(request):
    return render(request, 'scheme_recommender.html')

import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

genai.configure(api_key='AIzaSyAUxT_edNP0f7uYWXf9uiNghmAq9_Z2b3k')  # Replace with settings.GEMINI_API_KEY if using from settings

@csrf_exempt
def summarize_filtered_schemes(request):
    if request.method == 'POST':
        ministry = request.POST.get('ministry', '')
        sector = request.POST.get('sector', '')
        year = request.POST.get('year', '')
        cs_css = request.POST.get('cs_css', '')

        # Example: Fetching filtered schemes from your database
        from .models import Scheme
        schemes = Scheme.objects.all()
        if ministry:
            schemes = schemes.filter(ministry=ministry)
        if sector:
            schemes = schemes.filter(sector=sector)
        if year:
            schemes = schemes.filter(launch_year=year)
        if cs_css:
            schemes = schemes.filter(cs_css=cs_css)

        if not schemes.exists():
            return JsonResponse({'summary': 'No summaries available for selected filters.'})

        # Prepare input for Gemini
        prompt = "\n\n".join([f"{s.name}: {s.summary}" for s in schemes])
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"Summarize the following government schemes with:\n- Overview\n- Key Benefits\n- Eligibility Criteria\n- Application Process\n\nSchemes:\n{prompt}")

        return JsonResponse({'summary': response.text})
    return JsonResponse({'summary': 'Invalid request method.'})
def chatbot_view(request):
    return render(request, 'recommender/chatbot.html')

#video guide
def video_guides(request):
    # Example dummy data; replace with DB data
    schemes = [
  {
    "name": "PM-Kisan",
    "description": "Pradhan Mantri Kisan Samman Nidhi provides income support of ₹6,000 per year to eligible farmer families. The amount is paid in three equal installments directly into their bank accounts.",

    "youtube_id": "eaD5iRiTh94"
  },
  {
    "name": "Startup India",
    "description": "An initiative to build a strong ecosystem for nurturing innovation and startups. Offers tax exemptions, funding support, and simplified regulations to empower entrepreneurs across India.",
    "youtube_id": "fCz2x-NFK10"
  },
  {
    "name": "Stand-Up India",
    "description": "Aims to facilitate bank loans between ₹10 lakh to ₹1 crore to SC/ST and women entrepreneurs. Supports the establishment of greenfield enterprises to promote inclusive growth.",
    "youtube_id": "2xSKmOfT_xE"
  },
  {
    "name": "Ayushman Bharat",
    "description": "A flagship health scheme providing free health coverage of up to ₹5 lakh per family per year. Benefiting economically weaker sections for hospitalization in empanelled public and private hospitals.",
    "youtube_id": "mfdVJebmQyI"
  },
  {
    "name": "PM Awas Yojana",
    "description": "Targets “Housing for All” by 2022 through financial assistance and interest subsidies. Supports the construction or enhancement of homes for urban and rural poor.",
    "youtube_id": "APYfAaMIrgM"
  },
  {
    "name": "Digital India",
    "description": "Transforms India into a digitally empowered society and knowledge economy. Focuses on digital infrastructure, digital literacy, and delivery of government services electronically.",
    "youtube_id": "3_0TFahK3GE"
  },
  {
    "name": "Beti Bachao Beti Padhao",
    "description": "Promotes the education and empowerment of the girl child. Addresses declining child sex ratio and aims to change societal attitudes toward girls.",
    "youtube_id": "aL9cO-nPtPU"
  },
  {
    "name": "UDAN Scheme",
    "description": "Ude Desh Ka Aam Nagrik (UDAN) makes air travel affordable for the common man. Boosts regional connectivity by developing underserved airports across the country.",
    "youtube_id": "jvWWdMKUvFo"
  },
  {
    "name": "Skill India",
    "description": "Empowers youth with industry-relevant skills to improve employability. Includes training programs across sectors under the National Skill Development Mission.",
    "youtube_id": "7wz3aJkIK_0"
  },
  {
    "name": "PMEGP",
    "description": "Prime Minister’s Employment Generation Programme offers subsidies for setting up micro-enterprises. Supports self-employment for unemployed youth and traditional artisans.",
    "youtube_id": "4YoMWhqAhZI"
  },
  {
    "name": "National Pension Scheme",
    "description": "A voluntary retirement savings scheme regulated by PFRDA. Allows individuals to invest during their working years and receive pension benefits post-retirement.",
    "youtube_id": "SuPzIf0xU8Q"
  },
  {
    "name": "Sukanya Samriddhi Yojana",
    "description": "A savings scheme for the girl child with high interest rates and tax benefits. Encourages long-term savings for education and marriage expenses.",
    "youtube_id": "3R3uL90ekyc"
  },
  {
    "name": "Jan Dhan Yojana",
    "description": "Promotes financial inclusion by offering zero-balance bank accounts with benefits like direct benefit transfer, insurance, and pension schemes.",
    "youtube_id": "HhrFuyAYiV4"
  },
  {
    "name": "Ujjwala Yojana",
    "description": "Provides free LPG connections to women from BPL households. Aims to reduce health risks from indoor air pollution and promote clean cooking fuel.",
    "youtube_id": "a2jaG1Qcv6s"
  },
  {
    "name": "Swachh Bharat Mission",
    "description": "A cleanliness drive launched to eliminate open defecation and improve solid waste management. Encourages building toilets and promoting hygiene practices.",
    "youtube_id": "0--ZRm2HT28"
  },
  {
    "name": "Atal Pension Yojana",
    "description": "Targets unorganized sector workers with a guaranteed pension scheme. Offers a fixed monthly pension post-retirement depending on contribution.",
    "youtube_id": "9Uz_9vmeTC8"
  },
  {
    "name": "Make in India",
    "description": "Encourages manufacturing in India to boost economic growth and create jobs. Attracts foreign and domestic investment in key industrial sectors.",
    "youtube_id": "6YZR3REzvA8"
  },
  {
    "name": "Mission Shakti",
    "description": "An umbrella scheme for women’s safety, security, and empowerment. Integrates initiatives like One-Stop Centres, women helplines, and shelter homes.",
    "youtube_id": "NYlqxYk07qE"
  }
]

    return render(request, "recommender/video_guides.html", {"schemes": schemes})
# views.py


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import openai
from dotenv import load_dotenv
from .models import SchemeHistory

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt
def chatgpt_scheme_recommender(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            age = data.get("age")
            occupation = data.get("occupation")
            income = data.get("income")
            category = data.get("category")
            stage = data.get("stage", "initial")
            selected_scheme = data.get("selected_scheme", "")

            if stage == "initial":
                prompt = f"""
You are an AI assistant that helps users find relevant Indian government schemes.

User details:
- Age: {age}
- Occupation: {occupation}
- Annual Income: ₹{income}
- Category: {category}

List 3 to 5 schemes the user may be eligible for:
• [Scheme Name] - [One-line description]
                """
            else:
                prompt = f"""
Provide detailed info about this Indian government scheme: '{selected_scheme}'.
Include:
• Step-by-step application guide
• Required documents
• Deadlines
• Contact info
• YouTube search recommendation
                """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert assistant for government schemes in India."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )

            reply = response.choices[0].message.content.strip()

            if stage == "initial":
                SchemeHistory.objects.create(
                    age=age,
                    occupation=occupation,
                    income=income,
                    category=category,
                    recommended_schemes=reply
                )

            return JsonResponse({"schemes": reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=400)
