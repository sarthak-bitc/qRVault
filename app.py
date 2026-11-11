from flask import Flask, request, render_template_string
import qrcode
import io
import base64

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Universal QR Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; text-align: center; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        textarea { width: 90%; height: 150px; padding: 10px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; }
        button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #0056b3; }
        .qr-section { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Python Universal QR Code Generator</h2>
        <p>Convert links, plain text, or programming code snippets into a QR code</p>
        
        <!-- Javascript safely packages the code block before sending it to Python -->
        <form method="POST" action="/" onsubmit="prepareData()">
            <textarea id="raw_data" placeholder="Paste your link, text, or programming code here..." required></textarea>
            <input type="hidden" name="user_data" id="safe_data">
            <br>
            <button type="submit">Generate QR Code</button>
        </form>

        {% if qr_img %}
        <div class="qr-section">
            <h3>Scannable QR Code Result:</h3>
            <img src="data:image/png;base64,{{ qr_img }}" width="260" alt="Generated QR Code">
        </div>
        {% endif %}
    </div>

    <script>
        function prepareData() {
            var rawText = document.getElementById("raw_data").value;
            // Safely encode special characters using Base64 so Python doesn't break
            var safeText = btoa(unescape(encodeURIComponent(rawText)));
            document.getElementById("safe_data").value = safeText;
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_b64 = None
    
    if request.method == 'POST':
        safe_string = request.form.get('user_data')
        
        try:
            decoded_bytes = base64.b64decode(safe_string)
            raw_input = decoded_bytes.decode('utf-8')
            
            qr = qrcode.QRCode(
                version=None, 
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4
            )
            qr.add_data(raw_input)
            qr.make(fit=True)
            
            # 4. Turn it into a PNG image image
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            
    return render_template_string(HTML_TEMPLATE, qr_img=qr_b64)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)