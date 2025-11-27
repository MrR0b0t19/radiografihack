# script para crear un DICOM valido
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian
import datetime

# Crear metadatos
file_meta = FileMetaDataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
file_meta.MediaStorageSOPInstanceUID = "1.2.3.4.5.6.7.8.9"
file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

# Crear dataset principal
ds = FileDataset('test.dcm', {}, file_meta=file_meta, preamble=b"\0" * 128)

# Campos requeridos para DICOM
ds.PatientName = "Test^Patient"
ds.PatientID = "123456"
ds.StudyInstanceUID = "1.2.3.4.5.6"
ds.SeriesInstanceUID = "1.2.3.4.5.6.7"
ds.SOPInstanceUID = "1.2.3.4.5.6.7.8"
ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'

# Campo que vamos a modificar (Image Position Patient) movimiento en 3D
ds.ImagePositionPatient = ['0', '0', '0']

# Otros campos importantes modalidades y informacion de estudio
ds.Modality = "CT"
ds.StudyDescription = "Test Study"
ds.SeriesDescription = "Test Series"


ds.save_as('test.dcm')
print("Archivo DICOM creado: test.dcm")
