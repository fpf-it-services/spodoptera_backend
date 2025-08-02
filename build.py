import re
from pathlib import Path

TEMPLATE_FRONTEND_DIR = Path("../template/frontend")


def remove_backslashes(content: str) -> str:
    # Supprimer les backslashes qui précèdent uniquement des guillemets
    return content.replace('\\\'', '\'').replace('\\"', '"')


def convert_static_paths(content: str) -> str:
    print("Converting static paths in HTML content...")
    if "{% load static %}" not in content:
        content = "{% load static %}\n" + content
    
    # Pattern pour src/href avec ../ ou /static/
    content = re.sub(
        r'(src|href)=["\'](\.\./)*static/(.*?)["\']',
        r'\1="{% static \'\3\' %}"',  # Format exact demandé
        content,
        flags=re.IGNORECASE,
    )

    # Pattern pour url() dans CSS
    content = re.sub(
        r'url\(["\']?(\.\./)*static/(.*?)["\']?\)',
        r'url("{% static \'\2\' %}")',  # Format cohérent
        content,
        flags=re.IGNORECASE,
    )
    
    # Nettoyage des caractères \
    content = remove_backslashes(content)
    
    return content

def process_html_files():
    print("Processing HTML files in 'template/frontend'...")
    print(f"Directory: {TEMPLATE_FRONTEND_DIR}")
    print(f"Chemin absolu du répertoire: {TEMPLATE_FRONTEND_DIR.absolute()}")
    print("\nContenu du répertoire:")
    for item in TEMPLATE_FRONTEND_DIR.iterdir():
        print(f" - {item.name} ({'dossier' if item.is_dir() else 'fichier'})")
    html_files = list(TEMPLATE_FRONTEND_DIR.glob("*.html"))
    print(f"Found {len(html_files)} HTML files to process")
    for file_path in html_files:
        print(f"Processing file: {file_path}")
        content = file_path.read_text(encoding="utf-8")
        new_content = convert_static_paths(content)
        if content != new_content:
            file_path.write_text(new_content, encoding="utf-8")
            print(f"✔ Modifié: {file_path}")

if __name__ == "__main__":
    process_html_files()
    print("✅ Tous les fichiers HTML dans 'template/frontend' ont été adaptés.")
