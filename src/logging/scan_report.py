from datetime import datetime
from src.logging.scan_logger import ScanLogger

def generate_scan_report(logger: ScanLogger) -> str:
    summary = logger.summary()
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    duration = summary.get("duration_seconds", 0)
    total = summary.get("total_analyzed", 0)
    found = summary.get("opportunities_found", 0)
    config = summary.get("config", {})

    # Contadors específics segons el detall del skipping (UNIVERSE_FILTER)
    liq_count = 0
    market_count = 0
    zombie_count = 0
    
    for e in logger.events:
        if e["stage"] == "UNIVERSE_FILTER" and e["status"] == "SKIP":
            detail = e["detail"].lower()
            if "volum" in detail or "liquiditat" in detail:
                liq_count += 1
            if "market cap" in detail:
                market_count += 1
            if "zombie" in detail:
                zombie_count += 1

    report = f"""# RadarCore — Scan Report
**Data:** {date_str} | **Durada:** {duration}s

## Resum
- Tickers analitzats: {total}
- Oportunitats trobades: {found}
- Descartats per liquiditat: {liq_count}
- Descartats per filtre de mercat: {market_count}
- Descartats per criteri zombie: {zombie_count}

## Configuració de l'escaneig
- Univers: {config.get('universe', 'N/A')}
- Caiguda mínima: {config.get('min_drop_pct', 'N/A')}%
- Mode: {'Automatic' if config.get('auto_mode', True) else 'Watchlist'}

## Oportunitats detectades
"""
    
    opportunities_found = False
    for e in logger.events:
        if e["stage"] == "STRATEGY" and e["status"] == "PASS":
            opportunities_found = True
            symbol = e["symbol"]
            detail = e["detail"]
            
            # Buscar bucket i score en esdeveniments posteriors del mateix símbol
            bucket = "N/A"
            score = "N/A"
            for sub_e in logger.events:
                if sub_e["symbol"] == symbol:
                    if sub_e["stage"] == "CLASSIFIER":
                        bucket = sub_e["detail"].replace("Bucket: ", "")
                    if sub_e["stage"] == "STRATEGY": # El detall de STRATEGY PASS sol tenir info de l'oportunitat
                        # Intentar extreure score si està present (depèn de com ho loguem a MarketScanner)
                        pass

            report += f"### {symbol}\n"
            report += f"- Pattern: {bucket}\n"
            report += f"- {detail}\n\n"

    if not opportunities_found:
        report += "_No s'han detectat oportunitats en aquest escaneig._\n"

    report += "\n## Descartats (resum per motiu)\n"
    
    # Agrupar per motiu (detail) per SKIPs
    reasons = {}
    for e in logger.events:
        if e["status"] == "SKIP" or e["status"] == "FAIL":
            reason = e["detail"] or "Desconegut"
            reasons[reason] = reasons.get(reason, 0) + 1
            
    # Top 5 motius
    sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]
    for reason, count in sorted_reasons:
        report += f"- {reason}: {count} tickers\n"

    return report
