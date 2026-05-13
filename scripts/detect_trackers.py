import os
import json

def load_tracker_db(db_path):
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f).get("trackers", [])
    except Exception as e:
        print(f"[-] Erreur de chargement de la DB : {e}")
        return []

def scan_java_imports(jadx_dir, trackers_db):
    print(f"[*] Analyse du code source dans : {jadx_dir}")
    
    if not os.path.exists(jadx_dir):
        print("[-] Erreur : Le dossier jadx est introuvable.")
        return None

    detected_trackers = {}

    # Parcourir tous les fichiers du dossier jadx
    for root, dirs, files in os.walk(jadx_dir):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as java_file:
                        content = java_file.read()
                        
                        # Vérifier chaque tracker de la base de données
                        for tracker in trackers_db:
                            # On cherche si la signature (ex: import com.facebook) est dans le code
                            search_string = f"import {tracker['package']}"
                            if search_string in content:
                                # Si trouvé, on l'ajoute au dictionnaire (pour éviter les doublons)
                                if tracker['name'] not in detected_trackers:
                                    detected_trackers[tracker['name']] = tracker
                except Exception:
                    pass # On ignore les fichiers illisibles

    return list(detected_trackers.values())

if __name__ == "__main__":
    db_file = "data/trackers_db.json"
    jadx_folder = "output_jadx/sources"
    
    # Charger la base de connaissances
    db = load_tracker_db(db_file)
    print(f"[*] Base de données chargée : {len(db)} trackers connus.")
    
    # Lancer le scan
    results = scan_java_imports(jadx_folder, db)
    
    if results is not None:
        print("\n[+] Scan terminé !")
        print(f"Trackers détectés : {len(results)}")
        for t in results:
            print(f"  - {t['name']} (Cat: {t['category']}, Risque: {t['risk']})")
            
        # Sauvegarde temporaire
        with open("output/detected_trackers.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print("[+] Résultats sauvegardés dans output/detected_trackers.json")