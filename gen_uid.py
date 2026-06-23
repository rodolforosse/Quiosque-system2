import uuid

# Gera um objeto UUID aleatório
id_unico = uuid.uuid4()

# Exibe o formato padrão de string (Ex: "123e4567-e89b-12d3-a456-426614174000")
print(f"UUID completo: {str(id_unico)}")

# Exibe apenas os números e letras, sem os traços (-)
print(f"UUID sem traços: {id_unico.hex}")

