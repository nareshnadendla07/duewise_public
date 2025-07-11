# 🧠 Helper function to format verdict into styled HTML box
def render_verdict_box(verdict_text: str) -> str:
    lines = verdict_text.strip().splitlines()
    html_lines = [f"<p>{line.strip()}</p>" for line in lines if line.strip()]
    content = "\n".join(html_lines)

    styled_html = f"""
    <div style="padding: 1.25rem; background-color: #f8f9fb; border-left: 4px solid #1F4E79; border-radius: 8px;">
      <h4 style="margin-bottom: 0.75rem;">📝 <strong>Verdict Summary</strong></h4>
      {content}
    </div>
    """
    return styled_html