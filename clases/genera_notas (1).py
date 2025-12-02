from random import randint

NUM_FILAS = 200

if __name__ == '__main__':
    contenido = ""
    cabecera = f"codigo,{','.join([f"lab{i}" for i in range (1, 13)])},e1,e2\n"
    contenido += cabecera

    codigo_inicial = 20250001

    for i in range(NUM_FILAS):
        fila = f"{codigo_inicial + i}, {','.join([f"{randint(0, 20)}" for _ in range(14)])}\n"
        contenido += fila

    with open("notas.csv", "w+") as f:
        f.write(contenido)
    
