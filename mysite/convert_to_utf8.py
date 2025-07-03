import os
import sys
import codecs
import chardet
import shutil
import re

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    return encoding, raw_data

def convert_to_utf8(input_file, output_dir=None):
    """Convert a file to UTF-8 encoding."""
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist.")
        return False

    # Detect the encoding
    encoding, raw_data = detect_encoding(input_file)
    
    if not encoding:
        print(f"Error: Could not detect encoding for {input_file}")
        return False
    
    print(f"Detected encoding for {input_file}: {encoding}")
    
    # Determine output file path
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
    else:
        output_file = input_file + ".utf8"
    
    try:
        # Try to decode with detected encoding
        content = raw_data.decode(encoding, errors='replace')
        
        # Remove null bytes
        content = content.replace('\x00', '')
        
        # Write to the output file in UTF-8
        with codecs.open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully converted {input_file} to UTF-8 and saved to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_utf8.py <input_file> [output_directory]")
        return
    
    input_file = sys.argv[1]
    output_dir = None
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    convert_to_utf8(input_file, output_dir)

if __name__ == "__main__":
    main()

# Папка с исходными файлами
SRC_DIR = 'Lector'
# Папка для сохранения перекодированных файлов
DST_DIR = 'utf8_fixed'
# Лог ошибок
LOG_FILE = 'convert_to_utf8_errors.log'

# Кодировки, которые будем пробовать
ENCODINGS = ['utf-8', 'cp1251', 'koi8-r', 'iso8859-5']

# Создать папку для результата
os.makedirs(DST_DIR, exist_ok=True)

# Регулярное выражение для поиска "кракозябр" (последовательности типа Р—РґСЂР°РІ...)
KRAKOZYABRY_PATTERN = re.compile(r'Р[А-Яа-я]{2,}')

def has_cyrillic(text):
    """Проверяет, есть ли в тексте кириллица"""
    return bool(re.search('[а-яА-Я]', text))

def has_krakozyabry(text):
    """Проверяет, есть ли в тексте "кракозябры" (Р—РґСЂР°РІ...)"""
    return bool(KRAKOZYABRY_PATTERN.search(text))

def try_fix_krakozyabry(text):
    """Пытается восстановить текст с кракозябрами через двойное перекодирование"""
    try:
        # Пробуем восстановить через latin1 -> cp1251
        fixed = text.encode('latin1').decode('cp1251')
        if has_cyrillic(fixed) and not has_krakozyabry(fixed):
            return fixed, 'latin1->cp1251'
    except Exception:
        pass
    
    try:
        # Пробуем восстановить через cp1251 -> utf-8
        fixed = text.encode('cp1251').decode('utf-8', errors='ignore')
        if has_cyrillic(fixed) and not has_krakozyabry(fixed):
            return fixed, 'cp1251->utf-8'
    except Exception:
        pass
    
    return text, None

with open(LOG_FILE, 'w', encoding='utf-8') as log:
    for filename in os.listdir(SRC_DIR):
        if not filename.lower().endswith('.txt'):
            continue
        src_path = os.path.join(SRC_DIR, filename)
        dst_path = os.path.join(DST_DIR, filename)
        success = False
        
        # Пробуем разные кодировки
        for encoding in ENCODINGS:
            try:
                with open(src_path, 'r', encoding=encoding) as f:
                    content = f.read().replace('\x00', '')
                
                # Проверяем, есть ли в тексте кириллица
                if has_cyrillic(content):
                    # Проверяем, нет ли "кракозябр" (Р—РґСЂР°РІ...)
                    if has_krakozyabry(content):
                        fixed_content, method = try_fix_krakozyabry(content)
                        if method:
                            content = fixed_content
                            print(f'Файл {filename} восстановлен из "кракозябр" через {method}')
                            log.write(f'Файл {filename} восстановлен из "кракозябр" через {method}\n')
                        else:
                            print(f'ВНИМАНИЕ: Файл {filename} содержит "кракозябры", но не удалось восстановить')
                            log.write(f'ВНИМАНИЕ: Файл {filename} содержит "кракозябры", но не удалось восстановить\n')
                    
                    # Сохраняем файл в UTF-8
                    with open(dst_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f'OK ({encoding} -> utf-8): {filename}')
                    log.write(f'OK ({encoding} -> utf-8): {filename}\n')
                    success = True
                    break
            except Exception as e:
                print(f'Ошибка при чтении {filename} как {encoding}: {e}')
                log.write(f'Ошибка при чтении {filename} как {encoding}: {e}\n')
        
        if not success:
            print(f'ОШИБКА: Не удалось преобразовать {filename}')
            log.write(f'ОШИБКА: Не удалось преобразовать {filename}\n')

print(f'Готово! Результаты сохранены в папке {DST_DIR}')
print(f'Лог ошибок: {LOG_FILE}') 