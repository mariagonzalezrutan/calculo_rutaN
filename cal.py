from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import Wiql, JsonPatchOperation
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/update_work_items', methods=['POST'])
def update_work_items():
    try:
        # Obtener el token de acceso del encabezado de la solicitud
        personal_access_token = request.headers.get('Authorization')
        if not personal_access_token:
            return jsonify({'error': 'Token de acceso es obligatorio'}), 401

        # Configurar la conexión con Azure DevOps
        organization_url = 'https://dev.azure.com/CorporacionRutaN'
        credentials = BasicAuthentication('', personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)

        core_client = connection.clients.get_core_client()
        wit_client = connection.clients.get_work_item_tracking_client()

        # Obtener el nombre del proyecto desde el cuerpo de la solicitud
        project_name = request.json.get('project_name')
        if not project_name:
            return jsonify({'error': 'El nombre del proyecto es obligatorio'}), 400

        projects = core_client.get_projects()
        for project in projects:
            if project.name == project_name:
                query = Wiql(query=f"SELECT [System.Id], [System.Title], [System.State] FROM workitems WHERE [System.TeamProject] = '{project.name}'")
                work_items_query_result = wit_client.query_by_wiql(wiql=query)

                if not work_items_query_result.work_items:
                    return jsonify({'message': f'No se encontraron work items para el proyecto: {project.name}'}), 404

                work_item_ids = [item.id for item in work_items_query_result.work_items]

                if work_item_ids:
                    work_items = wit_client.get_work_items(ids=work_item_ids, expand='All')
                    updated_items = []

                    for wi in work_items:
                        cantidad = wi.fields.get('Custom.Cantidad')
                        meses = wi.fields.get('Custom.Meses')
                        valor_unitario = wi.fields.get('Custom.Valorunitario')

                        if cantidad is not None and meses is not None and valor_unitario is not None:
                            valor_total_estimado = cantidad * meses * valor_unitario
                            valor_total_formateado = valor_total_estimado

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
                                updated_items.append({
                                    'work_item_id': wi.id,
                                    'valor_total_estimado': valor_total_formateado
                                })
                            except Exception as e:
                                print(f"Error al actualizar el work item ID {wi.id}: {e}")
                        else:
                            print(f"No se encontraron suficientes datos para calcular el valor total estimado para el work item ID {wi.id}")

                    return jsonify({'updated_items': updated_items}), 200
                else:
                    return jsonify({'message': f'No se encontraron work items para el proyecto: {project.name}'}), 404

        return jsonify({'error': 'Proyecto no encontrado'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
