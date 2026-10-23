import click
from pmi_lib.dicom import read_dicom
from pmi_lib.nifti import write_nifti


def dicom_to_nifti(file_path_dicom: str, file_path_nifti: str) -> None:
    """Converts DICOM files or directories into NIfTI format."""
    try:
        dicom_image = read_dicom(file_path_dicom)
        click.secho(f"Read {file_path_dicom}, converting to {file_path_nifti}", fg="green")
        
        # Pass the DicomImage instance directly to write_nifti
        write_nifti(dicom_image, file_path_nifti)
        click.secho(f"Successfully converted", fg="green")

    except FileNotFoundError:
        click.secho(f"Error: File not found - {file_path_dicom}", err=True, fg="red")
    except PermissionError:
        click.secho(f"Error: Permission denied - {file_path_dicom}", err=True, fg="red")
    except Exception as e:
        click.secho(f"Error: Unexpected error occurred: {e}", err=True, fg="red")

