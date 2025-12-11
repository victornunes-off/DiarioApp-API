# run.py
# Executa a API

from app import create_app, db

app = create_app()


with app.app_context():
    print("\n=== CONEXÃO ATUAL DO BANCO ===")
    print("URL completa →", db.engine.url)
    print("Banco →", db.engine.url.database)
    print("Driver →", db.engine.url.drivername)
    print("Host →", db.engine.url.host)
    print("================================\n")
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)