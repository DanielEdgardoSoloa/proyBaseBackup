import os
import sys
import json
import xml.etree.ElementTree as ET
import zipfile

# # Alias de la Org registrada con SFDX o Usuario que identifica la Org registrada con SFDX
origen = sys.argv[1]

# # Definicion de la identacion del archivo XML


def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


# Listado de toda la metadata existente en la Org
os.system("sfdx force:mdapi:describemetadata -f ./data/meta.json -u "+origen)

allmeta = open('./data/meta.json',)
data = json.load(allmeta)

# Listado de todos los componentes por cada una de una de las metadata listadas
for i in data['metadataObjects']:
    os.system("sfdx force:mdapi:listmetadata -m " +
              i['xmlName'] + " -f ./data/" + i['xmlName'] + ".json -u"+origen)
allmeta.close()

# Creacion del Archivo XML
root = ET.Element(
    'Package', {'xmlns': 'http://soap.sforce.com/2006/04/metadata'})
for subdir, dirs, files in os.walk('./data'):
    for f in files:
        tipo = f.split('.')
        tipos = ET.SubElement(root, 'types')
        componentes = open('./data/'+f)
        s = componentes.read()
        members = json.loads(s)
        if not isinstance(members, list):
            members = json.loads('['+s+']')
        not_necessary= ['CustomObjectTranslation.json', 'Workflow.json', 'InstalledPackage.json', 'KeywordLis.json', 'ModerationRule.json', 'WebLink.json', 'WorkflowFieldUpdate.json', 'UserCriteria.json', 'SiteDotCom.json', 'SharingRules.json', 'SharingGuestRule.json', 'Report.json','meta.json']
        if not f in not_necessary:
        # if f != 'meta.json'
            for j in members:
                metadata = ET.SubElement(tipos, 'members')
                metadata.text = j['fullName']
            name = ET.SubElement(tipos, 'name')
            name.text = tipo[0]
            componentes.close()

version = ET.SubElement(root, 'version')
version.text = '50.0'
tree = ET.ElementTree(indent(root))
tree.write('package.xml', xml_declaration=True, encoding='utf-8')