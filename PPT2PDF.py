import os
import comtypes.client

def ppt_to_pdf(input_path, output_path):
    # Open the PowerPoint file
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    # Open the PowerPoint file
    presentation = powerpoint.Presentations.Open(input_path)

    # Save the PowerPoint file to PDF
    presentation.SaveAs(output_path, 32)

    # Close the PowerPoint file
    presentation.Close()

    # Quit the PowerPoint application
    powerpoint.Quit()

# Get the list of all PowerPoint files in the current directory
filenames = [f for f in os.listdir('.') if f.endswith(('.ppt', '.pptx'))]

# Convert each PowerPoint file to PDF
for filename in filenames:
    input_path = os.path.abspath(filename)
    output_path = os.path.abspath(filename).replace('.pptx', '.pdf').replace('.ppt', '.pdf')
    ppt_to_pdf(input_path, output_path)

print('Done!')
