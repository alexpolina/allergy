def generate_alert(emoji, text, alert_text, description):
    
    if alert_text == "dangerous":
        background_gradient = "linear-gradient(135deg, #EF3B36, #FFFFFF)"
        icon = "🚫"  # Proibido
        alert_text_color = "#EF3B36"
    elif alert_text == "alert":
        background_gradient = "linear-gradient(135deg, #FFD700, #FFFFFF)"
        icon = "⚠️"  # Alerta
        alert_text_color = "#fdbb2d"
    else:  # "safe"
        background_gradient = "linear-gradient(135deg, #56ab2f, #FFFFFF)"
        icon = "✅"  # Check
        alert_text_color = "#56ab2f"
    
    # HTML em uma linha
    return f'<div style="width:220px;border-radius:15px;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;font-family:Arial,sans-serif;background:{background_gradient};"><h1 style="font-size:40px">{emoji}</h1><span style="font-size:18px;color:black;">{text}</span><span style="font-size:16px;color:{alert_text_color};font-weight:bold;">{alert_text}</span><div style="position:absolute;top:5px;right:5px;width:20px;height:20px;background-color:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;color:black;">{icon}</div></div><br><p>{description}</p>'