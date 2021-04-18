import xml.etree.ElementTree as ET
import sys
import os

xml_folder = str(sys.argv[1])
img_folder = str(sys.argv[2])

xml_abspath = os.path.abspath(xml_folder)
img_abspath = os.path.abspath(img_folder)

for file in os.listdir(xml_folder):
    if '.xml' not in file:
        continue

    file_path = xml_abspath+'/'+file
    # print(file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    path = root.findall('./path')[0]
    name = root.findall('./object/name')[0]

    if 'Drone' not in name.text:
        print(f'Incorrect Object Name in file: {file}')
        name.text = 'Drone'

    path.text = img_abspath + '/' + file.strip('xml') + 'jpg'

    fixedXml = ET.tostring(root)

    fixedPath = xml_abspath+'/fixed_xmls'

    if not os.path.exists(fixedPath):
        os.makedirs(fixedPath)

    with open(fixedPath+'/'+file, 'wb+') as f:
        f.write(fixedXml)
        f.close()


