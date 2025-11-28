import csv, re, pathlib
ref_path = pathlib.Path('docs/reference/FMB140 - AVL parameters.csv')
map_path = pathlib.Path('docs/working/Fleeti_Field_Mapping_Expanded.csv')
ref_data = {}
with ref_path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = row['Property ID in AVL packet']
        if key and key.strip().isdigit():
            ref_data[int(key.strip())] = row
cols = ['Bytes','Type','Value range Min','Value range Max','Multiplier','Units','Description']
rows = []
with map_path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)
pattern = re.compile(r'^avl_io_(\d+)')
stats_total = 0
stats_populated = 0
missing_ids = []
for row in rows:
    nav_field = row['Navixy Fields']
    if nav_field.startswith('avl_io_'):
        stats_total += 1
        m = pattern.match(nav_field)
        if not m:
            missing_ids.append(nav_field)
            continue
        avl_id = int(m.group(1))
        ref_row = ref_data.get(avl_id)
        if not ref_row:
            missing_ids.append(str(avl_id))
            continue
        for col in cols:
            if (row.get(col, '') or '').strip():
                continue
            value = ref_row.get(col, '')
            row[col] = value
        stats_populated += 1
with map_path.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
print('TOTAL_AVL_ROWS', stats_total)
print('ROWS_WITH_REFERENCE', stats_populated)
print('MISSING_IDS', ','.join(missing_ids))
