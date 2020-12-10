# Altium library generator.

The tip is to export Altium schematic lib in .lia format, corresponding to a P-CAD library, which has the good taste to be a text format. Then it is possible to re-import a modified .lia using the Import Wizard. Select File -> Import Wizard -> PCAD Format, just select the .lia file when Wizards prompts for library and hit "Next" otherwise.

Be careful, Altium is very sensitive to encoding and line feeds: modified file must be \\r\\n line breaks and ISO-8859-1 encoding.

This script uses Jinja to customize a .lia file. The Jinja template looks like a .lia file but must be UTF-8.

## Post-treatment
Some data is lost during the import/export process.

* Use the SCHLIB List panel to display all parameters, and set them all to the right color and font.
* Use SHIFT-F to select all "PartNumber" parameters, modify the display boolean, color, font and position
Alternativery, use SCHLIB Filter panel and request: "(ObjectKind = 'Parameter') And (ParameterName = 'PartNumber')"
* Also use SHIFT-F to select all designators, change them to R? instead of U?, and modify display options
SCHLIB Filter request: "ObjectKind = 'Designator'"
* Select all parameters and toggle PartNumber and Designator visibility.
SCHLIB Filter request: "ObjectKind = 'Part'"
* Parameter Manager can be used to copy "Part Number" to the "Description" field
* The "Value" field reappeared, and has to be deleted. Also, some fields disappear, such as "TYPE" (RES\ GEN and RES\_GEN\_JP)
* Parameter Manager changes are very slow on such a big lib.
* Also do not forget to change jumpers designator to "JP" and their types to RES\_GEN\_TYPE.

## Known issues
* Bug with designator display: when opening SchLib file, the Designator are not visible on screen, even if the "visible" boolean has been correctly toggled. You will have to work "blindly" and try to place the component on SCH file to see any designators appearing.
