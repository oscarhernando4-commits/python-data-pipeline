import re

with open("real_money_trader.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the unconditional balance polling at the top of evaluate_and_trade_real_money
pattern1 = r"""    balances = get_real_balances\(\)
    
    usdt_free = sum\(\[float\(b\["free"\]\) for b in balances if b\["asset"\] == "USDT"\]\)
    bnb_free = sum\(\[float\(b\["free"\]\) for b in balances if b\["asset"\] == "BNB"\]\)
    
    # Cloud fallback: If Binance blocked our IP \(no proxy\), fallback to local JSON state so we don't freeze
    # We divide by 2 because the capital is split 50/50 between Spot and Futures
    if usdt_free == 0.0 and bnb_free == 0.0 and not balances:
        usdt_free = state.get\("current_balance_usd", 17.15\) / 2.0
    
    # Calculate BNB USD value
    bnb_usd = bnb_free \* 575.0  # Approx BNB price
    total_val = usdt_free \* 2.0 \+ bnb_usd # Multiply by 2.0 to restore total val for the JSON state
    
    # Check for active non-USDT crypto position on Binance Spot Real \(LONG\)
    crypto_balances = \[b for b in balances if b\["asset"\] not in \["USDT", "USDC", "BNB"\] and float\(b\["free"\]\) > 0\]
    
    # Check for active Futures positions \(SHORT\)
    futures_positions = get_real_futures_positions\(\)
    futures_usdt_free = get_real_futures_usdt_balance\(\)
    
    # Cloud fallback: If Futures API blocked our IP \(no proxy\), fallback to local JSON state
    if futures_usdt_free == 0.0 and not futures_positions:
        futures_usdt_free = state.get\("current_balance_usd", 17.15\) / 2.0"""

replacement1 = """    # FIXIE OPTIMIZATION: We rely entirely on the local JSON state for balances 
    # to avoid burning Fixie Proxy requests every 5 minutes.
    usdt_free = state.get("current_balance_usd", 17.15) / 2.0
    futures_usdt_free = state.get("current_balance_usd", 17.15) / 2.0
    
    crypto_balances = []
    futures_positions = []
    
    # Hydrate crypto_balances and futures_positions flags artificially from local state
    if state.get("position"):
        if state["position"].get("side") == "LONG":
            crypto_balances = [{"asset": state["position"]["symbol"].replace("USDT", ""), "free": state["position"]["quantity"]}]
        elif state["position"].get("side") == "SHORT":
            futures_positions = [{"symbol": state["position"]["symbol"], "positionAmt": -state["position"]["quantity"], "entryPrice": state["position"]["entry_price"]}]"""

content = re.sub(pattern1, replacement1, content)

with open("real_money_trader.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to real_money_trader.py successfully!")
