# -*- coding: utf-8 -*-

import os
import shutil
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import logging

# === Flask অ্যাপ ইনিশিয়ালাইজেশন ===
# একটি Flask অ্যাপ অবজেক্ট তৈরি করা হচ্ছে।
app = Flask(__name__)

# === CORS (Cross-Origin Resource Sharing) কনফিগারেশন ===
# আমাদের ফ্রন্টএন্ড (যা অন্য ডোমেইনে হোস্ট করা) থেকে API কল করার অনুমতি দেওয়ার জন্য CORS ব্যবহার করা হচ্ছে।
CORS(app)

# === ফোল্ডারের পাথ কনফিগারেশন ===
# আমাদের প্রজেক্টের বিভিন্ন ফোল্ডারের পাথ এখানে ভেরিয়েবলে রাখা হচ্ছে।
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_FOLDER = os.path.join(BASE_DIR, 'builds')
TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'webview_template')

# === লগিং কনফিগারেশন ===
# সার্ভারে কী ঘটছে তা দেখার জন্য লগিং সেটআপ করা হচ্ছে।
logging.basicConfig(level=logging.INFO)

# === APK জেনারেট করার জন্য মূল API রুট ===
@app.route('/generate_apk', methods=['POST'])
def generate_apk():
    """
    এই ফাংশনটি ফ্রন্টএন্ড থেকে POST রিকোয়েস্ট গ্রহণ করে,
    ডেটা প্রসেস করে এবং একটি APK ফাইল ফেরত পাঠায়।
    """
    
    # --- ধাপ ১: রিকোয়েস্ট থেকে ডেটা এবং ফাইল গ্রহণ ---
    try:
        website_url = request.form['website_url']
        app_name = request.form['app_name']
        
        if 'logo' not in request.files:
            return jsonify({"error": "No logo file provided"}), 400
            
        logo_file = request.files['logo']

        # অ্যাপের নাম থেকে স্পেস সরিয়ে আন্ডারস্কোর দেওয়া হচ্ছে, যা ফাইলের নাম হিসেবে নিরাপদ।
        safe_app_name = "".join(x if x.isalnum() else "_" for x in app_name)

        logging.info(f"Received request for App: {app_name}, URL: {website_url}")

    except KeyError as e:
        logging.error(f"Missing form data: {e}")
        return jsonify({"error": f"Missing required field: {e}"}), 400

    # --- ধাপ ২: অস্থায়ী ফোল্ডার তৈরি এবং লোগো সেভ করা ---
    # প্রতি রিকোয়েস্টের জন্য একটি ইউনিক অস্থায়ী ফোল্ডার তৈরি করা হচ্ছে।
    session_temp_folder = os.path.join(TEMP_FOLDER, safe_app_name)
    session_build_folder = os.path.join(BUILD_FOLDER, safe_app_name)
    
    # পুরোনো ফাইল থাকলে সেগুলো মুছে ফেলা হচ্ছে।
    if os.path.exists(session_temp_folder):
        shutil.rmtree(session_temp_folder)
    if os.path.exists(session_build_folder):
        shutil.rmtree(session_build_folder)
        
    os.makedirs(session_temp_folder, exist_ok=True)
    os.makedirs(session_build_folder, exist_ok=True)
    
    logo_path = os.path.join(session_temp_folder, logo_file.filename)
    logo_file.save(logo_path)
    logging.info(f"Logo saved to {logo_path}")

    # --- ধাপ ৩: APK বিল্ড প্রসেস (সিমুলেশন) ---
    try:
        # ******************** বাস্তব প্রজেক্টের জন্য গুরুত্বপূর্ণ নোট ********************
        # এখানে আসল APK বিল্ড করার জটিল কোডগুলো থাকবে। প্রক্রিয়াটি সাধারণত এমন হয়:
        # ১. একটি অ্যান্ড্রয়েড ওয়েবভিউ অ্যাপের সোর্স কোড টেমপ্লেট আনজিপ করা।
        # ২. টেমপ্লেটের কনফিগারেশন ফাইলে (e.g., strings.xml or a config file) website_url এবং app_name বসানো।
        # ৩. টেমপ্লেটের res/drawable ফোল্ডারে আপলোড করা লোগোটি কপি করে বসানো।
        # ৪. Gradle বা অন্য কোনো বিল্ড টুল ব্যবহার করে পুরো প্রজেক্টটি বিল্ড করে APK তৈরি করা।
        # এই কাজটি অনেক সময়সাপেক্ষ এবং সার্ভারে Android SDK ও Gradle ইনস্টল থাকা প্রয়োজন।
        # **************************************************************************

        # --- সিমুলেশন শুরু ---
        # আমরা webview_template ফোল্ডার থেকে sample.apk ফাইলটি কপি করে builds ফোল্ডারে রাখব।
        apk_filename = f"{safe_app_name}.apk"
        source_apk_path = os.path.join(TEMPLATE_FOLDER, 'sample.apk')
        destination_apk_path = os.path.join(session_build_folder, apk_filename)
        
        shutil.copy(source_apk_path, destination_apk_path)
        logging.info(f"SIMULATION: Copied sample APK to {destination_apk_path}")
        # --- সিমুলেশন শেষ ---

        # --- ধাপ ৪: তৈরি হওয়া APK ফাইলটি ইউজারকে পাঠানো ---
        logging.info(f"Sending APK file: {apk_filename}")
        return send_from_directory(
            directory=session_build_folder,
            path=apk_filename,
            as_attachment=True # এটি ব্রাউজারকে ফাইলটি ডাউনলোড করতে বলবে।
        )

    except Exception as e:
        logging.error(f"An error occurred during APK generation: {e}")
        return jsonify({"error": "Failed to generate APK. Please try again."}), 500
        
    finally:
        # --- ধাপ ৫: অস্থায়ী ফাইল এবং ফোল্ডার পরিষ্কার করা ---
        # APK পাঠানো হয়ে গেলে বা কোনো এরর হলে, সার্ভারকে পরিষ্কার রাখার জন্য অস্থায়ী ফাইলগুলো মুছে ফেলা হবে।
        try:
            shutil.rmtree(session_temp_folder)
            shutil.rmtree(session_build_folder)
            logging.info(f"Cleaned up temp folders for {safe_app_name}")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

# === অ্যাপটি চালানোর জন্য এন্ট্রি পয়েন্ট ===
if __name__ == '__main__':
    # ডেভেলপমেন্টের সময় সরাসরি এই ফাইলটি চালালে অ্যাপটি লোকালহোস্টে রান হবে।
    app.run(debug=True, port=5001)

