import click
from pmi_lib import * 

### in main zodat main.py aanroepen blijft werken
@click.command()
@click.option('--file_path_dicom', prompt='Input DICOM path', help='Path to the input DICOM file or directory.', required = True)
@click.option('--file_path_nifti', prompt='Output NIFTI path', help='Path to the output NIFTI file.', required = True)
def dicom_to_nifti_click(file_path_dicom, file_path_nifti):
    """Converts DICOM files or directories into NIfTI format, using click this can be run in the terminal.
    \n Simply input dicom-to-nifti in the terminal and you will be prompted for the input DICOM path and output NIFTI path this function requires"""
    try:
        dicom_image = read_dicom(file_path_dicom)
        click.secho(f"Read {file_path_dicom}, converting to {file_path_nifti}", fg="green")
        
        # Pass the DicomImage instance directly to write_nifti
        write_nifti(dicom_image, file_path_nifti)
        click.secho(f"Successfully converted", fg="green")

    except FileNotFoundError:
        click.secho(f"Error: DICOM file not found - {file_path_dicom}", err=True, fg="red")
    except PermissionError:
        click.secho(f"Error: Permission denied to DICOM file - {file_path_dicom}", err=True, fg="red")
    except Exception as e:
        click.secho(f"Error: Unexpected error occurred: {e}", err=True, fg="red")


if __name__ == '__main__':
    dicom_to_nifti_click()
  
