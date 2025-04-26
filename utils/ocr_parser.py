from paddleocr import PaddleOCR
import pandas as pd
import os
from datetime import datetime

def extract_fields(text):
    lines = text.split('\n')
    records = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            name = ' '.join(parts[:-3])
            start = parts[-3]
            end = parts[-2]
            try:
                start_dt = datetime.strptime(start, "%H:%M")
                end_dt = datetime.strptime(end, "%H:%M")
                hours = round((end_dt - start_dt).seconds / 3600, 2)
            except:
                hours = 0
            comment = parts[-1] if len(parts) > 4 else ""
            records.append([name, start, end, hours, comment])
    return records

def process_images_and_generate_excel(image_paths, output_file):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    combined_records = {}

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for i, image_path in enumerate(image_paths):
        result = ocr.ocr(image_path, cls=True)
        text = '\n'.join([line[1][0] for block in result for line in block])
        rows = extract_fields(text)
        for row in rows:
            name = row[0]
            if name not in combined_records:
                combined_records[name] = ["" for _ in range(6)]
            combined_records[name][i] = row[3]  # hours

    final_rows = []
    for i, (name, hours_list) in enumerate(combined_records.items(), start=1):
        total = sum([h for h in hours_list if isinstance(h, (int, float))])
        final_rows.append([i, name] + hours_list + [total])

    columns = ["No.", "Name"] + weekdays[:len(image_paths)] + ["Total"]
    df = pd.DataFrame(final_rows, columns=columns)
    df.to_excel(output_file, index=False)
