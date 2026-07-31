# Este archivo es para crear funciones auxiliares que se reusan
# en varias partes de la aplicación.
#
# Por ejemplo:
#   - formatear respuestas
#   - validaciones comunes
#   - lógica que se repite en varios resources


def paginate(query, page=1, per_page=10):
    items = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "total": items.total,
        "page": items.page,
        "per_page": items.per_page,
        "pages": items.pages,
        "data": [
            {"id": item.id, **{c.name: getattr(item, c.name) for c in item.__table__.columns if c.name != "id"}}
            for item in items.items
        ],
    }
