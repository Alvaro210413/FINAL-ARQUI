// ------------------------------------------
// 1. INCLUDES Y CONSTANTES
// ------------------------------------------

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_FILAS 1000
#define MAX_COLUMNAS 20
#define TOTAL_REP 1000

// ------------------------------------------
// 2. FUNCIONES DE TIEMPO (NO CAMBIA)
// ------------------------------------------

double tiempo() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

// ------------------------------------------
// 3. LECTURA DE ARCHIVO (CAMBIA SI EL CSV CAMBIA)
// ------------------------------------------

double datos[MAX_FILAS][MAX_COLUMNAS];
int filas = 0, columnas = 0;

void leer_csv(char *nombre) {
    FILE *f = fopen(nombre, "r");
    if (!f) { printf("No se puede abrir archivo\n"); exit(1); }

    char linea[500];
    fgets(linea, sizeof(linea), f); // saltar cabecera si existe

    while (fgets(linea, sizeof(linea), f)) {
        char *tok = strtok(linea, ",");
        int col = 0;
        while (tok != NULL) {
            datos[filas][col++] = atof(tok);
            tok = strtok(NULL, ",");
        }
        columnas = col;
        filas++;
    }
    fclose(f);
}

// ------------------------------------------
// 4. ANALISIS CPU-BOUND (ESTA PARTE CAMBIA)
// ------------------------------------------

void analisis_cpu() {

    // Ejemplo: procesar por columnas
    for (int c = 0; c < columnas; c++) {

        // Aquí colocas tu mean, min, max, moda o lo que pida el ejercicio
        // Ejemplo:
        // double promedio = mean_columna(c);
        // double mediana = mediana_columna(c);
        // ...
    }

    // Ejemplo: procesar por filas
    for (int i = 0; i < filas; i++) {
        // Procesamiento por alumno
        // Ejemplo:
        // double nota = calcular_fila(i);
    }
}

// ------------------------------------------
// 5. CPU SECUENCIAL (NO CAMBIA)
// ------------------------------------------

void cpu_secuencial() {
    double inicio = tiempo();
    for (int i = 0; i < TOTAL_REP; i++)
        analisis_cpu();
    printf("CPU secuencial: %.6f\n", tiempo() - inicio);
}

// ------------------------------------------
// 6. CPU CONCURRENTE (NO CAMBIA)
// ------------------------------------------

void *trabajo_hilo(void *arg) {
    int reps = *((int *)arg);
    for (int i = 0; i < reps; i++)
        analisis_cpu();
    return NULL;
}

void cpu_concurrente(int nh) {
    pthread_t h[nh];
    int reps = TOTAL_REP / nh;

    double inicio = tiempo();
    for (int i = 0; i < nh; i++)
        pthread_create(&h[i], NULL, trabajo_hilo, &reps);
    for (int i = 0; i < nh; i++)
        pthread_join(h[i], NULL);
    printf("CPU concurrente (%d hilos): %.6f\n", nh, tiempo() - inicio);
}

// ------------------------------------------
// 7. CPU PARALELA (NO CAMBIA)
// ------------------------------------------

void cpu_paralela(int np) {
    int reps = TOTAL_REP / np;

    double inicio = tiempo();

    for (int i = 0; i < np; i++) {
        if (fork() == 0) {
            for (int r = 0; r < reps; r++)
                analisis_cpu();
            exit(0);
        }
    }
    for (int i = 0; i < np; i++) wait(NULL);

    printf("CPU paralela (%d procesos): %.6f\n", np, tiempo() - inicio);
}

// ------------------------------------------
// 8. MAIN (SOLO CAMBIA EL NOMBRE DEL CSV)
//
