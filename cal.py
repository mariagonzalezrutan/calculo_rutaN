from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import Wiql, JsonPatchOperation


personal_access_token = ''
organization_url = 'https://dev.azure.com/CorporacionRutaN'

credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)


credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

core_client = connection.clients.get_core_client()
wit_client = connection.clients.get_work_item_tracking_client()

projects = core_client.get_projects()

for project in projects:
    if project.name == "CATI":
        print(f"Proyecto: {project.name}")

        query = Wiql(query=f"SELECT [System.Id], [System.Title], [System.State] FROM workitems WHERE [System.TeamProject] = '{project.name}'")
        
        work_items_query_result = wit_client.query_by_wiql(wiql=query)
        
        if not work_items_query_result.work_items:
            print(f"No se encontraron work items para el proyecto: {project.name}")
            continue
        
        work_item_ids = [item.id for item in work_items_query_result.work_items]
        
        if work_item_ids:
            # Obtener todos los campos de los work items usando expand='All'
            work_items = wit_client.get_work_items(ids=work_item_ids, expand='All')
            
            # Mostrar los work items
            for wi in work_items:
                cantidad = wi.fields.get('Custom.Cantidad')
                meses = wi.fields.get('Custom.Meses')
                valor_unitario = wi.fields.get('Custom.Valorunitario')

                if cantidad is not None and meses is not None and valor_unitario is not None:
                    # Calcular el valor total estimado
                    valor_total_estimado = cantidad * meses * valor_unitario

                    # Formatear el valor total como moneda en pesos colombianos
                    valor_total_formateado = valor_total_estimado
                    print(f"    Calculando Valor Total Estimado: {valor_total_formateado}")
                    
                    # Actualizar el campo Valor Total Estimado en Azure DevOps
                    try:
                        update_document = [
                            JsonPatchOperation(
                                op="add",
                                path="/fields/Custom.ValorTotal",
                                value=valor_total_formateado
                            )
                        ]
                        wit_client.update_work_item(
                            document=update_document,
                            id=wi.id
                        )
                        print(f"    Valor Total Estimado actualizado en el work item ID {wi.id}: {valor_total_formateado}")
                    except Exception as e:
                        print(f"    Error al actualizar el work item ID {wi.id}: {e}")
                else:
                    print(f"    No se encontraron suficientes datos para calcular el valor total estimado para el work item ID {wi.id}")

                print("====================================")
        else:
            print(f"No se encontraron work items para el proyecto: {project.name}")

        print("====================================")