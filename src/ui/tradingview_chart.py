import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

def render_tv_chart(
    symbol: str,
    hist_data: pd.DataFrame,
    metrics: dict,
    height: int = 500
) -> None:
    """
    Renders TradingView Lightweight Charts via CDN using st.components.v1.html.
    Includes a radio selector in Streamlit for switching views (Candles, Mountain, Pivots).
    """
    # 1. Selector de vista a sobre del gràfic (Streamlit)
    view = st.radio(
        "",
        options=["Candles", "Mountain", "Pivots"],
        horizontal=True,
        key=f"tv_view_{symbol}",
        index=0
    )

    # 2. Extract Javascript booleans based on view selection
    show_candles = "true" if view in ["Candles", "Pivots"] else "false"
    show_line = "true" if view == "Mountain" else "false"
    show_pivots = "true" if view == "Pivots" else "false"

    # 3. Data Prep for JSON
    candles = []
    for date, row in hist_data.iterrows():
        try:
            d_str = date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date)[:10]
            candles.append({
                "time": d_str,
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
            })
        except Exception:
            continue

    pivot_points = metrics.get("pivot_points", [])
    pivot_line = []
    for p in pivot_points:
        if p.get("date") and p.get("price"):
            # Ensure date is string
            dt_str = p["date"].strftime("%Y-%m-%d") if hasattr(p["date"], 'strftime') else str(p["date"])[:10]
            pivot_line.append({"time": dt_str, "value": round(float(p["price"]), 2)})
            
    next_earnings = metrics.get("next_earnings")
    # Make sure next earnings is properly formatted to YYYY-MM-DD
    earn_str = next_earnings.strftime("%Y-%m-%d") if hasattr(next_earnings, 'strftime') else (str(next_earnings)[:10] if next_earnings and str(next_earnings) != "Unknown" else None)

    candles_json = json.dumps(candles)
    pivot_json = json.dumps(pivot_line)
    
    # We pass the pivot structure for markers as well
    markers_list = []
    for p in pivot_points:
        if p.get("date") and p.get("price"):
            dt_str = p["date"].strftime("%Y-%m-%d") if hasattr(p["date"], 'strftime') else str(p["date"])[:10]
            markers_list.append({
                "time": dt_str,
                "type": p.get("type", ""),
                "label": p.get("label", "")
            })
    pivot_markers_json = json.dumps(markers_list)

    earnings_json = json.dumps(
        [{"time": earn_str, "position": "aboveBar",
          "color": "#FF9800", "shape": "arrowDown",
          "text": "Earnings"}]
        if earn_str else []
    )

    # 4. Create HTML Payload
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
      <style>
        body {{
          margin: 0;
          background: #000000;
        }}
        #chart {{
          width: 100%;
          height: {height}px;
        }}
      </style>
    </head>
    <body>
      <div id="chart"></div>
      <script>
        const chart = LightweightCharts.createChart(
          document.getElementById('chart'), {{
            width: document.body.clientWidth,
            height: {height},
            layout: {{
              background: {{ color: '#000000' }},
              textColor: '#d1d4dc',
            }},
            grid: {{
              vertLines: {{ color: '#1f1f1f' }},
              horzLines: {{ color: '#1f1f1f' }},
            }},
            rightPriceScale: {{
              borderColor: '#1f1f1f',
            }},
            timeScale: {{
              borderColor: '#1f1f1f',
              timeVisible: true,
            }},
            crosshair: {{
              mode: LightweightCharts.CrosshairMode.Normal,
            }},
          }}
        );

        // Candlestick series
        const candleSeries = chart.addCandlestickSeries({{
          upColor: '#26a69a',
          downColor: '#ef5350',
          borderVisible: false,
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
        }});
        candleSeries.setData({candles_json});
        candleSeries.applyOptions({{ visible: {show_candles} }});

        // Mountain/Line series
        const lineSeries = chart.addLineSeries({{
          color: '#F0B429',
          lineWidth: 1.5,
          priceLineVisible: false,
          lastValueVisible: true,
        }});
        const lineData = {candles_json}.map(d => ({{
          time: d.time,
          value: d.close
        }}));
        lineSeries.setData(lineData);
        lineSeries.applyOptions({{ visible: {show_line} }});

        // Línia de pivots RDP
        const pivotData = {pivot_json};
        if (pivotData.length > 0) {{
          const pivotSeries = chart.addLineSeries({{
            color: 'rgba(255, 255, 255, 0.6)',
            lineWidth: 1,
            lineStyle: 2, // dashed
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          }});
          pivotSeries.setData(pivotData);
          pivotSeries.applyOptions({{ visible: {show_pivots} }});
          
          // Markers per als pivots
          const markers = [];
          if ({show_pivots}) {{
              {pivot_markers_json}.forEach(p => {{
                markers.push({{
                  time: p.time,
                  position: p.type === 'PEAK' ? 'aboveBar' : 'belowBar',
                  color: '#F5C842',
                  shape: 'circle',
                  text: p.label,
                  size: 0.5,
                }});
              }});
          }}
          candleSeries.setMarkers(markers);
        }}

        // Earnings marker
        const earnings = {earnings_json};
        if (earnings.length > 0 && {show_candles}) {{
          candleSeries.setMarkers(
            [...(candleSeries.markers() || []), ...earnings]
          );
        }}

        // Fit content
        chart.timeScale().fitContent();
        
        // Responsive resize
        window.addEventListener('resize', () => {{
          chart.resize(document.body.clientWidth, {height});
        }});
      </script>
    </body>
    </html>
    """

    components.html(html, height=height + 20, scrolling=False)

