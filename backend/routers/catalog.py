from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import random
import os
import json
import google.generativeai as genai

try:
    from ..database import get_db
    from .. import models, schemas
except (ImportError, ValueError):
    from database import get_db
    import models, schemas

# Setup Gemini SDK from environment variables
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

router = APIRouter(
    prefix="/api/catalog",
    tags=["catalog"]
)

# Request schema that allows testing via voice_text_fallback
class CustomVoiceCatalogRequest(BaseModel):
    audio_base64: Optional[str] = None
    voice_text_fallback: Optional[str] = None
    language: str
    artisan_id: int

# We'll use predefined templates to make the mock AI engine return highly accurate, 
# smart, and realistic translations if actual API keys are not configured.
VERNACULAR_TEMPLATES = {
    "hindi": [
        {
            "trigger_keywords": ["मिट्टी", "घड़ा", "मटका", "कुल्हड़", "clay", "pot"],
            "title": "Handcrafted Terracotta Clay Water Pot (Mittika Ghada)",
            "description": "An eco-friendly, traditional clay water pot handcrafted by rural artisans using natural riverbed clay. Perfect for naturally cooling water during summers, chemical-free, and bio-degradable.",
            "category": "Handcrafted Pottery & Earthenware",
            "hsn_code": "69120010",
            "suggested_price": 250.0
        },
        {
            "trigger_keywords": ["टोकरी", "बांस", "लकड़ी", "basket", "bamboo"],
            "title": "Premium Hand-Woven Bamboo Storage Basket",
            "description": "Hand-woven utility basket made from organic, locally-sourced bamboo split fibers. Durable, multi-purpose, and ideal for home organization, fruit storage, or gift packaging.",
            "category": "Bamboo & Cane Crafts",
            "hsn_code": "46021100",
            "suggested_price": 380.0
        },
        {
            "trigger_keywords": ["मूर्ती", "पीतल", "धातु", "statue", "brass", "idol"],
            "title": "Traditional Hand-Cast Brass Ganesha Idol",
            "description": "A magnificent hand-cast brass Ganesha idol, crafted using the lost-wax casting technique. Features detailed traditional engravings, suitable for home decor, worship, and gifting.",
            "category": "Metal Art & Brassware",
            "hsn_code": "83062920",
            "suggested_price": 1250.0
        }
    ],
    "tamil": [
        {
            "trigger_keywords": ["செம்பு", "பாத்திரம்", "copper", "vessel"],
            "title": "Traditional Hand-Hammered Copper Water Bottle",
            "description": "Hand-hammered pure copper water flask crafted by traditional coppersmiths. Consuming water from copper storage vessels offers ancient Ayurvedic health benefits.",
            "category": "Traditional Copper Utensils",
            "hsn_code": "74181024",
            "suggested_price": 850.0
        }
    ]
}

DEFAULT_RESPONSE = {
    "title": "Artisanal Handmade Craft Item",
    "description": "A beautiful craft item handmade with care by local artisans using traditional heritage techniques and sustainable materials.",
    "category": "Handicrafts & Heritage Crafts",
    "hsn_code": "97030000",
    "suggested_price": 450.0
}

@router.post("/voice", response_model=schemas.VoiceCatalogResponse)
def process_voice_cataloging(request: CustomVoiceCatalogRequest, db: Session = Depends(get_db)):
    # 1. Verify if the artisan exists
    artisan = db.query(models.Artisan).filter(models.Artisan.id == request.artisan_id).first()
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan profile not found")

    # 2. Get the transcript
    input_text = request.voice_text_fallback or ""
    if request.audio_base64 and not input_text:
        # In a real app, send audio to Whisper/Bhashini API
        if request.language.lower() == "hindi":
            input_text = "मैंने अपने हाथों से मिट्टी का मटका बनाया है, प्राकृतिक लाल मिट्टी का उपयोग किया है।"
        elif request.language.lower() == "tamil":
            input_text = "கைவினை செம்பு பாத்திரம் தண்ணீர் சேமிக்க சிறந்தது."
        else:
            input_text = "Handmade traditional craft made with natural raw materials."

    # 3. Direct Live Gemini API Call (If API Key is configured in environment)
    if api_key:
        try:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                generation_config={"response_mime_type": "application/json"}
            )
            prompt = f"""
            You are the cataloging engine for Karigar Connect, a mobile app for rural Indian artisans.
            Analyze the following description of a handmade product:
            "{input_text}"
            
            The artisan's native language is: {request.language}.
            
            Generate the following fields in JSON format matching this Pydantic schema:
            {{
              "title": "A highly professional, attractive English title for the product listing",
              "description": "An appealing, SEO-friendly marketing description in English",
              "category": "Identify the standard Indian handicraft category (e.g. Pottery, Bamboo Crafts, Metal Art, Textiles)",
              "hsn_code": "The most appropriate 8-digit HSN/Tax code for this category in India (e.g. 69120010 for clay pots, 46021100 for bamboo baskets, 83062920 for brass)",
              "suggested_price": a suggested retail price in INR (float) based on the product description
            }}
            
            Provide only raw JSON.
            """
            response = model.generate_content(prompt)
            result_json = json.loads(response.text.strip())
            
            return schemas.VoiceCatalogResponse(
                transcription=input_text,
                translated_text=f"Original transcription: '{input_text}' (Translated & cataloged via Google Gemini 1.5 Flash)",
                title=result_json.get("title", DEFAULT_RESPONSE["title"]),
                description=result_json.get("description", DEFAULT_RESPONSE["description"]),
                category=result_json.get("category", DEFAULT_RESPONSE["category"]),
                hsn_code=str(result_json.get("hsn_code", DEFAULT_RESPONSE["hsn_code"])),
                suggested_price=float(result_json.get("suggested_price", DEFAULT_RESPONSE["suggested_price"]))
            )
        except Exception as e:
            # Fallback to local templates if live API call fails
            print(f"Gemini API Error, falling back to local templates: {e}")
            pass

    # 4. Fallback: Match against template keywords (Smart Mock AI)
    matched_template = None
    lang = request.language.lower()
    
    # Try searching the specific language templates
    templates = VERNACULAR_TEMPLATES.get(lang, VERNACULAR_TEMPLATES["hindi"])
    for temp in templates:
        for keyword in temp["trigger_keywords"]:
            if keyword in input_text.lower():
                matched_template = temp
                break
        if matched_template:
            break

    # If no match found, fallback to default template
    if not matched_template:
        matched_template = DEFAULT_RESPONSE

    # Synthesize transcription & translation text
    transcription = input_text
    translated_text = transcription
    if lang != "english":
        translated_text = f"Transcription: '{transcription}' translated to English: '{matched_template['title']} created using traditional methods.'"

    return schemas.VoiceCatalogResponse(
        transcription=transcription,
        translated_text=translated_text,
        title=matched_template["title"],
        description=matched_template["description"],
        category=matched_template["category"],
        hsn_code=matched_template["hsn_code"],
        suggested_price=matched_template["suggested_price"]
    )


@router.post("/enhance-image", response_model=schemas.ImageEnhanceResponse)
def enhance_product_image(request: schemas.ImageEnhanceRequest):
    # Mocking background removal and generative AI placement
    # We substitute a cluttered mockup image with a beautiful studio rendering based on theme
    original = request.original_image_url
    
    # Pre-compiled high quality authentic handicraft background renders
    theme_backgrounds = {
        "studio": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Blue_pottery_from_Jaipur_2.jpg/800px-Blue_pottery_from_Jaipur_2.jpg", # Handcrafted Jaipur Blue Pottery
        "wooden_table": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Earthen_Pot_for_Drinking_Water.JPG", # Terracotta Clay Water Pot (Mittika Ghada)
        "festival_lights": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Four-armed_Ganesha_-_Brass_-_Circa_20th_Century_CE_-_Madhya_Pradesh_-_ACCN_2000-53_-_Indian_Museum_-_Kolkata_2015-09-26_3997.JPG/800px-Four-armed_Ganesha_-_Brass_-_Circa_20th_Century_CE_-_Madhya_Pradesh_-_ACCN_2000-53_-_Indian_Museum_-_Kolkata_2015-09-26_3997.JPG" # Traditional Hand-Cast Brass Ganesha
    }
    
    enhanced = theme_backgrounds.get(request.theme.lower(), theme_backgrounds["studio"])
    
    return schemas.ImageEnhanceResponse(
        original_image_url=original,
        enhanced_image_url=enhanced
    )


@router.post("/products", response_model=schemas.ProductResponse)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Verify artisan exists
    artisan = db.query(models.Artisan).filter(models.Artisan.id == product_in.artisan_id).first()
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan not found")

    db_product = models.Product(**product_in.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products", response_model=List[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.get("/products/artisan/{artisan_id}", response_model=List[schemas.ProductResponse])
def get_artisan_products(artisan_id: int, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.artisan_id == artisan_id).all()


@router.post("/products/{product_id}/publish-ondc", response_model=schemas.ProductResponse)
def publish_to_ondc(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Simulate publication to ONDC network
    db_product.status = "Listed_ONDC"
    
    # We trigger a mock entry in local logistics pooling if the pincode is eligible
    artisan = db_product.artisan
    if artisan and artisan.pin_code:
        # Check if active pool exists for the pincode
        pool = db.query(models.LogisticsPool).filter(
            models.LogisticsPool.pincode == artisan.pin_code,
            models.LogisticsPool.status == "Collecting"
        ).first()
        
        if not pool:
            # Create new pool
            pool = models.LogisticsPool(
                village_name=artisan.state + " Village Cluster",
                pincode=artisan.pin_code,
                total_weight=1.5,  # Estimated weight
                orders_count=1
            )
            db.add(pool)
        else:
            pool.total_weight += 1.5
            pool.orders_count += 1
            
    db.commit()
    db.refresh(db_product)
    return db_product
