def calc_nota_final(labs: list[int], e1: int, e2: int) -> float:
    """
    Calcula nota final a partir de las notas parciales de labs y examenes
    """
    prom_lab = sum(labs) / len(labs)

    nota_final = ((prom_lab * 5) + (e1 * 2.5) + (e2 * 2.5)) / 10

    return nota_final


def calc_notas_individual() -> list[float]:
    try:
        iter = 201
        notas_finales = list()
        with open("notas.csv", "r") as f:
            while iter > 0:
                iter -= 1
                fila = f.readline()
                if len(fila) < 1 or "codigo" in fila:
                    continue
                fila = fila.split(",")
                labs = [int(fila[i]) for i in range(1, 13)]
                e1 = int(fila[13])
                e2 = int(fila[14])
                nota_final = calc_nota_final(labs, e1, e2)
                notas_finales.append(nota_final)
        
        return notas_finales
    except FileNotFoundError:
        print("Archivo no existe")
        exit(1)

if __name__ == '__main__':
    notas = calc_notas_individual()

    print(f"Las primeras 5 notas finales son: {','.join([f'{notas[i]:.2f}'for i in range(5)])}")
