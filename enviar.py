from pynetdicom import AE
from pydicom import dcmread
#datos del servidor
AE_TITLE = "SERVIDOR_DICOM"
IP = "127.0.0.1"
PUERTO = 11112
#prueba
ARCHIVO_DICOM = "./prueba.dcm"

ds = dcmread(ARCHIVO_DICOM)

ae = AE(ae_title="CLIENTE_DICOM")

ae.add_requested_context(
    ds.SOPClassUID,
    ds.file_meta.TransferSyntaxUID
)

print(f"Conectando a {AE_TITLE} en {IP}:{PUERTO}...")

assoc = ae.associate(IP, PUERTO, ae_title=AE_TITLE)

if assoc.is_established:
    print("Asociación establecida.")

    status = assoc.send_c_store(ds)

    if status and status.Status == 0x0000:
        print("Envío exitoso.")
    else:
        print(f"Error en C-STORE: 0x{status.Status:04x}")

    assoc.release()

else:
    print("No se pudo establecer la asociación.")
