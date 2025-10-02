#!/usr/bin/env python3
"""
AI Photo Restoration & Colorization Space
Hugging Face Spaces - CPU Optimized Version
Supports both Gradio UI and REST API
"""

import os
import io
import base64
import hashlib
import time
import asyncio
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Gradio imports
import gradio as gr
import PIL.Image as Image
import numpy as np

# ML imports
import torch
import cv2
from gfpgan import GFPGANer
from deoldify import device
from deoldify.device_id import DeviceId
from deoldify.visualize import get_image_colorizer

# Configure device for CPU-only operation
device.set(device=DeviceId.CPU)

# Global variables for models and cache
restorer = None
colorizer = None
result_cache = {}
CACHE_DURATION = 24 * 3600  # 24 hours in seconds

# Paths
MODEL_DIR = Path("./models")
OUTPUT_DIR = Path("./outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Stripe configuration (user needs to insert their own links)
STRIPE_PAYMENT_URL = "https://buy.stripe.com/9B6dR93I63dm45E3GzeQM00"
KOFI_URL = "https://ko-fi.com/primavera70043"

def get_image_hash(image: Image.Image) -> str:
    """Generate hash for image caching"""
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    return hashlib.md5(img_bytes.getvalue()).hexdigest()

def clean_cache():
    """Remove expired cache entries"""
    current_time = time.time()
    keys_to_remove = []
    for key, (timestamp, _) in result_cache.items():
        if current_time - timestamp > CACHE_DURATION:
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del result_cache[key]

def load_models():
    """Load GFPGAN and DeOldify models (CPU optimized)"""
    global restorer, colorizer
    
    if restorer is None:
        print("Loading GFPGAN model...")
        # Use GFPGAN v1.4 for better CPU performance
        restorer = GFPGANer(
            model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth',
            upscale=2,
            arch='clean',
            channel=2,
            bg_upsampler=None  # Disable background upsampler for CPU
        )
    
    if colorizer is None:
        print("Loading DeOldify model...")
        # Initialize DeOldify colorizer
        colorizer = get_image_colorizer(artistic=True)
    
    print("Models loaded successfully!")

def apply_watermark(image: Image.Image, opacity: float = 0.3) -> Image.Image:
    """Apply subtle watermark to free preview"""
    # Create watermark text
    watermark_text = "PREVIEW"
    
    # Convert to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create overlay for watermark
    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    
    # Try to use a default font, fallback to basic if not available
    try:
        from PIL import ImageDraw, ImageFont
        # Use a larger font size for better visibility
        font_size = max(20, min(image.size) // 15)
        font = ImageFont.load_default() if not hasattr(ImageFont, 'truetype') else ImageFont.load_default()
        draw = ImageDraw.Draw(overlay)
        
        # Calculate position (bottom right)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = image.width - text_width - 20
        y = image.height - text_height - 20
        
        # Draw watermark with opacity
        draw.text((x, y), watermark_text, fill=(255, 255, 255, int(255 * opacity)), font=font)
    except:
        # Fallback: simple white rectangle in bottom right
        x = image.width - 80
        y = image.height - 30
        overlay.paste((255, 255, 255, int(255 * opacity)), [x, y, x+80, y+30])
    
    # Composite watermark onto image
    watermarked = Image.alpha_composite(image, overlay)
    return watermarked.convert('RGB')

def resize_for_preview(image: Image.Image, max_size: int = 600) -> Image.Image:
    """Resize image for free preview"""
    width, height = image.size
    if max(width, height) > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image

def restore_and_colorize(image: Image.Image, restore_face: bool = True, colorize: bool = True) -> Tuple[Image.Image, str]:
    """Main restoration and colorization function"""
    clean_cache()
    
    # Check cache first
    image_hash = get_image_hash(image)
    cache_key = f"{image_hash}_{restore_face}_{colorize}"
    
    if cache_key in result_cache:
        _, cached_result = result_cache[cache_key]
        result_path = OUTPUT_DIR / f"result_{image_hash}.png"
        if result_path.exists():
            return Image.open(result_path), str(result_path)
    
    # Load models if not already loaded
    load_models()
    
    # Convert PIL to OpenCV format
    cv_image = np.array(image)
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    
    # Step 1: Face Restoration with GFPGAN
    if restore_face:
        print("Restoring faces...")
        _, _, restored_img = restorer.enhance(cv_image, has_aligned=False, only_center_face=False, paste_back=True)
        cv_image = restored_img
    
    # Step 2: Colorization with DeOldify
    if colorize:
        print("Colorizing image...")
        # Convert back to PIL for DeOldify
        pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        
        # Colorize the image
        colorized_pil = colorizer.get_transformed_image(pil_image, render_factor=35)
        
        # Convert back to OpenCV format
        cv_image = np.array(colorized_pil)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    
    # Convert final result back to PIL
    final_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
    
    # Save result
    result_path = OUTPUT_DIR / f"result_{image_hash}.png"
    final_image.save(result_path, quality=95)
    
    # Cache the result
    result_cache[cache_key] = (time.time(), str(result_path))
    
    return final_image, str(result_path)

# FastAPI app initialization
app = FastAPI(title="AI Photo Restoration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/restore")
async def restore_endpoint(
    file: UploadFile = File(...),
    restore_face: bool = Form(True),
    colorize: bool = Form(True)
):
    """REST API endpoint for photo restoration"""
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Process image
        result_image, result_path = restore_and_colorize(image, restore_face, colorize)
        
        # Convert result to base64
        buffer = io.BytesIO()
        result_image.save(buffer, format="PNG")
        result_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return JSONResponse({
            "success": True,
            "restored_image": result_base64,
            "restored_url": f"/outputs/{Path(result_path).name}",
            "message": "Image restored successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": restorer is not None and colorizer is not None}

# Gradio interface
def gradio_restore(image, restore_face=True, colorize=True):
    """Gradio interface function"""
    if image is None:
        return None, "Please upload an image"
    
    try:
        # Process image
        result_image, result_path = restore_and_colorize(image, restore_face, colorize)
        
        # Create preview version (watermarked, smaller)
        preview_image = resize_for_preview(result_image.copy())
        preview_image = apply_watermark(preview_image)
        
        return preview_image, result_path
        
    except Exception as e:
        return None, f"Error: {str(e)}"

# Create Gradio interface
iface = gr.Interface(
    fn=gradio_restore,
    inputs=[
        gr.Image(type="pil", label="Upload your old photo"),
        gr.Checkbox(label="Restore faces", value=True),
        gr.Checkbox(label="Colorize photo", value=True)
    ],
    outputs=[
        gr.Image(type="pil", label="Restored Preview (with watermark)"),
        gr.File(label="Download HD Version")
    ],
    title="AI Photo Restoration & Colorization",
    description="Restore and colorize your old photos with AI. Free preview available, HD download for $0.99.",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    .download-section {
        text-align: center;
        margin: 2rem 0;
        padding: 1rem;
        background: #f0f9ff;
        border-radius: 8px;
    }
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: #059669;
        margin: 1rem 0;
    }
    .original-price {
        text-decoration: line-through;
        color: #6b7280;
        font-size: 1.2rem;
    }
    .special-badge {
        background: #fbbf24;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
    }
    .share-buttons {
        margin-top: 2rem;
        text-align: center;
    }
    .share-button {
        display: inline-block;
        margin: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: #3b82f6;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 600;
    }
    .share-button:hover {
        background: #2563eb;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #e5e7eb;
        color: #6b7280;
    }
    """,
    allow_flagging="never"
)

# Custom HTML for enhanced UI
def create_enhanced_interface():
    with gr.Blocks(theme=gr.themes.Soft(), css=iface.css) as demo:
        gr.HTML("""
        <head>
            <title>Free AI Photo Restoration & Colorizer Online | 99¢ HD Download</title>
            <meta name="description" content="Restore and colorize old photos in seconds. No sign-up. Pay only when you love the result.">
            <meta property="og:title" content="Free AI Photo Restoration & Colorizer Online">
            <meta property="og:description" content="Restore and colorize old photos in seconds. No sign-up. Pay only when you love the result.">
            <meta property="og:image" content="https://huggingface.co/spaces/your-space/resolve/main/sample-before-after.png">
            <meta property="og:type" content="website">
        </head>
        """)
        
        gr.Markdown("# 📸 AI Photo Restoration & Colorization")
        gr.Markdown("### Restore and colorize your old photos with cutting-edge AI technology")
        
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(type="pil", label="Upload your old photo")
                restore_face = gr.Checkbox(label="Restore faces", value=True)
                colorize = gr.Checkbox(label="Colorize photo", value=True)
                process_btn = gr.Button("🎨 Restore Photo", variant="primary")
            
            with gr.Column():
                preview_output = gr.Image(type="pil", label="Restored Preview (with watermark)")
                download_file = gr.File(label="HD Version (no watermark)")
        
        # Enhanced download section with pricing psychology
        gr.HTML("""
        <div class="download-section">
            <div class="price-tag">
                <span class="original-price">$4.99</span> 
                <span style="color: #dc2626;">→ $0.99</span>
                <span class="special-badge">Launch Special</span>
            </div>
            <p style="margin: 1rem 0; color: #6b7280;">Get the full HD version without watermark</p>
            <a href=""" + STRIPE_PAYMENT_URL + """" target="_blank" style="
                display: inline-block;
                background: #059669;
                color: white;
                padding: 1rem 2rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.1rem;
                margin: 0.5rem;
            " onmouseover="this.style.background='#047857'" onmouseout="this.style.background='#059669'">
                💳 Download HD (No Watermark) - $0.99
            </a>
            <p style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">
                Launch price - limited time only!
            </p>
        </div>
        """)
        
        # Share buttons
        share_text = "I restored my grandparents' photo in 5 seconds – for less than a dollar!"
        share_url = "https://huggingface.co/spaces/your-space/your-app"
        
        gr.HTML(f"""
        <div class="share-buttons">
            <h3 style="margin-bottom: 1rem;">Share your experience!</h3>
            <a href="https://twitter.com/intent/tweet?text={share_text}&url={share_url}" target="_blank" class="share-button" style="background: #1da1f2;">
                🐦 Twitter
            </a>
            <a href="https://www.facebook.com/sharer/sharer.php?u={share_url}&quote={share_text}" target="_blank" class="share-button" style="background: #1877f2;">
                📘 Facebook
            </a>
            <a href="https://www.reddit.com/submit?url={share_url}&title={share_text}" target="_blank" class="share-button" style="background: #ff4500;">
                🔴 Reddit
            </a>
        </div>
        """)
        
        # Footer with Ko-fi link
        gr.HTML(f"""
        <div class="footer">
            <p>Made with ❤️ using open-source AI models</p>
            <p>
                <a href="{KOFI_URL}" target="_blank" style="color: #059669; text-decoration: none;">
                    ☕ Tip the robot - 49¢
                </a>
            </p>
            <p style="font-size: 0.75rem; margin-top: 1rem;">
                Your photos are processed locally and not stored permanently. Results are cached for 24 hours for performance.
            </p>
        </div>
        """)
        
        # Event handlers
        process_btn.click(
            fn=gradio_restore,
            inputs=[input_image, restore_face, colorize],
            outputs=[preview_output, download_file]
        )
    
    return demo

# Mount Gradio app to FastAPI
app = gr.mount_gradio_app(app, create_enhanced_interface(), path="/")

if __name__ == "__main__":
    # Pre-load models on startup
    print("Initializing AI Photo Restoration Space...")
    load_models()
    print("Starting server...")
    
    # Run the combined app
    uvicorn.run(app, host="0.0.0.0", port=7860)