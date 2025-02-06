def generate_alert(emoji, ingredient_name, safety_status, description):
    """
    Returns an HTML string with color-coded blocks.

    :param emoji: e.g. 🍅
    :param ingredient_name: e.g. 'Tomato'
    :param safety_status: 'dangerous', 'alert', or 'safe'
    :param description: short AI-provided text

    We color-code based on safety_status:
      - dangerous => red
      - alert => yellow
      - safe => green
    """
    # Choose a color
    if safety_status.lower() == "dangerous":
        color = "#ff6961"  # red
        label = "DANGEROUS"
    elif safety_status.lower() == "alert":
        color = "#FFD700"  # yellow
        label = "ALERT"
    else:
        color = "#77DD77"  # green
        label = "SAFE"

    # Build a styled HTML snippet
    html = f"""
    <div style="border: 2px solid {color};
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
                background-color: {color}20;">
        <h4 style="margin: 0;">
            {emoji} {ingredient_name}
            <span style="color:{color}; font-weight:600;">({label})</span>
        </h4>
        <p style="margin-top: 6px; font-size: 0.95em;">
            {description}
        </p>
    </div>
    """
    return html
