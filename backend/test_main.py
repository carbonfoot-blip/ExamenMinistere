print("=== DEMARRAGE ===")
try:
    from main import app
    print("=== APP IMPORTEE OK ===")
    print("Routes:", [r.path for r in app.routes])
except Exception as e:
    print(f"=== ERREUR IMPORT: {e} ===")
    import traceback
    traceback.print_exc()