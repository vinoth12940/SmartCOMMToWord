import os
import docx
from xml.etree import ElementTree

# Define the input and output directories
xmlFileFolder = '/Users/vinothrajalingam/Desktop/Python/xmlFileFolder'
newWordDocFolder = '/Users/vinothrajalingam/Desktop/Python/newWordDocFolder'

# Create the output directory if it does not exist
if not os.path.exists(newWordDocFolder):
    os.makedirs(newWordDocFolder)

# Loop through all the XML files in the input directory
for xml_file in os.listdir(xmlFileFolder):
    if xml_file.endswith('.xml'):
        # Open the XML file
        tree = ElementTree.parse(os.path.join(xmlFileFolder, xml_file))
        root = tree.getroot()

        # Create a new Word document
        doc = docx.Document()

        # Define a custom style for the hyperlink
        hyperlink_style = doc.styles.add_style('Hyperlink', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
        hyperlink_style.font.color.rgb = docx.shared.RGBColor(0, 0, 255)
        hyperlink_style.font.underline = True

        # Loop through the XML elements and add them to the document
        for elem in root.iter():
            if elem.text:
                if elem.tag == 'p':
                    if 'style' in elem.attrib and 'Heading' in elem.attrib['style']:
                        doc.add_heading(elem.text, int(elem.attrib['style'][-1]))
                    else:
                        doc.add_paragraph(elem.text)
                elif elem.tag == 'ulist':
                    for li in elem.iter('listitem'):
                        doc.add_paragraph(li.text, style='List Bullet')
                elif elem.tag == 'table':
                    tablebody = elem.find('tablebody')
                    if tablebody is not None:
                        colgroup = elem.find('colgroup')
                        if colgroup is not None:
                            table = doc.add_table(rows=1, cols=len(colgroup))
                            table.style = 'Table Grid'
                            for i, col in enumerate(colgroup):
                                table.columns[i].width = int(col.attrib['width'][:-1]) * 7.2
                            for row in tablebody.iter('row'):
                                table.add_row()
                                for i, cell in enumerate(row.iter('cell')):
                                    cell_text = cell.find('p').text
                                    if cell_text is not None:
                                        table.cell(-1, i).text = cell_text
                                    else:
                                        table.cell(-1, i).text = ''
                        else:
                            # Add a default width for each column in the table
                            num_cols = len(list(tablebody.find('row/cell')))
                            table = doc.add_table(rows=1, cols=num_cols)
                            table.style = 'Table Grid'
                            for col in table.columns:
                                col.width = int(1.0 * 7.2)
                            for row in tablebody.iter('row'):
                                table.add_row()
                                for i, cell in enumerate(row.iter('cell')):
                                    cell_text = cell.find('p').text
                                    if cell_text is not None:
                                        table.cell(-1, i).text = cell_text
                                    else:
                                        table.cell(-1, i).text = ''
                    else:
                        print('Warning: Table has no tablebody element')
                elif elem.tag == 'hyperlink':
                    ref = elem.find('ref')
                    if ref is not None:
                        url = ref.find('string').text
                        display = elem.find('display/string').text
                        doc.add_paragraph(display, style='Hyperlink').hyperlink = url

        # Save the Word document
        doc.save(os.path.join(newWordDocFolder, os.path.splitext(xml_file)[0] + '.docx'))