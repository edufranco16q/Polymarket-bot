import requests
import time
from datetime import datetime
import json

# ========== CONFIGURACIÓN ==========

TELEGRAM_TOKEN = “8212339584:AAEKE_wkah0zcurPNjXGCHwJQ0AMvyY7eGs”
CHAT_ID = “2052717453”

# Parámetros de alertas

MIN_WHALE_AMOUNT = 30000  # $30k mínimo
MIN_CONSECUTIVE_WINS = 5   # 5 predicciones exitosas seguidas
MULTIPLE_BETS_THRESHOLD = 5  # 5+ apuestas simultáneas
CHECK_INTERVAL = 300  # 5 minutos (en segundos)

# Billeteras a monitorear

WALLETS_TO_MONITOR = [
“0xdb27bf2ac5d428a9c63dbc914611036855a6c56e”,
“0x63ce342161250d705dc0b16df89036c8e5f9ba9a”,
“0x16b29c50f2439faf627209b2ac0c7bbddaa8a881”,
“0x204f72f35326db932158cba6adff0b9a1da95e14”,
]

# Categorías de interés

CATEGORIES = [“football”, “nba”, “crypto”]
LEAGUES = [“premier-league”, “saudi-pro-league”]

# ========== FUNCIONES DE TELEGRAM ==========

def send_telegram_message(message):
“”“Envía mensaje a Telegram”””
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {
“chat_id”: CHAT_ID,
“text”: message,
“parse_mode”: “HTML”
}
try:
response = requests.post(url, json=payload)
return response.json()
except Exception as e:
print(f”Error enviando mensaje: {e}”)
return None

# ========== FUNCIONES DE POLYMARKET API ==========

def get_markets():
“”“Obtiene mercados activos de Polymarket”””
try:
url = “https://clob.polymarket.com/markets”
response = requests.get(url, timeout=10)
if response.status_code == 200:
return response.json()
return []
except Exception as e:
print(f”Error obteniendo mercados: {e}”)
return []

def get_market_trades(market_id):
“”“Obtiene trades de un mercado específico”””
try:
url = f”https://clob.polymarket.com/trades?market={market_id}”
response = requests.get(url, timeout=10)
if response.status_code == 200:
return response.json()
return []
except Exception as e:
print(f”Error obteniendo trades: {e}”)
return []

def get_wallet_activity(wallet_address):
“”“Obtiene actividad de una billetera específica”””
try:
# Endpoint para obtener órdenes de una billetera
url = f”https://clob.polymarket.com/orders?address={wallet_address}”
response = requests.get(url, timeout=10)
if response.status_code == 200:
return response.json()
return []
except Exception as e:
print(f”Error obteniendo actividad de billetera: {e}”)
return []

# ========== FUNCIONES DE ANÁLISIS ==========

def is_whale_bet(trade):
“”“Detecta si es una apuesta de ballena”””
try:
amount = float(trade.get(‘size’, 0)) * float(trade.get(‘price’, 0))
return amount >= MIN_WHALE_AMOUNT
except:
return False

def filter_markets_by_category(markets):
“”“Filtra mercados por categorías de interés”””
filtered = []
for market in markets:
market_data = market if isinstance(market, dict) else {}
tags = market_data.get(‘tags’, [])
question = market_data.get(‘question’, ‘’).lower()

```
    # Verifica si es fútbol, NBA o crypto
    is_relevant = False
    
    if any(tag.lower() in ['football', 'soccer', 'nba', 'basketball', 'crypto', 'cryptocurrency'] for tag in tags):
        is_relevant = True
    
    if any(keyword in question for keyword in ['premier league', 'saudi pro league', 'nba', 'bitcoin', 'ethereum']):
        is_relevant = True
        
    if is_relevant:
        filtered.append(market)

return filtered
```

def analyze_wallet_patterns(wallet_address):
“”“Analiza patrones de una billetera”””
activity = get_wallet_activity(wallet_address)

```
if not activity:
    return None

# Analiza predicciones simultáneas
recent_bets = [bet for bet in activity if isinstance(bet, dict)]
simultaneous_bets = len(recent_bets)

analysis = {
    'wallet': wallet_address,
    'simultaneous_bets': simultaneous_bets,
    'is_active': simultaneous_bets >= MULTIPLE_BETS_THRESHOLD,
    'recent_activity': recent_bets[:5]  # Últimas 5 apuestas
}

return analysis
```

def format_alert_message(alert_type, data):
“”“Formatea el mensaje de alerta”””
timestamp = datetime.now().strftime(”%Y-%m-%d %H:%M:%S”)

```
if alert_type == "whale":
    message = f"""
```

🐋 <b>ALERTA DE BALLENA</b> 🐋

💰 Monto: ${data.get(‘amount’, 0):,.2f}
📊 Mercado: {data.get(‘market_name’, ‘N/A’)}
👛 Billetera: {data.get(‘wallet’, ‘N/A’)[:10]}…
📈 Posición: {data.get(‘side’, ‘N/A’)}
⏰ {timestamp}

🔗 Ver en Polymarket
“””

```
elif alert_type == "multiple_bets":
    message = f"""
```

🎯 <b>MÚLTIPLES APUESTAS DETECTADAS</b> 🎯

👛 Billetera: {data.get(‘wallet’, ‘N/A’)[:10]}…
🔢 Apuestas simultáneas: {data.get(‘count’, 0)}
📂 Categoría: {data.get(‘category’, ‘N/A’)}
⏰ {timestamp}

Posible insider o estrategia activa
“””

```
elif alert_type == "insider":
    message = f"""
```

🔥 <b>POSIBLE INSIDER</b> 🔥

👛 Billetera: {data.get(‘wallet’, ‘N/A’)[:10]}…
✅ Racha: {data.get(‘streak’, 0)} predicciones exitosas
💵 Volumen total: ${data.get(‘volume’, 0):,.2f}
⏰ {timestamp}

¡Billetera con patrón ganador!
“””

```
else:
    message = f"📢 Nueva actividad detectada\n⏰ {timestamp}"

return message
```

# ========== MONITOREO PRINCIPAL ==========

def monitor_markets():
“”“Función principal de monitoreo”””
print(“🚀 Iniciando monitoreo de Polymarket…”)
send_telegram_message(“🤖 Bot de alertas iniciado\n\n✅ Monitoreando:\n- Ballenas (>$30k)\n- Múltiples apuestas (5+)\n- Premier League, Saudi Pro League\n- NBA\n- Crypto”)

```
processed_trades = set()  # Para evitar duplicados

while True:
    try:
        print(f"\n⏰ Verificando mercados... {datetime.now().strftime('%H:%M:%S')}")
        
        # 1. Obtener mercados activos
        markets = get_markets()
        relevant_markets = filter_markets_by_category(markets)
        
        print(f"📊 Mercados relevantes encontrados: {len(relevant_markets)}")
        
        # 2. Monitorear trades en mercados relevantes
        for market in relevant_markets[:10]:  # Primeros 10 para no saturar
            market_id = market.get('id') or market.get('condition_id')
            if not market_id:
                continue
                
            trades = get_market_trades(market_id)
            
            for trade in trades[:5]:  # Últimos 5 trades
                if not isinstance(trade, dict):
                    continue
                    
                trade_id = trade.get('id', '')
                
                # Evitar procesar el mismo trade dos veces
                if trade_id and trade_id in processed_trades:
                    continue
                
                # Detectar ballenas
                if is_whale_bet(trade):
                    amount = float(trade.get('size', 0)) * float(trade.get('price', 0))
                    
                    alert_data = {
                        'amount': amount,
                        'market_name': market.get('question', 'N/A'),
                        'wallet': trade.get('maker_address', 'N/A'),
                        'side': 'YES' if trade.get('side') == 'BUY' else 'NO'
                    }
                    
                    message = format_alert_message("whale", alert_data)
                    send_telegram_message(message)
                    print(f"🐋 Alerta de ballena enviada: ${amount:,.2f}")
                    
                    if trade_id:
                        processed_trades.add(trade_id)
        
        # 3. Monitorear billeteras específicas
        for wallet in WALLETS_TO_MONITOR:
            analysis = analyze_wallet_patterns(wallet)
            
            if analysis and analysis['is_active']:
                alert_data = {
                    'wallet': wallet,
                    'count': analysis['simultaneous_bets'],
                    'category': 'Deportes/Crypto'
                }
                
                message = format_alert_message("multiple_bets", alert_data)
                send_telegram_message(message)
                print(f"🎯 Alerta de múltiples apuestas enviada para {wallet[:10]}...")
        
        # Limitar tamaño del set de trades procesados
        if len(processed_trades) > 1000:
            processed_trades.clear()
        
        print(f"✅ Verificación completada. Esperando {CHECK_INTERVAL//60} minutos...")
        time.sleep(CHECK_INTERVAL)
        
    except Exception as e:
        error_msg = f"❌ Error en monitoreo: {str(e)}"
        print(error_msg)
        send_telegram_message(error_msg)
        time.sleep(60)  # Esperar 1 minuto antes de reintentar
```

# ========== EJECUTAR BOT ==========

if **name** == “**main**”:
try:
monitor_markets()
except KeyboardInterrupt:
print(”\n🛑 Bot detenido por el usuario”)
send_telegram_message(“🛑 Bot detenido”)
except Exception as e:
print(f”❌ Error fatal: {e}”)
send_telegram_message(f”❌ Error fatal: {e}”)
