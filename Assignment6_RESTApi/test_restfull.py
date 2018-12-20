from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)

calendar_appo = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    if len(calendar_appo) > 0:
        return jsonify({'tasks': calendar_appo})
    else:
        return make_response(jsonify({'error': 'No records yet'}), 404)


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in calendar_appo if task['id'] == task_id]
    if len(task) == 0:
        return make_response(jsonify({'error': 'Not found'}), 404)
        # abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    # if not request.json or not 'title' in request.json:
    if not request.json or request.values:
        return make_response(jsonify({'error': 'Can''t add!'}), 404)
    if not 'title' in request.json:
        # abort(400)
        return make_response(jsonify({'error': 'Can''t add!'}), 404)
    task = {
        'id': calendar_appo[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    calendar_appo.append(task)
    return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in calendar_appo if task['id'] == task_id]
    if len(task) == 0:
        # abort(404)
        return make_response(jsonify({'error': 'No records in the database.'}))
    # if not request.json:
    #     abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        # abort(400)
        return make_response(jsonify({'error': 'Title not in json'}))
    if 'description' in request.json and type(request.json['description']) is not unicode:
        # abort(400)
        return make_response(jsonify({'error': 'Description not in json'}))

    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in calendar_appo if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    calendar_appo.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
