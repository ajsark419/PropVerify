from datetime import datetime
from markupsafe import Markup


def register_template_helpers(app):
    @app.template_filter("currency")
    def currency(value):
        try:
            return f"${float(value):,.0f}"
        except (TypeError, ValueError):
            return value

    @app.template_filter("date")
    def date_filter(value):
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%b %d, %Y")
        return str(value)

    @app.template_filter("status_badge")
    def status_badge(status):
        mapping = {
            "approved": "success",
            "pending": "warning",
            "rejected": "danger",
        }
        cls = mapping.get(status, "secondary")
        label = status.title() if status else "Unknown"
        return Markup(f'<span class="badge bg-{cls}">{label}</span>')

    @app.context_processor
    def inject_globals():
        return {"now": datetime.utcnow()}
