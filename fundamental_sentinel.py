import urllib.request
import xml.etree.ElementTree as ET
import json
import sys

CRITICAL_ALERT_KEYWORDS = [
    'hack', 'hacked', 'exploit', 'scam', 'lawsuit', 'sec', 'ban', 
    'banned', 'crackdown', 'crash', 'investigation', 'arrest', 'stolen'
]

def get_fear_and_greed_index():
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            val = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            return {"score": val, "sentiment": classification}
    except Exception as e:
        return {"score": 50, "sentiment": "Neutral (Fallback)"}

def fetch_live_crypto_news():
    headlines = []
    high_risk_alerts = []
    try:
        url = "https://cointelegraph.com/rss"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item')[:10]:
                title = item.find('title').text if item.find('title') is not None else ""
                headlines.append(title)
                title_lower = title.lower()
                for kw in CRITICAL_ALERT_KEYWORDS:
                    import re
                    if re.search(rf'\b{kw}\b', title_lower):
                        high_risk_alerts.append({"keyword": kw, "headline": title})
    except Exception as e:
        headlines.append(f"News Feed Notice: {e}")
    
    return headlines, high_risk_alerts

def get_crypto_fundamental_sentinel(symbol="BTCUSDT"):
    fng = get_fear_and_greed_index()
    headlines, risk_alerts = fetch_live_crypto_news()
    
    macro_risk = "LOW_RISK"
    if len(risk_alerts) >= 3 or fng['score'] <= 20:
        macro_risk = "HIGH_RISK"
    elif len(risk_alerts) >= 1:
        macro_risk = "MEDIUM_RISK"

    return {
        "symbol": symbol.upper(),
        "fear_and_greed": fng,
        "sentiment_label": fng['sentiment'],
        "macro_risk_level": macro_risk,
        "recent_headlines": headlines[:5],
        "risk_alerts_detected": risk_alerts
    }

def analyze_fundamental_catalysts(symbol="BTCUSDT"):
    return get_crypto_fundamental_sentinel(symbol)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'BTCUSDT'
    report = get_crypto_fundamental_sentinel(symbol)
    print(json.dumps(report, indent=2, ensure_ascii=False))
