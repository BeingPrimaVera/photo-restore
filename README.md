---
title: "AI Photo Restoration & Colorization Space"
tasks:
  - image-to-image
  - computer-vision
  - image-classification
emoji: 📸
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🤖 AI Photo Restoration & Colorization Space
[![Deploy to Hugging Face Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg)](https://huggingface.co/spaces/your-username/your-space-name)

Restore and colorize your old photos with cutting-edge AI technology. **100 % free to try**, pay only when you love the result!

## ✨ Features
- 🔍 **Face Restoration** - Enhance and restore faces using GFPGAN  
- 🎨 **Photo Colorization** - Add vibrant colors to black & white photos with DeOldify  
- ⚡ **Fast Processing** - Results in seconds, not minutes  
- 💰 **Pay What You Love** - Free preview, HD download for just $0.99  
- 🔒 **Privacy First** - Your photos are processed locally, not stored permanently  
- 📱 **Easy to Use** - Simple drag-and-drop interface  

## 🚀 Quick Start
### Deploy to Hugging Face Spaces
1. Click the "Deploy to Hugging Face Spaces" button above  
2. Choose your space name and set visibility to "Public"  
3. Click "Create Space"  
4. Your app will be live in 2-3 minutes!  

### Local Development
```bash
git clone https://huggingface.co/spaces/your-username/your-space-name
cd your-space-name
pip install -r requirements.txt
python app.py
```

## 📖 Usage

### Web Interface

1. Upload your old photo (JPG/PNG)
2. Select options:
   - ✅ Restore faces
   - ✅ Colorize photo
3. Click "Restore Photo"
4. View free preview (with watermark)
5. Download HD version for $0.99 (no watermark)

### REST API

The space also provides a developer-friendly REST API:

```bash
# Upload and restore photo
curl -X POST "https://your-space-name.hf.space/restore" \
  -F "file=@old_photo.jpg" \
  -F "restore_face=true" \
  -F "colorize=true"
```

**API Response:**
```json
{
  "success": true,
  "restored_image": "base64_encoded_image",
  "restored_url": "/outputs/result_hash.png",
  "message": "Image restored successfully"
}
```

### Python Client

```python
import requests
import base64
from PIL import Image
import io

# Upload and restore
with open("old_photo.jpg", "rb") as f:
    files = {"file": f}
    data = {"restore_face": True, "colorize": True}
    response = requests.post("https://your-space-name.hf.space/restore", files=files, data=data)

# Decode and save result
result = response.json()
if result["success"]:
    image_data = base64.b64decode(result["restored_image"])
    image = Image.open(io.BytesIO(image_data))
    image.save("restored_photo.png")
```

## 🎯 Pricing

| Feature | Price | Description |
|---------|-------|-------------|
| **Free Preview** | $0 | 600px preview with watermark |
| **HD Download** | **$0.99** | 1200px high-quality, no watermark |
| **Tip the Robot** | $0.49 | Optional coffee tip for the developer |

> 💡 **Launch Special**: $4.99 → $0.99 (Limited Time Offer!)

## 🛠️ Technical Details

### Models Used

- **[GFPGAN v1.4](https://github.com/TencentARC/GFPGAN)** - Face restoration
- **[DeOldify](https://github.com/jantic/DeOldify)** - Photo colorization

### System Requirements

- **CPU**: 2 vCPU minimum
- **RAM**: 4GB maximum (optimized for HF Spaces CPU-basic tier)
- **Storage**: <5GB model files
- **OS**: Linux/Windows/macOS

### Performance Optimizations

- ✅ CPU-optimized inference
- ✅ 24-hour result caching
- ✅ Lazy model loading
- ✅ Memory-efficient processing
- ✅ Automatic cache cleanup

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Custom Stripe payment link
STRIPE_PAYMENT_URL="https://buy.stripe.com/your-link"

# Optional: Custom Ko-fi tip link
KOFI_URL="https://ko-fi.com/yourname"
```

### Model Files

Models are automatically downloaded on first use:
- GFPGAN model: ~350MB
- DeOldify model: ~200MB

## 📱 Social Sharing

Share your restored photos easily:

- **Twitter**: "I restored my grandparents' photo in 5 seconds – for less than a dollar!"
- **Facebook**: Share your before/after results
- **Reddit**: Show off your restored family photos

## 🔒 Privacy & Security

- ✅ No photo storage - images are processed locally
- ✅ 24-hour cache only - results auto-delete
- ✅ No user tracking or analytics
- ✅ Open-source models and code

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [TencentARC](https://github.com/TencentARC) for GFPGAN
- [jantic](https://github.com/jantic/DeOldify) for DeOldify
- [Hugging Face](https://huggingface.co) for the Spaces platform

## 📞 Support

Having issues? Open an issue on this repository or reach out through:
- GitHub Issues
- Hugging Face Discussions

---

**Made with ❤️ using open-source AI models**  
*☕ [Tip the robot - 49¢](https://ko-fi.com/yourname)*