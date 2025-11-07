# Esta es una base de datos en memoria (un simple dict).
# En producción, reemplaza esto con una conexión a Redis.
db = {
    # Almacenará los tokens mágicos generados
    # "usuario@email.com": {
    #     "token_hash": "hash_del_token",
    #     "expires": "datetime_de_expiracion",
    #     "used": False
    # }
    "magic_tokens": {}
}
