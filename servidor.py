from pynetdicom import AE, evt
from pynetdicom.sop_class import CTImageStorage, MRImageStorage, SecondaryCaptureImageStorage
import os
from pydicom.uid import generate_uid
#almacenador
OUTPUT_DIR = "./dicom_storage"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def manejar_store(event):
    try:
        ds = event.dataset
        ds.file_meta = event.file_meta

        uid = getattr(ds, "SOPInstanceUID", generate_uid())
        filename = f"{uid}.dcm"
        filepath = os.path.join(OUTPUT_DIR, filename)

        ds.save_as(filepath, write_like_original=False)

        print(f"[+] Archivo guardado: {filepath}")
        return 0x0000

    except Exception as e:
        print(f"[!] Error: {e}")
        return 0xC210

handlers = [(evt.EVT_C_STORE, manejar_store)]

ae = AE(ae_title="SERVIDOR_DICOM")
#datos de imagen
ae.add_supported_context(CTImageStorage)
ae.add_supported_context(MRImageStorage)
ae.add_supported_context(SecondaryCaptureImageStorage)

print("Iniciando servidor DICOM en puerto 11112...")
#servidor en modo escucha
ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)
