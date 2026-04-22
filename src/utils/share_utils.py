from datetime import datetime

def format_opportunity_text(symbol: str, metrics: dict, result: dict) -> str:
    """
    Formats the technical details and phase of an opportunity ready for sharing
    via Telegram or Email for exclusively educational purposes.
    """
    bucket = metrics.get('bucket', result.get("bucket", "PATTERN"))
    conf = result.get("confidence", getattr(result, "confidence", 0))
    if type(conf) == dict: conf = 0
    phase = metrics.get('phase', 'NO_PATTERN')
    prog = metrics.get('progress_pct', 0)
    drop = metrics.get('drop_from_high_pct', metrics.get('drop_pct', 0))
    rebound = metrics.get('rebound_pct', 0)
    upside_3y = metrics.get('upside_to_ath3y', 0)
    price = result.get('current_price', 0)
    
    text = f"📡 RadarCore — Opportunity detected\n━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🏷 {symbol} · {bucket} · Conf: {conf:.1f}%\n"
    
    if phase not in ["NO_PATTERN", "UNKNOWN", "N/A"]:
        text += f"📊 Phase: {phase} ({prog:.1f}% progression)\n"
    
    if drop > 0 or rebound > 0:
        text += f"📉 Drop: {drop:.1f}% | Rebound: {rebound:.1f}%\n"
        
    if upside_3y > 0:
        text += f"📈 Upside ATH 3Y: {upside_3y:.1f}%\n"
        
    if price > 0:
        text += f"💰 Price ref: ${price:.2f}\n"

    # Earnings checks
    risk = metrics.get("earnings_risk_level", "NONE")
    d_next = metrics.get("days_to_next_earnings")
    if risk in ["HIGH", "MEDIUM"] and d_next is not None:
        text += f"⚠️ Earnings in {d_next} days\n"
        
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "⚠️ For educational use only. Not financial advice."
    
    return text

def format_scan_summary_text(opportunities_list: list) -> str:
    """
    Generates the global scan summary.
    The values of opportunities_list are the active items in active_analysis (dicts).
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    count = len(opportunities_list)
    
    lines = []
    lines.append(f"⏱️ RadarCore Scanner | {now} | {count} Opportunities found")
    lines.append("=" * 40)
    
    for item in opportunities_list:
        sym = item.get("symbol", "N/A")
        m = item.get("metrics", {})
        # Create pseudo-result object to resemble the one from classify/analyze
        r = {"confidence": item.get("confidence", 0), "current_price": m.get("current_price", 0)}
        lines.append(format_opportunity_text(sym, m, r))
        lines.append("\n") # Double line break
        
    return "\n".join(lines).strip()
