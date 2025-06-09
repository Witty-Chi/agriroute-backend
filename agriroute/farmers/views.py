#from inference_sdk import InferenceHTTPClient
import random
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
#from plant_disease_model import SimpleCNN
from .model_utils import predict_disease
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
from .models import Farmer
from .serializers import FarmerSerializer
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from .models import Farmer
from .serializers import FarmerSerializer
from .models import TransportRequest
from .serializers import TransportRequestSerializer
from farmers.models import Farmer
import requests
from .models import FarmerProfile
from .serializers import FarmerProfileSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # or IsAuthenticated


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])  # Change to IsAuthenticated if using auth
def farmer_profile(request, farmer_id):
    try:
        profile = FarmerProfile.objects.get(id=farmer_id)
    except FarmerProfile.DoesNotExist:
        if request.method == 'GET':
            return Response({"detail": "Profile not found"}, status=404)
        if request.method == 'PUT':
            serializer = FarmerProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(id=farmer_id)
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

    if request.method == 'GET':
        serializer = FarmerProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FarmerProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

'''
@api_view(['GET', 'PUT'])
def farmer_profile(request, pk):
    try:
        farmer = FarmerProfile.objects.get(pk=pk)
    except FarmerProfile.DoesNotExist:
        return Response({"error": "Farmer not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FarmerProfileSerializer(farmer)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FarmerProfileSerializer(farmer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 '''   
OPENAI_API_KEY = "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"

# farmers/views.py (voice command endpoint)
@api_view(['POST'])
def voices_command(request):
    text = request.data.get("text", "").strip()
    if not text:
        return Response({"error": "No input provided"}, status=400)

    # 1. Generate English reply using OpenAI ChatGPT
    try:
        gpt_res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an agriculture assistant for Liberian farmers. Keep answers short and practical."},
                    {"role": "user", "content": text}
                ]
            }
        )
        english_reply = gpt_res.json()['choices'][0]['message']['content']
    except Exception as e:
        return Response({"error": f"Failed to generate reply: {str(e)}"}, status=500)

    # 2. Translate English reply to Koloqua (using GPT for now)
    try:
        translate_res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Translate the following English agriculture advice to Liberian Koloqua."},
                    {"role": "user", "content": english_reply}
                ]
            }
        )
        koloqua_reply = translate_res.json()['choices'][0]['message']['content']
    except Exception as e:
        koloqua_reply = "(Failed to translate to Koloqua)"

    return Response({
        "english": english_reply.strip(),
        "koloqua": koloqua_reply.strip()
    })

@api_view(['POST'])
def voice_command(request):
    text = request.data.get("text", "").strip()
    if not text:
        return Response({"error": "No input provided"}, status=400)

    try:
        # Step 1: Generate English response
        gpt_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an agriculture assistant for Liberian farmers. Keep answers short and practical."},
                    {"role": "user", "content": text}
                ]
            }
        )
        data = gpt_response.json()
        english_reply = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

        if not english_reply:
            return Response({"error": "Failed to generate reply."}, status=500)

    except Exception as e:
        return Response({"error": f"OpenAI error: {str(e)}"}, status=500)

    try:
        # Step 2: Translate to Koloqua using GPT
        trans_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Translate the following English agriculture advice to Liberian Koloqua."},
                    {"role": "user", "content": english_reply}
                ]
            }
        )
        trans_data = trans_response.json()
        koloqua_reply = trans_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

    except Exception as e:
        koloqua_reply = "(Translation failed)"

    return Response({
        "english": english_reply,
        "koloqua": koloqua_reply
    })



@api_view(['GET'])
def market_insights(request):
    location = request.GET.get('location', 'Harper')
    api_key = "d670f91d67604b8a11ddb96ffeb8f898"

    # OpenWeatherMap
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={location},LR&appid={api_key}&units=metric"
    weather_data = requests.get(weather_url).json()

    temp = weather_data.get("main", {}).get("temp")
    humidity = weather_data.get("main", {}).get("humidity")
    rain = weather_data.get("rain", {}).get("1h", 0)
    condition = weather_data.get("weather", [{}])[0].get("description", "N/A")

    weather_summary = {
        "temp": temp,
        "humidity": humidity,
        "rain": rain,
        "condition": condition,
        "advice": "Expect mild weather, good for outdoor farming." if rain < 5 else "Heavy rains expected. Delay planting or harvesting."
    }

    # Simulated market prices (replace with scraper/API later)
    market_summary = {
        "prices": [
            {"crop": "Maize", "price": 1.15},
            {"crop": "Cassava", "price": 0.75},
            {"crop": "Rice", "price": 1.40},
        ],
        "advice": "Maize prices rising—consider harvesting early."
    }

    # AI-style Recommendations
    recommendations = {
        "plant": "You can plant maize from today for the next 6 days. Soil moisture is adequate.",
        "harvest": "Rice should be harvested within the week to avoid spoilage from upcoming rains.",
        "store": "Keep cassava in dry sheds due to high humidity forecast.",
        "sell": "Sell maize within the next 3 days for best market prices.",
        "rainfall": "Rainfall is moderate; ensure proper drainage to prevent flooding."
    }

    return Response({
        "weather": weather_summary,
        "market": market_summary,
        "recommendations": recommendations
    })


@api_view(['POST'])
def create_transport_request(request):
    try:
        farmer_id = request.data.get('farmer_id')  # pass farmer_id in the request
        farmer = Farmer.objects.get(id=farmer_id)
        data = request.data
        data['farmer'] = farmer.id
        serializer = TransportRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Farmer.DoesNotExist:
        return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def farmer_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        farmer = Farmer.objects.get(username=username)
        if check_password(password, farmer.password):
            return Response({
                'success': True,
                'id': farmer.id,
                'name': farmer.name,
                'location': farmer.location
            })
        else:
            return Response({'success': False, 'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    except Farmer.DoesNotExist:
        return Response({'success': False, 'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def farmer_register(request):
    try:
        print("Incoming data:", request.data)  # DEBUG LOG

        data = request.data.copy()
        data['password'] = make_password(data['password'])

        serializer = FarmerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        print("Validation failed:", serializer.errors)  # DEBUG LOG
        return Response(serializer.errors, status=400)
    except Exception as e:
        print("🚨 Registration error:", e)  # THIS IS WHAT WE NEED
        return Response({'error': str(e)}, status=500)
    
@api_view(['PATCH'])
def update_farmer(request, pk):
    try:
        farmer = Farmer.objects.get(pk=pk)
    except Farmer.DoesNotExist:
        return Response({'error': 'Farmer not found'}, status=404)

    serializer = FarmerSerializer(farmer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def detect_disease(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image is required.'}, status=status.HTTP_400_BAD_REQUEST)

    predictions = predict_disease(image)
    request.session['diagnosis_result'] = predictions
    return Response({"predictions": predictions}, status=status.HTTP_200_OK)

'''@api_view(['POST'])
@parser_classes([MultiPartParser])
def detect_disease(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Send image to Roboflow cloud model
        response = requests.post(
            "https://detect.roboflow.com/plant-disease-classifier/4",
            params={"api_key": "wNPAAjxL4UGPFeCWbB5y"},
            files={"file": image}
            )


        data = response.json()
        predictions = []

        for pred in data.get("predictions", [])[:3]:
            predictions.append({
                "name": pred.get("class", "Unknown"),
                "confidence": round(pred.get("confidence", 0) * 100, 2),
                "cause": f"Likely caused by typical conditions for {pred.get('class', 'this disease')}",
                "treatment": f"Standard treatment for {pred.get('class', 'this disease')}"
            })

        if not predictions:
            return Response({"predictions": []})

        request.session['diagnosis_result'] = predictions
        return Response({"predictions": predictions})
    

    except Exception as e:
            import traceback
            traceback.print_exc()  # 👈 Add this to print full stack trace in console
            return Response({"error": str(e)}, status=500)


 


'''

@csrf_exempt
@api_view(['POST'])
def download_diagnosis_pdf(request):
    predictions = request.data.get('predictions')
    if not predictions:
        return Response({ "error": "No predictions supplied." }, status=400)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "AgriRoute AI - Crop Disease Diagnosis Report")
    y -= 40

    p.setFont("Helvetica", 12)
    for i, d in enumerate(predictions):
        p.drawString(50, y, f"{i+1}. {d['name']} ({d['confidence']}%)")
        y -= 20
        p.drawString(70, y, f"Cause: {d['cause']}")
        y -= 20
        p.drawString(70, y, f"Treatment: {d['treatment']}")
        y -= 40

    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="crop_diagnosis_report.pdf")



