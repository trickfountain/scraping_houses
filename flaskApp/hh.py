from app import app, db
from app.models import Listing

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Listing': Listing}