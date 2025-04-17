import os
import datetime


def create_log(file_path, replacements):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    base_name = os.path.basename(file_path)
    log_file_name = f"log_{base_name.replace('.docx', '')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_path = os.path.join(log_dir, log_file_name)

    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Log de modification pour le fichier : {file_path}\n")
        log_file.write(f"Date : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("=" * 50 + "\n")
        for find_text, replace_text, column in replacements:
            log_file.write(f"Remplacé: '{find_text}' par '{replace_text}'")
            if column:
                log_file.write(f" (dans la colonne: {column})")
            log_file.write("\n")

    return log_path
