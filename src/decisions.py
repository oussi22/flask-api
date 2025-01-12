from flask import request
from flask_smorest import Blueprint
from flask.json import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.schemas import DecisionSchema
from src.database import Decision, db

decisions = Blueprint("decisions", __name__, url_prefix="/api/v1/decisions")


@decisions.get("/")
@decisions.response(200, DecisionSchema(many=True))
def get_decisions():
    
    formation = request.args.get('formation', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    if formation:
        decisions_query = Decision.query.filter_by(formation=formation)
    else:
        decisions_query = Decision.query

    decisions_paginated = decisions_query.with_entities(Decision.id, Decision.title, Decision.formation).paginate(page=page, per_page=per_page)

    data = []
    for decision in decisions_paginated.items:
        data.append({
            'id': decision.id,
            'title': decision.title,
            'formation': decision.formation
        })
    
    meta = {
        "page": decisions_paginated.page,
        "pages": decisions_paginated.pages,
        "total_count": decisions_paginated.total,
        "prev_page": decisions_paginated.prev_num,
        "next_page": decisions_paginated.next_num,
        'has_next': decisions_paginated.has_next,
        "has_prev": decisions_paginated.has_prev
    }
    
    return jsonify({"data": data, "meta": meta})

@decisions.get("/<string:id>")
@decisions.response(200, DecisionSchema)
#@jwt_required()
def get_decision(id):
    #current_user = get_jwt_identity()

    decision = Decision.query.filter_by(id=id).first()

    if not decision:
        return jsonify({"message" : "Item not found"})
    
    return jsonify({
            'id': decision.id,
            'title': decision.title,
            'formation': decision.formation,
            'content': decision.content
        })

@decisions.get("/search")
@decisions.response(200, DecisionSchema(many=True))
#@jwt_required()
def search_decisions():
    q = request.args.get('q', '').lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    if not q:
        return jsonify({"data": []})
    
    search_terms = q.split()
    query = Decision.query.filter(
        Decision.title.ilike(f"%{q}%") | 
        Decision.content.ilike(f"%{q}%")
    )
    
    decisions_paginated = query.paginate(page=page, per_page=per_page)
    
    data = []
    for decision in decisions_paginated.items:
        score = 0
        for term in search_terms:
            if term in decision.title.lower():
                score += 1
            if term in decision.content.lower():
                score += 1
        data.append({
            'id': decision.id,
            'title': decision.title,
            'content': decision.content,
            'score': score
        })
    
    data_sorted = sorted(data, key=lambda x: x['score'], reverse=True)
    
    meta = {
        "page": decisions_paginated.page,
        "pages": decisions_paginated.pages,
        "total_count": decisions_paginated.total,
        "prev_page": decisions_paginated.prev_num,
        "next_page": decisions_paginated.next_num,
        'has_next': decisions_paginated.has_next,
        "has_prev": decisions_paginated.has_prev
    }
    
    return jsonify({"data": data_sorted, "meta": meta})
