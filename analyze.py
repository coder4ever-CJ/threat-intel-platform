from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read the incoming message data from your web dashboard
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        user_text = data.get('text', '')

        # 2. Grab your Gemini API key securely from Vercel's environment settings
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"result": "Error: GEMINI_API_KEY is missing on the cloud server."}).encode('utf-8'))
            return

        # 3. Formulate the mission instructions for Gemini
        system_instruction = (
            "You are an expert Threat Intelligence Analyst tracking the cybercriminal group 'ShinyHunters'. "
            "Analyze the provided dark web log data and extract critical artifacts. Specifically search for: "
            "IP addresses, cryptocurrency wallets, user aliases, and leaked database names. "
            "Organize your findings cleanly in a Markdown table with clear explanations for each artifact."
        )

        # 4. Set up the payload packet to send to Google AI Studio
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_instruction}\n\nInput Data:\n{user_text}"}]
            }]
        }

        # 5. Securely send the packet to Google over the web
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                # Extract the text reply back out of the Gemini response structure
                ai_reply = res_data['candidates'][0]['content']['parts'][0]['text']
                output_message = ai_reply
        except Exception as e:
            output_message = f"Cloud Link Error: Failed to communicate with AI Studio. Details: {str(e)}"

        # 6. Send the final parsed data back to your dashboard screen
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"result": output_message}).encode('utf-8'))
        return