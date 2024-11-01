import requests
import json

# Datos de autenticación
organization = "tu-organizacion"
project = "tu-proyecto"
pat = "tu_token_de_acceso_personal"
work_item_id = "ID_DEL_WORK_ITEM"

# Endpoint para obtener el work item
url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{work_item_id}?api-version=6.0"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {pat}"
}

# Obtener work item actual
response = requests.get(url, headers=headers)
if response.status_code == 200:
    work_item_data = response.json()

    # Obtener los valores de los campos
    cantidad = work_item_data["fields"].get("Custom.Cantidad", 0)
    meses = work_item_data["fields"].get("Custom.Meses", 0)
    valor_unitario = work_item_data["fields"].get("Custom.ValorUnitario", 0)

    # Calcular el valor total estimado
    valor_total_estimado = cantidad * meses * valor_unitario

    # Actualizar el work item con el valor calculado
    update_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
    update_payload = [
        {
            "op": "add",
            "path": "/fields/Custom.ValorTotalEstimado",
            "value": valor_total_estimado
        }
    ]

    response = requests.patch(update_url, headers=headers, data=json.dumps(update_payload))
    if response.status_code == 200:
        print("Work item actualizado correctamente.")
    else:
        print(f"Error al actualizar el work item: {response.content}")
else:
    print(f"Error al obtener el work item: {response.content}")

