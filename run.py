import os
from app import create_app, db
from app.seed import seed_default_admin

app = create_app()


@app.shell_context_processor
def make_shell_context():
    from app import models
    return {"db": db, "models": models}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_default_admin()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
