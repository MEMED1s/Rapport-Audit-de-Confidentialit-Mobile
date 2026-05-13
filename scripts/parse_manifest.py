import xml.etree.ElementTree as ET
import json
import os

# Namespace officiel d'Android utilisé dans les fichiers XML
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

def parse_manifest(manifest_path):
    print(f"[*] Analyse du manifest : {manifest_path}")
    
    if not os.path.exists(manifest_path):
        print("[-] Erreur : AndroidManifest.xml introuvable.")
        return None

    tree = ET.parse(manifest_path)
    root = tree.getroot()

    # Dictionnaire pour stocker nos résultats
    results = {
        "package_name": root.attrib.get("package", "Unknown"),
        "permissions": [],
        "flags": {
            "usesCleartextTraffic": False,
            "allowBackup": True, # True par défaut sur Android
            "debuggable": False
        },
        "exported_components": []
    }

    # 1. Extraction des permissions
    for elem in root.findall('uses-permission'):
        perm_name = elem.attrib.get(f"{ANDROID_NS}name")
        if perm_name:
            results["permissions"].append(perm_name)

    # 2. Extraction des flags de configuration depuis la balise <application>
    app_elem = root.find('application')
    if app_elem is not None:
        # usesCleartextTraffic
        if f"{ANDROID_NS}usesCleartextTraffic" in app_elem.attrib:
            val = app_elem.attrib[f"{ANDROID_NS}usesCleartextTraffic"].lower() == "true"
            results["flags"]["usesCleartextTraffic"] = val
            
        # allowBackup
        if f"{ANDROID_NS}allowBackup" in app_elem.attrib:
            val = app_elem.attrib[f"{ANDROID_NS}allowBackup"].lower() == "true"
            results["flags"]["allowBackup"] = val
            
        # debuggable
        if f"{ANDROID_NS}debuggable" in app_elem.attrib:
            val = app_elem.attrib[f"{ANDROID_NS}debuggable"].lower() == "true"
            results["flags"]["debuggable"] = val

        # 3. Extraction des composants exportés (Activités, Services, etc.)
        for component_type in ['activity', 'service', 'receiver', 'provider']:
            for comp in app_elem.findall(component_type):
                if f"{ANDROID_NS}exported" in comp.attrib:
                    is_exported = comp.attrib[f"{ANDROID_NS}exported"].lower() == "true"
                    if is_exported:
                        comp_name = comp.attrib.get(f"{ANDROID_NS}name", "Unknown")
                        results["exported_components"].append({
                            "type": component_type,
                            "name": comp_name
                        })

    return results

if __name__ == "__main__":
    # Test rapide du script
    manifest_file = "output_apktool/AndroidManifest.xml"
    data = parse_manifest(manifest_file)
    
    if data:
        print("\n[+] Extraction réussie !")
        print(f"Package: {data['package_name']}")
        print(f"Permissions trouvées: {len(data['permissions'])}")
        print(f"Composants exportés: {len(data['exported_components'])}")
        
        # Sauvegarde temporaire pour tester
        with open("output/parsed_manifest.json", "w") as f:
            json.dump(data, f, indent=4)
        print("[+] Résultats sauvegardés dans output/parsed_manifest.json")