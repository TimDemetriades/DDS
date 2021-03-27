import xml.etree.ElementTree as ET
import sys
import os

folder = str(sys.argv[1])

abspath = os.path.abspath(folder)

for file in os.listdir(folder):
    if '.xml' not in file:
        continue

    file_path = abspath+'/'+file
    print(file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    path = root.findall('./path')[0]
    name = root.findall('./object/name')[0]

    if 'Drone' not in name.text:
        print(f'Incorrect Object Name in file: {file}')
        name.text = 'Drone'
    #path.text = file_path

    fixedXml = ET.tostring(root)

    fixedPath = abspath+'/fixed_xmls'

    if not os.path.exists(fixedPath):
        os.makedirs(fixedPath)

    with open(fixedPath+'/'+file, 'wb+') as f:
        f.write(fixedXml)
        f.close()


