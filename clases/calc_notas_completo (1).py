
def lee_archivo(nombre: str = "notas.csv") -> str | None:
    """
    Lee archivo definido en nombre y retorna los contenidos como un string
    """
    try:
        with open(nombre, "r") as f:
            contenido = f.read()
    except FileNotFoundError:
        print("Archivo no existe")
        return None
    
    return contenido


def calc_nota_final(labs: list[int], e1: int, e2: int) -> float:
    """
    Calcula nota final a partir de las notas parciales de labs y examenes
    """
    prom_lab = sum(labs) / len(labs)

    nota_final = ((prom_lab * 5) + (e1 * 2.5) + (e2 * 2.5)) / 10

    return nota_final


def calc_notas_full() -> list[float]:
    notas_raw = lee_archivo()
    if not notas_raw:
        exit(1)
    
    notas_parciales = notas_raw.split("\n")

    notas_finales = list()
    for idx in range(1, len(notas_parciales)):
        if len(notas_parciales[idx]) < 1:
            continue
        fila = notas_parciales[idx].split(",")
        labs = [int(fila[i]) for i in range(1, 13)]
        e1 = int(fila[13])
        e2 = int(fila[14])
        nota_final = calc_nota_final(labs, e1, e2)
        notas_finales.append(nota_final)

    return notas_finales

if __name__ == '__main__':
    notas = calc_notas_full()

    print(f"Las primeras 5 notas finales son: {','.join([f'{notas[i]:.2f}'for i in range(5)])}")