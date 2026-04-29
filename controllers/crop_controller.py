# controllers/crop_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.prediction import Prediction
from extensions.db import db
from services.ml_service import get_detector
import os
from datetime import datetime
import uuid

crop_bp = Blueprint('crop', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


# ==================== RICE DISEASE INFO DATABASE ====================
def get_disease_info(disease_name):
    """
    Get detailed information about rice diseases:
    - Brown Spot
    - Bacterial Blight
    - Leaf Blast
    """
    
    disease_database = {
        # ========== RICE BROWN SPOT ==========
        "Rice_brown_spot": {
            "name": "Rice Brown Spot (तांदूळ तपकिरी डाग)",
            "description": "Brown spot is a fungal disease caused by **Cochliobolus miyabeanus**. It causes 30-40% yield loss if not managed properly.",
            "causes": "• **Fungal Pathogen:** Helminthosporium oryzae\n• **Soil Conditions:** Nutrient-deficient soils (low potassium, magnesium)\n• **Weather:** High humidity (>85%) and warm temperatures (25-30°C)\n• **Cultural Practices:** Continuous rice cropping",
            "symptoms": "• **Leaf Spots:** Oval or circular brown spots with gray centers\n• **Halo Effect:** Spots surrounded by yellow halo\n• **Grain Infection:** Dark brown to black spots on grains\n• **Reduced Yield:** Grains become lightweight",
            "organic_solution": "🌱 **ORGANIC TREATMENTS:**\n\n• **Neem Oil Spray:** 5ml neem oil + 1ml soap in 1L water\n• **Compost Tea:** Steep 1kg compost in 10L water, filter and spray\n• **Trichoderma:** Apply 2.5kg/ha with FYM\n• **Pseudomonas:** Foliar spray of 10g/L at 10-day intervals",
            "chemical_solution": "🧪 **CHEMICAL TREATMENTS:**\n\n• **Mancozeb (75% WP):** 2g/L water\n• **Propiconazole (25% EC):** 1ml/L water\n• **Carbendazim (50% WP):** 1g/L water",
            "prevention": "🛡️ **PREVENTION:**\n\n• **Resistant Varieties:** CR Dhan 307\n• **Balanced Nutrition:** Apply potash (40kg/acre)\n• **Seed Treatment:** Carbendazim (2g/kg seed)\n• **Field Sanitation:** Remove infected debris",
            "treatment_plan": "📋 **8-10 DAY TREATMENT PLAN:**\n\n📅 **DAY 1-2:** Survey field, remove infected plants\n📅 **DAY 3-4:** Apply neem oil spray (organic)\n📅 **DAY 5-6:** Monitor new lesion development\n📅 **DAY 7-8:** Apply Mancozeb if needed\n📅 **DAY 9-10:** Final inspection",
            "fertilizer_recommendations": {
                "organic": "• Vermicompost: 5kg/plant\n• Neem Cake: 500g/plant\n• FYM: 3kg/plant",
                "chemical": "• NPK 20:20:20: 2g/L\n• Urea: 50kg/acre\n• Potash: 40kg/acre",
                "bio_fertilizer": "• Trichoderma: 2kg/ha\n• Pseudomonas: 1kg/ha\n• Azotobacter: 500g/acre"
            }
        },
        
        # ========== RICE BACTERIAL BLIGHT ==========
        "Rice_bacterial_blight": {
            "name": "Rice Bacterial Blight (तांदूळ जीवाणूजन्य रोग)",
            "description": "Bacterial blight is caused by **Xanthomonas oryzae**. Can cause yield loss up to 50-70%.",
            "causes": "• **Bacterial Pathogen:** Xanthomonas oryzae\n• **Weather:** High humidity (>85%), rain, wind\n• **Cultural Factors:** Excess nitrogen, continuous flooding",
            "symptoms": "• **Leaf Blight:** Water-soaked lesions from leaf tips\n• **Wilting:** Leaves roll and turn yellow-gray\n• **Bacterial Ooze:** Yellowish exudate on lesions\n• **Kresek Phase:** Complete wilting of young plants",
            "organic_solution": "🌱 **ORGANIC TREATMENTS:**\n\n• **Copper Oxychloride:** 30g in 10L water\n• **Neem Oil + Garlic:** 5ml + 10 cloves in 1L water\n• **Cow Dung Solution:** 1kg in 10L water, ferment 3 days\n• **Pseudomonas:** Apply 10g/L as foliar spray",
            "chemical_solution": "🧪 **CHEMICAL TREATMENTS:**\n\n• **Streptocycline:** 200mg + Copper Oxychloride 3g/L\n• **Plantomycin:** 1g/L water\n• **Copper Oxychloride:** 3g/L water",
            "prevention": "🛡️ **PREVENTION:**\n\n• **Resistant Varieties:** IRBB lines\n• **Seed Treatment:** Soak in Streptocycline (1g/10L)\n• **Water Management:** Avoid continuous flooding\n• **Reduce Nitrogen:** Split application",
            "treatment_plan": "📋 **8-10 DAY TREATMENT PLAN:**\n\n📅 **DAY 1-2:** Inspect fields, look for water-soaked lesions\n📅 **DAY 3-4:** Remove infected plants, improve drainage\n📅 **DAY 5-6:** Apply Streptocycline + Copper spray\n📅 **DAY 7-8:** Monitor, apply potash fertilizer\n📅 **DAY 9-10:** Final assessment",
            "fertilizer_recommendations": {
                "organic": "• Vermicompost: 4kg/plant\n• Neem Cake: 400g/plant\n• FYM: 2kg/plant",
                "chemical": "• NPK 15:15:15: 3g/L\n• Urea: 30kg/acre (REDUCE)\n• Potash: 50kg/acre (INCREASE)",
                "bio_fertilizer": "• Pseudomonas: 2kg/ha\n• Bacillus subtilis: 1kg/ha\n• Azotobacter: 500g/acre"
            }
        },
        
        # ========== RICE LEAF BLAST ==========
        "Rice_leaf_blast": {
            "name": "Rice Leaf Blast (तांदूळ पाने करपा)",
            "description": "Rice blast is caused by **Magnaporthe oryzae**. Most devastating rice disease, can cause 100% yield loss.",
            "causes": "• **Fungal Pathogen:** Magnaporthe oryzae\n• **Weather:** High humidity (90-100%), 25-28°C\n• **Nitrogen:** Excessive nitrogen increases susceptibility",
            "symptoms": "• **Leaf Lesions:** Diamond/boat-shaped spots with gray center\n• **Node Blast:** Dark lesions on nodes, stem breakage\n• **Panicle Blast:** White empty grains",
            "organic_solution": "🌱 **ORGANIC TREATMENTS:**\n\n• **Neem Oil + Salt:** 5ml + 2g in 1L water\n• **Trichoderma:** 2.5kg/ha as seed treatment\n• **Pseudomonas:** 10g/L foliar spray\n• **Baking Soda:** 1g + 1ml oil in 1L water",
            "chemical_solution": "🧪 **CHEMICAL TREATMENTS:**\n\n• **Tricyclazole (75% WP):** 0.6g/L water\n• **Carbendazim (50% WP):** 1g/L water\n• **Edifenphos (50% EC):** 1ml/L water",
            "prevention": "🛡️ **PREVENTION:**\n\n• **Resistant Varieties:** Tetep, IR64\n• **Seed Treatment:** Carbendazim (2g/kg) or hot water (52°C/15min)\n• **Balanced Nutrition:** Avoid excess nitrogen\n• **Wider Spacing:** Improves air circulation",
            "treatment_plan": "📋 **8-10 DAY TREATMENT PLAN:**\n\n📅 **DAY 1-2:** Scout field for diamond-shaped lesions\n📅 **DAY 3-4:** Apply Tricyclazole or Carbendazim\n📅 **DAY 5-6:** Apply potash fertilizer (15kg/acre)\n📅 **DAY 7-8:** Monitor new lesions, reapply if needed\n📅 **DAY 9-10:** Final check",
            "fertilizer_recommendations": {
                "organic": "• Vermicompost: 5kg/plant\n• Neem Cake: 600g/plant\n• FYM: 3kg/plant",
                "chemical": "• NPK 20:20:20: 2g/L\n• Urea: 40kg/acre (REDUCE)\n• Potash: 45kg/acre (INCREASE)",
                "bio_fertilizer": "• Trichoderma: 2.5kg/ha\n• Pseudomonas: 2kg/ha\n• Azotobacter: 500g/acre"
            }
        }
    }
    
    # Default info if disease not found
    default_info = {
        "name": disease_name.replace("_", " ").title(),
        "description": "Consult with local agricultural experts for accurate diagnosis.",
        "causes": "• Consult local agricultural extension office",
        "symptoms": "• Visible symptoms on leaves\n• May affect crop yield",
        "organic_solution": "• Remove affected plant parts\n• Improve air circulation\n• Apply neem oil spray",
        "chemical_solution": "• Consult with agricultural expert\n• Use recommended fungicides",
        "prevention": "• Practice crop rotation\n• Use disease-resistant varieties",
        "treatment_plan": "📅 **Consult local agricultural expert for treatment plan**",
        "fertilizer_recommendations": {
            "organic": "• Vermicompost: 3-5kg/plant\n• Neem Cake: 300-500g/plant",
            "chemical": "• NPK 20:20:20: 2g/L\n• Urea: 40-50kg/acre",
            "bio_fertilizer": "• Trichoderma: 2kg/ha\n• Pseudomonas: 1kg/ha"
        }
    }
    
    return disease_database.get(disease_name, default_info)


@crop_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

    if request.method == "POST":

        if 'file' not in request.files:
            flash("❌ No file selected", "danger")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("❌ No file selected", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):

            try:

                original_filename = secure_filename(file.filename)
                ext = original_filename.rsplit('.', 1)[1].lower()

                unique_filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"

                filepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    unique_filename
                )

                file.save(filepath)

                flash("✅ Image uploaded! Analyzing...", "info")

                detector = get_detector()

                if detector and detector.model:

                    result = detector.predict(filepath)

                    if result:
                        # ✅ CRITICAL: Only accept if disease is NOT Healthy
                        # We ONLY want diseased leaves, NOT healthy ones!
                        
                        # Check if prediction is valid
                        if not result.get('is_valid', True):
                            error_message = result.get('message', 'Invalid image')
                            flash(f"❌ {error_message}", "danger")
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            return redirect(url_for('crop.upload'))
                        
                        # ✅ REJECT if the model says "Healthy"
                        # We ONLY want diseased leaves!
                        if result["disease"] == "Healthy":
                            flash("❌ This appears to be a HEALTHY leaf. Please upload a photo of a DISEASED leaf showing clear symptoms (spots, lesions, discoloration).", "warning")
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            return redirect(url_for('crop.upload'))
                        
                        # ✅ REJECT if confidence is suspiciously high for disease
                        # Real diseased leaves rarely have >95% confidence
                        if result["confidence"] > 0.95:
                            flash("⚠️ Unusual confidence level. Please upload a clearer photo of the affected crop leaf.", "warning")
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            return redirect(url_for('crop.upload'))
                        
                        # Handle uncertain prediction
                        if result.get('disease') in ['Uncertain', 'Ambiguous', 'Invalid']:
                            flash(result.get('message', 'Please upload a clearer photo'), "warning")
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            return redirect(url_for('crop.upload'))
                        
                        # ✅ Check confidence threshold
                        if result["confidence"] < 0.65:
                            flash(f"⚠️ Low confidence ({result['confidence']*100:.1f}%). Please upload a clearer photo of the disease symptoms.", "warning")
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            return redirect(url_for('crop.upload'))

                        disease_info = get_disease_info(result["disease"])

                        # Save prediction - ONLY for diseased leaves
                        prediction = Prediction(
                            user_id=current_user.id,
                            image_path=f"uploads/{unique_filename}",
                            disease_name=result["disease"],
                            confidence=result["confidence"],
                            created_at=datetime.utcnow()
                        )

                        db.session.add(prediction)
                        db.session.commit()

                        flash(
                            f"✅ Disease detected: {disease_info['name']}",
                            "success"
                        )

                        return render_template(
                            "crop/result.html",
                            result=result,
                            disease_info=disease_info,
                            prediction=prediction,
                            confidence_percent=round(result["confidence"] * 100, 2)
                        )

                    else:
                        flash("❌ Error processing image", "danger")

                else:
                    flash("❌ AI model not loaded", "danger")

            except Exception as e:
                flash("❌ Error while processing image", "danger")
                print("Upload error:", e)
                
            # Clean up on error
            if os.path.exists(filepath):
                os.remove(filepath)

        else:
            flash("❌ Invalid file type (PNG/JPG only)", "danger")

        return redirect(request.url)

    recent_predictions = Prediction.get_user_predictions(
        current_user.id,
        limit=5
    )

    return render_template(
        "crop/upload.html",
        recent_predictions=recent_predictions
    )


@crop_bp.route("/history")
@login_required
def history():

    page = request.args.get("page", 1, type=int)

    predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Prediction.created_at.desc()
    ).paginate(page=page, per_page=10)

    return render_template(
        "crop/history.html",
        predictions=predictions
    )


@crop_bp.route("/prediction/<int:prediction_id>")
@login_required
def view_prediction(prediction_id):

    prediction = Prediction.query.get_or_404(prediction_id)

    if prediction.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("crop.history"))

    disease_info = get_disease_info(prediction.disease_name)

    return render_template(
        "crop/view_prediction.html",
        prediction=prediction,
        disease_info=disease_info,
        confidence_percent=round(prediction.confidence * 100, 2)
    )


@crop_bp.route("/delete/<int:prediction_id>", methods=["POST"])
@login_required
def delete_prediction(prediction_id):

    prediction = Prediction.query.get_or_404(prediction_id)

    if prediction.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("crop.history"))

    try:

        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            os.path.basename(prediction.image_path)
        )

        if os.path.exists(image_path):
            os.remove(image_path)

        db.session.delete(prediction)
        db.session.commit()

        flash("✅ Prediction deleted", "success")

    except Exception as e:

        db.session.rollback()
        flash("❌ Error deleting prediction", "danger")
        print(e)

    return redirect(url_for("crop.history"))